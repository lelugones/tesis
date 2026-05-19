import uuid
import time
import logging
from datetime import datetime
from src.drivers.mcp_client import MCPClient
from src.agents.extractor.fetcher import ExtractorAgent
from src.agents.transformador.refiner import TransformadorAgent
from src.agents.cargador.writer import CargadorAgent
from src.utils.contracts import validate_coordinador_payload

logger = logging.getLogger(__name__)

class CoordinadorAgent:
    """Orchestrates the entire ETL workflow, handling MCP handshakes, error retries, and audit logging."""
    
    def __init__(self, secretaria_cmd: str = "python", secretaria_args: list[str] | None = None, 
                 tais_dm_cmd: str = "python", tais_dm_args: list[str] | None = None):
        self.secretaria_cmd = secretaria_cmd
        self.secretaria_args = secretaria_args or ["-m", "src.drivers.secretaria_mcp_server"]
        self.tais_dm_cmd = tais_dm_cmd
        self.tais_dm_args = tais_dm_args or ["-m", "src.drivers.tais_dm_mcp_server"]
        
        self.secretaria_client: MCPClient | None = None
        self.tais_dm_client: MCPClient | None = None

    def run_etl(self, start_date: datetime, end_date: datetime, execution_mode: str = "incremental", force: bool = False, max_retries: int = 3, initial_backoff: float = 0.1) -> str:
        """Alias for backwards compatibility if run_etl is called."""
        return self.run(execution_mode, force, max_retries, initial_backoff, _forced_start=start_date, _forced_end=end_date)

    def run(self, execution_mode: str = "incremental", force: bool = False, max_retries: int = 3, initial_backoff: float = 0.1, _forced_start: datetime | None = None, _forced_end: datetime | None = None) -> str:
        """Executes the orchestrator flow with exponential backoff retry and audit persistence."""
        start_time = datetime.now()
        batch_id = str(uuid.uuid4())
        logger.info(f"CoordinadorAgent: Initiating ETL pipeline. Batch ID: {batch_id}")
        
        try:
            # Conectar clientes MCP
            self.secretaria_client = MCPClient(self.secretaria_cmd, self.secretaria_args)
            self.secretaria_client.connect()
            
            self.tais_dm_client = MCPClient(self.tais_dm_cmd, self.tais_dm_args)
            self.tais_dm_client.connect()
            
            self.extractor = ExtractorAgent(self.secretaria_client)
            self.transformador = TransformadorAgent(None) # Ya no necesita DBConnectionManager
            self.cargador = CargadorAgent(self.tais_dm_client)
            
            # 1. Determine incremental window range
            start_date = _forced_start or datetime(1970, 1, 1, 0, 0)
            end_date = _forced_end or datetime.now()
            
            if execution_mode == "incremental" and not force and not _forced_start:
                last_date = self._get_last_successful_run_date()
                if last_date:
                    start_date = last_date
                    
            # Validate parameters against coordinator contract
            validate_coordinador_payload({
                "batch_id": batch_id,
                "execution_mode": execution_mode,
                "target_period_start": start_date.isoformat(),
                "target_period_end": end_date.isoformat(),
                "force_execution": force
            })
            
            # 2. Main orchestration loop with retry logic
            attempt = 0
            raw_data = None
            refined_data = None
            
            while True:
                try:
                    logger.info(f"CoordinadorAgent: Starting execution attempt {attempt + 1} of {max_retries + 1}...")
                    
                    # Step A: Extract
                    raw_data = self.extractor.extract(start_date, end_date)
                    
                    # Step B: Transform
                    refined_data = self.transformador.transform(
                        raw_data["df_persona"],
                        raw_data["df_familia"],
                        raw_data["df_tarjeta"]
                    )
                    
                    # Step C: Load
                    self.cargador.load(
                        batch_id,
                        refined_data["df_dimBeneficiarios"],
                        refined_data["df_dimProgramas"],
                        refined_data["df_factPolíticasAlimentarias"],
                        refined_data["df_curacion_geografica"]
                    )
                    
                    # Persist SUCCESS execution audit log
                    self._write_audit_log(
                        batch_id=batch_id,
                        start_time=start_time,
                        end_time=datetime.now(),
                        mode=execution_mode,
                        processed=len(refined_data["df_dimBeneficiarios"]),
                        discarded=len(refined_data["df_curacion_geografica"]),
                        status="SUCCESS"
                    )
                    
                    logger.info(f"CoordinadorAgent: Batch {batch_id} completed successfully in attempt {attempt + 1}!")
                    return batch_id
                    
                except Exception as e:
                    attempt += 1
                    logger.error(f"CoordinadorAgent: Exception encountered on attempt {attempt}: {str(e)}")
                    
                    if attempt <= max_retries:
                        sleep_time = initial_backoff * (2 ** (attempt - 1))
                        logger.info(f"CoordinadorAgent: Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        self._write_audit_log(
                            batch_id=batch_id,
                            start_time=start_time,
                            end_time=datetime.now(),
                            mode=execution_mode,
                            processed=0,
                            discarded=0,
                            status="FAILED",
                            error_msg=str(e)
                        )
                        raise RuntimeError(f"ETL Execution failed after {max_retries + 1} attempts: {str(e)}")
        finally:
            if self.secretaria_client:
                self.secretaria_client.disconnect()
            if self.tais_dm_client:
                self.tais_dm_client.disconnect()

    def _get_last_successful_run_date(self) -> datetime | None:
        """Retrieves the last successful run date from registro_ejecuciones table in OLAP via MCP."""
        if self.tais_dm_client is None:
            return None
        try:
            res = self.tais_dm_client.call_tool("get_incremental_data", {
                "table_name": "registro_ejecuciones_status",
                "start_date": "1970-01-01T00:00:00",
                "end_date": "2099-01-01T00:00:00",
                "cursor_value": 0,
                "page_size": 1
            })
            if not isinstance(res, dict):
                logger.warning(f"CoordinadorAgent: Unexpected response type from MCP tool: {type(res)}")
                records = []
            else:
                records = res.get("records", [])
            if records and "ended_at" in records[0]:
                val = records[0]["ended_at"]
                if isinstance(val, str):
                    return datetime.fromisoformat(val)
                return val
            return None
        except Exception as e:
            logger.warning(f"Failed to query last successful execution run via MCP: {str(e)}")
            return None

    def _write_audit_log(self, batch_id: str, start_time: datetime, end_time: datetime, mode: str, 
                        processed: int, discarded: int, status: str, error_msg: str | None = None) -> None:
        """Writes execution audit metrics in the registro_ejecuciones metadata table via MCP."""
        if self.tais_dm_client is None:
            return
        try:
            self.tais_dm_client.call_tool("load_dimension", {
                "dim_name": "registro_ejecuciones",
                "records": [{
                    "batch_id": batch_id,
                    "started_at": start_time.isoformat(),
                    "ended_at": end_time.isoformat(),
                    "records_extracted": processed + discarded,
                    "records_loaded": processed,
                    "status": status,
                    "error_details": error_msg
                }]
            })
        except Exception as e:
            logger.critical(f"FATAL: Failed to write audit executions record via MCP: {str(e)}")

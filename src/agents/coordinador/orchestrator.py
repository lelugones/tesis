import uuid
import time
import logging
from datetime import datetime
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.agents.extractor.fetcher import ExtractorAgent
from src.agents.transformador.refiner import TransformadorAgent
from src.agents.cargador.writer import CargadorAgent
from src.utils.contracts import validate_coordinador_payload

logger = logging.getLogger(__name__)

class CoordinadorAgent:
    """Orchestrates the entire ETL workflow, handling agent handshakes, error retries, and audit logging."""
    
    def __init__(self, connection_manager: DBConnectionManager):
        self.connection_manager = connection_manager
        self.extractor = ExtractorAgent(connection_manager)
        self.transformador = TransformadorAgent(connection_manager)
        self.cargador = CargadorAgent(connection_manager)

    def run(self, execution_mode: str = "incremental", force: bool = False, max_retries: int = 3, initial_backoff: float = 0.1) -> str:
        """Executes the orchestrator flow with exponential backoff retry and audit persistence."""
        start_time = datetime.now()
        batch_id = str(uuid.uuid4())
        logger.info(f"CoordinadorAgent: Initiating ETL pipeline. Batch ID: {batch_id}")
        
        # 1. Determine incremental window range
        start_date = datetime(1970, 1, 1, 0, 0)
        end_date = datetime.now()
        
        if execution_mode == "incremental" and not force:
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
                    # Calculate exponential backoff sleep: initial_backoff * (2 ** retry_index)
                    sleep_time = initial_backoff * (2 ** (attempt - 1))
                    logger.info(f"CoordinadorAgent: Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    # Log final failure to database (T022 / ASSERT-COORD-03)
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

    def _get_last_successful_run_date(self) -> datetime:
        """Retrieves the last successful run date from registro_ejecuciones table in OLAP."""
        session = self.connection_manager.get_olap_session()
        try:
            query = text("SELECT MAX(ended_at) FROM registro_ejecuciones WHERE status = 'SUCCESS'")
            result = session.execute(query).scalar()
            if result:
                if isinstance(result, str):
                    return datetime.fromisoformat(result)
                return result
            return None
        except Exception as e:
            logger.warning(f"Failed to query last successful execution run: {str(e)}")
            return None
        finally:
            session.close()

    def _write_audit_log(self, batch_id: str, start_time: datetime, end_time: datetime, mode: str, 
                        processed: int, discarded: int, status: str, error_msg: str = None) -> None:
        """Writes execution audit metrics in the registro_ejecuciones metadata table."""
        session = self.connection_manager.get_olap_session()
        try:
            # We open an independent write transaction
            with session.begin():
                session.execute(
                    text(
                        "INSERT INTO registro_ejecuciones (batch_id, started_at, ended_at, "
                        "records_extracted, records_loaded, status, error_details) "
                        "VALUES (:batch, :start, :end, :extracted, :loaded, :status, :err)"
                    ),
                    {
                        "batch": batch_id,
                        "start": start_time,
                        "end": end_time,
                        "extracted": processed + discarded,
                        "loaded": processed,
                        "status": status,
                        "err": error_msg
                    }
                )
        except Exception as e:
            logger.critical(f"FATAL: Failed to write audit executions record: {str(e)}")
        finally:
            session.close()

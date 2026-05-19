import logging
from src.drivers.mcp_client import MCPClient
from src.utils.logging import LoadError
from src.utils.contracts import validate_cargador_payload

logger = logging.getLogger(__name__)

class CargadorAgent:
    """Consumes cleaned dimensional payloads and persists them into the TAIS_DM OLAP Data Mart via MCP."""
    
    def __init__(self, connection_manager: MCPClient):
        self.connection_manager = connection_manager

    def load(self, batch_id: str, beneficiarios: list, programas: list, facts: list, curaciones: list | None = None) -> None:
        """Sends dimensions and facts to the MCP server for atomic load."""
        logger.info(f"CargadorAgent: Starting persistence phase via MCP for batch_id: {batch_id}")
        
        # Validate data contracts first
        validate_cargador_payload(beneficiarios, programas, facts)
        
        try:
            # A. PERSIST dimBeneficiarios
            if beneficiarios:
                self.connection_manager.call_tool("load_dimension", {
                    "dim_name": "dimBeneficiarios",
                    "records": beneficiarios
                })
                
            # B. PERSIST dimProgramas
            if programas:
                self.connection_manager.call_tool("load_dimension", {
                    "dim_name": "dimProgramas",
                    "records": programas
                })
                
            # C & D. PERSIST Facts and dimTiempo
            if facts:
                # El servidor MCP se encargará de resolver las Surrogate Keys (sk) e insertar
                # dimTiempo si no existe. Le pasamos el batch_id como lote.
                for f in facts:
                    f["tote_lote"] = batch_id
                    
                self.connection_manager.call_tool("load_fact", {
                    "fact_name": "factPolíticasAlimentarias",
                    "records": facts
                })
                
            # E. PERSIST curacion_geografica discards if present
            if curaciones:
                for c in curaciones:
                    c["batch_id"] = batch_id
                self.connection_manager.call_tool("load_dimension", {
                    "dim_name": "curacion_geografica",
                    "records": curaciones
                })
            
            logger.info("CargadorAgent: Persistence transactions via MCP completed successfully.")
            
        except Exception as e:
            logger.error(f"CargadorAgent: MCP transaction failed: {str(e)}")
            raise LoadError(f"Cargador persistence failed: {str(e)}")

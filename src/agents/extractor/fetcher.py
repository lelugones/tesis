import time
import logging
from datetime import datetime
from decimal import Decimal
from src.drivers.mcp_client import MCPClient
from src.utils.logging import ExtractionError
from src.utils.contracts import validate_extractor_payload

logger = logging.getLogger(__name__)

class ExtractorAgent:
    """Extracts incremental updates from OLTP (Secretaria) with paginated chunking using MCP."""
    
    def __init__(self, connection_manager: MCPClient, page_size: int = 5000):
        self.connection_manager = connection_manager  # Now an MCPClient instance
        self.page_size = page_size

    def extract(self, start_date: datetime, end_date: datetime) -> dict:
        """Extracts Persona, Familia, and Tarjeta tables incrementally via MCP."""
        logger.info(f"ExtractorAgent: Starting incremental extraction [{start_date} to {end_date}]")
        
        try:
            # Extract data from Persona table
            personas = self._extract_table("Persona", start_date, end_date)
            # Extract data from Familia table
            familias = self._extract_table("Familia", start_date, end_date)
            # Extract data from Tarjeta table
            tarjetas = self._extract_table("Tarjeta", start_date, end_date)
            
            # Map decimal conversions (ASSERT-EXT-02)
            for p in personas:
                if "ingresos_estimados" in p and p["ingresos_estimados"] is not None:
                    p["ingresos_estimados"] = Decimal(str(p["ingresos_estimados"]))
            for t in tarjetas:
                if "monto_asignado" in t and t["monto_asignado"] is not None:
                    t["monto_asignado"] = Decimal(str(t["monto_asignado"]))
            
            # Validate output payload contract
            validate_extractor_payload(personas, familias, tarjetas)
            
            logger.info(
                f"ExtractorAgent: Extracted {len(personas)} personas, "
                f"{len(familias)} familias, {len(tarjetas)} tarjetas successfully."
            )
            
            return {
                "df_persona": personas,
                "df_familia": familias,
                "df_tarjeta": tarjetas
            }
            
        except Exception as e:
            logger.error(f"ExtractorAgent failed: {str(e)}")
            raise ExtractionError(f"Extraction execution failed: {str(e)}")

    def _extract_table(self, table_name: str, start_date: datetime, end_date: datetime) -> list:
        """Helper to retrieve table rows with watermark pagination over MCP stdio transport."""
        all_records = []
        cursor_value = 0
        
        while True:
            # MCP tool payload
            arguments = {
                "table_name": table_name,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "cursor_value": cursor_value,
                "page_size": self.page_size
            }
            
            response = self.connection_manager.call_tool("get_incremental_data", arguments)
            
            if not isinstance(response, dict):
                logger.warning(f"ExtractorAgent: Unexpected response type from get_incremental_data: {type(response)}")
                break
            
            records = response.get("records", [])
            next_cursor = response.get("next_cursor", cursor_value)
            
            if not records:
                break
                
            all_records.extend(records)
            
            if len(records) < self.page_size:
                break
                
            cursor_value = next_cursor
            
            # Throttling transition sleep (ASSERT-EXT-03)
            logger.info(f"ExtractorAgent: Sleeping 500ms after fetching MCP page for {table_name}")
            time.sleep(0.5)
            
        return all_records

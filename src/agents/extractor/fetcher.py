import time
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.utils.logging import ExtractionError
from src.utils.contracts import validate_extractor_payload

logger = logging.getLogger(__name__)

class ExtractorAgent:
    """Extracts incremental updates from OLTP (Secretaria) with paginated chunking and throttling."""
    
    def __init__(self, connection_manager: DBConnectionManager, page_size: int = 5000):
        self.connection_manager = connection_manager
        self.page_size = page_size

    def extract(self, start_date: datetime, end_date: datetime) -> dict:
        """Extracts Persona, Familia, and Tarjeta tables incrementally."""
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
                p["ingresos_estimados"] = Decimal(str(p["ingresos_estimados"]))
            for t in tarjetas:
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
        """Helper to retrieve table rows with paginated chunk limits and throttling (time.sleep)."""
        session = self.connection_manager.get_oltp_session()
        all_records = []
        offset = 0
        
        try:
            while True:
                # Build paginated query
                query = text(
                    f"SELECT * FROM {table_name} "
                    f"WHERE fecha_modificacion >= :start_date AND fecha_modificacion <= :end_date "
                    f"LIMIT :limit OFFSET :offset"
                )
                
                result = session.execute(
                    query,
                    {"start_date": start_date, "end_date": end_date, "limit": self.page_size, "offset": offset}
                ).fetchall()
                
                if not result:
                    break
                
                # Convert list of rows to list of dicts
                # In SQLAlchemy 2.0, result row is mapping-like
                for row in result:
                    all_records.append(dict(row._mapping))
                
                # Check if we retrieved a full page (meaning there might be another page)
                if len(result) < self.page_size:
                    break
                
                # Throttling transition sleep (ASSERT-EXT-03)
                logger.info(f"ExtractorAgent: Sleeping 500ms after fetching page offset {offset} for {table_name}")
                time.sleep(0.5)
                offset += self.page_size
                
            return all_records
            
        finally:
            session.close()

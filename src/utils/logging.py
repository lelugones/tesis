import logging
import sys

# Configure standard structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("TAIS_DM_ETL")

# ==========================================
# Custom Pipeline Exceptions
# ==========================================

class ETLException(Exception):
    """Base exception for all ETL pipeline operations."""
    pass

class ExtractionError(ETLException):
    """Raised when there is an error extracting data from the OLTP source."""
    pass

class ValidationError(ETLException):
    """Raised when incoming payloads violate schemas or data contracts."""
    pass

class TransformationError(ETLException):
    """Raised when transformation normalizations or mappings fail."""
    pass

class LoadError(ETLException):
    """Raised when loading into the analítica OLAP target fails."""
    pass

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class DBConnectionManager:
    """Manages connections to OLTP (Secretaria) and OLAP (TAIS_DM) databases."""
    
    def __init__(self, oltp_url: str, olap_url: str):
        self.oltp_engine = create_engine(oltp_url)
        self.olap_engine = create_engine(olap_url)
        
        self.oltp_session_factory = sessionmaker(bind=self.oltp_engine)
        self.olap_session_factory = sessionmaker(bind=self.olap_engine)
        logger.info("Database engines and session factories initialized successfully.")

    def get_oltp_session(self):
        """Returns a session to the transactional database (Secretaria)."""
        return self.oltp_session_factory()

    def get_olap_session(self):
        """Returns a session to the Data Mart database (TAIS_DM)."""
        return self.olap_session_factory()

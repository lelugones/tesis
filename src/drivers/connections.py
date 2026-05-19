import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class DBConnectionManager:
    """Manages pool connections to OLTP (Secretaria) and OLAP (TAIS_DM) databases for tests and initialization.
    Defaults to SQLite in-memory for development and TDD testing environments.
    """
    
    def __init__(self, oltp_url: str | None = None, olap_url: str | None = None):
        self.oltp_url = oltp_url or os.environ.get(
            "OLTP_DB_CONN",
            "sqlite:///:memory:"
        )
        
        self.olap_url = olap_url or os.environ.get(
            "OLAP_DB_CONN",
            "sqlite:///:memory:"
        )
        
        self.oltp_engine = create_engine(
            self.oltp_url,
            pool_pre_ping=True,
            echo=False
        )
        self.olap_engine = create_engine(
            self.olap_url,
            pool_pre_ping=True,
            echo=False
        )
        
        self.oltp_session_factory = sessionmaker(bind=self.oltp_engine)
        self.olap_session_factory = sessionmaker(bind=self.olap_engine)
        
        logger.info(
            "Database connection manager initialized. "
            f"OLTP: {self.oltp_url} | OLAP: {self.olap_url}"
        )

    def get_oltp_session(self):
        """Returns a new session to the transactional database (Secretaria)."""
        return self.oltp_session_factory()

    def get_olap_session(self):
        """Returns a new session to the Data Mart database (TAIS_DM)."""
        return self.olap_session_factory()

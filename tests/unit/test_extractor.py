import pytest
import time
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases, oltp_metadata
from src.agents.extractor.fetcher import ExtractorAgent

@pytest.fixture
def connection_manager():
    """Returns a fresh, isolated DBConnectionManager pointing to SQLite in-memory databases."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_extractor_incremental_filter(connection_manager):
    """ASSERT-EXT-01: Extractor should retrieve only modified records since last execution date."""
    session = connection_manager.get_oltp_session()
    
    # Seed data: one older persona, one newer persona
    session.execute(
        oltp_metadata.tables['Persona'].insert(),
        [
            {"id": 1, "nombre": "Juan Perez", "ingresos_estimados": 45000.00, "fecha_modificacion": datetime(2026, 5, 10, 12, 0), "municipio_id": 1},
            {"id": 2, "nombre": "Maria Gomez", "ingresos_estimados": 60000.00, "fecha_modificacion": datetime(2026, 5, 18, 15, 30), "municipio_id": 2}
        ]
    )
    session.commit()
    session.close()

    agent = ExtractorAgent(connection_manager)
    
    # Query with target start date set to 2026-05-15
    start_date = datetime(2026, 5, 15, 0, 0)
    end_date = datetime(2026, 5, 19, 0, 0)
    
    payload = agent.extract(start_date, end_date)
    
    # Should only retrieve Maria Gomez (ID: 2)
    assert len(payload["df_persona"]) == 1
    assert payload["df_persona"][0]["id"] == 2
    assert payload["df_persona"][0]["nombre"] == "Maria Gomez"

def test_extractor_decimal_mapping(connection_manager):
    """ASSERT-EXT-02: Extractor must map all currency fields to decimal.Decimal."""
    session = connection_manager.get_oltp_session()
    session.execute(
        oltp_metadata.tables['Persona'].insert(),
        {"id": 10, "nombre": "Carlos", "ingresos_estimados": 125000.55, "fecha_modificacion": datetime.now(), "municipio_id": 1}
    )
    session.execute(
        oltp_metadata.tables['Tarjeta'].insert(),
        {"id": 20, "persona_id": 10, "activa": True, "monto_asignado": 15000.75, "fecha_modificacion": datetime.now()}
    )
    session.commit()
    session.close()

    agent = ExtractorAgent(connection_manager)
    payload = agent.extract(datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=1))
    
    # Asserting Decimal mapping
    assert isinstance(payload["df_persona"][0]["ingresos_estimados"], Decimal)
    assert payload["df_persona"][0]["ingresos_estimados"] == Decimal("125000.55")
    
    assert isinstance(payload["df_tarjeta"][0]["monto_asignado"], Decimal)
    assert payload["df_tarjeta"][0]["monto_asignado"] == Decimal("15000.75")

@patch("time.sleep")
def test_extractor_chunking_and_throttling(mock_sleep, connection_manager):
    """ASSERT-EXT-03: Extractor must chunk queries and throttle by sleeping between pages."""
    session = connection_manager.get_oltp_session()
    
    # Insert 15,000 mock personas to trigger throttling (page size = 5,000)
    personas = [
        {
            "id": i,
            "nombre": f"Persona {i}",
            "ingresos_estimados": 10000.00,
            "fecha_modificacion": datetime.now(),
            "municipio_id": 1
        }
        for i in range(1, 15001)
    ]
    session.execute(oltp_metadata.tables['Persona'].insert(), personas)
    session.commit()
    session.close()

    # Create agent with page size override = 5000
    agent = ExtractorAgent(connection_manager, page_size=5000)
    
    payload = agent.extract(datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=1))
    
    assert len(payload["df_persona"]) == 15000
    # Throttling triggers on pagination transitions. 15,000 items / 5,000 per page = 3 pages.
    # Page transitions: from page 1 to 2, and page 2 to 3 = 2 sleep pauses.
    assert mock_sleep.call_count == 3
    mock_sleep.assert_called_with(0.5)

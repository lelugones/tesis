import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases
from src.agents.coordinador.orchestrator import CoordinadorAgent
from src.utils.logging import ValidationError

@pytest.fixture
def connection_manager():
    """Returns DBConnectionManager pointing to SQLite in-memory."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_coordinador_uuid_generation(connection_manager):
    """ASSERT-COORD-01: Coordinator generates a valid UUID v4 batch id."""
    agent = CoordinadorAgent(connection_manager)
    
    # Mock extract, transform, load to succeed immediately
    with patch("src.agents.extractor.fetcher.ExtractorAgent.extract", return_value={"df_persona": [], "df_familia": [], "df_tarjeta": []}), \
         patch("src.agents.transformador.refiner.TransformadorAgent.transform", return_value={"df_dimBeneficiarios": [], "df_dimProgramas": [], "df_factPolíticasAlimentarias": [], "df_curacion_geografica": []}), \
         patch("src.agents.cargador.writer.CargadorAgent.load") as mock_load:
         
        batch_id = agent.run()
        
        # Verify batch_id is valid UUID
        val = uuid.UUID(batch_id)
        assert val.version == 4
        
        # Verify it was passed to the Cargador
        mock_load.assert_called_once()
        assert mock_load.call_args[0][0] == batch_id

@patch("time.sleep")
def test_coordinador_retry_policy_with_backoff(mock_sleep, connection_manager):
    """ASSERT-COORD-02: Coordinator executes exponential backoff retries upon failures."""
    agent = CoordinadorAgent(connection_manager)
    
    # Mock extractor to raise an exception
    with patch("src.agents.extractor.fetcher.ExtractorAgent.extract", side_effect=RuntimeError("OLTP Offline")) as mock_extract:
        with pytest.raises(Exception) as exc_info:
            agent.run(max_retries=3, initial_backoff=0.2)
            
        assert "OLTP Offline" in str(exc_info.value)
        # Should try 4 times total: 1 initial + 3 retries
        assert mock_extract.call_count == 4
        
        # Verify exponential backoff sleep calls:
        # Retry 1: 0.2s, Retry 2: 0.4s, Retry 3: 0.8s
        assert mock_sleep.call_count == 3
        mock_sleep.assert_any_call(0.2)
        mock_sleep.assert_any_call(0.4)
        mock_sleep.assert_any_call(0.8)

def test_coordinador_audit_writes(connection_manager):
    """ASSERT-COORD-03: Coordinator writes execution summaries to registro_ejecuciones."""
    agent = CoordinadorAgent(connection_manager)
    
    # 1. Success Run Audit Write
    with patch("src.agents.extractor.fetcher.ExtractorAgent.extract", return_value={"df_persona": [{"id": 1}], "df_familia": [], "df_tarjeta": []}), \
         patch("src.agents.transformador.refiner.TransformadorAgent.transform", return_value={
             "df_dimBeneficiarios": [{"id_persona_oltp": 1}], 
             "df_dimProgramas": [], 
             "df_factPolíticasAlimentarias": [{"id_persona_oltp": 1}], 
             "df_curacion_geografica": [{"id_persona_oltp": 2, "provincia_capturada": "Jujuy", "municipio_invalido": "San Salvador", "fecha_descarte": datetime.now()}]
         }), \
         patch("src.agents.cargador.writer.CargadorAgent.load") as mock_load:
         
        batch_id = agent.run()
        
        session = connection_manager.get_olap_session()
        # Verify success row written
        row = session.execute(text("SELECT batch_id, status, records_extracted, records_loaded FROM registro_ejecuciones WHERE batch_id = :b"), {"b": batch_id}).fetchone()
        assert row is not None
        assert row[1] == "SUCCESS"
        assert row[2] == 2 # records_extracted = 1 processed + 1 discarded = 2
        assert row[3] == 1 # records_loaded = 1 processed
        session.close()

    # 2. Failed Run Audit Write
    with patch("src.agents.extractor.fetcher.ExtractorAgent.extract", side_effect=RuntimeError("Contract violation")):
        with pytest.raises(Exception):
            agent.run(max_retries=0)
            
        session = connection_manager.get_olap_session()
        # Verify failed row written
        failed_row = session.execute(text("SELECT status, error_details FROM registro_ejecuciones WHERE status = 'FAILED'")).fetchone()
        assert failed_row is not None
        assert "Contract violation" in failed_row[1]
        session.close()

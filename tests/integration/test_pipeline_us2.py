import pytest
from datetime import datetime
from sqlalchemy import text
from unittest.mock import patch, MagicMock
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases, oltp_metadata
from src.agents.coordinador.orchestrator import CoordinadorAgent

@pytest.fixture
def connection_manager():
    """Returns DBConnectionManager pointing to SQLite in-memory."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_integration_pipeline_transactional_rollback(connection_manager):
    """US2 Integration: Validates complete transactional rollback of dimension inserts on facts failure."""
    oltp_session = connection_manager.get_oltp_session()
    
    # 1. Seed OLTP data
    oltp_session.execute(oltp_metadata.tables['Municipio'].insert(), {"id": 1, "nombre": "Orán"})
    oltp_session.execute(
        oltp_metadata.tables['Persona'].insert(),
        {"id": 10, "nombre": "Estela Salta", "ingresos_estimados": 55000.00, "fecha_modificacion": datetime.now(), "municipio_id": 1}
    )
    oltp_session.execute(oltp_metadata.tables['Familia'].insert(), {"id": 10, "indice_vulnera": 8.0, "fecha_modificacion": datetime.now()})
    oltp_session.execute(
        oltp_metadata.tables['Tarjeta'].insert(),
        {"id": 100, "persona_id": 10, "activa": True, "monto_asignado": 15000.00, "fecha_modificacion": datetime.now()}
    )
    oltp_session.commit()
    oltp_session.close()

    # Seed Geografia dimension in OLAP
    olap_session = connection_manager.get_olap_session()
    olap_session.execute(text(
        "INSERT INTO dimGeografia (sk_geografia, id_municipio_oltp, localidad, municipio, departamento, provincia) "
        "VALUES (50, 1, 'Orán', 'Orán', 'Orán', 'Salta')"
    ))
    olap_session.commit()
    olap_session.close()

    coordinator = CoordinadorAgent(connection_manager)
    
    # Mocking the session.execute on Cargador's Fact loading step to raise an Exception, forcing transactional rollback
    original_load = coordinator.cargador.load
    
    def failing_load(*args, **kwargs):
        # We let the method execute normally but we force an exception inside it
        # Let's mock load to raise a custom load error mid-way
        raise RuntimeError("Integrity Constraint Violated - Mid load crash")
        
    with patch.object(coordinator.cargador, "load", side_effect=failing_load):
        with pytest.raises(Exception) as exc:
            coordinator.run(max_retries=0)
            
        assert "Integrity Constraint Violated" in str(exc.value)

    # Verify that NO dimension updates or facts were committed to OLAP!
    olap_session = connection_manager.get_olap_session()
    
    # dimBeneficiarios must be empty because the transaction was rolled back!
    ben_rows = olap_session.execute(text("SELECT sk_beneficiario, nombre_completo FROM dimBeneficiarios")).fetchall()
    assert len(ben_rows) == 0
    
    # factPolíticasAlimentarias must be empty
    fact_rows = olap_session.execute(text("SELECT id_hecho FROM factPolíticasAlimentarias")).fetchall()
    assert len(fact_rows) == 0

    # There should, however, be a record in registro_ejecuciones detailing the failure
    exec_row = olap_session.execute(text("SELECT status, error_details FROM registro_ejecuciones")).fetchone()
    assert exec_row is not None
    assert exec_row[0] == "FAILED"
    assert "Integrity Constraint Violated" in exec_row[1]
    
    olap_session.close()

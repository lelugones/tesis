import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases, olap_metadata
from src.agents.cargador.writer import CargadorAgent

@pytest.fixture
def connection_manager():
    """Returns DBConnectionManager pointing to SQLite in-memory."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_cargador_dimension_upsert_idempotency(connection_manager):
    """ASSERT-LOAD-01: Cargador executes Upserts to maintain dimension idempotency without duplicates."""
    agent = CargadorAgent(connection_manager)
    
    beneficiarios = [
        {"id_persona_oltp": 1, "nombre_completo": "Juan Perez", "grupo_etario": "Adulto", "tarjeta_activa": True, "ingresos_estimados": 45000.00}
    ]
    programas = [
        {"id_programa_oltp": 101, "nombre_programa": "Nutrir", "estado": "Activo"}
    ]
    facts = []

    # Run load 1
    agent.load("batch-1", beneficiarios, programas, facts)
    
    session = connection_manager.get_olap_session()
    # Check 1 record created
    rows = session.execute(text("SELECT sk_beneficiario, nombre_completo, ingresos_estimados FROM dimBeneficiarios")).fetchall()
    assert len(rows) == 1
    assert rows[0][1] == "Juan Perez"
    assert float(rows[0][2]) == 45000.00
    
    # Run load 2 with updated income for same id_persona_oltp
    beneficiarios_updated = [
        {"id_persona_oltp": 1, "nombre_completo": "Juan Perez", "grupo_etario": "Adulto", "tarjeta_activa": True, "ingresos_estimados": 55000.00}
    ]
    agent.load("batch-2", beneficiarios_updated, programas, facts)
    
    # Re-query and check that NO duplicates were created and the income was updated (Upsert)
    rows_updated = session.execute(text("SELECT sk_beneficiario, nombre_completo, ingresos_estimados FROM dimBeneficiarios")).fetchall()
    assert len(rows_updated) == 1
    assert float(rows_updated[0][2]) == 55000.00
    session.close()

def test_cargador_surrogate_key_mapping(connection_manager):
    """ASSERT-LOAD-02: Cargador maps facts OLTP IDs to generated Surrogate Keys."""
    agent = CargadorAgent(connection_manager)
    
    beneficiarios = [
        {"id_persona_oltp": 5, "nombre_completo": "Carlos Perez", "grupo_etario": "Adulto", "tarjeta_activa": True, "ingresos_estimados": 80000.00}
    ]
    programas = [
        {"id_programa_oltp": 202, "nombre_programa": "Tarjeta Social", "estado": "Activo"}
    ]
    
    # Pre-populate Geografia dimension so we can mock its resolution
    session = connection_manager.get_olap_session()
    session.execute(text(
        "INSERT INTO dimGeografia (sk_geografia, id_municipio_oltp, localidad, municipio, departamento, provincia) "
        "VALUES (10, 15, 'Oran', 'Oran', 'Oran', 'Salta')"
    ))
    session.commit()
    session.close()

    # Fact payload with OLTP IDs
    facts = [
        {
            "id_persona_oltp": 5,
            "id_programa_oltp": 202,
            "id_municipio_oltp": 15,
            "fecha_transaccion": datetime(2026, 5, 18, 12, 0),
            "admPersonas": 1,
            "efiProgramas": 1.0,
            "vulneraSocial": 0.65,
            "participaMunicipal": 100.00,
            "usoTarjetas": 5000.00
        }
    ]

    agent.load("batch-1", beneficiarios, programas, facts)
    
    session = connection_manager.get_olap_session()
    # Check that surrogate keys are resolved correctly in the facts table
    fact_rows = session.execute(text("SELECT sk_beneficiario, sk_programa, sk_geografia, sk_tiempo, vulneraSocial FROM factPolíticasAlimentarias")).fetchall()
    assert len(fact_rows) == 1
    
    sk_ben = fact_rows[0][0]
    sk_prog = fact_rows[0][1]
    sk_geo = fact_rows[0][2]
    sk_time = fact_rows[0][3]
    
    # Check dim values match
    ben = session.execute(text(f"SELECT id_persona_oltp FROM dimBeneficiarios WHERE sk_beneficiario = {sk_ben}")).fetchone()
    assert ben[0] == 5
    
    prog = session.execute(text(f"SELECT id_programa_oltp FROM dimProgramas WHERE sk_programa = {sk_prog}")).fetchone()
    assert prog[0] == 202
    
    assert sk_geo == 10
    assert sk_time == 20260518
    session.close()

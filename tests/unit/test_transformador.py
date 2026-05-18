import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases
from src.agents.transformador.refiner import TransformadorAgent
from src.utils.logging import ValidationError

@pytest.fixture
def connection_manager():
    """Returns DBConnectionManager pointing to SQLite in-memory."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_transformador_vulnera_social_normalization(connection_manager):
    """ASSERT-TRANS-01: Transformador normalizes vulnerability index to [0.00, 1.00]."""
    # Create input in-memory data
    persona_records = [
        {"id": 1, "nombre": "Juana", "ingresos_estimados": 50000.00, "fecha_modificacion": datetime.now(), "municipio_id": 1}
    ]
    familia_records = [
        {"id": 1, "indice_vulnera": 7.5, "fecha_modificacion": datetime.now()} # indice_vulnera on scale [0, 10]
    ]
    tarjeta_records = [
        {"id": 10, "persona_id": 1, "activa": True, "monto_asignado": 12000.00, "fecha_modificacion": datetime.now()}
    ]

    agent = TransformadorAgent(connection_manager)
    
    # Mocking geographic call to return Salta
    with patch.object(agent, '_resolve_geografia', return_value={
        "sk_geografia": 101, "municipio": "Orán", "provincia": "Salta", "departamento": "Orán", "localidad": "Orán"
    }):
        output = agent.transform(persona_records, familia_records, tarjeta_records)
        
    facts = output["df_factPolíticasAlimentarias"]
    assert len(facts) == 1
    # 7.5 out of 10.0 becomes 0.75
    assert facts[0]["vulneraSocial"] == 0.75

def test_transformador_geocuration_isolation(connection_manager):
    """ASSERT-TRANS-02: Non-Salta geographies must be routed to curacion_geografica and logged."""
    persona_records = [
        {"id": 1, "nombre": "Juana (Salta)", "ingresos_estimados": 50000.00, "fecha_modificacion": datetime.now(), "municipio_id": 10},
        {"id": 2, "nombre": "Pedro (Tucuman)", "ingresos_estimados": 40000.00, "fecha_modificacion": datetime.now(), "municipio_id": 20}
    ]
    familia_records = [
        {"id": 1, "indice_vulnera": 6.0, "fecha_modificacion": datetime.now()},
        {"id": 2, "indice_vulnera": 5.0, "fecha_modificacion": datetime.now()}
    ]
    tarjeta_records = [
        {"id": 10, "persona_id": 1, "activa": True, "monto_asignado": 10000.00, "fecha_modificacion": datetime.now()},
        {"id": 20, "persona_id": 2, "activa": True, "monto_asignado": 8000.00, "fecha_modificacion": datetime.now()}
    ]

    agent = TransformadorAgent(connection_manager)
    
    # Mock geographic lookup: municipio 10 -> Salta, municipio 20 -> Tucuman
    def mock_lookup(municipio_id):
        if municipio_id == 10:
            return {"sk_geografia": 1, "municipio": "Metán", "provincia": "Salta", "departamento": "Metán", "localidad": "Metán"}
        else:
            return {"sk_geografia": 2, "municipio": "San Miguel", "provincia": "Tucumán", "departamento": "Capital", "localidad": "San Miguel"}
            
    with patch.object(agent, '_resolve_geografia', side_effect=mock_lookup):
        output = agent.transform(persona_records, familia_records, tarjeta_records)
        
    # Check that Tucuman (Pedro, ID: 2) was routed to geographic curations
    curations = output["df_curacion_geografica"]
    assert len(curations) == 1
    assert curations[0]["id_persona_oltp"] == 2
    assert curations[0]["provincia_capturada"] == "Tucumán"
    
    # Salta (Juana, ID: 1) processed in main dimensions and facts
    beneficiarios = output["df_dimBeneficiarios"]
    assert len(beneficiarios) == 1
    assert beneficiarios[0]["id_persona_oltp"] == 1
    
    facts = output["df_factPolíticasAlimentarias"]
    assert len(facts) == 1
    assert facts[0]["id_persona_oltp"] == 1

def test_transformador_stored_procedure_mock(connection_manager):
    """ASSERT-TRANS-03: Dimension resolution mocks database or routine mappings correctly."""
    persona_records = [
        {"id": 3, "nombre": "Sofia", "ingresos_estimados": 75000.00, "fecha_modificacion": datetime.now(), "municipio_id": 15}
    ]
    familia_records = [
        {"id": 3, "indice_vulnera": 9.0, "fecha_modificacion": datetime.now()}
    ]
    tarjeta_records = [
        {"id": 30, "persona_id": 3, "activa": False, "monto_asignado": 0.00, "fecha_modificacion": datetime.now()}
    ]

    agent = TransformadorAgent(connection_manager)
    
    # Pre-populate Geografia dimension in OLAP directly to verify lookup
    session = connection_manager.get_olap_session()
    session.execute(text(
        "INSERT INTO dimGeografia (sk_geografia, id_municipio_oltp, localidad, municipio, departamento, provincia) "
        "VALUES (99, 15, 'Cerrillos', 'Cerrillos', 'Cerrillos', 'Salta')"
    ))
    session.commit()
    session.close()
    
    geo = agent._resolve_geografia(15)
    assert geo["sk_geografia"] == 99
    assert geo["provincia"] == "Salta"

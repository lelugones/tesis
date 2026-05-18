import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.drivers.init_db import init_databases, oltp_metadata
from src.agents.extractor.fetcher import ExtractorAgent
from src.agents.transformador.refiner import TransformadorAgent
from src.agents.cargador.writer import CargadorAgent

@pytest.fixture
def connection_manager():
    """Returns DBConnectionManager pointing to SQLite in-memory."""
    manager = DBConnectionManager("sqlite:///:memory:", "sqlite:///:memory:")
    init_databases(manager)
    return manager

def test_integration_pipeline_happy_path(connection_manager):
    """US1 Integration Test: Validates incremental extract, transform, and load of valid Salta records."""
    oltp_session = connection_manager.get_oltp_session()
    
    # 1. Seed OLTP source data
    # Municipio (1 -> Orán, Salta | 2 -> Capital, Tucuman)
    oltp_session.execute(
        oltp_metadata.tables['Municipio'].insert(),
        [
            {"id": 1, "nombre": "Orán"},
            {"id": 2, "nombre": "San Miguel de Tucumán"}
        ]
    )
    # Personas: One inside Salta (Orán), one outside Salta (Tucumán)
    oltp_session.execute(
        oltp_metadata.tables['Persona'].insert(),
        [
            {"id": 10, "nombre": "Estela Salta", "ingresos_estimados": 55000.00, "fecha_modificacion": datetime.now(), "municipio_id": 1},
            {"id": 20, "nombre": "Pedro Tucuman", "ingresos_estimados": 48000.00, "fecha_modificacion": datetime.now(), "municipio_id": 2}
        ]
    )
    # Familias
    oltp_session.execute(
        oltp_metadata.tables['Familia'].insert(),
        [
            {"id": 10, "indice_vulnera": 8.0, "fecha_modificacion": datetime.now()},
            {"id": 20, "indice_vulnera": 6.5, "fecha_modificacion": datetime.now()}
        ]
    )
    # Tarjetas
    oltp_session.execute(
        oltp_metadata.tables['Tarjeta'].insert(),
        [
            {"id": 100, "persona_id": 10, "activa": True, "monto_asignado": 15000.00, "fecha_modificacion": datetime.now()},
            {"id": 200, "persona_id": 20, "activa": True, "monto_asignado": 12000.00, "fecha_modificacion": datetime.now()}
        ]
    )
    oltp_session.commit()
    oltp_session.close()

    # Seed Geografia dimension in OLAP to simulate static geography dimensions
    olap_session = connection_manager.get_olap_session()
    olap_session.execute(text(
        "INSERT INTO dimGeografia (sk_geografia, id_municipio_oltp, localidad, municipio, departamento, provincia) "
        "VALUES (50, 1, 'Orán', 'Orán', 'Orán', 'Salta')"
    ))
    olap_session.execute(text(
        "INSERT INTO dimGeografia (sk_geografia, id_municipio_oltp, localidad, municipio, departamento, provincia) "
        "VALUES (60, 2, 'San Miguel', 'San Miguel', 'Capital', 'Tucumán')"
    ))
    olap_session.commit()
    olap_session.close()

    # 2. Run Extractor
    extractor = ExtractorAgent(connection_manager)
    payload_raw = extractor.extract(datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=1))
    
    # 3. Run Transformador
    transformador = TransformadorAgent(connection_manager)
    payload_refined = transformador.transform(
        payload_raw["df_persona"],
        payload_raw["df_familia"],
        payload_raw["df_tarjeta"]
    )
    
    # 4. Run Cargador
    cargador = CargadorAgent(connection_manager)
    cargador.load(
        "batch-integration-us1",
        payload_refined["df_dimBeneficiarios"],
        payload_refined["df_dimProgramas"],
        payload_refined["df_factPolíticasAlimentarias"],
        payload_refined["df_curacion_geografica"]
    )
    
    # 5. Assertions on analytical OLAP database (TAIS_DM)
    olap_session = connection_manager.get_olap_session()
    
    # Validate dimBeneficiarios: only Estela Salta (ID: 10) was inserted since Pedro (ID: 20) was filtered out.
    ben_rows = olap_session.execute(text("SELECT id_persona_oltp, nombre_completo, ingresos_estimados FROM dimBeneficiarios")).fetchall()
    assert len(ben_rows) == 1
    assert ben_rows[0][0] == 10
    assert ben_rows[0][1] == "Estela Salta"
    assert float(ben_rows[0][2]) == 55000.00

    # Validate curacion_geografica: Pedro Tucuman (ID: 20) was correctly routed
    discard_rows = olap_session.execute(text("SELECT id_persona_oltp, provincia_capturada FROM curacion_geografica")).fetchall()
    assert len(discard_rows) == 1
    assert discard_rows[0][0] == 20
    assert discard_rows[0][1] == "Tucumán"

    # Validate factPolíticasAlimentarias: Only the facts for Estela Salta exist, and vulnerability is normalized (8.0 -> 0.8)
    fact_rows = olap_session.execute(text("SELECT sk_beneficiario, sk_geografia, vulneraSocial, usoTarjetas FROM factPolíticasAlimentarias")).fetchall()
    assert len(fact_rows) == 1
    # 8.0 vulnerability normalized to 0.8
    assert float(fact_rows[0][2]) == 0.80
    assert float(fact_rows[0][3]) == 15000.00
    olap_session.close()

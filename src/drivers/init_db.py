import logging
from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric, DateTime, Boolean, Date, ForeignKey, text
from src.drivers.connections import DBConnectionManager

logger = logging.getLogger(__name__)

# Metadata instances
oltp_metadata = MetaData()
olap_metadata = MetaData()

# ==========================================
# OLTP (Secretaria) Source Tables
# ==========================================

Table(
    'Municipio', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('nombre', String(100), nullable=False)
)

Table(
    'Persona', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('nombre', String(100), nullable=False),
    Column('ingresos_estimados', Numeric(12, 2), nullable=False),
    Column('fecha_modificacion', DateTime, nullable=False),
    Column('municipio_id', Integer, nullable=False)
)

Table(
    'Familia', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('indice_vulnera', Numeric(5, 2), nullable=False),
    Column('fecha_modificacion', DateTime, nullable=False)
)

Table(
    'Tarjeta', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('persona_id', Integer, nullable=False),
    Column('activa', Boolean, nullable=False),
    Column('monto_asignado', Numeric(12, 2), nullable=False),
    Column('fecha_modificacion', DateTime, nullable=False)
)

Table(
    'Novedad', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('programa_id', Integer, nullable=False),
    Column('fecha_modificacion', DateTime, nullable=False)
)

Table(
    'Satisfaccion', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('programa_id', Integer, nullable=False),
    Column('nota', Numeric(3, 2), nullable=False)
)

Table(
    'Transaccion', oltp_metadata,
    Column('id', Integer, primary_key=True),
    Column('tarjeta_id', Integer, nullable=False),
    Column('monto', Numeric(12, 2), nullable=False),
    Column('fecha', DateTime, nullable=False)
)

# ==========================================
# OLAP (TAIS_DM) Data Mart Tables
# ==========================================

Table(
    'registro_ejecuciones', olap_metadata,
    Column('batch_id', String(36), primary_key=True),
    Column('status', String(10), nullable=False), # SUCCESS / FAILED
    Column('records_extracted', Integer, nullable=False),
    Column('records_loaded', Integer, nullable=False),
    Column('started_at', DateTime, nullable=False),
    Column('ended_at', DateTime, nullable=False),
    Column('error_details', String(500), nullable=True)
)

Table(
    'curacion_geografica', olap_metadata,
    Column('id_descarte', Integer, primary_key=True, autoincrement=True),
    Column('id_persona_oltp', Integer, nullable=False),
    Column('municipio_invalido', String(100), nullable=True),
    Column('provincia_capturada', String(100), nullable=True),
    Column('fecha_descarte', DateTime, nullable=False),
    Column('batch_id', String(36), nullable=False)
)

Table(
    'dimBeneficiarios', olap_metadata,
    Column('sk_beneficiario', Integer, primary_key=True, autoincrement=True),
    Column('id_persona_oltp', Integer, nullable=False),
    Column('nombre_completo', String(200), nullable=False),
    Column('grupo_etario', String(20), nullable=False), # Niño, Adulto, Mayor
    Column('tarjeta_activa', Boolean, nullable=False),
    Column('ingresos_estimados', Numeric(12, 2), nullable=False)
)

Table(
    'dimProgramas', olap_metadata,
    Column('sk_programa', Integer, primary_key=True, autoincrement=True),
    Column('id_programa_oltp', Integer, nullable=False),
    Column('nombre_programa', String(100), nullable=False),
    Column('estado', String(20), nullable=False)
)

Table(
    'dimGeografia', olap_metadata,
    Column('sk_geografia', Integer, primary_key=True, autoincrement=True),
    Column('id_municipio_oltp', Integer, nullable=False),
    Column('localidad', String(100), nullable=False),
    Column('municipio', String(100), nullable=False),
    Column('departamento', String(100), nullable=False),
    Column('provincia', String(50), nullable=False) # 'Salta'
)

Table(
    'dimTiempo', olap_metadata,
    Column('sk_tiempo', Integer, primary_key=True), # YYYYMMDD
    Column('fecha', Date, nullable=False),
    Column('anio', Integer, nullable=False),
    Column('mes', Integer, nullable=False),
    Column('nombre_mes', String(20), nullable=False),
    Column('trimestre', Integer, nullable=False)
)

Table(
    'factPolíticasAlimentarias', olap_metadata,
    Column('id_hecho', Integer, primary_key=True, autoincrement=True),
    Column('sk_beneficiario', Integer, ForeignKey('dimBeneficiarios.sk_beneficiario'), nullable=False),
    Column('sk_programa', Integer, ForeignKey('dimProgramas.sk_programa'), nullable=False),
    Column('sk_geografia', Integer, ForeignKey('dimGeografia.sk_geografia'), nullable=False),
    Column('sk_tiempo', Integer, ForeignKey('dimTiempo.sk_tiempo'), nullable=False),
    Column('admPersonas', Integer, nullable=False, default=0),
    Column('efiProgramas', Numeric(5, 2), nullable=False, default=0.00),
    Column('vulneraSocial', Numeric(3, 2), nullable=False),
    Column('participaMunicipal', Numeric(5, 2), nullable=False, default=0.00),
    Column('usoTarjetas', Numeric(12, 2), nullable=False, default=0.00),
    Column('fecha_carga', DateTime, nullable=False),
    Column('agente_responsable', String(50), nullable=False),
    Column('tote_lote', String(36), nullable=False)
)

def init_databases(connection_manager: DBConnectionManager):
    """Initializes schemas on OLTP and OLAP engines."""
    logger.info("Initializing OLTP schema...")
    oltp_metadata.create_all(connection_manager.oltp_engine)
    
    logger.info("Initializing OLAP schema...")
    olap_metadata.create_all(connection_manager.olap_engine)
    
    logger.info("All schemas initialized successfully.")

import logging
from datetime import datetime
from sqlalchemy import text
from src.drivers.connections import DBConnectionManager
from src.utils.logging import LoadError
from src.utils.contracts import validate_cargador_payload

logger = logging.getLogger(__name__)

class CargadorAgent:
    """Consumes cleaned dimensional payloads and persists them into the TAIS_DM OLAP Data Mart."""
    
    def __init__(self, connection_manager: DBConnectionManager):
        self.connection_manager = connection_manager

    def load(self, batch_id: str, beneficiarios: list, programas: list, facts: list, curaciones: list = None) -> None:
        """Atomically loads dimensions, resolves surrogate keys, and writes fact tables within a transaction."""
        logger.info(f"CargadorAgent: Starting persistence phase for batch_id: {batch_id}")
        
        # Validate data contracts first
        validate_cargador_payload(beneficiarios, programas, facts)
        
        session = self.connection_manager.get_olap_session()
        
        try:
            # 1. Begin SQL Transaction (ASSERT-LOAD-03 / T020 atomic constraint)
            with session.begin():
                
                # A. PERSIST dimBeneficiarios (Upsert Logic - ASSERT-LOAD-01)
                for ben in beneficiarios:
                    existing = session.execute(
                        text("SELECT sk_beneficiario FROM dimBeneficiarios WHERE id_persona_oltp = :id"),
                        {"id": ben["id_persona_oltp"]}
                    ).fetchone()
                    
                    if existing:
                        session.execute(
                            text(
                                "UPDATE dimBeneficiarios SET nombre_completo = :name, grupo_etario = :group, "
                                "tarjeta_activa = :active, ingresos_estimados = :income "
                                "WHERE id_persona_oltp = :id"
                            ),
                            {
                                "name": ben["nombre_completo"],
                                "group": ben["grupo_etario"],
                                "active": ben["tarjeta_activa"],
                                "income": ben["ingresos_estimados"],
                                "id": ben["id_persona_oltp"]
                            }
                        )
                    else:
                        session.execute(
                            text(
                                "INSERT INTO dimBeneficiarios (id_persona_oltp, nombre_completo, grupo_etario, tarjeta_activa, ingresos_estimados) "
                                "VALUES (:id, :name, :group, :active, :income)"
                            ),
                            {
                                "id": ben["id_persona_oltp"],
                                "name": ben["nombre_completo"],
                                "group": ben["grupo_etario"],
                                "active": ben["tarjeta_activa"],
                                "income": ben["ingresos_estimados"]
                            }
                        )
                
                # B. PERSIST dimProgramas (Upsert Logic)
                for prog in programas:
                    existing_prog = session.execute(
                        text("SELECT sk_programa FROM dimProgramas WHERE id_programa_oltp = :id"),
                        {"id": prog["id_programa_oltp"]}
                    ).fetchone()
                    
                    if existing_prog:
                        session.execute(
                            text("UPDATE dimProgramas SET nombre_programa = :name, estado = :status WHERE id_programa_oltp = :id"),
                            {"name": prog["nombre_programa"], "status": prog["estado"], "id": prog["id_programa_oltp"]}
                        )
                    else:
                        session.execute(
                            text("INSERT INTO dimProgramas (id_programa_oltp, nombre_programa, estado) VALUES (:id, :name, :status)"),
                            {"id": prog["id_programa_oltp"], "name": prog["nombre_programa"], "status": prog["estado"]}
                        )
                
                # C. PERSIST dimTiempo for each transaction date dynamically
                for fact in facts:
                    dt = fact["fecha_transaccion"]
                    if isinstance(dt, str):
                        dt = datetime.fromisoformat(dt)
                    
                    sk_tiempo = int(dt.strftime("%Y%m%d"))
                    
                    # Check if date is already loaded
                    existing_time = session.execute(
                        text("SELECT sk_tiempo FROM dimTiempo WHERE sk_tiempo = :sk"),
                        {"sk": sk_tiempo}
                    ).fetchone()
                    
                    if not existing_time:
                        # Extract date attributes
                        fecha_val = dt.date()
                        anio_val = dt.year
                        mes_val = dt.month
                        nombre_mes_val = dt.strftime("%B")
                        trimestre_val = (dt.month - 1) // 3 + 1
                        
                        session.execute(
                            text(
                                "INSERT INTO dimTiempo (sk_tiempo, fecha, anio, mes, nombre_mes, trimestre) "
                                "VALUES (:sk, :fecha, :anio, :mes, :nombre_mes, :trimestre)"
                            ),
                            {
                                "sk": sk_tiempo,
                                "fecha": fecha_val,
                                "anio": anio_val,
                                "mes": mes_val,
                                "nombre_mes": nombre_mes_val,
                                "trimestre": trimestre_val
                            }
                        )
                
                # D. PERSIST factPolíticasAlimentarias (Surrogate Key Mapping - ASSERT-LOAD-02)
                for fact in facts:
                    # Resolve sk_beneficiario
                    sk_ben = session.execute(
                        text("SELECT sk_beneficiario FROM dimBeneficiarios WHERE id_persona_oltp = :id"),
                        {"id": fact["id_persona_oltp"]}
                    ).scalar()
                    
                    # Resolve sk_programa
                    sk_prog = session.execute(
                        text("SELECT sk_programa FROM dimProgramas WHERE id_programa_oltp = :id"),
                        {"id": fact["id_programa_oltp"]}
                    ).scalar()
                    
                    # Resolve sk_geografia (from static dimGeografia mapping)
                    sk_geo = session.execute(
                        text("SELECT sk_geografia FROM dimGeografia WHERE id_municipio_oltp = :id"),
                        {"id": fact["id_municipio_oltp"]}
                    ).scalar() or 1 # Fallback to default index 1
                    
                    # Resolve sk_tiempo
                    dt = fact["fecha_transaccion"]
                    if isinstance(dt, str):
                        dt = datetime.fromisoformat(dt)
                    sk_time = int(dt.strftime("%Y%m%d"))
                    
                    # Insert Fact record
                    session.execute(
                        text(
                            "INSERT INTO factPolíticasAlimentarias (sk_beneficiario, sk_programa, sk_geografia, sk_tiempo, "
                            "admPersonas, efiProgramas, vulneraSocial, participaMunicipal, usoTarjetas, fecha_carga, "
                            "agente_responsable, tote_lote) "
                            "VALUES (:sk_ben, :sk_prog, :sk_geo, :sk_time, :adm, :efi, :vul, :part, :uso, :fecha_c, :agente, :lote)"
                        ),
                        {
                            "sk_ben": sk_ben,
                            "sk_prog": sk_prog,
                            "sk_geo": sk_geo,
                            "sk_time": sk_time,
                            "adm": fact["admPersonas"],
                            "efi": fact["efiProgramas"],
                            "vul": fact["vulneraSocial"],
                            "part": fact["participaMunicipal"],
                            "uso": fact["usoTarjetas"],
                            "fecha_c": datetime.now(),
                            "agente": "CargadorAgent",
                            "lote": batch_id
                        }
                    )
                
                # E. PERSIST curacion_geografica discards if present
                if curaciones:
                    for cur in curaciones:
                        session.execute(
                            text(
                                "INSERT INTO curacion_geografica (id_persona_oltp, municipio_invalido, provincia_capturada, fecha_descarte, batch_id) "
                                "VALUES (:id, :mun, :prov, :fecha_d, :lote)"
                            ),
                            {
                                "id": cur["id_persona_oltp"],
                                "mun": cur["municipio_invalido"],
                                "prov": cur["provincia_capturada"],
                                "fecha_d": cur["fecha_descarte"],
                                "lote": batch_id
                            }
                        )
            
            logger.info("CargadorAgent: Persistence transactions completed successfully.")
            
        except Exception as e:
            logger.error(f"CargadorAgent: Database transaction failed and was rolled back: {str(e)}")
            raise LoadError(f"Cargador persistence failed: {str(e)}")
        finally:
            session.close()

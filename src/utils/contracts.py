import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from src.utils.logging import ValidationError

# ==========================================
# Coordinador Payload Contract
# ==========================================

class CoordinadorControlPayload(BaseModel):
    batch_id: str
    execution_mode: Literal["incremental", "full"]
    target_period_start: datetime
    target_period_end: datetime
    force_execution: bool

    @field_validator("batch_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("batch_id must be a valid UUID v4")

# ==========================================
# Extractor Payload Contract
# ==========================================

class PersonaSchema(BaseModel):
    id: int
    nombre: str
    ingresos_estimados: float
    fecha_modificacion: datetime
    municipio_id: int

class FamiliaSchema(BaseModel):
    id: int
    indice_vulnera: float
    fecha_modificacion: datetime

class TarjetaSchema(BaseModel):
    id: int
    persona_id: int
    activa: bool
    monto_asignado: float
    fecha_modificacion: datetime

class ExtractorOutputPayload(BaseModel):
    df_persona: List[PersonaSchema]
    df_familia: List[FamiliaSchema]
    df_tarjeta: List[TarjetaSchema]

# ==========================================
# Cargador Payload Contract
# ==========================================

class DimBeneficiariosSchema(BaseModel):
    id_persona_oltp: int
    nombre_completo: str
    grupo_etario: Literal["Niño", "Adulto", "Mayor"]
    tarjeta_activa: bool
    ingresos_estimados: float

class DimProgramasSchema(BaseModel):
    id_programa_oltp: int
    nombre_programa: str
    estado: str

class FactPoliticasAlimentariasSchema(BaseModel):
    id_persona_oltp: int
    id_programa_oltp: int
    id_municipio_oltp: int
    fecha_transaccion: datetime
    admPersonas: int
    efiProgramas: float
    vulneraSocial: float = Field(..., ge=0.0, le=1.0)
    participaMunicipal: float
    usoTarjetas: float

class CargadorInputPayload(BaseModel):
    df_dimBeneficiarios: List[DimBeneficiariosSchema]
    df_dimProgramas: List[DimProgramasSchema]
    df_factPolíticasAlimentarias: List[FactPoliticasAlimentariasSchema]

# ==========================================
# Validation Helpers
# ==========================================

def validate_coordinador_payload(payload_dict: dict) -> CoordinadorControlPayload:
    """Validates Coordinator control parameters."""
    try:
        return CoordinadorControlPayload(**payload_dict)
    except Exception as e:
        raise ValidationError(f"Coordinator payload validation failed: {str(e)}")

def validate_extractor_payload(df_persona_records: list, df_familia_records: list, df_tarjeta_records: list) -> ExtractorOutputPayload:
    """Validates Extractor output in-memory payloads."""
    try:
        return ExtractorOutputPayload(
            df_persona=df_persona_records,
            df_familia=df_familia_records,
            df_tarjeta=df_tarjeta_records
        )
    except Exception as e:
        raise ValidationError(f"Extractor output payload validation failed: {str(e)}")

def validate_cargador_payload(df_beneficiarios_records: list, df_programas_records: list, df_fact_records: list) -> CargadorInputPayload:
    """Validates Cargador input in-memory payloads."""
    try:
        return CargadorInputPayload(
            df_dimBeneficiarios=df_beneficiarios_records,
            df_dimProgramas=df_programas_records,
            df_factPolíticasAlimentarias=df_fact_records
        )
    except Exception as e:
        raise ValidationError(f"Cargador input payload validation failed: {str(e)}")

# Data Mart Model & Schema Mappings: TAIS_DM

**Branch**: `001-multiagent-etl` | **Date**: 2026-05-18

Este documento detalla el esquema multidimensional lógico y físico del Data Mart `TAIS_DM`, diseñado bajo la metodología Hefesto para responder a los requerimientos de la Secretaría de Políticas Alimentarias.

---

## 1. Tabla de Hechos: `factPolíticasAlimentarias`

Almacena las métricas de asistencia alimentaria asociadas a los beneficiarios, programas, distribución geográfica e hitos temporales.

| Nombre de Columna | Tipo de Dato Físico (SQL) | Tipo de Dato Lógico (Agente) | Restricción | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **id_hecho** | SERIAL (PK) | int | NOT NULL | Clave primaria autoincremental de la tabla de hechos. |
| **sk_beneficiario** | INT (FK) | int | NOT NULL | Surrogate Key que apunta a `dimBeneficiarios`. |
| **sk_programa** | INT (FK) | int | NOT NULL | Surrogate Key que apunta a `dimProgramas`. |
| **sk_geografia** | INT (FK) | int | NOT NULL | Surrogate Key que apunta a `dimGeografia`. |
| **sk_tiempo** | INT (FK) | int | NOT NULL | Surrogate Key que apunta a `dimTiempo`. |
| **admPersonas** | INT | int | DEFAULT 0 | Conteo de personas activas o asistidas en la transacción. |
| **efiProgramas** | NUMERIC(5, 2) | Decimal | DEFAULT 0.00 | Índice de eficiencia obtenido de encuestas de satisfacción. |
| **vulneraSocial** | NUMERIC(3, 2) | Decimal | NOT NULL | Índice de vulnerabilidad normalizado `[0.00, 1.00]`. |
| **participaMunicipal** | NUMERIC(5, 2) | Decimal | DEFAULT 0.00 | Tasa porcentual de participación municipal calculada. |
| **usoTarjetas** | NUMERIC(12, 2) | Decimal | DEFAULT 0.00 | Monto acumulado de transacciones del subsidio. |
| **fecha_carga** | TIMESTAMP | datetime | NOT NULL | Auditoría: fecha y hora en que se persistió el lote. |
| **agente_responsable** | VARCHAR(50) | str | NOT NULL | Auditoría: slug del agente que cargó el registro (`cargador`). |
| **tote_lote** | VARCHAR(36) | str | NOT NULL | Auditoría: ID único del lote de ejecución (`batch_id`). |

---

## 2. Tablas de Dimensiones (Dim)

### A. Dimensión: `dimBeneficiarios`
Representa al padrón de personas y familias vulnerables con características socioeconómicas.

| Nombre de Columna | Tipo de Dato Físico | Tipo Lógico | Descripción |
| :--- | :--- | :--- | :--- |
| **sk_beneficiario** | SERIAL (PK) | int | Surrogate Key de la dimensión. |
| **id_persona_oltp** | SMALLINT | int | Clave natural en la base de datos `Secretaria`. |
| **nombre_completo** | VARCHAR(200) | str | Nombre del beneficiario normalizado (sin caracteres extraños). |
| **grupo_etario** | VARCHAR(20) | str | Clasificación: `Niño` (0-14), `Adulto` (15-64), `Mayor` (65+). |
| **tarjeta_activa** | BOOLEAN | bool | Estado de tarjeta de subsidio bancarizada. |
| **ingresos_estimados** | NUMERIC(12, 2) | Decimal | Ingresos promedio de la persona/familia. |

### B. Dimensión: `dimProgramas`
Mapeo de los programas sociales alimentarios operados por la Secretaría.

| Nombre de Columna | Tipo de Dato Físico | Tipo Lógico | Descripción |
| :--- | :--- | :--- | :--- |
| **sk_programa** | SERIAL (PK) | int | Surrogate Key de la dimensión. |
| **id_programa_oltp** | SMALLINT | int | Clave natural del programa en `Secretaria`. |
| **nombre_programa** | VARCHAR(100) | str | Nombre del programa social (e.g., "Tarjeta TAIS", "Comedores"). |
| **estado** | VARCHAR(20) | str | Estado actual: `Activo`, `Suspendido`, `Finalizado`. |

### C. Dimensión: `dimGeografia`
Jerarquía territorial estricta limitada a la Provincia de Salta.

| Nombre de Columna | Tipo de Dato Físico | Tipo Lógico | Descripción |
| :--- | :--- | :--- | :--- |
| **sk_geografia** | SERIAL (PK) | int | Surrogate Key de la dimensión. |
| **id_municipio_oltp** | SMALLINT | int | Clave natural de geografía en `Secretaria`. |
| **localidad** | VARCHAR(100) | str | Localidad (e.g., San Ramón de la Nueva Orán, Cafayate). |
| **municipio** | VARCHAR(100) | str | Municipio (e.g., Orán, Tartagal, Cafayate, Cachi). |
| **departamento** | VARCHAR(100) | str | Departamento en la Provincia de Salta. |
| **provincia** | VARCHAR(50) | str | Limitada estrictamente a `Salta`. |

### D. Dimensión: `dimTiempo`
Desglose temporal para análisis histórico en Inteligencia de Negocios (BI).

| Nombre de Columna | Tipo de Dato Físico | Tipo Lógico | Descripción |
| :--- | :--- | :--- | :--- |
| **sk_tiempo** | INT (PK) | int | Surrogate Key en formato `YYYYMMDD`. |
| **fecha** | DATE | datetime.date | Fecha completa en formato calendario. |
| **anio** | INT | int | Año calendario (e.g., 2026). |
| **mes** | INT | int | Número de mes (1 a 12). |
| **nombre_mes** | VARCHAR(20) | str | Nombre de mes en español (e.g., "Mayo"). |
| **trimestre** | INT | int | Trimestre del año (1 a 4). |

---

## 3. Tabla de Descarte: `curacion_geografica`

Almacena los registros con inconsistencias territoriales detectadas por el Agente Transformador para su posterior análisis manual sin bloquear el pipeline.

| Nombre de Columna | Tipo de Dato Físico | Tipo Lógico | Descripción |
| :--- | :--- | :--- | :--- |
| **id_descarte** | SERIAL (PK) | int | ID autoincremental del descarte. |
| **id_persona_oltp** | SMALLINT | int | Clave natural del beneficiario afectado. |
| **municipio_invalido** | VARCHAR(100) | str | Nombre del municipio incorrecto capturado. |
| **provincia_capturada** | VARCHAR(100) | str | Provincia incorrecta capturada (diferente a Salta). |
| **fecha_descarte** | TIMESTAMP | datetime | Fecha y hora en que se detectó la inconsistencia. |
| **batch_id** | VARCHAR(36) | str | ID del lote en ejecución. |

---

## 4. Reglas de Validación de Datos (Data Quality Gates)

1. **Rango de Vulnerabilidad Social**:
   $$\text{vulneraSocial} \in [0.00, 1.00]$$
   Cualquier valor menor a `0.00` o mayor a `1.00` debe rechazar el registro entero de la persona por inconsistencia matemática grave.
2. **Restricción Territorial de Salta**:
   La columna `provincia` en `dimGeografia` debe ser validada contra una lista blanca que contiene únicamente `"Salta"`. Si el registro de origen indica cualquier otra provincia, se desvía a `curacion_geografica`.
3. **Conversión Estricta de Monedas**:
   Toda asignación monetaria de `usoTarjetas` o `ingresos_estimados` debe validarse como positiva o cero. Los valores negativos no permitidos se configuran en `0.00` de forma controlada lanzando un Warning.

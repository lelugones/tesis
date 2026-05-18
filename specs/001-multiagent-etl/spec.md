# Feature Specification: Pipeline Multiagente ETL para Data Mart (TAIS_DM)

**Feature Branch**: `001-multiagent-etl`
**Created**: 2026-05-18
**Status**: Approved
**Input**: Modelos relacionales de origen OLTP "Secretaria" y destino OLAP "TAIS_DM", con requerimientos de orquestación y extracción incremental para políticas alimentarias.

---

## Clarifications

### Session 2026-05-18
- Q: ¿Cuáles de los siguientes aspectos quedan explícitamente fuera del alcance para la primera versión del pipeline? → A: Ambos (Streaming y sincronización bidireccional) quedan fuera de alcance; la carga es estrictamente unidireccional y por lotes periódicos.
- Q: ¿Cómo debe manejar el Extractor el control de carga sobre la base transaccional de origen? → A: Extracción paginada en lotes de tamaño parametrizable (por defecto 5,000 filas) con pausas breves (e.g., 500 ms) entre lotes para mitigar la sobrecarga en el motor OLTP.
- Q: ¿Qué política de curación y alerta debe seguir el Transformador cuando encuentre un registro geográfico inválido (fuera de Salta)? → A: Aislamiento y Continuidad: desviar registros huérfanos/fuera de Salta a la tabla `curacion_geografica` en el Data Mart, registrar un aviso estructurado en el log de auditoría y continuar el procesamiento del lote.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carga Incremental Automatizada y Consistente (Priority: P1)
Como Ingeniero de Datos de la Secretaría, quiero que el pipeline extraiga, transforme y cargue incrementalmente los datos de asistencia social sin duplicar registros, para contar con métricas actualizadas y confiables en el Data Mart.

**Why this priority**: Es la funcionalidad básica requerida para operar el sistema de reportes de políticas alimentarias.
**Independent Test**: Ejecutar el pipeline para un período cerrado del origen, validar que el Data Mart se cargue correctamente, y luego re-ejecutar para el mismo período verificando que no haya registros duplicados ni inconsistencias.

**Acceptance Scenarios**:
1. **Given** un origen OLTP con nuevos registros del municipio de Orán y tarjeta de asistencia para la métrica `usoTarjetas`, **When** el Coordinador inicia el pipeline, **Then** el Extractor recupera solo los registros modificados, el Transformador procesa la vulnerabilidad social, y el Cargador los inserta de forma consistente en el Data Mart.
2. **Given** una carga previa del período actual, **When** se ejecuta el pipeline por segunda vez, **Then** el Cargador realiza un "Upsert" actualizando los registros existentes sin generar registros duplicados.

---

### User Story 2 - Resiliencia de Transacciones y Recuperación ante Errores (Priority: P2)
Como Administrador del Sistema, quiero que si ocurre una desconexión o fallo en cualquier punto del pipeline, la base de datos destino no quede en un estado inconsistente o con cargas parciales.

**Why this priority**: Evita la corrupción de datos históricos y asegura la integridad referencial en el Data Mart.
**Independent Test**: Forzar una desconexión del servidor OLAP a mitad de la carga y verificar la ausencia de registros de hechos huérfanos.

**Acceptance Scenarios**:
1. **Given** que el Transformador ha enviado los datos validados al Cargador, **When** el Cargador pierde conexión a la base `TAIS_DM` a mitad de la persistencia de hechos, **Then** todas las inserciones parciales de ese lote se revierten (Rollback) y el Coordinador registra el fallo y lanza una alerta.

---

## Agente Coordinador
### 1. Interfaces de Datos e Inferencia Semicerrada
El Agente Coordinador es el orquestador principal del pipeline. Recibe las solicitudes de inicio de la ejecución por parte del planificador del sistema o mediante llamadas directas.
- **Entrada (Payload de control)**:
  ```json
  {
    "batch_id": "UUID-v4",
    "execution_mode": "incremental | full",
    "target_period_start": "datetime (ISO YYYY-MM-DDTHH:MM:SS)",
    "target_period_end": "datetime (ISO YYYY-MM-DDTHH:MM:SS)",
    "force_execution": "boolean"
  }
  ```
- **Salida (Estado consolidado de ejecución)**:
  ```json
  {
    "batch_id": "UUID-v4",
    "status": "SUCCESS | FAILED",
    "records_extracted": 15240,
    "records_loaded": 15240,
    "started_at": "datetime (ISO)",
    "ended_at": "datetime (ISO)",
    "error_details": "string (null if SUCCESS)"
  }
  ```

### 2. Contratos de Datos y Reglas de Negocio Funcionales
El Coordinador gestiona de forma secuencial y supervisada el ciclo de vida de los agentes dependientes:
1. **Inicialización**: Genera un ID de lote (`batch_id`) único y recupera la fecha límite de la última ejecución exitosa del Data Mart (`TAIS_DM`).
2. **Orquestación del Extractor**: Llama al Agente Extractor pasando los límites temporales. Si falla, activa la política de reintentos: 3 intentos con retroceso exponencial (Exponential Backoff).
3. **Orquestación del Transformador**: Pasa los DataFrames recuperados al Agente Transformador. Monitorea la consistencia de los datos intermedios. Si se devuelven DataFrames vacíos o inválidos, aborta la ejecución para prevenir daños.
4. **Orquestación del Cargador**: Envía los DataFrames transformados al Agente Cargador para la persistencia atómica.
5. **Auditoría e Historial**: Escribe el resultado de la ejecución en la tabla `registro_ejecuciones` del Data Mart con las columnas `fecha_carga` (timestamp), `agente_responsable` (slug) y `batch_id`.

### 3. Criterios de Aceptación Ejecutables (Spec Kit Asserts)
- **ASSERT-COORD-01**: Si el Extractor falla de forma persistente tras 3 intentos, la ejecución general se interrumpe y se marca como `FAILED`.
- **ASSERT-COORD-02**: El Coordinador no debe invocar al Cargador si el Transformador ha arrojado una alerta crítica de validación de datos.
- **ASSERT-COORD-03**: La tabla de logs de auditoría en la base de datos debe reflejar exactamente el estado final de la ejecución, con marcas de tiempo correctas.

---

# Agente Extractor
### 1. Interfaces de Datos e Inferencia Semicerrada
El Agente Extractor realiza la conexión física al origen OLTP transaccional (SQL Server base "Secretaria") y genera los DataFrames estructurados en Pandas con tipado estricto.
- **Entradas**: Intervalo temporal (`target_period_start` a `target_period_end`).
- **Salidas (Mapeo de Tipos)**:
  | Tabla Origen (SQL Server) | Tipo de Dato SQL Server | Tipo Lógico en Agente (Pandas/Python) | Tabla de Destino en DataFrame |
  |----------------------------|-------------------------|---------------------------------------|--------------------------------|
  | Persona.id                 | smallint (PK)           | int / Pydantic integer                | df_persona.id                  |
  | Persona.ingresos_estimados | money                   | Decimal (Python stdlib)               | df_persona.ingresos            |
  | Familia.indice_vulnera     | decimal(5,2)            | float                                 | df_familia.vulnera             |
  | Municipio.nombre           | varchar(100)            | str                                   | df_municipio.nombre            |
  | Transaccion.monto          | money                   | Decimal                               | df_transaccion.monto           |
  | Tarjeta.activa             | bit                     | bool                                  | df_tarjeta.activa              |
  | Novedad.fecha_registro     | datetime                | datetime (Pandas datetime64[ns])       | df_novedad.fecha               |

### 2. Contratos de Datos y Reglas de Negocio Funcionales
El Extractor realiza la extracción incremental bajo el siguiente flujo algorítmico:
1. **Conexión Eficiente**: Utiliza pool de conexiones establecido por `connections.py` para conectarse a "Secretaria".
2. **Consulta Incremental**: Ejecuta consultas SQL parametrizadas filtrando por el campo `fecha_modificacion` en las tablas: `Persona`, `Familia`, `Municipio`, `Novedad`, `Satisfaccion`, `Transaccion` y `Tarjeta`.
3. **Mapeo Tipado**: Convierte de forma segura los tipos de datos nativos de SQL Server a Python/Pandas sin pérdida de precisión decimal en campos de tipo `money` (evitando redondeos de punto flotante).
4. **Validación Inicial**: Valida la completitud del esquema crudo. En caso de inconsistencias críticas en el origen (ej. campos de ID nulos), descarta el registro erróneo y lo registra en un archivo de logs locales.
5. **Control de Carga (Throttling)**: La extracción debe realizarse de forma paginada en lotes de tamaño parametrizable (por defecto 5,000 filas por consulta) introduciendo pausas controladas de 500 ms entre lotes para mitigar la sobrecarga en el motor OLTP durante horas de alta concurrencia.

### 3. Criterios de Aceptación Ejecutables (Spec Kit Asserts)
- **ASSERT-EXT-01**: Las columnas que contienen valores de tipo `money` o `decimal` en SQL Server deben ser cargadas en el DataFrame como instancias de `decimal.Decimal`.
- **ASSERT-EXT-02**: El filtro temporal de extracción incremental debe asegurar que ningún registro con fecha de modificación inferior a `target_period_start` sea retornado.
- **ASSERT-EXT-03**: La extracción debe lanzarse de forma paginada por tabla en lotes de hasta 5,000 registros, verificando que se introduzcan pausas de 500 ms entre lotes para controlar el throttling en el servidor OLTP.

---

# Agente Transformador
### 1. Interfaces de Datos e Inferencia Semicerrada
El Agente Transformador procesa los datos crudos extraídos para conformar el modelo de hechos y dimensiones con la lógica de negocio del TFI.
- **Entrada**: DataFrames de entrada crudos (`df_persona`, `df_familia`, `df_municipio`, `df_novedad`, `df_satisfaccion`, `df_transaccion`, `df_tarjeta`).
- **Salida**: DataFrames de dimensiones homologadas (`dimBeneficiarios`, `dimProgramas`, `dimGeografia`, `dimTiempo`) y tabla de hechos (`factPolíticasAlimentarias`).

### 2. Contratos de Datos y Reglas de Negocio Funcionales
El Transformador implementa la lógica multidimensional y ejecuta cálculos analíticos:
1. **Llamadas Analíticas del OLTP**: Para calcular las métricas complejas de forma consistente, invoca los Stored Procedures y funciones definidos en el origen mediante llamadas parametrizadas:
   - `sp_CalcularCrecimientoMunicipal(id_municipio, anio)` -> Tasa porcentual de incremento.
   - `sp_NivelSatisfaccionPromedio(id_programa)` -> Nota decimal para `efiProgramas`.
   - `sp_PorcentajeMejoraPersona(id_persona)` -> Retorna la mejora en la calidad de vida.
   - `sp_MontoTotalAsignado(id_familia)` -> Monto de asistencia acumulado.
2. **Cálculo de Métricas del Data Mart**:
   - **admPersonas**: Conteo total consolidado de beneficiarios activos e incorporaciones del período.
   - **efiProgramas**: Mapeo del resultado de `sp_NivelSatisfaccionPromedio` normalizado para medir el impacto.
   - **vulneraSocial**: Ponderación multidimensional basada en ingresos familiares, tamaño familiar y condiciones sanitarias. El índice de vulnerabilidad debe normalizarse estrictamente en el intervalo `[0.00, 1.00]`.
   - **participaMunicipal**: Nivel de integración municipal de programas alimentarios calculada con `sp_CalcularCrecimientoMunicipal`.
   - **usoTarjetas**: Cantidad total transaccionada de subsidio mediante tarjetas activas e inactivas.
3. **Mapeo Dimensional de Geografía**: Limita y valida que la geografía corresponda estrictamente a los Municipios y Localidades de la Provincia de Salta (ej. Tartagal, Orán, Rivadavia). Cualquier registro fuera de la provincia debe ser derivado a la tabla de exclusión `curacion_geografica` (política de Aislamiento y Continuidad), registrando un Warning estructurado en los logs de auditoría sin interrumpir el procesamiento del lote.

### 3. Criterios de Aceptación Ejecutables (Spec Kit Asserts)
- **ASSERT-TRANS-01**: El índice `vulneraSocial` debe validarse en cada registro y arrojar error si su valor es menor que 0.00 o mayor que 1.00.
- **ASSERT-TRANS-02**: Toda fila con datos de geografía fuera de Salta debe ser filtrada del flujo principal, guardarse en `curacion_geografica` y registrar un Warning estructurado en el log de auditoría, sin abortar la ejecución del lote.
- **ASSERT-TRANS-03**: La métrica `efiProgramas` debe contener valores calculados dinámicamente llamando a los Stored Procedures correspondientes para cada programa en el lote.

---

# Agente Cargador
### 1. Interfaces de Datos e Inferencia Semicerrada
El Agente Cargador realiza la persistencia física en el Data Mart destino "TAIS_DM" (PostgreSQL/SQL Server).
- **Entrada**: DataFrames de salida del Transformador (`df_dimBeneficiarios`, `df_dimProgramas`, `df_dimGeografia`, `df_dimTiempo`, `df_factPolíticasAlimentarias`).
- **Salida**: Inserciones físicas exitosas y confirmación de la carga incremental (Upsert).

### 2. Contratos de Datos y Reglas de Negocio Funcionales
El Cargador aplica un flujo secuencial estricto y atómico de persistencia bajo aislamiento transaccional:
1. **Aislamiento Transaccional**: Abre una transacción única a nivel de lote (`batch_id`) con nivel de aislamiento `READ COMMITTED`.
2. **Carga Secuencial de Dimensiones**: Inserta/Actualiza en primer lugar las dimensiones (`dimTiempo`, `dimGeografia`, `dimBeneficiarios`, `dimProgramas`) para generar y mapear las claves subrogadas (Surrogate Keys).
3. **Mapeo de Claves Subrogadas**: Asocia las claves naturales de origen con las claves subrogadas en el DataFrame de hechos.
4. **Carga de Hechos**: Inserta en último lugar los hechos en la tabla `factPolíticasAlimentarias` con la respectiva integridad referencial.
5. **Manejo de Errores e Integridad**: Si alguna de las claves foráneas de los hechos falla o no encuentra su dimensión asociada, la transacción completa (Dimensiones + Hechos) realiza un `Rollback` completo para asegurar que no existan inconsistencias parciales en el Data Mart.

### 3. Criterios de Aceptación Ejecutables (Spec Kit Asserts)
- **ASSERT-LOAD-01**: La carga de hechos no debe persistirse si se detecta un error de integridad referencial (claves huérfanas) en las dimensiones asociadas.
- **ASSERT-LOAD-02**: Si ocurre un error de base de datos a mitad de la ejecución, ninguna de las dimensiones creadas de forma parcial en esa ejecución debe quedar persistida.
- **ASSERT-LOAD-03**: El tiempo de ejecución del volcado en la base de datos debe ser inferior a 1 ms por fila insertada en condiciones normales.

---

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: El pipeline MUST realizar la extracción incremental del origen OLTP basándose en la fecha del último lote exitoso en `TAIS_DM`.
- **FR-002**: Las transformaciones de vulnerabilidad social y participación municipal MUST ejecutarse en memoria utilizando Pandas DataFrames para garantizar la velocidad de procesamiento.
- **FR-003**: El sistema MUST invocar las funciones analíticas del origen transaccional (`sp_CalcularCrecimientoMunicipal`, `sp_NivelSatisfaccionPromedio`, etc.) mediante consultas tipadas.
- **FR-004**: Toda carga de datos MUST ser atómica a nivel de lote: o se guarda todo (Dimensiones y Hechos del lote) o no se guarda nada (Rollback total).
- **FR-005**: Las métricas de geografía y distribución de políticas alimentarias MUST limitarse de manera estricta a los Municipios y Localidades de la Provincia de Salta.
- **FR-006**: El pipeline MUST operar de forma estrictamente unidireccional (OLTP -> OLAP) y por lotes periódicos (batch), quedando fuera de alcance cualquier sincronización en tiempo real (streaming) o bidireccional.

### Key Entities
- **dimBeneficiarios**: Representa el padrón único de personas y familias vulnerables con atributos socioeconómicos de origen.
- **dimGeografia**: Jerarquía territorial que divide los datos por Provincia (Salta), Departamento, Municipio y Localidad.
- **factPolíticasAlimentarias**: Contiene las métricas de monitoreo de asistencia alimentaria (`admPersonas`, `vulneraSocial`, `efiProgramas`, `participaMunicipal`, `usoTarjetas`) para la toma de decisiones.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: El pipeline completo procesa un lote mensual promedio de 50,000 beneficiarios en un tiempo total menor a 20 segundos de extremo a extremo.
- **SC-002**: El 100% de los registros de hechos persistidos en `TAIS_DM` debe mantener perfecta integridad referencial con sus dimensiones asociadas (0 registros huérfanos).
- **SC-003**: La cobertura de pruebas automatizadas en Pytest para el Agente Transformador y Cargador debe ser superior o igual al 90%.

## Assumptions
- Se asume que el servidor transaccional OLTP cuenta con los Stored Procedures analíticos precargados y optimizados.
- Se asume que el volumen de datos incrementales diarios no supera los 100,000 registros, permitiendo el procesamiento directo en memoria RAM del servidor.

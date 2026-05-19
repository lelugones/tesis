# Feature Specification: mcp-db-access

**Feature Branch**: `002-mcp-db-access`

**Created**: 2026-05-19

**Status**: Draft

**Input**: User description: "implementar el acceso a las bases de datos SQL Server locales mediante los MCP definidos: secretaria-local y tais-dm-local"

## Clarifications

### Session 2026-05-19
- Q: Protocolo de Transporte para MCP Local → A: stdio (Los agentes inician el servidor MCP localmente como un subproceso)
- Q: Manejo de Paginación en Grandes Volúmenes de Datos → A: Cursores (Watermarks) (Extraer iterativamente basándose en la última fecha/ID procesado)

## User Scenarios & Testing *(mandatory)*


### User Story 1 - Extracción de Datos OLTP a través de MCP (Priority: P1)

Como agente Extractor, quiero poder acceder a los datos de la base de datos origen "Secretaria" utilizando exclusivamente el servidor MCP `secretaria-local`, para obtener los datos incrementales necesarios sin utilizar drivers tradicionales de conexión directa.

**Why this priority**: Es la base del pipeline ETL; sin acceso a los datos de origen, ninguna extracción puede llevarse a cabo.

**Independent Test**: Can be fully tested by solicitando un dataset de prueba simple a través del MCP `secretaria-local` y verificando que la conexión sea exitosa y devuelva los datos sin usar drivers nativos de forma directa.

**Acceptance Scenarios**:

1. **Given** un entorno local con la instancia MCP `secretaria-local` corriendo, **When** el agente Extractor envía un requerimiento de lectura a través del MCP, **Then** los datos son recuperados exitosamente en formato estructurado.
2. **Given** un fallo de conexión en el servidor MCP `secretaria-local`, **When** el agente Extractor intenta obtener datos, **Then** el sistema arroja un error controlado de MCP sin exponer credenciales ni fallar catastróficamente.

---

### User Story 2 - Carga de Datos al Data Mart a través de MCP (Priority: P1)

Como agente Cargador, quiero poder persistir las dimensiones y tablas de hechos conformadas en la base de datos "TAIS_DM" utilizando exclusivamente el servidor MCP `tais-dm-local`, para garantizar la integridad referencial y cumplir con las restricciones de la arquitectura.

**Why this priority**: Es el paso final y esencial del ETL; sin él, las transformaciones en memoria no se persistirán.

**Independent Test**: Can be fully tested by enviando un payload de datos de prueba a través de herramientas de inserción del MCP `tais-dm-local` y verificando que los registros se graben correctamente en la base de datos.

**Acceptance Scenarios**:

1. **Given** un lote de datos válidos transformados, **When** el agente Cargador invoca las herramientas del MCP `tais-dm-local` para la inserción, **Then** los datos se persisten en "TAIS_DM" y se mantiene la integridad referencial.
2. **Given** un lote de datos con una llave primaria duplicada, **When** el agente Cargador invoca la herramienta MCP, **Then** el MCP devuelve un error claro que el Cargador captura e informa para auditoría.

---

### Edge Cases

- ¿Qué pasa si los servidores MCP `secretaria-local` o `tais-dm-local` no están respondiendo o sufren timeouts durante grandes volúmenes de datos?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST delegar todas las consultas de lectura en la base de datos "Secretaria" a las herramientas expuestas por `secretaria-local`.
- **FR-002**: El sistema MUST delegar todas las operaciones de inserción/actualización en la base de datos "TAIS_DM" a las herramientas expuestas por `tais-dm-local`.
- **FR-003**: El sistema MUST prohibir explícitamente y a nivel de diseño el uso de conexiones directas a base de datos dentro de la lógica central de los agentes.
- **FR-003.1**: El sistema MUST conectarse a los servidores MCP locales utilizando el protocolo de transporte **stdio** (ejecutando el servidor MCP como un subproceso del agente).
- **FR-004**: El sistema MUST manejar excepciones provenientes de las respuestas de los servidores MCP y proveer telemetría/auditoría clara en caso de falla.
- **FR-005**: El sistema MUST implementar paginación basada en Cursores (Watermarks - timestamp/ID) para extraer grandes lotes de datos y evitar exceder los límites de tamaño de mensaje del protocolo MCP.

### Key Entities

- **MCP `secretaria-local`**: Abstracción del contexto de acceso a la base de datos fuente. Expone herramientas predefinidas para consultas controladas al OLTP.
- **MCP `tais-dm-local`**: Abstracción del contexto de almacenamiento del Data Mart. Expone herramientas predefinidas para cargar o actualizar dimensiones y tablas de hechos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las operaciones de base de datos se efectúan a través de los servidores MCP definidos, verificado estáticamente mediante la ausencia de paquetes de conexión a SQL Server en la lógica de los agentes.
- **SC-002**: El tiempo de overhead por el uso del protocolo MCP para la transmisión de registros no excede 1 segundo por cada lote de 1000 registros procesados.
- **SC-003**: En caso de fallo de cualquiera de los MCP, el sistema reacciona deteniendo el pipeline de forma segura e informando el evento en el 100% de los casos observados.

## Assumptions

- Se asume que los servidores MCP `secretaria-local` y `tais-dm-local` ya están configurados en el entorno o se configurarán de forma independiente para exponer las herramientas correctas (read-only para origen, upserts para destino).
- Las credenciales de acceso a las bases de datos son administradas exclusivamente por los servidores MCP y no forman parte de la configuración del agente.
- El uso de MCP en forma local no introducirá latencia prohibitiva debido a la serialización de datos JSON entre el proceso y el servidor.

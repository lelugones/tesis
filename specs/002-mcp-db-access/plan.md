# Implementation Plan: Acceso a Bases de Datos mediante MCP (mcp-db-access)

**Branch**: `002-mcp-db-access` | **Date**: 2026-05-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-mcp-db-access/spec.md`

## Summary

Este plan detalla la reestructuración de la capa de acceso a datos del pipeline ETL. Se eliminará el uso de conexiones SQLAlchemy directas en la lógica de los agentes, reemplazándolas por conexiones locales mediante el protocolo Model Context Protocol (MCP) a través de transporte `stdio`. Los agentes Extractor y Cargador consumirán las herramientas expuestas por los servidores `secretaria-local` (para origen OLTP) y `tais-dm-local` (para destino OLAP). Adicionalmente, se implementará paginación robusta basada en marcas de agua (Watermarks) para el manejo seguro de grandes volúmenes de datos.

## Technical Context

- **Language/Version**: Python 3.10.11 o superior.
- **Primary Dependencies**: `mcp` (SDK oficial de Python para Model Context Protocol), `pytest`, `pytest-asyncio` (para pruebas asíncronas de clientes MCP), `pydantic` v2.x.
- **Storage**:
  - Origen OLTP (Secretaria): Microsoft SQL Server (Instancia Local) a través del MCP `secretaria-local`.
  - Destino OLAP (TAIS_DM): Microsoft SQL Server (Instancia Local) a través del MCP `tais-dm-local`.
- **Testing**: Pytest y `pytest-asyncio` simulando la ejecución de servidores MCP stdio mediante mocks y subprocesos de prueba.
- **Target Platform**: Windows 11 (Instancia Local).
- **Project Type**: Database Abstraction Layer / Multi-Agent MCP Integration.
- **Performance Goals**: Overhead de transporte MCP < 1s por lote de 1000 registros procesados.
- **Constraints**: 
  - Queda estrictamente prohibido el uso de pyodbc, SQLAlchemy u otros drivers tradicionales directamente dentro de `ExtractorAgent` y `CargadorAgent`.
  - Conexión vía transporte `stdio` mediante ejecución de comandos configurables para iniciar los subprocesos MCP.
  - Paginación basada en Cursores / Watermarks (ID / fecha_modificacion).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **SDD Compliance**: ✅ `spec.md` define los contratos funcionales y de testing.
- **TDD Compliance**: ✅ Se escribirán test asíncronas con pytest-asyncio que validen el flujo de error y desconexión en fase "Fallo" antes del código de producción.
- **Capa de Abstracción MCP**: ✅ Se prohíbe el uso de conexiones directas de DB en los agentes. Se introduce `src/drivers/mcp_client.py` para aislar la comunicación con los servidores MCP locales.
- **Paginación por Cursores**: ✅ FR-005 obliga al uso de marcas de agua para la extracción incremental, cumpliendo con la restricción de tamaño del contexto MCP.

## Project Structure

### Documentation (this feature)

```text
specs/002-mcp-db-access/
├── spec.md              # Feature specification (completed & clarified)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output: Research and design justifications
├── data-model.md        # Phase 1 output: Client/Server schemas and cursors
├── quickstart.md        # Phase 1 output: Running with MCP servers and mock scripts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── contracts/
    ├── secretaria_tools.json  # Contract for secretaria-local tools
    └── tais_dm_tools.json     # Contract for tais-dm-local tools
```

### Source Code (repository root)

```text
src/
├── agents/
│   ├── extractor/
│   │   └── fetcher.py         # [MODIFY] Cambiar DBConnectionManager por MCPClient
│   └── cargador/
│       └── writer.py          # [MODIFY] Cambiar DBConnectionManager por MCPClient
├── drivers/
│   ├── connections.py         # [RETAIN] Se conserva solo si los servidores MCP locales lo usan internamente.
│   └── mcp_client.py          # [NEW] Cliente MCP genérico con transporte stdio
tests/
├── integration/
│   ├── test_mcp_integration.py  # [NEW] Test de integración real/mock con subprocesos MCP
│   └── test_pipeline_mcp.py    # [NEW] Test de integración del pipeline completo con MCP
└── unit/
    ├── test_mcp_client.py     # [NEW] Test unitario del cliente de transporte stdio
    └── test_extractor_mcp.py  # [NEW] Test unitario del extractor mockeando respuestas de herramientas MCP
```

**Structure Decision**: Introducimos `mcp_client.py` como un driver común para evitar la duplicación de código de inicialización asíncrona de MCP stdio. Los agentes Extractor y Cargador mantendrán su firma pero recibirán una instancia de `MCPClientContext` en lugar del antiguo `DBConnectionManager`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Introducción de programación asíncrona (`asyncio` / `async def`) | El SDK de MCP de Python requiere ejecutores asíncronos y transporte asíncrono para stdio. | Clientes MCP síncronos no existen en el SDK oficial de Python. |
| Ejecución de subprocesos en la suite de pruebas | Para validar que los agentes pueden arrancar e interactuar con subprocesos stdio reales. | Mocks puros de llamadas no prueban la negociación del protocolo ni la resiliencia ante caídas del subproceso. |

# Research: Acceso a Bases de Datos mediante MCP (mcp-db-access)

## 1. Integración del SDK de Python MCP en Clientes Stdio

El SDK oficial de Python para Model Context Protocol (`mcp`) proporciona herramientas para interactuar con servidores MCP a través de canales de entrada/salida estándar (`stdio`). 

### Arquitectura de Conexión
La conexión se establece instanciando un `stdio_client` con los parámetros de comando del servidor (ej. ejecutable del servidor, argumentos):

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "src.drivers.secretaria_mcp_server"],  # Servidor mock local
    env=None
)

async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        # Inicializar conexión
        await session.initialize()
        
        # Listar herramientas
        tools = await session.list_tools()
        
        # Ejecutar una herramienta
        result = await session.call_tool("get_incremental_data", arguments={
            "table_name": "Persona",
            "start_date": "2026-05-01T00:00:00",
            "end_date": "2026-05-19T00:00:00",
            "cursor_column": "id",
            "cursor_value": 0,
            "page_size": 1000
        })
```

### Decisión Síncrono vs. Asíncrono
Dado que el pipeline ETL original en `001-multiagent-etl` está diseñado síncronamente (utilizando Pandas y SQLAlchemy tradicional en hilos normales), introducir llamadas asíncronas requiere definir la frontera de sincronización:
- **Opción A (Convertir agentes a Async)**: Convertir todos los agentes (`ExtractorAgent`, `CargadorAgent`, `CoordinadorAgent`) a `async def`. Esto requiere modificar la suite de pruebas para usar `pytest-asyncio` extensamente.
- **Opción B (Wrapper Síncrono)**: Crear un cliente síncrono `SyncMCPClient` que encapsule las llamadas asíncronas usando `asyncio.run()` o manteniendo un bucle de eventos (`EventLoop`) corriendo en un hilo secundario.

**Decisión**: **Opción B (Wrapper Síncrono)**. Mantener la lógica de los agentes síncrona minimiza el impacto en las transformaciones de Pandas, el flujo lineal de control del Coordinador y las pruebas unitarias existentes. El driver `src/drivers/mcp_client.py` expondrá una interfaz síncrona que inicializa y gestiona el bucle de eventos asíncrono en segundo plano para el transporte stdio.

---

## 2. Definición de Herramientas y Contratos de los Servidores MCP

Los servidores MCP locales deben exponer herramientas específicas para la lectura y escritura.

### Servidor `secretaria-local` (Lectura OLTP)
Herramientas expuestas:
1. `get_incremental_data(table_name: str, start_date: str, end_date: str, cursor_value: int | str, page_size: int)`
   - Retorna: JSON conteniendo `records` (lista de diccionarios) y `next_cursor` (el ID o timestamp máximo del lote actual).

### Servidor `tais-dm-local` (Escritura OLAP)
Herramientas expuestas:
1. `load_dimension(dim_name: str, records: list)`
   - Inserta lotes en la dimensión correspondiente aplicando estrategias de Upsert si aplica.
2. `load_fact(fact_name: str, records: list)`
   - Inserta lotes en la tabla de hechos garantizando integridad transaccional.

---

## 3. Paginación Basada en Marcas de Agua (Watermarks)

Para evitar desbordamientos de buffer o límites de token en el canal stdio de MCP (que serializa payloads JSON pesados):
- El agente Extractor no solicitará todo el rango de datos en una sola llamada.
- Utilizará el parámetro `cursor_value`. En cada iteración, el agente llamará a `get_incremental_data` pasando el último cursor procesado.
- El servidor MCP responderá con los registros y el `next_cursor` derivado del valor máximo de la columna de ordenación (ej: `id` o `fecha_modificacion`).
- El ciclo de extracción se detiene cuando la herramienta retorne una lista de registros vacía o un tamaño menor a `page_size`.

---

## 4. Estrategia de Pruebas TDD (Mock de Servidor MCP)

Para las pruebas unitarias y de integración sin depender de SQL Server real levantado en el puerto local:
- Se implementará un script de servidor MCP mínimo (`tests/mocks/mcp_server_mock.py`) que interactúe por stdio simulando el protocolo.
- Durante el setup de `conftest.py`, las pruebas levantarán este subproceso mock y apuntarán el `MCPClient` a él.
- Esto valida el transporte stdio real, el handshake del protocolo, y el manejo de excepciones (timeouts y desconexiones) sin dependencias externas pesadas.

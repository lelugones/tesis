# Developer Quickstart: Acceso a Bases de Datos mediante MCP (mcp-db-access)

Este documento describe cómo configurar, ejecutar y probar la capa de acceso a base de datos basada en MCP.

## 1. Requisitos e Instalación

Instala el SDK de MCP para Python en tu entorno virtual:

```bash
pip install mcp pytest-asyncio
```

Asegúrate de que los servidores MCP locales estén registrados en tu archivo de configuración del agente, o bien ten a mano sus comandos de ejecución. En este proyecto se inician como subprocesos stdio:

- **Origen (Secretaria)**: `python -m src.drivers.secretaria_mcp_server`
- **Destino (TAIS_DM)**: `python -m src.drivers.tais_dm_mcp_server`

---

## 2. Ejecutar Pruebas con Mocks de Servidor MCP

Las pruebas unitarias y de integración del cliente MCP no requieren una instancia real de SQL Server corriendo, ya que utilizan el servidor mock stdio provisto en la suite de pruebas.

Para ejecutar los tests de este componente:

```bash
# Ejecutar todas las pruebas unitarias del cliente MCP y del Extractor
pytest tests/unit/test_mcp_client.py tests/unit/test_extractor_mcp.py

# Ejecutar las pruebas de integración del pipeline completo con transporte stdio
pytest tests/integration/test_pipeline_mcp.py
```

---

## 3. Ejemplo de Uso del Wrapper Síncrono `MCPClient`

Los agentes interactúan con `MCPClient` de manera puramente síncrona. A continuación se muestra un ejemplo de cómo instanciar e invocar herramientas:

```python
from src.drivers.mcp_client import MCPClient

# Configurar parámetros del subproceso del servidor MCP
command = "python"
args = ["-m", "src.drivers.secretaria_mcp_server"]

# Instanciar el cliente
client = MCPClient(command=command, args=args)

# Iniciar la sesión stdio (lanza el subproceso)
client.connect()

try:
    # Llamar a una herramienta de manera síncrona
    response = client.call_tool("get_incremental_data", {
        "table_name": "Persona",
        "start_date": "2026-05-01T00:00:00",
        "end_date": "2026-05-19T00:00:00",
        "cursor_value": 0,
        "page_size": 1000
    })
    
    records = response["records"]
    next_cursor = response["next_cursor"]
    print(f"Registros extraídos: {len(records)}. Siguiente cursor: {next_cursor}")
    
finally:
    # Detener el subproceso del servidor de forma limpia
    client.disconnect()
```

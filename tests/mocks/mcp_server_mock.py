import asyncio
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import Any

# Instanciar el servidor (en pruebas se ejecutará como subproceso stdio)
mcp = FastMCP("mock-db-server")

@mcp.tool()
async def get_incremental_data(
    table_name: str,
    start_date: str,
    end_date: str,
    cursor_value: int | str,
    page_size: int = 5000
) -> str:
    """Mock extractor tool."""
    # Retornar una página simulada. Si el cursor es 0, devolvemos 2 registros, sino 0.
    if isinstance(cursor_value, int) and cursor_value == 0:
        records = [
            {
                "id": 1,
                "nombre": "Test 1",
                "ingresos_estimados": "100.50",
                "fecha_modificacion": "2026-05-18T00:00:00",
                "monto_asignado": "5000.00",
                "activa": True,
                "persona_id": 1,
                "indice_vulnera": "0.50",
                "municipio_id": 1
            },
            {
                "id": 2,
                "nombre": "Test 2",
                "ingresos_estimados": "200.50",
                "fecha_modificacion": "2026-05-18T01:00:00",
                "monto_asignado": "1000.00",
                "activa": False,
                "persona_id": 2,
                "indice_vulnera": "0.80",
                "municipio_id": 2
            }
        ]
        next_cursor = 2
    else:
        records = []
        next_cursor = cursor_value

    return json.dumps({
        "records": records,
        "next_cursor": next_cursor
    })

@mcp.tool()
async def load_dimension(dim_name: str, records: list[dict[str, Any]]) -> str:
    """Mock loader for dimension."""
    # Simulamos el procesamiento exitoso
    return json.dumps({"status": "ok", "inserted": len(records)})

@mcp.tool()
async def load_fact(fact_name: str, records: list[dict[str, Any]]) -> str:
    """Mock loader for fact table."""
    return json.dumps({"status": "ok", "inserted": len(records)})

if __name__ == "__main__":
    mcp.run(transport='stdio')

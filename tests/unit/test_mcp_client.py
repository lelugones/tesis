import pytest
from src.drivers.mcp_client import MCPClient
import sys
import os

@pytest.fixture
def mock_mcp_client():
    # Usar el servidor mock a través del interprete actual de python
    client = MCPClient(command=sys.executable, args=["-m", "tests.mocks.mcp_server_mock"])
    client.connect()
    yield client
    client.disconnect()

def test_mcp_client_call_tool_incremental_data(mock_mcp_client):
    """Prueba que el cliente sincronizado puede llamar a get_incremental_data del servidor mock"""
    response = mock_mcp_client.call_tool("get_incremental_data", {
        "table_name": "Persona",
        "start_date": "2026-05-01T00:00:00",
        "end_date": "2026-05-19T00:00:00",
        "cursor_value": 0,
        "page_size": 1000
    })
    
    assert "records" in response
    assert "next_cursor" in response
    assert len(response["records"]) == 2
    assert response["records"][0]["id"] == 1
    assert response["next_cursor"] == 2

def test_mcp_client_call_tool_empty_cursor(mock_mcp_client):
    """Prueba que devuelve registros vacios cuando el cursor no es 0 en el mock"""
    response = mock_mcp_client.call_tool("get_incremental_data", {
        "table_name": "Persona",
        "start_date": "2026-05-01T00:00:00",
        "end_date": "2026-05-19T00:00:00",
        "cursor_value": 2,
        "page_size": 1000
    })
    
    assert "records" in response
    assert len(response["records"]) == 0
    assert response["next_cursor"] == 2

import pytest
import sys
from datetime import datetime
from src.agents.extractor.fetcher import ExtractorAgent
from src.drivers.mcp_client import MCPClient

@pytest.fixture
def mcp_extractor():
    # Usar mock stdio server para secretaria
    client = MCPClient(command=sys.executable, args=["-m", "tests.mocks.mcp_server_mock"])
    client.connect()
    # Paginación pequeña para probar múltiples ciclos si fuera necesario
    agent = ExtractorAgent(connection_manager=client, page_size=1)
    yield agent
    client.disconnect()

def test_extractor_agent_with_mcp(mcp_extractor):
    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 5, 19)
    
    # Esto debe iterar utilizando la herramienta get_incremental_data
    result = mcp_extractor.extract(start_date, end_date)
    
    assert "df_persona" in result
    assert "df_familia" in result
    assert "df_tarjeta" in result
    
    # En nuestro mock, cursor 0 devuelve 2 registros, siguiente devuelve 0.
    assert len(result["df_persona"]) == 2
    assert result["df_persona"][0]["nombre"] == "Test 1"

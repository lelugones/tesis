import pytest
import sys
import pandas as pd
from src.agents.cargador.writer import CargadorAgent
from src.drivers.mcp_client import MCPClient

@pytest.fixture
def mcp_cargador():
    # Usar mock stdio server para tais-dm
    client = MCPClient(command=sys.executable, args=["-m", "tests.mocks.mcp_server_mock"])
    client.connect()
    agent = CargadorAgent(connection_manager=client)
    yield agent
    client.disconnect()

def test_cargador_agent_with_mcp(mcp_cargador):
    df_dim_mock = pd.DataFrame([{"id": 1, "nombre": "Test 1"}])
    df_fact_mock = pd.DataFrame([{"dim_id": 1, "valor": 100}])
    
    payload = {
        "dim_test": df_dim_mock,
        "fact_test": df_fact_mock
    }
    
    # CargadorAgent.load() should call load_dimension and load_fact
    # and not crash
    try:
        mcp_cargador.load(payload)
        success = True
    except Exception as e:
        success = False
        print(e)
        
    assert success

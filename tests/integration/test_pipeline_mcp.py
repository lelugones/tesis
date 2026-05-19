import pytest
import sys
from datetime import datetime
from src.agents.coordinador.orchestrator import CoordinadorAgent

def test_pipeline_end_to_end_mcp():
    """Prueba que el Coordinador puede ejecutar una extracción y carga completa con clientes MCP."""
    # Usaremos el mock para simular ambos servidores
    server_cmd = sys.executable
    server_args = ["-m", "tests.mocks.mcp_server_mock"]
    
    coordinador = CoordinadorAgent(
        secretaria_cmd=server_cmd,
        secretaria_args=server_args,
        tais_dm_cmd=server_cmd,
        tais_dm_args=server_args
    )
    
    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 5, 19)
    
    # Run the ETL pipeline
    try:
        coordinador.run_etl(start_date, end_date)
        success = True
    except Exception as e:
        success = False
        print(f"ETL failed: {e}")
        
    assert success

# Quickstart Guide: Pipeline Multiagente ETL (TAIS_DM)

**Branch**: `001-multiagent-etl` | **Date**: 2026-05-18

Esta guía rápida proporciona las instrucciones necesarias para levantar el entorno de desarrollo, configurar las variables de entorno, y ejecutar las pruebas de aserciones lógicas bajo la suite Pytest.

---

## 1. Requisitos Previos

- Python 3.10.x o superior instalado en el sistema.
- Acceso local a un entorno de comandos (Terminal de comandos o PowerShell en Windows).
- Dependencias mínimas instaladas:
  ```bash
  pip install sqlalchemy pandas pytest pytest-cov pydantic
  ```

---

## 2. Configuración de Entorno de Datos

El pipeline busca las credenciales y motores de base de datos desde variables de entorno. Para propósitos de desarrollo y testeo automatizado, si estas variables no se declaran, `DBConnectionManager` levanta automáticamente bases de datos SQLite en memoria de forma transparente.

Para configurar conexiones a servidores físicos, declare las siguientes variables en su sesión de PowerShell:

```powershell
$env:OLTP_DB_CONN = "postgresql+psycopg2://user:password@localhost:5432/Secretaria"
$env:OLAP_DB_CONN = "postgresql+psycopg2://user:password@localhost:5432/TAIS_DM"
```

O en Linux / Bash:

```bash
export OLTP_DB_CONN="postgresql+psycopg2://user:password@localhost:5432/Secretaria"
export OLAP_DB_CONN="postgresql+psycopg2://user:password@localhost:5432/TAIS_DM"
```

---

## 3. Ejecución del Ciclo TDD con Pytest

De acuerdo con el principio constitucional **II. Desarrollo Guiado por Pruebas (TDD)**, todas las aserciones lógicas y contratos deben validarse antes del despliegue en producción.

### Ejecutar todas las pruebas
Desde la raíz del repositorio (`c:\Proyects\ai\tesis`), ejecute:
```bash
pytest -v
```

### Ejecutar pruebas por categoría física
- **Pruebas Unitarias** (para probar la lógica de transformación de Pandas y el control de errores en caliente):
  ```bash
  pytest tests/unit/ -v
  ```
- **Pruebas de Integración** (para probar transacciones de base de datos, rollbacks y flujo continuo):
  ```bash
  pytest tests/integration/ -v
  ```
- **Pruebas de Contrato** (para validar consistencia de payloads inter-agentes):
  ```bash
  pytest tests/contract/ -v
  ```

### Reporte de Cobertura de Código
Para generar el reporte detallado y validar que se cumple el umbral mínimo del **90%** de cobertura obligatoria:
```bash
pytest --cov=src tests/ --cov-report=term-missing
```

---

## 4. Ejecución del Pipeline en Desarrollo

Para ejecutar el pipeline de forma manual en un flujo de pruebas de punta a punta, se puede invocar la clase `CoordinadorAgent` mediante el siguiente script de desarrollo en Python:

```python
from src.agents.coordinador.orchestrator import CoordinadorAgent
from src.drivers.connections import DBConnectionManager

# 1. Instanciar gestor de conexiones (SQLite en memoria por defecto)
db_manager = DBConnectionManager()

# 2. Inicializar agente orquestador
coordinador = CoordinadorAgent(connection_manager=db_manager)

# 3. Disparar ejecución del pipeline
batch_id = coordinador.run(execution_mode="incremental")

print(f"ETL Execution finished! Batch ID: {batch_id}")
```

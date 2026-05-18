# Pipeline Multiagente ETL para Data Mart (TAIS_DM)

Este repositorio contiene la implementación de un **Sistema de Agentes Inteligentes Cooperativos** diseñado para automatizar el flujo ETL (Extracción, Transformación y Carga) de datos de asistencia social. El sistema extrae registros de manera incremental de la base de datos transaccional (`Secretaria` OLTP), los procesa bajo las reglas multidimensionales de la Metodología Hefesto, y los carga de forma atómica y segura en el Data Mart analítico (`TAIS_DM` OLAP).

---

## 🤖 Arquitectura del Sistema de Agentes

El pipeline está compuesto por cuatro agentes especializados que cooperan secuencialmente en memoria (usando estructuras de datos de Pandas) para evitar escrituras intermedias y maximizar la eficiencia:

1. **Agente Extractor (`ExtractorAgent`)**: 
   Realiza la extracción incremental de datos históricos y nuevos desde el origen OLTP mediante paginación controlada (*throttling*) y mapeo preciso de tipos de datos complejos (como `money` a `decimal.Decimal` en Python) para preservar la precisión de los montos financieros.

2. **Agente Transformador (`TransformadorAgent`)**: 
   Filtra los datos geográficamente para restringir el ámbito estrictamente a la provincia de Salta, envía registros anómalos o huérfanos a un flujo de curación geográfica, y normaliza en memoria el índice de vulnerabilidad social en una escala de `[0.00, 1.00]`.

3. **Agente Cargador (`CargadorAgent`)**: 
   Resuelve y asocia claves subrogadas (*Surrogate Keys*) e inyecta las dimensiones y la tabla de hechos en el Data Mart de destino aplicando estrategias de *Upsert* para garantizar la idempotencia de las ejecuciones.

4. **Agente Coordinador (`CoordinadorAgent`)**: 
   Actúa como el orquestador principal del ciclo de vida del pipeline. Gestiona la trazabilidad mediante identificadores únicos (`batch_id`), escribe bitácoras de auditoría en la tabla `registro_ejecuciones`, y controla políticas de reintentos mediante *backoff* exponencial ante fallos temporales.

---

## 🛠️ Metodología y Entorno de Desarrollo

### 📋 Spec-Driven Development (SDD)
El proyecto ha sido desarrollado bajo la metodología de **Desarrollo Guiado por Especificaciones (SDD)** utilizando **GitHub Spec Kit**. Esto garantiza que cada fase del diseño técnico (definido formalmente en `specs/001-multiagent-etl/`) se traduzca de forma directa y estructurada en especificaciones claras y listas de tareas validadas en `tasks.md`, asegurando una consistencia perfecta entre los requerimientos y la implementación del código.

### 🧪 Verificación y Pruebas
La robustez y contratos del sistema se validan mediante una suite de pruebas unitarias, de integración y de contrato bajo Pytest con una cobertura superior al **90%**, simulando bases de datos transaccionales y analíticas mediante entornos SQLite en memoria.

### 💻 IDE Antigravity y Python 3.14
Los agentes y la infraestructura se implementaron y probaron utilizando el **IDE Antigravity** sobre el entorno de ejecución **Python 3.14**, garantizando un alto rendimiento y compatibilidad con las últimas características del lenguaje y el tipado estático.

---

## 📦 Instalación y Configuración

Las dependencias del sistema están especificadas en el archivo `requirements.txt`. Para instalarlas, siga los siguientes pasos:

### 1. Clonar el repositorio y configurar el entorno
Abra una consola de comandos (PowerShell en Windows o Terminal en Linux) en la raíz del repositorio y cree un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
Instale los paquetes requeridos ejecutando:

```bash
pip install -r requirements.txt
```

Las librerías principales instaladas son:
* **SQLAlchemy (>=2.0.0)**: ORM y gestor de pools de conexión transaccionales y atómicas.
* **Pandas (>=2.2.0)**: Procesamiento de datos ultrarrápido y transformaciones en memoria.
* **Pydantic (>=2.0.0)**: Validación robusta de los contratos de datos entre agentes.
* **Pytest (>=8.0.0)** y **Pytest-Cov (>=4.1.0)**: Suite de ejecución de pruebas y reportes de cobertura de código.

---

## 🚦 Ejecución de Pruebas

Para validar el funcionamiento del sistema y la cobertura del código en cualquier momento, ejecute la suite de pruebas desde la raíz del proyecto:

### Ejecutar todas las pruebas con salida detallada
```bash
pytest -v
```

### Obtener el reporte de cobertura de código (Tasa objetivo >= 90%)
```bash
pytest --cov=src tests/ --cov-report=term-missing
```

# Research & Design Justifications: Pipeline Multiagente ETL (TAIS_DM)

**Branch**: `001-multiagent-etl` | **Date**: 2026-05-18

Este documento consolida las decisiones de diseño arquitectónico, las tecnologías seleccionadas y el análisis de alternativas evaluadas para la implementación del pipeline de datos multiagente de la Secretaría de Políticas Alimentarias.

---

## 1. Mapeo Tipado de Monedas (`money` en SQL Server)

- **Decisión**: Utilizar la clase nativa `decimal.Decimal` de Python para todas las columnas de importes monetarios y porcentajes, prohibiendo estrictamente el uso de tipos `float`.
- **Razón**: Los tipos de datos de punto flotante en Python introducen imprecisiones aritméticas de redondeo binario (e.g., `0.1 + 0.2 != 0.3`). Para reportes financieros y auditorías de transferencias monetarias mediante Tarjetas sociales, cualquier desviación centesimal invalida los reportes. El tipo `Decimal` almacena números con precisión fija de base 10, reflejando fielmente el tipo `money` u `numeric` de SQL Server.
- **Alternativas consideradas**:
  - *Castear a float*: Rechazado debido al riesgo de desbordamientos de precisión acumulada tras millones de agregaciones.
  - *Almacenar como enteros en centavos*: Requiere reescribir lógica de consulta y dificulta operaciones matemáticas directas en Pandas. Rechazado en favor de `decimal.Decimal`.

---

## 2. Motor de Transformación en Memoria (Pandas DataFrames)

- **Decisión**: Ejecutar el 100% de la lógica de homologación, calidad y limpieza en memoria mediante Pandas DataFrames en el Agente Transformador.
- **Razón**: El procesamiento por lotes (batch) incrementales de tamaño acotado (5,000 registros) permite que toda la carga útil quepa cómodamente en la RAM del servidor. Pandas es extremadamente eficiente para realizar filtrados condicionales, reemplazo de nulos, formateo de fechas y joins multidimensionales de dimensiones en memoria, optimizando la latencia de transformación por debajo de los 2 segundos por lote.
- **Alternativas consideradas**:
  - *Transformación directa con consultas SQL en base OLAP*: Incrementa el acoplamiento y sobrecarga la base analítica destino. Las transformaciones inter-agentes son más difíciles de testear de forma aislada bajo TDD.
  - *Apache Spark / PySpark*: Añade sobrecarga y complejidad excesiva a la infraestructura para los volúmenes de datos proyectados (<100,000 registros diarios). Rechazado en favor de la simplicidad y eficiencia de Pandas.

---

## 3. Estrategia de Invocación Analítica a Stored Procedures

- **Decisión**: Delegar métricas complejas e históricas (ej. `sp_CalcularCrecimientoMunicipal`, `sp_PorcentajeMejoraPersona`) al servidor transaccional OLTP invocando los Stored Procedures existentes mediante llamadas parametrizadas y encapsulando el retorno en DataFrames temporales.
- **Razón**: Los Stored Procedures y funciones analíticas ya se encuentran implementados, indexados y optimizados en la base transaccional de origen por parte del equipo de TI. Re-codificar esa compleja lógica histórica en Python aumentaría el riesgo de discrepancias y duplicación de código de negocio. Invocarlos mediante SQLAlchemy aprovecha el motor de la base de datos para cálculos pesados antes de la transferencia.
- **Alternativas consideradas**:
  - *Re-escribir lógica analítica en Python*: Descartado por el alto costo de mantenimiento y el riesgo de inconsistencias con otros sistemas gubernamentales.

---

## 4. Aislamiento Transaccional y Persistencia (SQLAlchemy)

- **Decisión**: Utilizar SQLAlchemy con nivel de aislamiento `READ COMMITTED` y control de transacción atómica a nivel de lote en el Agente Cargador.
- **Razón**: SQLAlchemy gestiona de forma nativa pools de conexiones eficientes y provee una abstracción de sesiones limpia (`session.begin()`, `session.commit()`, `session.rollback()`). La atómica secuencia de dimensiones primero y hechos después, garantiza que si falla la inserción de algún hecho por claves huérfanas, toda la sesión se revierta, manteniendo el Data Mart `TAIS_DM` libre de datos corruptos.
- **Alternativas consideradas**:
  - *Conexiones físicas crudas (DB-API psycopg2 / pyodbc)*: Requiere escribir manualmente la lógica de manejo de transacciones complejas y conexiones manuales, aumentando la propensión a fugas de recursos (resource leaks).

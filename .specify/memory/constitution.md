<!--
SYNC IMPACT REPORT
- Version change: 1.1.0 -> 1.1.0
- List of modified principles: None
- Added sections: None
- Removed sections: None
- Templates requiring updates: None
- Follow-up TODOs: None
-->
# TAIS_DM Constitution

## Core Principles

### I. Desarrollo Guiado por Especificaciones (Spec-Driven Development - SDD)
Cada componente de software y cada agente inteligente (Coordinador, Extractor, Transformador, Cargador) debe ser definido formalmente mediante una especificación ejecutable antes de iniciar su desarrollo. Las especificaciones actúan como contratos funcionales y técnicos inviolables que definen entradas, salidas, comportamientos esperados y manejo de errores. 

Toda interacción de los agentes con el contexto de persistencia debe estar estrictamente regulada en la especificación, prohibiendo conexiones directas ad-hoc o la evasión de las abstracciones de interfaz establecidas.

### II. Desarrollo Guiado por Pruebas (Test-Driven Development - TDD)
Las pruebas unitarias y de integración de Pytest deben escribirse en estado "Fallo" (Red) antes de escribir el código de producción. La suite de pruebas debe verificar tanto el comportamiento individual de cada agente como la interacción y consistencia del pipeline ETL completo de manera automatizada, garantizando una cobertura mínima del 90%.

### III. Modelado Multidimensional con Metodología Hefesto
Toda la lógica de transformación y carga del Data Mart TAIS_DM debe regirse estrictamente por el modelo multidimensional derivado de la Metodología Hefesto aplicada a la Secretaría de Políticas Alimentarias. Esto incluye la correcta carga de dimensiones y tablas de hechos con sus respectivas métricas: `admPersonas`, `efiProgramas`, `vulneraSocial`, `participaMunicipal`, `usoTarjetas`.

### IV. Arquitectura Multi-Agente Cooperativa
El sistema se compone de cuatro agentes independientes con responsabilidades claras y contratos explícitos, cuya manipulación de datos se delega en las capacidades del protocolo MCP:
- **Coordinador**: Orquesta y supervisa la ejecución del pipeline y la cooperación de los agentes.
- **Extractor**: Recupera datos incrementales de la base de datos de origen OLTP consumiendo exclusivamente las herramientas expuestas por el MCP `secretaria-local`.
- **Transformador**: Aplica reglas de calidad, limpieza, homologación y conformación dimensional de datos en memoria o áreas de staging autorizadas.
- **Cargador**: Almacena las dimensiones y tablas de hechos en el Data Mart consumiendo exclusivamente las herramientas expuestas por el MCP `tais-dm-local`, asegurando la integridad referencial.

### V. Trazabilidad, Monitoreo y Calidad de Datos
El pipeline ETL debe generar logs estructurados y metadatos de auditoría detallados para cada ejecución. Se debe garantizar la validación de esquemas y la consistencia en cada etapa del proceso (Extracción, Transformación, Carga) con mecanismos claros de manejo de excepciones y alertas ante inconsistencias en los datos.

## Restricciones de la Arquitectura y Stack Tecnológico

El stack tecnológico y de infraestructura debe cumplir estrictamente con los siguientes requisitos:
- **Lenguaje**: Python 3.10 o superior.
- **Base de Datos Origen**: Microsoft SQL Server (Instancia Local - Base de Datos "Secretaria").
- **Base de Datos Destino**: Microsoft SQL Server (Instancia Local - Base de Datos "TAIS_DM").
- **Capa de Abstracción de Datos (Agentes)**: Model Context Protocol (MCP). Queda estrictamente prohibido el uso de drivers tradicionales de conexión directa (como pyodbc o SQLAlchemy nativo) dentro de la lógica central de los agentes. El acceso se realizará mediante el uso de Skills de Spec Kit vinculadas a los siguientes servidores:
  - Acceso a Origen (*Secretaria*): Servidor MCP `secretaria-local`.
  - Acceso a Destino (*TAIS_DM*): Servidor MCP `tais-dm-local`.
- **Pruebas**: Pytest para pruebas unitarias y de integración, mockeando o levantando las herramientas MCP correspondientes.
- **Framework de Especificaciones**: Spec Kit de GitHub para la gestión del ciclo de vida del desarrollo y la ejecución de herramientas inteligentes de base de datos.

## Flujo de Trabajo y Ciclo de Vida del Desarrollo

El desarrollo de cada nueva funcionalidad, agente o componente debe seguir el siguiente flujo secuencial de calidad:
1. **Especificación**: Definición de la Especificación del Agente en `specs/` usando el template ejecutable, declarando explícitamente qué herramientas y schemas de las MCP Skills va a consumir.
2. **Revisión**: Aprobación de la especificación técnica por parte del equipo.
3. **Fase Red**: Creación de pruebas unitarias (`tests/`) que validen la especificación y verificación de su fallo.
4. **Fase Green**: Implementación del código fuente del agente hasta que pasen las pruebas.
5. **Fase Refactor**: Optimización de la calidad y rendimiento del código sin alterar el comportamiento contratado.

## Governance

1. Cualquier modificación a las especificaciones o al esquema del Data Mart requiere una enmienda formal de esta Constitución y la actualización de los contratos.
2. Todas las tareas de implementación deben validarse contra las especificaciones activas del sistema.
3. No se permite la inclusión de código en la rama principal (`master`) que no cuente con una cobertura de pruebas adecuada y el paso exitoso de todas las pruebas en la suite.
4. Para la guía en tiempo de ejecución de desarrollo, se utilizará el archivo `AGENTS.md` y las especificaciones almacenadas en `specs/`.

**Version**: 1.1.0 | **Ratified**: 2026-05-19 | **Last Amended**: 2026-05-19
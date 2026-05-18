<!--
SYNC IMPACT REPORT
- Version change: [TEMPLATE] -> 1.0.0
- List of modified principles:
  - PRINCIPLE 1: I. Desarrollo Guiado por Especificaciones (Spec-Driven Development - SDD)
  - PRINCIPLE 2: II. Desarrollo Guiado por Pruebas (Test-Driven Development - TDD)
  - PRINCIPLE 3: III. Modelado Multidimensional con Metodología Hefesto
  - PRINCIPLE 4: IV. Arquitectura Multi-Agente Cooperativa
  - PRINCIPLE 5: V. Trazabilidad, Monitoreo y Calidad de Datos
- Added sections:
  - Restricciones de la Arquitectura y Stack Tecnológico
  - Flujo de Trabajo y Ciclo de Vida del Desarrollo
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: None
-->
# TAIS_DM Constitution

## Core Principles

### I. Desarrollo Guiado por Especificaciones (Spec-Driven Development - SDD)
Cada componente de software y cada agente inteligente (Coordinador, Extractor, Transformador, Cargador) debe ser definido formalmente mediante una especificación ejecutable antes de iniciar su desarrollo. Las especificaciones actúan como contratos funcionales y técnicos inviolables que definen entradas, salidas, comportamientos esperados y manejo de errores.

### II. Desarrollo Guiado por Pruebas (Test-Driven Development - TDD)
Las pruebas unitarias y de integración de Pytest deben escribirse en estado "Fallo" (Red) antes de escribir el código de producción. La suite de pruebas debe verificar tanto el comportamiento individual de cada agente como la interacción y consistencia del pipeline ETL completo de manera automatizada, garantizando una cobertura mínima del 90%.

### III. Modelado Multidimensional con Metodología Hefesto
Toda la lógica de transformación y carga del Data Mart TAIS_DM debe regirse estrictamente por el modelo multidimensional derivado de la Metodología Hefesto aplicada a la Secretaría de Políticas Alimentarias. Esto incluye la correcta carga de dimensiones y tablas de hechos con sus respectivas métricas: `admPersonas`, `efiProgramas`, `vulneraSocial`, `participaMunicipal`, `usoTarjetas`.

### IV. Arquitectura Multi-Agente Cooperativa
El sistema se compone de cuatro agentes independientes con responsabilidades claras y contratos explícitos:
- **Coordinador**: Orquesta y supervisa la ejecución del pipeline y la cooperación de los agentes.
- **Extractor**: Recupera datos incrementales del origen OLTP (Base de Datos 'Secretaria').
- **Transformador**: Aplica reglas de calidad, limpieza, homologación y conformación dimensional de datos.
- **Cargador**: Almacena las dimensiones y tablas de hechos en el Data Mart 'TAIS_DM' asegurando la integridad referencial.

### V. Trazabilidad, Monitoreo y Calidad de Datos
El pipeline ETL debe generar logs estructurados y metadatos de auditoría detallados para cada ejecución. Se debe garantizar la validación de esquemas y la consistencia en cada etapa del proceso (Extracción, Transformación, Carga) con mecanismos claros de manejo de excepciones y alertas ante inconsistencias en los datos.

## Restricciones de la Arquitectura y Stack Tecnológico

El stack tecnológico y de infraestructura debe cumplir estrictamente con los siguientes requisitos:
- **Lenguaje**: Python 3.10 o superior.
- **Base de Datos Origen**: PostgreSQL u otra base de datos OLTP ("Secretaria").
- **Base de Datos Destino**: PostgreSQL u otra base de datos OLAP ("TAIS_DM").
- **Pruebas**: Pytest para pruebas unitarias y de integración.
- **Manejo de Base de Datos**: SQLAlchemy y controladores robustos de bases de datos bajo la carpeta `drivers/`.
- **Framework de Especificaciones**: Spec Kit de GitHub para la gestión del ciclo de vida del desarrollo.

## Flujo de Trabajo y Ciclo de Vida del Desarrollo

El desarrollo de cada nueva funcionalidad, agente o componente debe seguir el siguiente flujo secuencial de calidad:
1. **Especificación**: Definición de la Especificación del Agente en `specs/` usando el template ejecutable.
2. **Revisión**: Aprobación de la especificación técnica por parte del equipo.
3. **Fase Red**: Creación de pruebas unitarias (`tests/`) que validen la especificación y verificación de su fallo.
4. **Fase Green**: Implementación del código fuente del agente hasta que pasen las pruebas.
5. **Fase Refactor**: Optimización de la calidad y rendimiento del código sin alterar el comportamiento contratado.

## Governance

1. Cualquier modificación a las especificaciones o al esquema del Data Mart requiere una enmienda formal de esta Constitución y la actualización de los contratos.
2. Todas las tareas de implementación deben validarse contra las especificaciones activas del sistema.
3. No se permite la inclusión de código en la rama principal (`master`) que no cuente con una cobertura de pruebas adecuada y el paso exitoso de todas las pruebas en la suite.
4. Para la guía en tiempo de ejecución de desarrollo, se utilizará el archivo `AGENTS.md` y las especificaciones almacenadas en `specs/`.

**Version**: 1.0.0 | **Ratified**: 2026-05-18 | **Last Amended**: 2026-05-18

# Agent Technical Specification: [AGENT_NAME]

**System Acronym**: TAIS_DM
**Component**: [Coordinador | Extractor | Transformador | Cargador]
**Version**: [X.Y.Z]
**Status**: Draft | Under Review | Approved
**Target Module**: [e.g., `src/agents/extractor/`]

## 1. Executive Summary & Purpose

[Provide a high-level summary of what this agent does, its role in the TFI Maestría en Ciencia de Datos, and how it fits into the Hefesto Methodology for the Secretaría de Políticas Alimentarias.]

---

## 2. Contract & Interfaces

Use this section to declare the strict data and operational contracts for this agent.

<% CONTRACT_INTERFACE %>
### Inputs
- **Data Source**: [e.g., OLTP 'Secretaria' Database, or input queue / upstream agent payload]
- **Schema / Payload format**:
  ```json
  {
    "input_parameter": "type_definition"
  }
  ```

### Outputs
- **Data Destination**: [e.g., OLAP 'TAIS_DM' Database, or output payload to downstream agent]
- **Schema / Payload format**:
  ```json
  {
    "output_parameter": "type_definition"
  }
  ```

### Dependencies & Drivers
- **Drivers Required**: [e.g., SQLAlchemy, psycopg2, connections.py]
- **API/Method Signature**: `def execute(self, session, *args, **kwargs) -> dict`
<% END_CONTRACT_INTERFACE %>

---

## 3. Measurable Metrics & Data Mart Mapping

Declare the specific metrics and multidimensional columns this agent is responsible for extracting, transforming, or loading.

<% METRICS_SPEC %>
### Primary Metrics Handled
- **admPersonas**: [Description of count/volume of food policy beneficiaries]
- **efiProgramas**: [Performance/efficiency ratios of the nutritional programs]
- **vulneraSocial**: [Socio-economic vulnerability indexes calculated or stored]
- **participaMunicipal**: [Municipal-level engagement / segmentation of Salta municipalities]
- **usoTarjetas**: [Electronic food card usage transaction counts and amounts]

### Schema Attributes & Data Types
| Target Dimension/Fact | Field Name | Data Type | Constraint | Source Field |
|-----------------------|------------|-----------|------------|--------------|
| [e.g., dimBeneficiarios] | [id_beneficiario] | [INTEGER] | [PRIMARY KEY] | [Secretaria.dbo.personas.id] |
| [e.g., factPolíticasAlimentarias] | [admPersonas] | [INTEGER] | [NOT NULL] | [Calculated Count] |
<% END_METRICS_SPEC %>

---

## 4. Test-Driven Development (TDD) Acceptance Scenarios

These scenarios are parsed by Spec Kit and translated into executable Pytest test cases.

<% TDD_SCENARIOS %>
### Scenario 1: Successful Execution under Normal Conditions
- **Given**: [Initial database state or mock data input]
- **When**: The agent's `execute()` function is called with valid parameters
- **Then**: The return payload matches the expected schema
- **And**: The state of the destination DB/medium matches the expected state
- **And**: The operation is completed within [X] milliseconds

### Scenario 2: Handling Missing or Malformed Inputs
- **Given**: Input payload is missing [Mandatory Field]
- **When**: The agent is executed
- **Then**: It raises `ValidationError` or returns an explicit failure state
- **And**: Logs a structured warning detailing the invalid fields

### Scenario 3: Transaction Isolation and Error Recovery
- **Given**: Connection to the destination database is lost mid-transaction
- **When**: The agent is executing
- **Then**: All changes are rolled back completely
- **And**: It propagates `DatabaseConnectionError` to the Coordinador Agent
<% END_TDD_SCENARIOS %>

---

## 5. Compliance & Data Quality Rules

Define the strict validations, security checks, and data quality limits.

<% COMPLIANCE_RULE %>
- **RULE-01 (Data Integrity)**: The agent MUST NOT load facts without checking the existence of referenced dimension keys in `TAIS_DM` (Referential Integrity).
- **RULE-02 (Geographical Bound)**: Geographical records MUST be restricted to the Province of Salta and its municipalities (e.g., Orán, Tartagal, Cafayate, Cachi). Any other geographical records must be flagged and sent to a curation table.
- **RULE-03 (Vulnerability Range)**: Vulnerability metric `vulneraSocial` MUST be a normalized index between 0.00 and 1.00.
- **RULE-04 (Traceability)**: Every data block processed MUST append audit columns: `fecha_carga` (timestamp), `agente_responsable` (agent slug), and `tote_lote` (execution batch ID).
<% END_COMPLIANCE_RULE %>

# Tasks: Pipeline Multiagente ETL para Data Mart (TAIS_DM)

**Input**: Design documents from `specs/001-multiagent-etl/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Pytest-based TDD is mandated. All tasks include test creation in the "Red" (Failing) state before implementing the production code.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project directory initialization and base configuration.

- [x] T001 Initialize the project structure creating folders: `src/agents/coordinador`, `src/agents/extractor`, `src/agents/transformador`, `src/agents/cargador`, `src/drivers` and `tests/unit`, `tests/integration`, `tests/contract` per plan.md.
- [x] T002 Configure Python virtual environment, project requirements and verify Pytest dependencies inside root `requirements.txt`.
- [x] T003 [P] Setup linting, formatting (e.g., black/flake8) and config files (`pyproject.toml` or `setup.cfg`).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core connection manager and database schemas that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Implement `DBConnectionManager` in `src/drivers/connections.py` utilizing SQLAlchemy pools to support connections to OLTP and OLAP, including SQLite in-memory for testing.
- [x] T005 Create database initialization script `src/drivers/init_db.py` to set up OLTP mock schemas and OLAP target schemas (including auditing and `curacion_geografica` tables) in SQLite.
- [x] T006 [P] Implement shared logging and exception handling modules in `src/utils/logging.py`.
- [x] T007 [P] Implement payload schema loading and validation utility in `src/utils/contracts.py` using Pydantic or JSON schemas from `specs/001-multiagent-etl/contracts/`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Carga Incremental Automatizada (Priority: P1) 🎯 MVP

**Goal**: Incremental extraction, transformation, and load of social assistance metrics without duplicating records under normal pipeline run conditions.

**Independent Test**: Seed transaccional OLTP mock DB with new and modified beneficiarios in Orán/Salta, run the pipeline, check OLAP Data Mart rows match, re-run for same period and assert idempotencia (no duplicates created, upsert logic updates matches).

### Tests for User Story 1 (TDD Red Phase) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Create unit tests for ExtractorAgent (`tests/unit/test_extractor.py`) testing incremental filter parameters, `decimal.Decimal` mapping, and chunk page throttling (ASSERT-EXT-01, ASSERT-EXT-02, ASSERT-EXT-03).
- [x] T009 [P] [US1] Create unit tests for TransformadorAgent (`tests/unit/test_transformador.py`) testing Salta geographic isolation, index normalizations, and Stored Procedure mocks (ASSERT-TRANS-01, ASSERT-TRANS-02, ASSERT-TRANS-03).
- [x] T010 [P] [US1] Create unit tests for CargadorAgent (`tests/unit/test_cargador.py`) verifying dimension insertions, surrogate keys mapping, and upsert idempotency logic (ASSERT-LOAD-01, ASSERT-LOAD-02, ASSERT-LOAD-03).
- [x] T011 [P] [US1] Create integration tests (`tests/integration/test_pipeline_us1.py`) validating the whole success path of US1 from end-to-end.

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement the `ExtractorAgent` in `src/agents/extractor/fetcher.py` using query chunking (5,000 records) and 500 ms sleep pauses for throttling.
- [x] T013 [P] [US1] Implement `decimal.Decimal` type mapping in `src/agents/extractor/fetcher.py` for all monetales fields.
- [x] T014 [P] [US1] Implement the `TransformadorAgent` in `src/agents/transformador/refiner.py` executing normalizations for `vulneraSocial` (`[0.00, 1.00]`).
- [x] T015 [US1] Implement territorial filter in `src/agents/transformador/refiner.py` to route non-Salta records to the `curacion_geografica` DataFrame and write Warning logs.
- [x] T016 [US1] Implement the `CargadorAgent` in `src/agents/cargador/writer.py` performing upsert loading for `dimBeneficiarios`, `dimProgramas`, `dimGeografia`, `dimTiempo` and `factPolíticasAlimentarias`.
- [x] T017 [US1] Verify that Pytest suite runs, tests pass ("Green Phase"), and refactor code for performance optimization.

**Checkpoint**: At this point, User Story 1 (incremental success flow) is fully functional and testable independently.

---

## Phase 4: User Story 2 - Resiliencia de Transacciones y Coordinación (Priority: P2)

**Goal**: Atomic transactional execution, complete rollback on failures, retry policies, and execution log audits controlled by the Coordinador Agent.

**Independent Test**: Run pipeline, inject database error in Cargador mid-run, check that OLAP database was fully rolled back (no records inserted for this batch), and verify `registro_ejecuciones` table logs a `FAILED` execution.

### Tests for User Story 2 (TDD Red Phase) ⚠️

- [x] T018 [P] [US2] Create unit tests for CoordinadorAgent (`tests/unit/test_coordinador.py`) testing batch_id UUID generations, retry policies with backoff, and execution logs (ASSERT-COORD-01, ASSERT-COORD-02, ASSERT-COORD-03).
- [x] T019 [P] [US2] Create integration tests (`tests/integration/test_pipeline_us2.py`) that mock connection failures or schema violations during facts load and assert full transactional rollback.

### Implementation for User Story 2

- [x] T020 [P] [US2] Implement transaction management in `src/agents/cargador/writer.py` utilizing SQLAlchemy session blocks (`session.begin()`, `session.rollback()`) to ensure complete atomic batch execution.
- [x] T021 [P] [US2] Implement the `CoordinadorAgent` in `src/agents/coordinador/orchestrator.py` controlling UUID generation, orchestrating agent handshakes, and running exponential backoff retries.
- [x] T022 [US2] Implement audit writes in `src/agents/coordinador/orchestrator.py` to persist execution summaries to the `registro_ejecuciones` table.
- [x] T023 [US2] Verify that Pytest integration suite runs, tests pass, and refactor code.

**Checkpoint**: At this point, transaction rollbacks and coordinate retries are fully robust and testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validations, profiling, documentation, and cleanup.

- [x] T024 Perform manual verification of the whole flow on a staged SQLite configuration.
- [x] T025 Run test suite coverage and ensure overall coverage is >= 90% via `pytest --cov`.
- [x] T026 Update developers quickstart documentation in `specs/001-multiagent-etl/quickstart.md` and complete walkthrough.md.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. Blocks all User Stories.
- **User Stories (Phase 3+)**: All depend on Foundational completion.
  - User stories can run in sequence: Phase 3 (US1 - MVP) -> Phase 4 (US2 - Robustness).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

---

## Parallel Example: User Story 1

```bash
# Launch test files in TDD Red phase in parallel
pytest tests/unit/test_extractor.py tests/unit/test_transformador.py -v

# Code ExtractorAgent and TransformadorAgent in parallel (separate files)
Task: "Implement the ExtractorAgent in src/agents/extractor/fetcher.py"
Task: "Implement the TransformadorAgent in src/agents/transformador/refiner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run Pytest tests, verify incremental loaders and Salta curations.

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready.
2. Add User Story 1 -> Test independently -> Deploy/Demo (MVP!).
3. Add User Story 2 -> Test independently -> Rollback resilience and coordinate logs ready.
4. Final Polish -> Validate 90%+ coverage.

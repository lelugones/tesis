# Tasks: Acceso a Bases de Datos mediante MCP (mcp-db-access)

**Input**: Design documents from `/specs/002-mcp-db-access/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: TDD is required by the project constitution. Test tasks are included below and must be written to fail first.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install dependencies (`mcp`, `pytest-asyncio`) in `requirements.txt`
- [x] T002 Create mock MCP stdio servers in `tests/mocks/mcp_server_mock.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core MCP client infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Implement the generic `MCPClient` wrapper with stdio transport in `src/drivers/mcp_client.py`
- [x] T004 [P] Write unit tests for `MCPClient` using stdio mocks in `tests/unit/test_mcp_client.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Extracción de Datos OLTP a través de MCP (Priority: P1) 🎯 MVP

**Goal**: ExtractorAgent retrieves data incrementally via `secretaria-local` MCP server.

**Independent Test**: Verify `ExtractorAgent` queries table data and paginates through cursors without using direct SQLAlchemy calls.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Write failing unit test for `ExtractorAgent` in `tests/unit/test_extractor_mcp.py` verifying MCP tools call logic

### Implementation for User Story 1

- [x] T006 [US1] Modify `ExtractorAgent` in `src/agents/extractor/fetcher.py` to use `MCPClient` for paginating over `get_incremental_data` tool

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Carga de Datos al Data Mart a través de MCP (Priority: P1)

**Goal**: CargadorAgent persists dimensions and fact tables via `tais-dm-local` MCP server.

**Independent Test**: Verify `CargadorAgent` sends dimensional and fact loads to `tais-dm-local` tools without pyodbc or SQLAlchemy connection manager.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US2] Write failing unit test for `CargadorAgent` in `tests/unit/test_cargador_mcp.py` verifying MCP tools call logic

### Implementation for User Story 2

- [x] T008 [US2] Modify `CargadorAgent` in `src/agents/cargador/writer.py` to use `MCPClient` to call `load_dimension` and `load_fact` tools

**Checkpoint**: User Story 2 is fully functional and testable independently.

---

## Phase 5: Pipeline & Orchestration Integration (Priority: P2)

**Goal**: CoordinadorAgent manages connection lifetimes and full pipeline orchestration.

**Independent Test**: Complete pipeline integration test executes successfully using MCP stdio clients.

### Tests for Integration Phase

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US3] Write failing integration test in `tests/integration/test_pipeline_mcp.py` executing full ETL using stdio MCP mocks

### Implementation for Integration Phase

- [x] T010 [US3] Modify `CoordinadorAgent` in `src/agents/coordinador/orchestrator.py` to setup, connect, and tear down MCP clients

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, validation, and documentation updates.

- [x] T011 [P] Remove unused direct database connection logic from `src/drivers/connections.py`
- [x] T012 [P] Verify setup and run documentation in `specs/002-mcp-db-access/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- Setup tasks T001 and T002 can run in parallel.
- Unit tests T004, T005, and T007 can be drafted in parallel.
- Cleanup T011 and Quickstart check T012 can run in parallel in the Polish phase.

---

## Parallel Example: User Story 1

```bash
# Draft test files for US1 and US2 in parallel:
Task: "Write failing unit test for ExtractorAgent in tests/unit/test_extractor_mcp.py"
Task: "Write failing unit test for CargadorAgent in tests/unit/test_cargador_mcp.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

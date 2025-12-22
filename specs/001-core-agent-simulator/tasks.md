# Tasks: Core Agent Simulator

**Input**: Design documents from `/specs/001-core-agent-simulator/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and core structure

- [ ] T001 Create directory structure: `adk_agent_sim/ui/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- [ ] T002 Add dependencies to pyproject.toml: `streamlit>=1.30.0` (google-adk already present)
- [ ] T003 [P] Create `tests/fixtures/mock_agents.py` with mock Agent and Tool implementations for testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create `adk_agent_sim/session.py` with `SessionState` and `TraceStep` dataclasses per data-model.md
- [ ] T005 [P] Create `tests/unit/test_session.py` with tests for SessionState initialization and TraceStep creation
- [ ] T006 Create `adk_agent_sim/execution.py` with `_run_async()` helper for async-to-sync bridging
- [ ] T007 [P] Create `tests/unit/test_execution.py` with tests for async execution helper
- [ ] T008 Create `adk_agent_sim/introspection.py` with ADK wrapper functions:
  - `get_agent_tools(agent)` → wraps `agent.canonical_tools()`
  - `get_agent_instruction(agent)` → wraps `agent.canonical_instruction()`
  - `get_tool_declaration(tool)` → wraps `tool._get_declaration()`
- [ ] T009 [P] Create `tests/unit/test_introspection.py` with tests using mock agents

**Checkpoint**: Foundation ready - core models and utilities tested and working

---

## Phase 3: User Story 1 - Roleplay as Agent (Priority: P1) 🎯 MVP

**Goal**: Developer can load an agent, view its tools, fill in parameters, and execute tools via UI

**Independent Test**: Load agent → see instructions → select tool → fill form → execute → see output

### Tests for User Story 1

- [ ] T010 [P] [US1] Create `tests/unit/test_schema_renderer.py` with tests for all type mappings:
  - STRING → text_input
  - INTEGER → number_input(step=1)
  - NUMBER → number_input
  - BOOLEAN → checkbox
  - ENUM → selectbox
  - OBJECT/ARRAY → text_area (JSON)
- [ ] T011 [P] [US1] Create `tests/integration/test_tool_execution.py` testing tool execution with mocked ToolContext

### Implementation for User Story 1

- [ ] T012 [US1] Create `adk_agent_sim/schema_renderer.py` with `SchemaRenderer` class:
  - `render_form(declaration: FunctionDeclaration) -> dict` method
  - Type-to-widget mapping per spec FR-06
  - Required field validation per spec FR-07
- [ ] T013 [US1] Create `adk_agent_sim/context_mock.py` with minimal ToolContext/InvocationContext construction
- [ ] T014 [US1] Create `adk_agent_sim/ui/__init__.py` (empty, marks as package)
- [ ] T015 [P] [US1] Create `adk_agent_sim/ui/sidebar.py`:
  - Agent selector dropdown (if multiple agents)
  - Tool list with names and descriptions
  - Tool selection callback
- [ ] T016 [P] [US1] Create `adk_agent_sim/ui/tool_form.py`:
  - Dynamic form generation using SchemaRenderer
  - "Run Tool" button
  - Tool output display area
- [ ] T017 [US1] Create `adk_agent_sim/ui/main.py`:
  - Streamlit page config
  - Agent info display (name, description, instructions)
  - Import and compose sidebar + tool_form components
  - Session state initialization
- [ ] T018 [US1] Add tool execution handler in `ui/main.py`:
  - Collect form values
  - Call `tool.run_async()` via `_run_async()` helper
  - Display output or error per spec FR-10

**Checkpoint**: User Story 1 complete - can load agent, view tools, execute them, see results

---

## Phase 4: User Story 2 - Record Golden Traces (Priority: P2)

**Goal**: Developer can record multi-step session and export as JSON for evaluation

**Independent Test**: Enter query → execute tools → submit final response → download valid JSON trace

### Tests for User Story 2

- [ ] T019 [P] [US2] Create `tests/unit/test_trace_export.py`:
  - Test `GoldenTrace` serialization
  - Test JSON matches schema in `contracts/golden-trace-schema.json`
  - Test metadata population

### Implementation for User Story 2

- [ ] T020 [US2] Create `adk_agent_sim/trace_export.py`:
  - `GoldenTrace`, `GoldenTraceMetadata`, `GoldenTraceStep` dataclasses
  - `export_trace(session: SessionState) -> dict` function
  - `to_json(trace: GoldenTrace) -> str` function
- [ ] T021 [US2] Create `adk_agent_sim/ui/chat_history.py`:
  - Display user query at top
  - Render chronological list of TraceSteps
  - Format tool calls: show name, arguments, output
  - Format final answers distinctly
- [ ] T022 [US2] Create `adk_agent_sim/ui/export_panel.py`:
  - User query text input
  - "End Turn" button with final response text area
  - "Download Trace" button using `st.download_button`
- [ ] T023 [US2] Update `adk_agent_sim/ui/main.py`:
  - Integrate chat_history component
  - Integrate export_panel component
  - Wire session state updates on tool execution
  - Wire trace export on download click

**Checkpoint**: User Stories 1 AND 2 complete - full debugging workflow with export

---

## Phase 5: User Story 3 - Multiple Agent Selection (Priority: P3)

**Goal**: Developer can switch between agents without restarting the application

**Independent Test**: Load multiple agents → switch via dropdown → verify tools/instructions update

### Tests for User Story 3

- [ ] T024 [P] [US3] Add tests to `tests/unit/test_session.py` for session clearing on agent switch

### Implementation for User Story 3

- [ ] T025 [US3] Update `adk_agent_sim/ui/sidebar.py`:
  - Agent selector dropdown (visible when >1 agent)
  - On-change callback to update session state
- [ ] T026 [US3] Update `adk_agent_sim/ui/main.py`:
  - Handle agent switch: clear/archive previous session
  - Reload tools and instructions for new agent
  - Update page title/header with agent name

**Checkpoint**: All user stories complete - multi-agent support working

---

## Phase 6: Integration & Entry Point

**Purpose**: Wire everything together in the main AgentSimulator class

- [ ] T027 Create `adk_agent_sim/simulator.py` with `AgentSimulator` class:
  - `__init__(self, agents: dict[str, Agent])` constructor
  - `run(self, port: int = 8501)` method that launches Streamlit
- [ ] T028 Update `adk_agent_sim/__init__.py` to export `AgentSimulator`
- [ ] T029 Create `tests/integration/test_simulator.py` testing AgentSimulator initialization
- [ ] T030 Update demo script to use AgentSimulator (optional, for validation)

---

## Phase 7: Polish & Documentation

**Purpose**: Error handling, edge cases, and documentation

- [ ] T031 [P] Add error handling throughout UI for edge cases:
  - Agent with no tools → display message
  - Tool execution exception → display as "Tool Error"
  - Invalid JSON in complex parameter → validation error
- [ ] T032 [P] Add type hints to all public interfaces
- [ ] T033 [P] Add docstrings to all public classes and functions
- [ ] T034 Update README.md with usage instructions and example
- [ ] T035 Run full test suite and fix any failures

---

## Parallel Execution Groups

Tasks marked `[P]` can run in parallel within their phase:

**Phase 1**: T003
**Phase 2**: T005, T007, T009
**Phase 3**: T010, T011, T015, T016
**Phase 4**: T019
**Phase 5**: T024
**Phase 7**: T031, T032, T033

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 | T001-T003 | Project setup |
| 2 | T004-T009 | Foundation (blocking) |
| 3 | T010-T018 | US1: Roleplay as Agent (MVP) |
| 4 | T019-T023 | US2: Golden Trace Recording |
| 5 | T024-T026 | US3: Multi-Agent Selection |
| 6 | T027-T030 | Integration & Entry Point |
| 7 | T031-T035 | Polish & Documentation |

**Total**: 35 tasks
**Critical Path**: T001 → T004 → T012 → T017 → T020 → T023 → T027

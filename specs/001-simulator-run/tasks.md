# Tasks: Simulator Run

**Input**: Design documents from `/specs/001-simulator-run/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- All paths are relative to repository root

## Path Conventions

Based on plan.md structure:

```text
adk_agent_sim/           # Source code
tests/                   # Test files
  unit/
  integration/
```

---

## Phase 1: Setup

**Purpose**: Project initialization and package structure

- [X] T001 Add `nicegui>=2.0.0` dependency to pyproject.toml
- [X] T002 [P] Create package structure: `adk_agent_sim/models/__init__.py`
- [X] T003 [P] Create package structure: `adk_agent_sim/ui/__init__.py`
- [X] T004 [P] Create package structure: `adk_agent_sim/ui/pages/__init__.py`
- [X] T005 [P] Create package structure: `adk_agent_sim/ui/components/__init__.py`
- [X] T006 [P] Create package structure: `adk_agent_sim/execution/__init__.py`
- [X] T007 [P] Create package structure: `adk_agent_sim/export/__init__.py`
- [X] T008 Run `uv sync` to install dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T09 Implement `SessionState` enum and `SimulationSession` model in `adk_agent_sim/models/session.py`
- [X] T010 [P] Implement `HistoryEntry` discriminated union types (`UserQuery`, `ToolCall`, `ToolOutput`, `ToolError`, `FinalResponse`) in `adk_agent_sim/models/history.py`
- [X] T011 [P] Export models from `adk_agent_sim/models/__init__.py`
- [X] T012 Implement `create_tool_context()` and `create_invocation_context()` in `adk_agent_sim/execution/context_factory.py` (FR-034, FR-035)
- [X] T013 Implement `ToolRunner` class with `execute()` and `cancel()` methods in `adk_agent_sim/execution/tool_runner.py` (FR-013, FR-028, FR-033)
- [X] T014 [P] Create shared CSS constants in `adk_agent_sim/ui/styles.py`
- [X] T015 Implement `SimulationController` class in `adk_agent_sim/controller.py` with agent selection, tool lookup, and session management
- [X] T016 Export `SimulationController` from `adk_agent_sim/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Execute a Simple Tool Call (Priority: P1) 🎯 MVP

**Goal**: User can select a tool, fill in parameters via dynamically-generated form, execute it, and see the output.

**Independent Test**: Provide an Agent with one tool, render its form, fill in values, execute, verify output displays.

### Implementation for User Story 1

- [X] T017 [US1] Implement universal `render_schema_form()` function in `adk_agent_sim/ui/components/schema_form.py` supporting:
  - `Type.STRING` → `ui.input`
  - `Type.INTEGER` / `Type.NUMBER` → `ui.number`
  - `Type.BOOLEAN` → `ui.checkbox`
  - `Type.STRING` with `Schema.enum` → `ui.select`
  - (FR-004)
- [X] T018 [US1] Add recursive OBJECT handling to `schema_form.py` for nested `Schema.properties` (FR-004)
- [X] T019 [US1] Add ARRAY handling to `schema_form.py` with dynamic add/remove for `Schema.items` (FR-004)
- [X] T020 [US1] Add `Schema.description` display as field hints in `schema_form.py` (FR-005)
- [X] T021 [US1] Add `Schema.required` validation before form submission in `schema_form.py` (FR-006)
- [X] T022 [US1] Implement tool executor component with form + execute button in `adk_agent_sim/ui/components/tool_executor.py`
- [X] T023 [US1] Add execution timer display (stopwatch) to `tool_executor.py` (FR-032)
- [X] T024 [US1] Add cancel button to `tool_executor.py` that triggers `ToolRunner.cancel()` (FR-033)
- [X] T025 [US1] Implement action panel component with tool selector dropdown in `adk_agent_sim/ui/components/action_panel.py`
- [X] T026 [US1] Implement history panel component rendering `HistoryEntry` variants in `adk_agent_sim/ui/components/history_panel.py` (FR-018)
- [X] T027 [US1] Add distinct visual styles per entry type (user input, tool call, tool output) in `history_panel.py` (FR-019)
- [X] T028 [US1] Wire `controller.execute_tool()` to add `ToolCall` + `ToolOutput` entries to session history (FR-014)

**Checkpoint**: User Story 1 complete - can execute a single tool and see result in history

---

## Phase 4: User Story 2 - Complete a Multi-Step Simulation Session (Priority: P1)

**Goal**: User starts with a query, executes multiple tools in sequence, views accumulated history, and submits a final response.

**Independent Test**: Start session with query, execute 2+ tools, verify history shows all steps, submit final response.

### Implementation for User Story 2

- [X] T029 [US2] Implement agent selection page with `ui.select` dropdown in `adk_agent_sim/ui/pages/agent_select.py` (FR-007)
- [X] T030 [US2] Implement collapsible system instructions panel in `adk_agent_sim/ui/components/system_prompt.py` using `ui.expansion` (FR-008)
- [X] T031 [US2] Implement main simulation page layout in `adk_agent_sim/ui/pages/simulation.py` integrating:
  - System prompt component
  - History panel
  - Action panel
  - Tool executor
- [X] T032 [US2] Add initial query input (plain text) to simulation page (FR-009)
- [X] T033 [US2] Add "Send Final Response" action to action panel with text input (FR-012)
- [X] T034 [US2] Implement NiceGUI app routing in `adk_agent_sim/ui/app.py`:
  - `/` → agent selection page
  - `/simulate` → simulation page
- [X] T035 [US2] Implement `AgentSimulator` entry point class in `adk_agent_sim/simulator.py` with:
  - Constructor accepting `dict[str, Agent]`
  - `run()` method that starts NiceGUI server
- [X] T036 [US2] Export `AgentSimulator` from `adk_agent_sim/__init__.py` as public API
- [X] T037 [US2] Wire session state transitions in controller: `SELECTING_AGENT` → `AWAITING_QUERY` → `ACTIVE` → `COMPLETED`

**Checkpoint**: User Story 2 complete - full simulation workflow from agent selection to final response

---

## Phase 5: User Story 3 - Export Golden Trace (Priority: P1)

**Goal**: User exports completed session as ADK-compatible `EvalCase` JSON file.

**Independent Test**: Complete minimal session, export, validate JSON structure matches `EvalCase` schema.

### Implementation for User Story 3

- [X] T038 [US3] Implement `GoldenTraceBuilder` class in `adk_agent_sim/export/golden_trace.py` with:
  - `build()` method returning `EvalCase`
  - `_generate_eval_id()` using `{snake_case_agent_name}_{iso_timestamp}` format (FR-022)
- [X] T039 [US3] Implement `_extract_user_query()` to build `Content(parts=[Part(text=query)])` (FR-024)
- [X] T040 [US3] Implement `_extract_final_response()` to build `Content(parts=[Part(text=response)])` (FR-025)
- [X] T041 [US3] Implement `_extract_tool_data()` to build `FunctionCall` and `FunctionResponse` lists (FR-026)
- [X] T042 [US3] Assemble `Invocation` with `intermediate_data` containing tool_uses and tool_responses (FR-023, FR-026)
- [X] T043 [US3] Add `creation_timestamp` to exported `EvalCase` (FR-027)
- [X] T044 [US3] Implement `export_json()` method using `model_dump_json()` (FR-020, FR-021)
- [X] T045 [US3] Add "Export Golden Trace" button to simulation page (visible when state=COMPLETED)
- [X] T046 [US3] Wire export button to trigger JSON download via NiceGUI `ui.download()`

**Checkpoint**: User Story 3 complete - sessions export to valid `EvalCase` JSON

---

## Phase 6: User Story 4 - Handle Structured Input/Output Schemas (Priority: P2)

**Goal**: Agents with Pydantic `input_schema` and `output_schema` render appropriate forms instead of plain text.

**Independent Test**: Provide Agent with `input_schema`/`output_schema`, verify forms render and validate correctly.

### Implementation for User Story 4

- [X] T047 [US4] Add Pydantic → Schema conversion helper in `adk_agent_sim/ui/components/schema_form.py`:
  - `pydantic_to_schema(model: type[BaseModel]) -> Schema` using `Schema.from_json_schema()` (FR-010)
- [X] T048 [US4] Update simulation page to render schema form for initial query if `agent.input_schema` exists (FR-010)
- [X] T049 [US4] Update action panel to render schema form for final response if `agent.output_schema` exists (FR-015)
- [X] T050 [US4] Add Pydantic validation for structured final response before submission (FR-016)
- [X] T051 [US4] Store structured input/output as JSON string in `UserQuery.content` and `FinalResponse.content`

**Checkpoint**: User Story 4 complete - structured schemas render as forms with validation

---

## Phase 7: User Story 5 - Handle Tool Execution Errors Gracefully (Priority: P2)

**Goal**: Tool exceptions are captured, displayed in history, and included in Golden Trace export.

**Independent Test**: Execute a tool that throws exception, verify error appears in history, export includes error.

### Implementation for User Story 5

- [X] T052 [US5] Update `ToolRunner.execute()` to catch exceptions and return `ExecutionResult` with error details (FR-028)
- [X] T053 [US5] Update controller to add `ToolError` entry to history on failure (FR-029)
- [X] T054 [US5] Add error-styled card variant to `history_panel.py` for `ToolError` entries (FR-019)
- [X] T055 [US5] Ensure session remains in `ACTIVE` state after tool error (FR-030)
- [X] T056 [US5] Update `GoldenTraceBuilder._extract_tool_data()` to convert `ToolError` to `FunctionResponse` with error payload (FR-031)

**Checkpoint**: User Story 5 complete - errors display and export correctly

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, edge cases, and quality gates

- [X] T057 [P] Handle empty tool list edge case - allow direct final response submission
- [X] T058 [P] Add large tool output truncation in history panel (show preview, full data in export)
- [X] T059 [P] Add unit tests for schema form rendering in `tests/unit/test_schema_form.py`
- [X] T060 [P] Add unit tests for session state machine in `tests/unit/test_session.py`
- [X] T061 [P] Add unit tests for history entry models in `tests/unit/test_history.py`
- [X] T062 [P] Add unit tests for Golden Trace export in `tests/unit/test_golden_trace.py`
- [X] T063 Add integration test for tool execution in `tests/integration/test_tool_execution.py`
- [X] T064 Add integration test for end-to-end simulation flow in `tests/integration/test_simulation_flow.py`
- [X] T065 Run `ruff format --check` and `ruff check` on all new files
- [X] T066 Run `pyright --strict` on all new files
- [X] T067 Manual smoke test: complete full simulation with demo agent and verify export

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────┐
                                 ▼
Phase 2 (Foundational) ──────────┤ BLOCKS ALL STORIES
                                 ▼
┌────────────────────────────────┴────────────────────────────────┐
│                                                                 │
▼                    ▼                    ▼                       │
Phase 3 (US1)    Phase 4 (US2)*     Phase 5 (US3)*               │
Tool Execution   Session Flow       Export                        │
                                                                  │
* US2 depends on US1 components (schema_form, history_panel)      │
* US3 depends on US2 for complete sessions                        │
                                                                  │
▼                                                                 │
Phase 6 (US4) ← Depends on US2 (extends query/response forms)     │
                                                                  │
▼                                                                 │
Phase 7 (US5) ← Depends on US1 (extends tool execution)           │
                                                                  │
└──────────────────────────────────────────────────────────────────┘
                                 ▼
Phase 8 (Polish) ─────────────────  After all stories complete
```

### Recommended Execution Order

1. **Setup (Phase 1)**: T001-T008 (parallel where marked)
2. **Foundational (Phase 2)**: T009-T016
3. **User Story 1 (Phase 3)**: T017-T028 → **MVP Checkpoint: Tool execution works**
4. **User Story 2 (Phase 4)**: T029-T037 → **MVP Checkpoint: Full simulation flow**
5. **User Story 3 (Phase 5)**: T038-T046 → **MVP Checkpoint: Export works**
6. **User Story 4 (Phase 6)**: T047-T051 → Structured schemas
7. **User Story 5 (Phase 7)**: T052-T056 → Error handling
8. **Polish (Phase 8)**: T057-T067

### Within User Story 1 (Parallel Opportunities)

```bash
# These can run in parallel (different files):
T017: schema_form.py (basic types)
# Then sequential:
T018-T021: Extend schema_form.py (must be sequential - same file)
T022-T024: tool_executor.py
T025: action_panel.py
T026-T027: history_panel.py
T028: Wire to controller (depends on all above)
```

### Within User Story 2 (Parallel Opportunities)

```bash
# These can run in parallel:
T029: agent_select.py
T030: system_prompt.py
# Then:
T031: simulation.py (integrates above)
T032-T033: Extend simulation.py
T034: app.py (routing)
T035-T037: simulator.py + wiring
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational **(CRITICAL - blocks all stories)**
3. Complete Phase 3: User Story 1 → **TEST: Execute single tool**
4. Complete Phase 4: User Story 2 → **TEST: Full session flow**
5. Complete Phase 5: User Story 3 → **TEST: Export Golden Trace**
6. **STOP and VALIDATE**: Demo end-to-end simulation with export

At this point, the core product is complete. User Stories 4 and 5 add polish.

### Incremental Delivery

| Milestone | Stories Complete | Capability |
|-----------|------------------|------------|
| Alpha | US1 | Can execute individual tools |
| Beta | US1 + US2 | Full simulation workflow |
| v1.0 | US1 + US2 + US3 | Export Golden Traces |
| v1.1 | + US4 | Structured input/output |
| v1.2 | + US5 | Error handling |

---

## Notes

- All code uses **2-space indentation** (ruff config)
- All code must pass `pyright --strict`
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate independently
- Task IDs (T001-T067) are for tracking; adjust as needed during implementation

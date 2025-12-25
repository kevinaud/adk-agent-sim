# Tasks: E2E Test Suite

**Input**: Design documents from `/specs/002-e2e-test-suite/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅ (N/A)

**Tests**: This feature IS a test suite. Test implementation tasks ARE the deliverable.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and dev container configuration

- [X] T001 Add `pytest-playwright` as dev dependency via `uv add --dev pytest-playwright`
- [X] T002 Update `.devcontainer/devcontainer.json` to add `uv run playwright install --with-deps` to postCreateCommand
- [X] T003 [P] Create `tests/e2e/__init__.py` (empty module marker)
- [X] T004 [P] Create `tests/fixtures/agents/__init__.py` (empty module marker)
- [X] T005 [P] Create `tests/fixtures/agents/test_agent/__init__.py` (empty module marker)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Test agent and fixtures that ALL test cases depend on

**⚠️ CRITICAL**: No test case implementation can begin until this phase is complete

- [X] T006 Create `tests/fixtures/agents/test_agent/agent.py` with `add_numbers(a: int, b: int)` FunctionTool
- [X] T007 Add `greet(name: str, formal: bool)` FunctionTool to `tests/fixtures/agents/test_agent/agent.py`
- [X] T008 Add `get_status(level: Literal["low", "medium", "high"])` FunctionTool to `tests/fixtures/agents/test_agent/agent.py`
- [X] T009 Add `fail_always()` FunctionTool that raises RuntimeError to `tests/fixtures/agents/test_agent/agent.py`
- [X] T010 Create `get_test_agent()` factory function and `root_agent` export in `tests/fixtures/agents/test_agent/agent.py`
- [X] T011 Create `tests/e2e/conftest.py` with `TEST_SERVER_PORT`, `TEST_BASE_URL`, and timeout constants (`SERVER_STARTUP_TIMEOUT=10`, `ELEMENT_TIMEOUT=10`, `TOOL_EXECUTION_TIMEOUT=30`)
- [X] T012 Add session-scoped `run_server` fixture to `tests/e2e/conftest.py` using background thread with `native=False, show=False, reload=False` and server readiness polling
- [X] T013 Add `ADK_AGENT_MODULE` env var injection pointing to `tests.fixtures.agents.test_agent` in `tests/e2e/conftest.py`
- [X] T014 Add function-scoped `page` fixture that navigates to base URL with appropriate wait states in `tests/e2e/conftest.py`

**Checkpoint**: Foundation ready - test case implementation can now begin

---

## Phase 3: User Story 1 - Complete Simulation Flow (Priority: P1) 🎯 MVP

**Goal**: Verify the complete "Simulator Run" happy path from start to finish

**Independent Test**: Run `uv run pytest tests/e2e/test_simulation.py::test_happy_path -v`

### Implementation for User Story 1

- [X] T015 [US1] Create `tests/e2e/test_simulation.py` with test file structure and imports
- [X] T016 [US1] Implement `test_happy_path_agent_selection` - verify Playwright connects and can select TestAgent
- [X] T017 [US1] Implement `test_happy_path_query_submission` - enter query, verify tools displayed
- [X] T018 [US1] Implement `test_happy_path_tool_selection` - select `add_numbers` tool, verify form renders
- [X] T019 [US1] Implement `test_happy_path_tool_execution` - fill form (a=5, b=3), execute, verify result "8" in history
- [X] T020 [US1] Implement `test_happy_path_final_response` - submit final response, verify session completion

**Checkpoint**: TC-01 (Happy Path) complete and passing

---

## Phase 4: User Story 2 - Dynamic Form Rendering (Priority: P2)

**Goal**: Verify different ADK schema types render correct UI widgets

**Independent Test**: Run `uv run pytest tests/e2e/test_simulation.py -k "widget" -v`

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement `test_widget_number_input` - verify `add_numbers` renders numeric inputs for `a` and `b`
- [X] T022 [P] [US2] Implement `test_widget_string_input` - verify `greet` renders text input for `name` parameter
- [X] T023 [P] [US2] Implement `test_widget_checkbox` - verify `greet` renders checkbox for `formal` boolean parameter
- [X] T024 [P] [US2] Implement `test_widget_dropdown` - verify `get_status` renders dropdown/select for `level` enum parameter

**Checkpoint**: TC-02 (Dynamic Forms) complete and passing

---

## Phase 5: User Story 3 - Error Handling (Priority: P2)

**Goal**: Verify tool execution errors are displayed gracefully and session continues

**Independent Test**: Run `uv run pytest tests/e2e/test_simulation.py::test_error_handling -v`

### Implementation for User Story 3

- [X] T025 [US3] Implement `test_error_handling_display` - execute `fail_always`, verify error card with red/error styling
- [X] T026 [US3] Implement `test_error_handling_session_continues` - after error, verify can still select other tools
- [X] T027 [US3] Implement `test_error_handling_history_preserved` - verify error remains visible in history after continuing

**Checkpoint**: TC-03 (Error Handling) complete and passing

---

## Phase 6: User Story 4 - State Isolation (Priority: P3)

**Goal**: Verify sessions are ephemeral and state clears on reload

**Independent Test**: Run `uv run pytest tests/e2e/test_simulation.py::test_state_isolation -v`

### Implementation for User Story 4

- [X] T028 [US4] Implement `test_state_isolation_on_reload` - perform actions, reload page, verify history cleared
- [X] T029 [US4] Implement `test_state_isolation_fresh_start` - verify fresh session has no artifacts from previous sessions

**Checkpoint**: TC-04 (State Isolation) complete and passing

---

## Phase 7: User Story 5 - Screenshot Capture (Priority: P2)

**Goal**: Capture screenshots of all major UX views for visual documentation and AI analysis

**Independent Test**: Run `uv run pytest tests/e2e/test_simulation.py -k "screenshot" -v` and verify files in `docs/screenshots/`

### Implementation for User Story 5

- [X] T033 Create `docs/screenshots/` directory and add `.gitkeep` file
- [X] T034 Add `SCREENSHOT_DIR` constant and `capture_screenshot` fixture to `tests/e2e/conftest.py` with 1280x720 viewport
- [X] T035 [US5] Add screenshot capture for agent selection page (`agent-selection.png`) in TC-01
- [X] T036 [US5] Add screenshot capture for query input form (`query-input.png`) in TC-01
- [X] T037 [US5] Add screenshot capture for tool selection panel (`tool-selection.png`) in TC-01
- [X] T038 [US5] Add screenshot capture for tool parameter form (`tool-form.png`) in TC-01
- [X] T039 [US5] Add screenshot capture for tool execution result (`tool-result.png`) in TC-01
- [X] T040 [US5] Add screenshot capture for error display (`error-display.png`) in TC-03
- [X] T041 [US5] Add screenshot capture for session completion (`session-complete.png`) in TC-01
- [X] T042 Verify all 7 screenshots exist in `docs/screenshots/` after test run

**Checkpoint**: TC-05 (Screenshot Capture) complete - all 7 screenshots saved

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [X] T030 [P] Add docstrings to all test functions explaining what they verify
- [X] T031 Run full E2E suite via `uv run pytest tests/e2e/ -v` and verify all tests pass
- [X] T032 Run quickstart.md validation - execute all commands and verify expected output
- [X] T043 Update quickstart.md with screenshot verification instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T005) - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (T006-T014) completion
  - User stories can proceed in priority order (P1 → P2 → P3)
  - Within each story, tasks should be sequential
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies on US1 (tests different tools)
- **User Story 3 (P2)**: Can start after Foundational - No dependencies on US1/US2
- **User Story 4 (P3)**: Can start after Foundational - No dependencies on other stories
- **User Story 5 (P2)**: Depends on User Story 1 (TC-01) and User Story 3 (TC-03) for screenshot contexts

### Parallel Opportunities per Phase

```
Phase 1 Setup:
  T003, T004, T005 can run in parallel (different files)

Phase 2 Foundational:
  T006 → T007 → T008 → T009 → T010 (same file, sequential)
  T011 → T012 → T013 → T014 (same file, sequential)

Phase 4 User Story 2:
  T021, T022, T023, T024 can run in parallel (independent test functions)

Phase 7 User Story 5:
  T035-T041 can run in parallel (independent screenshot captures)

Phase 8 Polish:
  T030 can run in parallel with validation tasks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014)
3. Complete Phase 3: User Story 1 (T015-T020)
4. **STOP and VALIDATE**: Run `uv run pytest tests/e2e/test_simulation.py::test_happy_path -v`
5. MVP delivered - core simulation flow verified

### Incremental Delivery

1. Setup + Foundational → Test infrastructure ready
2. Add User Story 1 → TC-01 passing → MVP!
3. Add User Story 2 → TC-02 passing → Widget coverage
4. Add User Story 3 → TC-03 passing → Error resilience verified
5. Add User Story 4 → TC-04 passing → State isolation verified
6. Add User Story 5 → TC-05 passing → Screenshots captured for AI analysis
7. Polish → Full suite validated

---

## Task Count Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | 5 | 3 |
| Foundational | 9 | 0 (sequential within files) |
| User Story 1 | 6 | 0 (sequential flow) |
| User Story 2 | 4 | 4 |
| User Story 3 | 3 | 0 (sequential) |
| User Story 4 | 2 | 0 (sequential) |
| User Story 5 | 10 | 7 (screenshot captures) |
| Polish | 4 | 1 |
| **Total** | **43** | **15** |

---

## Notes

- All tests run headlessly via `pytest-playwright` defaults
- Test agent uses only local `FunctionTool` - no MCP server required
- Port 8081 dedicated for E2E tests (distinct from dev port 8080)
- Screenshots saved to `docs/screenshots/` at 1280x720 resolution
- Screenshots are committed to version control for AI-assisted analysis
- Commit after each phase completion
- Stop at any checkpoint to validate independently

# Tasks: UX Modernization Event Stream Fixes

**Input**: Design documents from `/specs/003-ux-modernization/plan-fixes.md`
**Prerequisites**: plan-fixes.md (gap analysis), spec.md (User Story 2 acceptance scenarios)

**Tests**: Included - this fix plan explicitly requires test coverage for acceptance scenarios 4-9.

**Organization**: Tasks organized by fix area (matching the three issues identified in plan-fixes.md).

## Format: `[ID] [P?] [Fix] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Fix]**: Which fix area (Fix1=expanded default, Fix2=state persistence, Fix3=bulk buttons)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Foundation for Fixes)

**Purpose**: Create the state management infrastructure needed for fixes

- [X] T001 Create ExpansionStateManager class in adk_agent_sim/ui/components/expansion_state.py
- [X] T002 [P] Add unit tests for ExpansionStateManager in tests/unit/test_expansion_state.py
- [X] T003 Run unit tests to verify ExpansionStateManager works correctly

**Checkpoint**: State manager ready for integration

---

## Phase 2: Fix 1 - Expanded by Default (Scenarios 4)

**Goal**: Tool outputs and collapsible sections are expanded when first rendered

**Independent Test**: Execute a tool and verify expansion items have `.q-expansion-item--expanded` class

### Tests for Fix 1

- [X] T004 [P] [Fix1] Add E2E test `test_tool_output_expanded_by_default` in tests/e2e/test_event_stream_expansion.py

### Implementation for Fix 1

- [X] T005 [Fix1] Change `expanded=False` to `expanded=True` in EventStream._render_events() at adk_agent_sim/ui/components/event_stream.py#L65
- [X] T006 [Fix1] Change `expanded=False` to `expanded=True` in RefreshableEventStream._render_stream() at adk_agent_sim/ui/components/event_stream.py#L159
- [X] T007 [Fix1] Run E2E test to verify fix

**Checkpoint**: New tool outputs now render expanded by default

---

## Phase 3: Fix 2 - State Persistence (Scenarios 5-6)

**Goal**: Expand/collapse state preserved across UI actions and when new events are added

**Independent Test**: Collapse a section, perform action, verify section stays collapsed

### Tests for Fix 2

- [X] T008 [P] [Fix2] Add E2E test `test_collapse_state_preserved_on_action` in tests/e2e/test_event_stream_expansion.py
- [X] T009 [P] [Fix2] Add E2E test `test_expand_state_preserved_on_new_event` in tests/e2e/test_event_stream_expansion.py

### Implementation for Fix 2

- [X] T010 [Fix2] Add state_manager instance to EventStream.__init__() in adk_agent_sim/ui/components/event_stream.py
- [X] T011 [Fix2] Generate stable event IDs from history entries (timestamp + type hash) in adk_agent_sim/ui/components/event_stream.py
- [X] T012 [Fix2] Update render_event_block to accept state_manager and event_id parameters in adk_agent_sim/ui/components/event_block.py
- [X] T013 [Fix2] Update EventBlock.__init__() to store expansion references in adk_agent_sim/ui/components/event_block.py
- [X] T014 [Fix2] Register on_value_change callbacks to update state_manager when user expands/collapses in adk_agent_sim/ui/components/event_block.py
- [X] T015 [Fix2] Pass state_manager and event_id to render_event_block calls in adk_agent_sim/ui/components/event_stream.py
- [ ] T016 [Fix2] Update EventStream.refresh() to use incremental append instead of full clear in adk_agent_sim/ui/components/event_stream.py
- [X] T017 [Fix2] Run E2E tests to verify state persistence

**Checkpoint**: Expand/collapse state now persists within session

---

## Phase 4: Fix 3 - Bulk Expand/Collapse Buttons (Scenarios 7-9)

**Goal**: Expand All and Collapse All buttons work correctly

**Independent Test**: Click Expand All, verify all sections expanded; click Collapse All, verify all collapsed

### Tests for Fix 3

- [X] T018 [P] [Fix3] Add E2E test `test_expand_all_button_works` in tests/e2e/test_event_stream_expansion.py
- [X] T019 [P] [Fix3] Add E2E test `test_collapse_all_button_works` in tests/e2e/test_event_stream_expansion.py

### Implementation for Fix 3

- [X] T020 [Fix3] Store ui.expansion references in EventBlock._expansions list in adk_agent_sim/ui/components/event_block.py
- [X] T021 [Fix3] Rewrite EventBlock._expand_all() to iterate _expansions and call .set_value(True) in adk_agent_sim/ui/components/event_block.py
- [X] T022 [Fix3] Rewrite EventBlock._collapse_all() to iterate _expansions and call .set_value(False) in adk_agent_sim/ui/components/event_block.py
- [X] T023 [Fix3] Update state_manager when bulk expand/collapse is triggered in adk_agent_sim/ui/components/event_block.py
- [X] T024 [Fix3] Run E2E tests to verify bulk buttons work

**Checkpoint**: Bulk expand/collapse buttons now functional

---

## Phase 5: Polish & Verification

**Purpose**: Final validation and documentation

- [X] T025 [P] Run full E2E test suite to verify no regressions in tests/e2e/
- [X] T026 [P] Run quality checks (ruff, pyright) via ./scripts/check_quality.sh
- [ ] T027 Capture updated screenshots for event stream in docs/screenshots/
- [ ] T028 Manual QA: Run demo app and verify all acceptance scenarios 4-9

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         │
Phase 2 (Fix 1: Expanded Default) ────────────────────────────┤
    │                                                         │
    ▼                                                         │
Phase 3 (Fix 2: State Persistence) ───────────────────────────┤
    │                                                         │
    ▼                                                         │
Phase 4 (Fix 3: Bulk Buttons) ────────────────────────────────┤
    │                                                         │
    ▼                                                         │
Phase 5 (Polish) ◄────────────────────────────────────────────┘
```

### Task Dependencies Within Phases

**Phase 1**:
- T001 → T002 (tests need class to exist)
- T002 → T003 (run tests after writing them)

**Phase 2**:
- T004 can run in parallel with T005-T006
- T005, T006 → T007 (run test after fix)

**Phase 3**:
- T008, T009 can run in parallel
- T010 → T011 → T012 → T013 → T014 → T015 → T016 (sequential integration)
- T016 → T017 (run tests after implementation)

**Phase 4**:
- T018, T019 can run in parallel
- T020 → T021, T022 → T023 → T024 (sequential, same file)

**Phase 5**:
- T025, T026 can run in parallel
- T027, T028 depend on all fixes complete

### Parallel Opportunities

```bash
# Phase 1: Tests and implementation
T001 then T002  # Sequential - tests need class

# Phase 2: Test and fix in parallel
T004 | T005, T006  # Parallel - different files
T007 after T004, T005, T006  # Verify

# Phase 3: Tests in parallel
T008 | T009  # Parallel - same file but different test functions

# Phase 4: Tests in parallel  
T018 | T019  # Parallel - same file but different test functions

# Phase 5: Verification in parallel
T025 | T026  # Parallel - different tools
```

---

## Implementation Strategy

### Quick Win First (Fix 1 Only)

1. Complete Phase 1: Create state manager (T001-T003)
2. Complete Phase 2: Fix expanded default (T004-T007)
3. **STOP and VALIDATE**: Scenarios 4 now passing
4. Deploy quick fix if urgent

### Full Fix (All Scenarios)

1. Phase 1: Setup state manager
2. Phase 2: Fix 1 (expanded default) - Scenario 4 ✓
3. Phase 3: Fix 2 (state persistence) - Scenarios 5-6 ✓
4. Phase 4: Fix 3 (bulk buttons) - Scenarios 7-9 ✓
5. Phase 5: Polish and verify all scenarios

---

## Acceptance Criteria Mapping

| Task Range | Scenarios Covered | Spec Requirement |
|------------|-------------------|------------------|
| T004-T007 | Scenario 4 | Expanded by default |
| T008-T017 | Scenarios 5-6 | State persistence |
| T018-T024 | Scenarios 7-9 | Bulk expand/collapse |

---

## Files Modified

| File | Tasks | Changes |
|------|-------|---------|
| `adk_agent_sim/ui/components/expansion_state.py` | T001 | NEW FILE |
| `adk_agent_sim/ui/components/event_stream.py` | T005, T006, T010, T011, T015, T016 | State manager integration |
| `adk_agent_sim/ui/components/event_block.py` | T012-T014, T020-T023 | State tracking, bulk buttons |
| `tests/unit/test_expansion_state.py` | T002 | NEW FILE |
| `tests/e2e/test_event_stream_expansion.py` | T004, T008, T009, T018, T019 | NEW FILE |

---

## Notes

- [P] tasks = different files, no dependencies
- [Fix] label maps task to specific fix area for traceability
- Each fix can be delivered incrementally (Fix 1 → Fix 2 → Fix 3)
- State manager is session-only (per spec: NOT persisted across page refresh)
- Existing E2E tests in test_simulation.py should continue to pass

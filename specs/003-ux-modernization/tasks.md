# Tasks: UX Modernization

**Input**: Design documents from `/specs/003-ux-modernization/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not explicitly requested in spec. Omitting test tasks per guidelines.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Completed ✅)

**Purpose**: Foundational styling and reusable components

- [x] T001 Update design tokens and add new layout constants in adk_agent_sim/ui/styles.py
- [x] T002 [P] Create JsonTree component for collapsible JSON display in adk_agent_sim/ui/components/json_tree.py
- [x] T003 [P] Create EventBlock component for rendering history entries in adk_agent_sim/ui/components/event_block.py
- [x] T004 [P] Create AgentCard component for clickable agent cards in adk_agent_sim/ui/components/agent_card.py

**Checkpoint**: Core reusable components ready ✅

---

## Phase 2: User Story 1 - Modern Agent Selection Dashboard (Priority: P1) 🎯 MVP

**Goal**: Replace dropdown agent selection with a visually appealing card grid dashboard

**Independent Test**: Launch app, verify agents display as interactive cards with hover effects and **actual descriptions**

### Implementation for User Story 1

- [x] T005 [US1] Rewrite AgentSelectPage to use card grid layout in adk_agent_sim/ui/pages/agent_select.py
- [x] T006 [US1] Add hover and click interaction states to agent cards in adk_agent_sim/ui/pages/agent_select.py
- [x] T007 [US1] Update page header and styling for dashboard appearance in adk_agent_sim/ui/pages/agent_select.py

### New Tasks for Session 2025-12-24

- [x] T007a [US1] Fix agent description bug - ensure description property is correctly retrieved from Agent object in adk_agent_sim/ui/components/agent_card.py
- [x] T007b [US1] Verify cards show actual description text (NOT "No description available" for agents with descriptions) in adk_agent_sim/ui/pages/agent_select.py

**Checkpoint**: Agent selection page complete with actual descriptions displayed

---

## Phase 3: User Story 2 - Structured Event Stream Interface (Priority: P1)

**Goal**: Replace simple history list with full-width event blocks showing structured data with expand-by-default and state persistence

**Independent Test**: Run simulation, verify history renders as distinct event blocks with **expanded sections by default** and **persistent expand/collapse state**

### Implementation for User Story 2 (Completed ✅)

- [x] T008 [US2] Create EventStream container component in adk_agent_sim/ui/components/event_stream.py
- [x] T009 [US2] Implement UserInputBlock rendering in event_block.py in adk_agent_sim/ui/components/event_block.py
- [x] T010 [US2] Implement ToolExecutionBlock with JsonTree for args/result in adk_agent_sim/ui/components/event_block.py
- [x] T011 [US2] Implement ToolErrorBlock with collapsible traceback in adk_agent_sim/ui/components/event_block.py
- [x] T012 [US2] Implement AgentResponseBlock (FinalResponse) rendering in adk_agent_sim/ui/components/event_block.py
- [x] T013 [US2] Add auto-scroll behavior to EventStream in adk_agent_sim/ui/components/event_stream.py
- [x] T014 [US2] Update components/__init__.py to export new event stream components in adk_agent_sim/ui/components/__init__.py

### New Tasks for Session 2025-12-24 (Expand/Collapse Enhancements)

- [x] T014a [US2] Set expanded=True as default for all collapsible sections in event blocks in adk_agent_sim/ui/components/event_block.py
- [x] T014b [US2] Implement ExpandCollapseStateManager class for session-only state persistence in adk_agent_sim/ui/components/event_stream.py
- [x] T014c [US2] Integrate ExpandCollapseStateManager so expand/collapse state persists within session (resets on page refresh) in adk_agent_sim/ui/components/event_stream.py
- [x] T014d [US2] Add "Expand All" / "Collapse All" buttons to each event block in adk_agent_sim/ui/components/event_block.py
- [x] T014e [US2] Wire expand_all/collapse_all buttons to ExpandCollapseStateManager in adk_agent_sim/ui/components/event_block.py

**Checkpoint**: Event stream component complete with session-only expand/collapse state persistence

---

## Phase 4: User Story 3 - Integrated Wizard Control Panel (Priority: P2)

**Goal**: Restructure simulation page with right sidebar layout for controls

**Independent Test**: Verify simulation page shows 2/3 event stream + 1/3 sidebar with tool controls

### Implementation for User Story 3 (Completed ✅)

- [x] T015 [US3] Update SystemPromptHeader to use expandable header pattern in adk_agent_sim/ui/components/system_prompt.py
- [x] T016 [US3] Restructure SimulationPage layout to 2/3 + 1/3 split in adk_agent_sim/ui/pages/simulation.py
- [x] T017 [US3] Move ActionPanel to right sidebar section in adk_agent_sim/ui/pages/simulation.py
- [x] T018 [US3] Integrate EventStream component replacing HistoryPanel in adk_agent_sim/ui/pages/simulation.py
- [x] T019 [US3] Update tool form rendering within sidebar context in adk_agent_sim/ui/components/action_panel.py

**Checkpoint**: Simulation page layout complete - full page structure working ✅

---

## Phase 5: User Story 4 - Enhanced Tool Execution Feedback (Priority: P2)

**Goal**: Add loading indicators and improve tool output formatting with JSON auto-parsing

**Independent Test**: Execute tool returning JSON, verify loading spinner appears and JSON results show in collapsible tree; verify embedded JSON strings are auto-parsed

### Implementation for User Story 4 (Completed ✅)

- [x] T020 [US4] Create LoadingBlock component for executing state in adk_agent_sim/ui/components/event_block.py
- [x] T021 [US4] Add loading state management to SimulationPage in adk_agent_sim/ui/pages/simulation.py
- [x] T022 [US4] Update ToolExecutor with inline spinner during execution in adk_agent_sim/ui/components/tool_executor.py
- [x] T023 [US4] Implement "Show More" truncation for large outputs in json_tree.py in adk_agent_sim/ui/components/json_tree.py

### New Tasks for Session 2025-12-24 (Text Presentation Toggle)

- [x] T023a [P] [US4] Create text_presenter.py component skeleton with PresentationMode enum in adk_agent_sim/ui/components/text_presenter.py
- [x] T023b [US4] Implement Raw mode - display plain text content in adk_agent_sim/ui/components/text_presenter.py
- [x] T023c [US4] Implement JSON mode - use JsonTree for parsed/pretty-printed JSON in adk_agent_sim/ui/components/text_presenter.py
- [x] T023d [US4] Implement Markdown mode - render content as markdown using ui.markdown() in adk_agent_sim/ui/components/text_presenter.py
- [x] T023e [US4] Add toggle button group (Raw/JSON/Markdown) with active state highlighting in adk_agent_sim/ui/components/text_presenter.py
- [x] T023f [US4] Implement JSON auto-detection - default to JSON mode if content is valid JSON object/array in adk_agent_sim/ui/components/text_presenter.py
- [x] T023g [US4] Implement truncation in Raw mode - show first 500 chars with "Show More" link in adk_agent_sim/ui/components/text_presenter.py
- [x] T023h [US4] Integrate TextPresenter into event_block.py for tool output text fields in adk_agent_sim/ui/components/event_block.py

**Checkpoint**: Text presentation toggle complete with Raw/JSON/Markdown modes and auto-detection

---

## Phase 6: User Story 5 - Comprehensive Tool Selection Interface (Priority: P2) 🆕

**Goal**: Replace dropdown with tool catalog showing all tools with full metadata (name, description, schemas)

**Independent Test**: Verify tool selection displays all tools simultaneously with name, description, input/output schemas visible

### Implementation for User Story 5

- [x] T024a [P] [US5] Create tool_catalog.py component skeleton in adk_agent_sim/ui/components/tool_catalog.py
- [x] T024b [US5] Implement ToolCatalog component showing all tools as scrollable card list in adk_agent_sim/ui/components/tool_catalog.py
- [x] T024c [US5] Add tool name and description display to each tool card in adk_agent_sim/ui/components/tool_catalog.py
- [x] T024d [US5] Add collapsible input schema panel (ui.expansion) per tool in adk_agent_sim/ui/components/tool_catalog.py
- [x] T024e [US5] Add collapsible output schema panel per tool (if available) in adk_agent_sim/ui/components/tool_catalog.py
- [x] T024f [US5] Replace dropdown in action_panel.py with ToolCatalog component in adk_agent_sim/ui/components/action_panel.py
- [x] T024g [US5] Add click handler to select tool and show parameter form in adk_agent_sim/ui/components/action_panel.py

**Checkpoint**: Tool catalog functional with full metadata visible

---

## Phase 7: Polish & Integration (Partially Complete)

**Purpose**: Final cleanup and validation

- [x] T025 [P] history_panel.py deprecated - no longer imported by simulation.py (kept for reference)
- [x] T026 [P] Update components/__init__.py with final exports in adk_agent_sim/ui/components/__init__.py
- [x] T027 Run quality checks (ruff, pyright) and fix any issues
- [x] T028 Manual validation - all tests pass (78 passed, 20 skipped)

### New Tasks for Session 2025-12-24 (Final Validation)

- [x] T028a Re-run quality checks after new feature implementation
- [x] T028b Verify feature parity - all existing functionality still works

**Note**: E2E tests (tests/e2e/) updated for new card-based agent selection UI.

---

## Phase 8: Screenshot Verification (Constitution IX)

**Purpose**: Capture and review screenshots per Constitution Principle IX

**Execution**: Run `pytest tests/e2e/test_simulation.py::TestScreenshotCapture -v` to capture screenshots automatically.

- [X] T029 [P] Capture screenshot of Agent Selection page (card grid with descriptions) → docs/screenshots/agent-selection.png
- [X] T030 [P] Capture screenshot of Tool Selection view (action panel with tool catalog) → docs/screenshots/tool-selection.png
- [X] T031 [P] Capture screenshot of Query Input form → docs/screenshots/query-input.png
- [X] T032 [P] Capture screenshot of Tool Form with parameters → docs/screenshots/tool-form.png
- [X] T033 [P] Capture screenshot of Tool Result in history → docs/screenshots/tool-result.png
- [X] T034 [P] Capture screenshot of Error display → docs/screenshots/error-display.png
- [X] T035 [P] Capture screenshot of Session Complete state → docs/screenshots/session-complete.png
- [X] T036 ✅ Screenshots captured via automated e2e tests (TestScreenshotCapture class)

**Note**: Screenshot capture is automated via `pytest tests/e2e/test_simulation.py::TestScreenshotCapture`. Run with `uv run pytest tests/e2e/test_simulation.py::TestScreenshotCapture -v` to regenerate screenshots.

**Checkpoint**: All screenshots captured via automated tests ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - complete ✅
- **Phase 2 (US1)**: Depends on T004 (AgentCard) - mostly complete, new tasks T007a-b pending
- **Phase 3 (US2)**: Depends on T002 (JsonTree), T003 (EventBlock) - mostly complete, new tasks T014a-e pending
- **Phase 4 (US3)**: Depends on Phase 3 completion - complete ✅
- **Phase 5 (US4)**: Depends on Phase 3 - mostly complete, new tasks T023a-c pending
- **Phase 6 (US5)**: NEW - depends on Setup phase only (independent of US1-US4)
- **Phase 7 (Polish)**: Depends on all user stories complete
- **Phase 8 (Screenshots)**: Depends on Phase 7 (all UI complete)

### User Story Independence

- **US1 (Agent Selection)**: Mostly complete - new tasks fix description bug
- **US2 (Event Stream)**: Mostly complete - new tasks add expand/collapse state management
- **US3 (Layout)**: Complete ✅
- **US4 (Feedback)**: Mostly complete - new tasks add JSON auto-parse
- **US5 (Tool Catalog)**: NEW - fully independent, can be implemented in parallel

### New Task Dependencies (Session 2025-12-24)

```
T007a → T007b (description fix then verify)
T014b → T014c → T014d → T014e (state manager then integrate then buttons)
T014a can run in parallel with T014b
T023a → T023b → T023c (auto-parse implementation)
T024a → T024b → T024c → T024d → T024e → T024f → T024g (tool catalog build)
```

### Parallel Opportunities

```bash
# US1, US2, US4, US5 new tasks can start in parallel:
T007a (US1 description fix)
T014a (US2 expand default)
T014b (US2 state manager)
T023a (US4 JSON auto-parse)
T024a (US5 tool catalog skeleton)
```

---

## Implementation Strategy

### Incremental Delivery (Session 2025-12-24 Tasks)

1. **Bug Fix First**: T007a-b (Agent description fix) - quick win
2. **Core UX**: T014a-e (Expand/collapse state) - high impact
3. **Enhanced Display**: T023a-c (JSON auto-parse) - usability improvement
4. **New Feature**: T024a-g (Tool catalog) - larger scope
5. **Validation**: T028a-b (Quality checks)
6. **Screenshots**: T029-T036 (Visual verification)

### Suggested Priority Order

1. T007a-b (description bug) - impacts first impression
2. T014a (expand by default) - quick UX win
3. T014b-e (state persistence + buttons) - core UX improvement
4. T023a-c (JSON auto-parse) - developer experience
5. T024a-g (tool catalog) - new feature
6. T028a-b + T029-T036 (validation + screenshots)

---

## Summary

| Phase | Status | New Tasks |
|-------|--------|-----------|
| Setup (Phase 1) | ✅ Complete | — |
| US1 - Agent Dashboard (Phase 2) | ✅ Complete | T007a-b (description fix) |
| US2 - Event Stream (Phase 3) | ✅ Complete | T014a-e (expand/collapse, session-only) |
| US3 - Control Panel (Phase 4) | ✅ Complete | — |
| US4 - Tool Feedback (Phase 5) | ✅ Complete | T023a-h (text presentation toggle) |
| US5 - Tool Catalog (Phase 6) | ✅ Complete | T024a-g (full implementation) |
| Polish (Phase 7) | ✅ Complete | T028a-b (re-validation) |
| Screenshots (Phase 8) | ✅ Complete | T029-T036 (automated via e2e tests) |

**Total New Tasks**: 24 tasks
- US1: 2 tasks
- US2: 5 tasks
- US4: 8 tasks (text presentation toggle)
- US5: 7 tasks (new feature)
- Polish/Screenshots: 2 + 8 tasks

**MVP Scope for New Features**: T007a-b + T014a-e + T023a-h = 15 tasks (excludes tool catalog)

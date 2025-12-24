# Tasks: UX Modernization

**Input**: Design documents from `/specs/003-ux-modernization/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in spec. Omitting test tasks per guidelines.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Foundational styling and reusable components

- [X] T001 Update design tokens and add new layout constants in adk_agent_sim/ui/styles.py
- [X] T002 [P] Create JsonTree component for collapsible JSON display in adk_agent_sim/ui/components/json_tree.py
- [X] T003 [P] Create EventBlock component for rendering history entries in adk_agent_sim/ui/components/event_block.py
- [X] T004 [P] Create AgentCard component for clickable agent cards in adk_agent_sim/ui/components/agent_card.py

**Checkpoint**: Core reusable components ready

---

## Phase 2: User Story 1 - Modern Agent Selection Dashboard (Priority: P1) 🎯 MVP

**Goal**: Replace dropdown agent selection with a visually appealing card grid dashboard

**Independent Test**: Launch app, verify agents display as interactive cards with hover effects

### Implementation for User Story 1

- [X] T005 [US1] Rewrite AgentSelectPage to use card grid layout in adk_agent_sim/ui/pages/agent_select.py
- [X] T006 [US1] Add hover and click interaction states to agent cards in adk_agent_sim/ui/pages/agent_select.py
- [X] T007 [US1] Update page header and styling for dashboard appearance in adk_agent_sim/ui/pages/agent_select.py

**Checkpoint**: Agent selection page complete - can demo agent card grid independently

---

## Phase 3: User Story 2 - Structured Event Stream Interface (Priority: P1)

**Goal**: Replace simple history list with full-width event blocks showing structured data

**Independent Test**: Run simulation, verify history renders as distinct event blocks with proper styling

### Implementation for User Story 2

- [X] T008 [US2] Create EventStream container component in adk_agent_sim/ui/components/event_stream.py
- [X] T009 [US2] Implement UserInputBlock rendering in event_block.py in adk_agent_sim/ui/components/event_block.py
- [X] T010 [US2] Implement ToolExecutionBlock with JsonTree for args/result in adk_agent_sim/ui/components/event_block.py
- [X] T011 [US2] Implement ToolErrorBlock with collapsible traceback in adk_agent_sim/ui/components/event_block.py
- [X] T012 [US2] Implement AgentResponseBlock (FinalResponse) rendering in adk_agent_sim/ui/components/event_block.py
- [X] T013 [US2] Add auto-scroll behavior to EventStream in adk_agent_sim/ui/components/event_stream.py
- [X] T014 [US2] Update components/__init__.py to export new event stream components in adk_agent_sim/ui/components/__init__.py

**Checkpoint**: Event stream component complete - can test history rendering independently

---

## Phase 4: User Story 3 - Integrated Wizard Control Panel (Priority: P2)

**Goal**: Restructure simulation page with right sidebar layout for controls

**Independent Test**: Verify simulation page shows 2/3 event stream + 1/3 sidebar with tool controls

### Implementation for User Story 3

- [X] T015 [US3] Update SystemPromptHeader to use expandable header pattern in adk_agent_sim/ui/components/system_prompt.py
- [X] T016 [US3] Restructure SimulationPage layout to 2/3 + 1/3 split in adk_agent_sim/ui/pages/simulation.py
- [X] T017 [US3] Move ActionPanel to right sidebar section in adk_agent_sim/ui/pages/simulation.py
- [X] T018 [US3] Integrate EventStream component replacing HistoryPanel in adk_agent_sim/ui/pages/simulation.py
- [X] T019 [US3] Update tool form rendering within sidebar context in adk_agent_sim/ui/components/action_panel.py

**Checkpoint**: Simulation page layout complete - full page structure working

---

## Phase 5: User Story 4 - Enhanced Tool Execution Feedback (Priority: P2)

**Goal**: Add loading indicators and improve tool output formatting

**Independent Test**: Execute tool, verify loading spinner appears and JSON results show in collapsible tree

### Implementation for User Story 4

- [X] T020 [US4] Create LoadingBlock component for executing state in adk_agent_sim/ui/components/event_block.py
- [X] T021 [US4] Add loading state management to SimulationPage in adk_agent_sim/ui/pages/simulation.py
- [X] T022 [US4] Update ToolExecutor with inline spinner during execution in adk_agent_sim/ui/components/tool_executor.py
- [X] T023 [US4] Implement "Show More" truncation for large outputs in json_tree.py in adk_agent_sim/ui/components/json_tree.py

**Checkpoint**: Tool execution feedback complete - full UX modernization done

---

## Phase 6: Polish & Integration

**Purpose**: Final cleanup and validation

- [X] T024 [P] history_panel.py deprecated - no longer imported by simulation.py (kept for reference)
- [X] T025 [P] Update components/__init__.py with final exports in adk_agent_sim/ui/components/__init__.py
- [X] T026 Run quality checks (ruff, pyright) and fix any issues
- [ ] T027 Manual validation against quickstart.md test scenarios

**Note**: E2E tests (tests/e2e/) updated for new card-based agent selection UI.

---

## Phase 7: Screenshot Verification (Constitution IX)

**Purpose**: Capture and review screenshots per Constitution Principle IX

- [ ] T028 [P] Capture screenshot of Agent Selection page (card grid) → docs/screenshots/agent-selection.png
- [ ] T029 [P] Capture screenshot of Simulation page (event stream + sidebar) → docs/screenshots/simulation-view.png
- [ ] T030 [P] Capture screenshot of Tool Execution form → docs/screenshots/tool-form.png
- [ ] T031 [P] Capture screenshot of Tool Result (JSON tree expanded) → docs/screenshots/tool-result.png
- [ ] T032 [P] Capture screenshot of Loading state during execution → docs/screenshots/loading-state.png
- [ ] T033 [P] Capture screenshot of Error display → docs/screenshots/error-display.png
- [ ] T034 Human review of all captured screenshots for visual correctness and design consistency

**Checkpoint**: All screenshots captured, reviewed, and approved - ready to merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (US1)**: Depends on T004 (AgentCard)
- **Phase 3 (US2)**: Depends on T002 (JsonTree), T003 (EventBlock)
- **Phase 4 (US3)**: Depends on Phase 3 completion (EventStream)
- **Phase 5 (US4)**: Depends on Phase 3 (EventBlock, JsonTree)
- **Phase 6 (Polish)**: Depends on all user stories complete
- **Phase 7 (Screenshots)**: Depends on Phase 6 (all UI complete)

### User Story Independence

- **US1 (Agent Selection)**: Fully independent - can be completed and demoed alone
- **US2 (Event Stream)**: Fully independent - can be tested with existing simulation page
- **US3 (Layout)**: Integrates US2 but US2 can work in old layout first
- **US4 (Feedback)**: Depends on US2/US3 components being in place

### Parallel Opportunities

```bash
# Phase 1 - All can run in parallel:
T002: JsonTree component
T003: EventBlock component  
T004: AgentCard component

# Phase 3 - Event block types can run in parallel:
T009: UserInputBlock
T010: ToolExecutionBlock
T011: ToolErrorBlock
T012: AgentResponseBlock

# Phase 6 - Cleanup tasks can run in parallel:
T024: Remove deprecated file
T025: Update exports
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. T001 → T004 (Setup + AgentCard)
2. T005 → T007 (Agent Selection Page)
3. **STOP**: Demo card-based agent selection

### Incremental Delivery

1. Setup → US1 → Demo agent cards ✓
2. US2 → Demo event stream (in old layout) ✓
3. US3 → Demo new layout ✓
4. US4 → Demo loading states ✓
5. Polish → Quality checks ✓
6. Screenshots → Capture & review ✓
7. Ship!

---

## Notes

- All new files use 2-space indentation per constitution
- Run `./scripts/check_quality.sh` after each phase
- EventStream replaces HistoryPanel but keep old file until Phase 6
- Existing functionality (export, tool execution) must continue working throughout
- **Constitution IX**: All screenshots MUST be captured and reviewed before merge

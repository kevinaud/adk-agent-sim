# Tasks: DevTools-Style Event Stream Renderer

**Input**: Design documents from `/specs/004-devtools-event-renderer/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

> ⚠️ **CRITICAL CONSTRAINT**: NO code reuse from existing `json_tree.py`. All components are clean-room implementations.

## Format: `[ID] [P?] [PR#] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[PR#]**: Which pull request this task belongs to (PR1, PR2, PR3, PR4, PR5)
- Include exact file paths in descriptions

---

## Phase 1: PR1 - Core DevTools Tree Renderer

**Goal**: Create the foundational tree component with expand/collapse and visual styling
**User Story**: US1 (P1) - View Execution Trace at a Glance
**Branch**: `004-devtools-event-renderer-pr1`

### PR1 Setup

- [ ] T001 [PR1] Ensure main branch is up to date: `git checkout main && git pull origin main`
- [ ] T002 [PR1] Create feature branch for PR1: `git checkout -b 004-devtools-event-renderer-pr1`

### PR1 Implementation

- [ ] T003 [PR1] Add `DEVTOOLS_TREE_STYLES` constants to adk_agent_sim/ui/styles.py (colors, fonts, spacing)
- [ ] T004 [PR1] Create `GlobalMode` enum in adk_agent_sim/ui/components/tree_expansion_state.py
- [ ] T005 [PR1] Create `TreeExpansionState` dataclass in adk_agent_sim/ui/components/tree_expansion_state.py
- [ ] T006 [PR1] Implement `is_expanded()`, `toggle()`, `expand_all()`, `collapse_all()` methods
- [ ] T007 [PR1] Create `ValueType` enum in adk_agent_sim/ui/components/devtools_tree.py
- [ ] T008 [PR1] Implement `DevToolsTree` class with `__init__()` accepting data, tree_id, expansion_state
- [ ] T009 [PR1] Implement `_render_node()` recursive method for dict/list/primitive rendering
- [ ] T010 [PR1] Implement thread line CSS via inline styles with `::before` pseudo-element pattern
- [ ] T011 [PR1] Implement syntax coloring for keys (purple), strings (red), numbers (blue), booleans (dark blue), null (gray)
- [ ] T012 [PR1] Implement click-to-toggle expand/collapse on chevron icons
- [ ] T013 [PR1] Ensure all nodes expanded by default (default_expanded=True)

### PR1 Tests

- [ ] T014 [P] [PR1] Create tests/unit/test_tree_expansion_state.py with state management tests
- [ ] T015 [P] [PR1] Create tests/unit/test_devtools_tree.py with rendering tests for nested structures
- [ ] T016 [PR1] Add test for expand_all/collapse_all bulk operations
- [ ] T017 [PR1] Add test for path-based sparse state storage

### PR1 Quality & Submission

- [ ] T018 [PR1] Run `./scripts/check_quality.sh` and fix any issues
- [ ] T019 [PR1] Run `uv run pytest tests/unit/test_tree_expansion_state.py tests/unit/test_devtools_tree.py -v`
- [ ] T020 [PR1] Commit all changes with message: `feat(ui): add DevToolsTree component with expansion state`
- [ ] T021 [PR1] Push branch to remote: `git push -u origin 004-devtools-event-renderer-pr1`
- [ ] T022 [PR1] Open PR via GitHub CLI: `gh pr create --title "feat(ui): Core DevTools Tree Renderer [PR1/5]" --body "## Summary\nAdds the foundational DevToolsTree component with:\n- Hierarchical tree rendering\n- Monospace typography with syntax coloring\n- Thread lines connecting parent-child nodes\n- Expand/collapse state management\n\n## User Story\nUS1 (P1) - View Execution Trace at a Glance\n\n## Test Plan\n- Unit tests for TreeExpansionState\n- Unit tests for DevToolsTree rendering\n\n## Part of\n004-devtools-event-renderer feature (PR 1 of 5)"`
- [ ] T023 [PR1] Wait for CI checks to complete: `gh pr checks --watch`
- [ ] T024 [PR1] If CI fails, retrieve logs: `gh run view --log-failed`, fix issues, commit, push, repeat T023
- [ ] T025 [PR1] **STOP**: Inform user PR1 is ready for review at PR link, wait for verbal approval
- [ ] T026 [PR1] Merge PR after approval: `gh pr merge --squash --delete-branch`
- [ ] T027 [PR1] Update local main: `git checkout main && git pull origin main`

---

## Phase 2: PR2 - Smart Blob Detection

**Goal**: Implement content type detection for strings (JSON, Markdown, Plain)
**User Stories**: US3, US4, US5 (P2) - Detection logic only
**Branch**: `004-devtools-event-renderer-pr2`
**Depends on**: PR1 merged

### PR2 Setup

- [ ] T028 [PR2] Ensure on updated main: `git checkout main && git pull origin main`
- [ ] T029 [PR2] Create feature branch for PR2: `git checkout -b 004-devtools-event-renderer-pr2`

### PR2 Implementation

- [ ] T030 [PR2] Create `BlobType` enum (JSON, MARKDOWN, PLAIN) in adk_agent_sim/ui/components/smart_blob.py
- [ ] T031 [PR2] Implement `SmartBlobDetector.try_parse_json()` - returns (parsed_data, error_msg)
- [ ] T032 [PR2] Implement `SmartBlobDetector.detect_markdown_patterns()` - regex for `**`, `##`, `- `, `1. `, triple backticks
- [ ] T033 [PR2] Implement `SmartBlobDetector.detect_type()` - returns BlobType based on content analysis
- [ ] T034 [PR2] Handle edge cases: empty strings, whitespace-only, very short strings
- [ ] T035 [PR2] Handle malformed JSON gracefully (return PLAIN, not error)

### PR2 Tests

- [ ] T036 [P] [PR2] Create tests/unit/test_smart_blob.py with detection tests
- [ ] T037 [P] [PR2] Add tests for valid JSON objects and arrays
- [ ] T038 [P] [PR2] Add tests for malformed JSON (should return PLAIN)
- [ ] T039 [P] [PR2] Add tests for Markdown patterns (headers, bold, lists, code blocks)
- [ ] T040 [P] [PR2] Add tests for edge cases (empty, whitespace, single char, no patterns)

### PR2 Quality & Submission

- [ ] T041 [PR2] Run `./scripts/check_quality.sh` and fix any issues
- [ ] T042 [PR2] Run `uv run pytest tests/unit/test_smart_blob.py -v`
- [ ] T043 [PR2] Commit all changes with message: `feat(ui): add SmartBlobDetector for content type detection`
- [ ] T044 [PR2] Push branch to remote: `git push -u origin 004-devtools-event-renderer-pr2`
- [ ] T045 [PR2] Open PR via GitHub CLI: `gh pr create --title "feat(ui): Smart Blob Detection [PR2/5]" --body "## Summary\nAdds SmartBlobDetector utility for detecting structured content in strings:\n- JSON detection (objects/arrays)\n- Markdown detection (headers, bold, lists, code blocks)\n- Graceful handling of malformed content\n\n## User Stories\nUS3, US4, US5 (P2) - Detection logic\n\n## Test Plan\n- Comprehensive unit tests for all detection scenarios\n- Edge case coverage\n\n## Part of\n004-devtools-event-renderer feature (PR 2 of 5)"`
- [ ] T046 [PR2] Wait for CI checks to complete: `gh pr checks --watch`
- [ ] T047 [PR2] If CI fails, retrieve logs: `gh run view --log-failed`, fix issues, commit, push, repeat T046
- [ ] T048 [PR2] **STOP**: Inform user PR2 is ready for review at PR link, wait for verbal approval
- [ ] T049 [PR2] Merge PR after approval: `gh pr merge --squash --delete-branch`
- [ ] T050 [PR2] Update local main: `git checkout main && git pull origin main`

---

## Phase 3: PR3 - View Mode Toggles

**Goal**: Create toggle pill UI and view mode state management
**User Stories**: US3, US4, US5 (P2) - Toggle UI
**Branch**: `004-devtools-event-renderer-pr3`
**Depends on**: PR2 merged

### PR3 Setup

- [ ] T051 [PR3] Ensure on updated main: `git checkout main && git pull origin main`
- [ ] T052 [PR3] Create feature branch for PR3: `git checkout -b 004-devtools-event-renderer-pr3`

### PR3 Implementation

- [ ] T053 [PR3] Add `SMART_BLOB_STYLES` constants to adk_agent_sim/ui/styles.py (toggle colors, sizing)
- [ ] T054 [PR3] Create `ViewMode` enum (RAW, JSON, MARKDOWN) in adk_agent_sim/ui/components/smart_blob.py
- [ ] T055 [PR3] Create `BlobViewState` dataclass with `get_mode()`, `set_mode()` methods
- [ ] T056 [PR3] Implement default mode selection based on detected type (JSON→JSON view, MD→MD view)
- [ ] T057 [PR3] Create `BlobTogglePills` component in adk_agent_sim/ui/components/blob_toggle_pills.py
- [ ] T058 [PR3] Implement pill rendering with [RAW], [JSON], [MD] buttons
- [ ] T059 [PR3] Style active toggle (solid background) vs inactive (outlined)
- [ ] T060 [PR3] Implement click handlers to update BlobViewState

### PR3 Tests

- [ ] T061 [P] [PR3] Create tests/unit/test_blob_toggle_pills.py
- [ ] T062 [P] [PR3] Add tests for toggle rendering with correct labels
- [ ] T063 [P] [PR3] Add tests for active/inactive visual state
- [ ] T064 [P] [PR3] Add tests for click handler updating state
- [ ] T065 [P] [PR3] Add tests for default mode selection based on BlobType

### PR3 Quality & Submission

- [ ] T066 [PR3] Run `./scripts/check_quality.sh` and fix any issues
- [ ] T067 [PR3] Run `uv run pytest tests/unit/test_smart_blob.py tests/unit/test_blob_toggle_pills.py -v`
- [ ] T068 [PR3] Commit all changes with message: `feat(ui): add BlobTogglePills component and ViewMode state`
- [ ] T069 [PR3] Push branch to remote: `git push -u origin 004-devtools-event-renderer-pr3`
- [ ] T070 [PR3] Open PR via GitHub CLI: `gh pr create --title "feat(ui): View Mode Toggles [PR3/5]" --body "## Summary\nAdds toggle pill UI for switching between content views:\n- ViewMode enum (RAW, JSON, MARKDOWN)\n- BlobViewState for tracking active modes\n- BlobTogglePills component with styled buttons\n- Default mode selection based on detected content type\n\n## User Stories\nUS3, US4, US5 (P2) - Toggle UI\n\n## Test Plan\n- Unit tests for toggle rendering\n- Unit tests for state management\n\n## Part of\n004-devtools-event-renderer feature (PR 3 of 5)"`
- [ ] T071 [PR3] Wait for CI checks to complete: `gh pr checks --watch`
- [ ] T072 [PR3] If CI fails, retrieve logs: `gh run view --log-failed`, fix issues, commit, push, repeat T071
- [ ] T073 [PR3] **STOP**: Inform user PR3 is ready for review at PR link, wait for verbal approval
- [ ] T074 [PR3] Merge PR after approval: `gh pr merge --squash --delete-branch`
- [ ] T075 [PR3] Update local main: `git checkout main && git pull origin main`

---

## Phase 4: PR4 - Inline Expansion & EventBlock Integration

**Goal**: Connect all components and integrate into event stream
**User Stories**: US3, US4, US5 (P2) - Full rendering
**Branch**: `004-devtools-event-renderer-pr4`
**Depends on**: PR3 merged

### PR4 Setup

- [ ] T076 [PR4] Ensure on updated main: `git checkout main && git pull origin main`
- [ ] T077 [PR4] Create feature branch for PR4: `git checkout -b 004-devtools-event-renderer-pr4`

### PR4 Implementation - SmartBlobRenderer

- [ ] T078 [PR4] Create `SmartBlobRenderer` class in adk_agent_sim/ui/components/smart_blob_renderer.py
- [ ] T079 [PR4] Implement RAW view rendering (monospace, preserved whitespace)
- [ ] T080 [PR4] Implement JSON view rendering (recursive DevToolsTree for parsed content)
- [ ] T081 [PR4] Implement MARKDOWN view rendering (ui.markdown() with proper styling)
- [ ] T082 [PR4] Implement inline expansion (content pushes tree down, respects parent indentation)
- [ ] T083 [PR4] Handle malformed JSON gracefully (fallback to RAW view with error indication)
- [ ] T084 [PR4] Support recursive JSON (double-encoded strings get nested toggles)

### PR4 Implementation - Integration

- [ ] T085 [PR4] Modify devtools_tree.py to integrate SmartBlobRenderer for string values
- [ ] T086 [PR4] Modify event_block.py - replace all `render_json_tree()` calls with `DevToolsTree`
- [ ] T087 [PR4] Modify event_block.py - replace all `JsonTree` usage with `DevToolsTree`
- [ ] T088 [PR4] Update imports in event_block.py (remove json_tree imports, add devtools_tree imports)
- [ ] T089 [PR4] Ensure expansion state is shared across blob renderers within same tree

### PR4 Tests

- [ ] T090 [P] [PR4] Create tests/unit/test_smart_blob_renderer.py
- [ ] T091 [P] [PR4] Add tests for RAW view rendering
- [ ] T092 [P] [PR4] Add tests for JSON view rendering with nested structure
- [ ] T093 [P] [PR4] Add tests for MARKDOWN view rendering
- [ ] T094 [P] [PR4] Add tests for malformed JSON fallback
- [ ] T095 [PR4] Create tests/e2e/test_devtools_tree_e2e.py with integration tests
- [ ] T096 [PR4] Add E2E test for toggle interaction flow

### PR4 Quality & Submission

- [ ] T097 [PR4] Run `./scripts/check_quality.sh` and fix any issues
- [ ] T098 [PR4] Run `uv run pytest tests/unit/test_smart_blob_renderer.py -v`
- [ ] T099 [PR4] Run `uv run pytest tests/e2e/test_devtools_tree_e2e.py -v`
- [ ] T100 [PR4] Commit all changes with message: `feat(ui): integrate SmartBlobRenderer and replace JsonTree in EventBlock`
- [ ] T101 [PR4] Push branch to remote: `git push -u origin 004-devtools-event-renderer-pr4`
- [ ] T102 [PR4] Open PR via GitHub CLI: `gh pr create --title "feat(ui): Inline Expansion & EventBlock Integration [PR4/5]" --body "## Summary\nCompletes Smart Blob rendering and integrates into event stream:\n- SmartBlobRenderer with RAW/JSON/MARKDOWN views\n- Inline expansion (no modals)\n- EventBlock now uses DevToolsTree instead of JsonTree\n- Error handling for malformed content\n\n## User Stories\nUS3, US4, US5 (P2) - Full rendering\n\n## Test Plan\n- Unit tests for SmartBlobRenderer\n- E2E tests for toggle interactions\n\n## Breaking Changes\nEventBlock no longer uses JsonTree (will be deleted in PR5)\n\n## Part of\n004-devtools-event-renderer feature (PR 4 of 5)"`
- [ ] T103 [PR4] Wait for CI checks to complete: `gh pr checks --watch`
- [ ] T104 [PR4] If CI fails, retrieve logs: `gh run view --log-failed`, fix issues, commit, push, repeat T103
- [ ] T105 [PR4] **STOP**: Inform user PR4 is ready for review at PR link, wait for verbal approval
- [ ] T106 [PR4] Merge PR after approval: `gh pr merge --squash --delete-branch`
- [ ] T107 [PR4] Update local main: `git checkout main && git pull origin main`

---

## Phase 5: PR5 - Global Controls & Final Polish

**Goal**: Add global expand/collapse, remove old code, finalize screenshots
**User Stories**: US2 (P1), US6 (P3) - Completion
**Branch**: `004-devtools-event-renderer-pr5`
**Depends on**: PR4 merged

### PR5 Setup

- [ ] T108 [PR5] Ensure on updated main: `git checkout main && git pull origin main`
- [ ] T109 [PR5] Create feature branch for PR5: `git checkout -b 004-devtools-event-renderer-pr5`

### PR5 Implementation - Global Controls

- [ ] T110 [PR5] Modify event_stream.py - add global TreeExpansionState shared across all event blocks
- [ ] T111 [PR5] Add "Expand All" button to EventStream header
- [ ] T112 [PR5] Add "Collapse All" button to EventStream header
- [ ] T113 [PR5] Implement button click handlers that call global state expand_all()/collapse_all()
- [ ] T114 [PR5] Ensure all DevToolsTree instances use shared expansion state
- [ ] T115 [PR5] Add refresh mechanism to update all trees when global state changes

### PR5 Implementation - Cleanup

- [ ] T116 [PR5] Delete adk_agent_sim/ui/components/json_tree.py entirely
- [ ] T117 [PR5] Remove any remaining imports of JsonTree or render_json_tree from codebase
- [ ] T118 [PR5] Update __init__.py exports if json_tree was exported
- [ ] T119 [PR5] Run grep to verify no json_tree references remain: `grep -r "json_tree\|JsonTree\|render_json_tree" adk_agent_sim/`

### PR5 Implementation - Screenshots

- [ ] T120 [PR5] Capture screenshot of DevToolsTree fully expanded state
- [ ] T121 [PR5] Save to docs/screenshots/components/devtools-tree-expanded.png
- [ ] T122 [PR5] Capture screenshot of DevToolsTree collapsed state
- [ ] T123 [PR5] Save to docs/screenshots/components/devtools-tree-collapsed.png
- [ ] T124 [PR5] Update tests/e2e/test_component_screenshots.py with new screenshot tests

### PR5 Tests

- [ ] T125 [PR5] Add E2E test for global "Expand All" button functionality
- [ ] T126 [PR5] Add E2E test for global "Collapse All" button functionality
- [ ] T127 [PR5] Add E2E test verifying no json_tree imports exist
- [ ] T128 [PR5] Run full E2E test suite: `uv run pytest tests/e2e/ -v`

### PR5 Quality & Submission

- [ ] T129 [PR5] Run `./scripts/check_quality.sh` and fix any issues
- [ ] T130 [PR5] Run full test suite: `uv run pytest -v`
- [ ] T131 [PR5] Commit all changes with message: `feat(ui): add global expand/collapse controls and remove json_tree`
- [ ] T132 [PR5] Push branch to remote: `git push -u origin 004-devtools-event-renderer-pr5`
- [ ] T133 [PR5] Open PR via GitHub CLI: `gh pr create --title "feat(ui): Global Controls & Final Polish [PR5/5]" --body "## Summary\nCompletes the DevTools-style event stream renderer:\n- Global Expand All / Collapse All buttons\n- Deletes old buggy json_tree.py\n- Screenshot baselines for new UI\n\n## User Stories\n- US2 (P1) - Manage Large Data Trees\n- US6 (P3) - Visual Aesthetic Matches DevTools\n\n## Test Plan\n- E2E tests for global controls\n- Full test suite passing\n- Screenshot verification\n\n## Breaking Changes\njson_tree.py deleted - all usages now use DevToolsTree\n\n## Part of\n004-devtools-event-renderer feature (PR 5 of 5) - FEATURE COMPLETE"`
- [ ] T134 [PR5] Wait for CI checks to complete: `gh pr checks --watch`
- [ ] T135 [PR5] If CI fails, retrieve logs: `gh run view --log-failed`, fix issues, commit, push, repeat T134
- [ ] T136 [PR5] **STOP**: Inform user PR5 is ready for review at PR link, wait for verbal approval
- [ ] T137 [PR5] Merge PR after approval: `gh pr merge --squash --delete-branch`
- [ ] T138 [PR5] Update local main: `git checkout main && git pull origin main`

---

## Phase 6: Feature Completion

- [ ] T139 Clean up feature branch if still exists: `git branch -D 004-devtools-event-renderer 2>/dev/null || true`
- [ ] T140 Verify all 5 PRs merged successfully: `gh pr list --state merged --search "004-devtools-event-renderer"`
- [ ] T141 Run quickstart.md validation to confirm feature works end-to-end
- [ ] T142 Update spec.md status from "Draft" to "Complete"

---

## Dependencies & Execution Order

### PR Sequence (Strictly Sequential)

```
PR1 (Core Tree) 
    → PR2 (Detection) 
        → PR3 (Toggles) 
            → PR4 (Integration) 
                → PR5 (Global + Cleanup)
```

Each PR must be:
1. Implemented
2. Pushed to remote
3. PR opened via `gh pr create`
4. CI passing (loop until green)
5. **User approval obtained**
6. Merged via `gh pr merge`
7. Main pulled locally

Only then can the next PR begin.

### Task Dependencies Within PRs

**PR1**:
- T003 (styles) → T010, T011 (uses styles)
- T004, T005, T006 (state) → T008-T013 (tree uses state)
- T008-T013 (implementation) → T014-T017 (tests)

**PR2**:
- T030 (enum) → T031-T035 (detector uses enum)
- T031-T035 (implementation) → T036-T040 (tests)

**PR3**:
- T053 (styles) → T057-T060 (pills use styles)
- T054-T056 (state) → T057-T060 (pills use state)
- T057-T060 (implementation) → T061-T065 (tests)

**PR4**:
- T078-T084 (renderer) → T085-T089 (integration)
- T085-T089 (integration) → T090-T096 (tests)

**PR5**:
- T110-T115 (global controls) before T116-T119 (cleanup)
- T120-T124 (screenshots) can parallel with controls
- All implementation → T125-T128 (tests)

### Parallel Opportunities

Within each PR, tasks marked [P] can run in parallel:
- PR1: T014, T015 (test files)
- PR2: T036-T040 (test cases)
- PR3: T061-T065 (test cases)
- PR4: T090-T094 (unit test cases)

---

## Summary

| PR | Tasks | LOC Est. | User Stories |
|----|-------|----------|--------------|
| PR1 | T001-T027 | ~200 | US1 (P1) |
| PR2 | T028-T050 | ~100 | US3-5 detection |
| PR3 | T051-T075 | ~150 | US3-5 toggles |
| PR4 | T076-T107 | ~250 | US3-5 full |
| PR5 | T108-T138 | ~150 | US2 (P1), US6 (P3) |
| Cleanup | T139-T142 | - | - |

**Total Tasks**: 142
**Total Estimated LOC**: ~850

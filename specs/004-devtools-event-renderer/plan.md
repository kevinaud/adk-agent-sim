# Implementation Plan: DevTools-Style Event Stream Renderer

**Branch**: `004-devtools-event-renderer` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-devtools-event-renderer/spec.md`

## Summary

Replace the accordion-based event stream renderer with a compact, DevTools-style hierarchical tree that displays all data expanded by default, includes vertical thread lines for visual hierarchy, and provides Smart Blob detection for inline JSON/Markdown rendering.

**Critical Constraint**: The existing `json_tree.py` has multiple hard-to-diagnose bugs. This is a **clean-room implementation** — NO code reuse from existing components.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: NiceGUI (web UI framework)  
**Storage**: N/A (session-only in-memory state)  
**Testing**: pytest, playwright (E2E)  
**Target Platform**: Web browser (Chrome, Firefox, Safari latest 2 versions)  
**Project Type**: Single Python package with NiceGUI frontend  
**Performance Goals**: Render 1000 nodes within 500ms (SC-007)  
**Constraints**: No code reuse from buggy `json_tree.py`; must pass all Constitution quality gates  
**Scale/Scope**: Single UI component replacing existing tree renderer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Library-First Architecture | ✅ PASS | UI component, no changes to library API |
| II. Wrapper Integration Pattern | ✅ PASS | No changes to agent wrapping |
| III. Wizard of Oz Interaction Model | ✅ PASS | Enhances data visibility for human operator |
| IV. ADK Dependency & Abstractions | ✅ PASS | No ADK changes |
| V. Golden Trace Output | ✅ PASS | No changes to trace format |
| VI. Hermetic Development Environment | ✅ PASS | No new external dependencies |
| VII. Strict Development Standards | ✅ PASS | Will use ruff, pyright strict, 2-space indent |
| VIII. Flexible UI Strategy | ✅ PASS | NiceGUI already chosen for project |
| IX. Screenshot-Verified UX Changes | ⚠️ REQUIRED | Must capture screenshots for new tree component |

**Gate Result**: PASS with screenshot requirement

## Project Structure

### Documentation (this feature)

```text
specs/004-devtools-event-renderer/
├── plan.md              # This file
├── research.md          # Phase 0 output ✅
├── data-model.md        # Phase 1 output ✅
├── quickstart.md        # Phase 1 output ✅
├── contracts/           # Phase 1 output ✅
│   └── component-apis.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
adk_agent_sim/
├── ui/
│   ├── components/
│   │   ├── devtools_tree.py         # NEW - Core tree component
│   │   ├── tree_expansion_state.py  # NEW - Expansion state management
│   │   ├── smart_blob.py            # NEW - Detection & state utilities
│   │   ├── blob_toggle_pills.py     # NEW - Toggle pill UI component
│   │   ├── smart_blob_renderer.py   # NEW - Full blob renderer
│   │   ├── event_stream.py          # MODIFY - Add global controls
│   │   ├── event_block.py           # MODIFY - Use DevToolsTree
│   │   └── json_tree.py             # DELETE - Remove buggy component
│   └── styles.py                    # MODIFY - Add new style constants

tests/
├── unit/
│   ├── test_devtools_tree.py        # NEW
│   ├── test_tree_expansion_state.py # NEW
│   ├── test_smart_blob.py           # NEW
│   └── test_blob_toggle_pills.py    # NEW
└── e2e/
    ├── test_devtools_tree_e2e.py    # NEW
    └── test_component_screenshots.py # MODIFY - Update screenshots

docs/screenshots/
└── components/
    └── devtools-tree*.png           # NEW - Screenshot baselines
```

**Structure Decision**: Single Python package. New components added to existing `adk_agent_sim/ui/components/` directory. Old `json_tree.py` deleted entirely.

---

## Pull Request Sequence

This feature is implemented across **5 sequential PRs** for digestible code review.

### PR1: Core DevTools Tree Renderer

**User Stories**: US1 (P1) - View Execution Trace at a Glance  
**Estimated Size**: ~200 LOC  
**Dependencies**: None (first PR)

**Scope**:
- `DevToolsTree` component renders JSON as hierarchical tree
- Monospace typography with syntax coloring (keys, strings, numbers, booleans, null)
- Thin vertical thread lines via CSS `::before` pseudo-elements
- All nodes expanded by default
- Individual node expand/collapse via click
- `TreeExpansionState` dataclass with path-based sparse state storage

**Files Created**:
| File | Description |
|------|-------------|
| `adk_agent_sim/ui/components/devtools_tree.py` | Core tree rendering component (~150 LOC) |
| `adk_agent_sim/ui/components/tree_expansion_state.py` | Expansion state management (~50 LOC) |
| `tests/unit/test_devtools_tree.py` | Unit tests for tree rendering |
| `tests/unit/test_tree_expansion_state.py` | Unit tests for state management |

**Files Modified**:
| File | Changes |
|------|---------|
| `adk_agent_sim/ui/styles.py` | Add `DEVTOOLS_TREE_STYLES` constants |

**Acceptance Criteria**:
- [ ] Tree renders nested dict/list/primitives correctly
- [ ] All nodes expanded on initial render
- [ ] Clicking chevron toggles node expansion
- [ ] Thread lines visible connecting parents to children
- [ ] Syntax coloring distinguishes keys from values
- [ ] `./scripts/check_quality.sh` passes

---

### PR2: Smart Blob Detection

**User Stories**: US3, US4, US5 (P2) - Detection logic only  
**Estimated Size**: ~100 LOC  
**Dependencies**: PR1 merged

**Scope**:
- `BlobType` enum: JSON, MARKDOWN, PLAIN
- `SmartBlobDetector` utility class
- JSON detection: strings starting with `{` or `[` that parse successfully
- Markdown detection: regex patterns for `**`, `##`, `- `, `1. `, triple backticks
- Comprehensive edge case handling

**Files Created**:
| File | Description |
|------|-------------|
| `adk_agent_sim/ui/components/smart_blob.py` | Detection utilities (~80 LOC) |
| `tests/unit/test_smart_blob.py` | Detection tests with edge cases |

**Acceptance Criteria**:
- [ ] Valid JSON objects/arrays detected correctly
- [ ] Malformed JSON returns PLAIN type
- [ ] Markdown patterns detected (headers, bold, lists, code blocks)
- [ ] Plain strings without patterns return PLAIN type
- [ ] Edge cases: empty strings, whitespace-only, single characters
- [ ] `./scripts/check_quality.sh` passes

---

### PR3: View Mode Toggles

**User Stories**: US3, US4, US5 (P2) - Toggle UI  
**Estimated Size**: ~150 LOC  
**Dependencies**: PR2 merged

**Scope**:
- `ViewMode` enum: RAW, JSON, MARKDOWN
- `BlobViewState` dataclass for mode tracking
- `BlobTogglePills` component: [RAW], [JSON], [MD] buttons
- Default mode selection based on detected type (per clarification)
- Pill styling: outlined when inactive, solid when active

**Files Created**:
| File | Description |
|------|-------------|
| `adk_agent_sim/ui/components/blob_toggle_pills.py` | Toggle pill component (~100 LOC) |
| `tests/unit/test_blob_toggle_pills.py` | Toggle behavior tests |

**Files Modified**:
| File | Changes |
|------|---------|
| `adk_agent_sim/ui/components/smart_blob.py` | Add `ViewMode`, `BlobViewState` (~50 LOC) |
| `adk_agent_sim/ui/styles.py` | Add `SMART_BLOB_STYLES` constants |

**Acceptance Criteria**:
- [ ] Toggle pills render with correct labels
- [ ] Active toggle visually distinct (solid background)
- [ ] Clicking toggle updates view mode state
- [ ] JSON blobs default to JSON view on render
- [ ] Markdown blobs default to MARKDOWN view on render
- [ ] `./scripts/check_quality.sh` passes

---

### PR4: Inline Expansion & EventBlock Integration

**User Stories**: US3, US4, US5 (P2) - Full rendering  
**Estimated Size**: ~250 LOC  
**Dependencies**: PR3 merged

**Scope**:
- `SmartBlobRenderer` renders string with toggles + content
- RAW view: Monospace with preserved whitespace
- JSON view: Recursive `DevToolsTree` for parsed content
- MARKDOWN view: `ui.markdown()` rendering
- Inline expansion (pushes tree content down, no modals)
- Integration into `EventBlock` subclasses (replace `JsonTree` usage)
- Error handling for malformed JSON (graceful fallback to RAW)

**Files Created**:
| File | Description |
|------|-------------|
| `adk_agent_sim/ui/components/smart_blob_renderer.py` | Full blob renderer (~150 LOC) |
| `tests/unit/test_smart_blob_renderer.py` | Renderer unit tests |
| `tests/e2e/test_devtools_tree_e2e.py` | E2E integration tests |

**Files Modified**:
| File | Changes |
|------|---------|
| `adk_agent_sim/ui/components/devtools_tree.py` | Integrate `SmartBlobRenderer` for string values |
| `adk_agent_sim/ui/components/event_block.py` | Replace `JsonTree`/`render_json_tree` with `DevToolsTree` |

**Acceptance Criteria**:
- [ ] Strings with JSON show parsed tree when JSON toggle active
- [ ] Strings with Markdown show formatted text when MD toggle active
- [ ] RAW toggle shows original string with whitespace preserved
- [ ] Expanded content respects parent indentation
- [ ] Recursive JSON (double-encoded) offers nested toggles
- [ ] Malformed JSON falls back to RAW view gracefully
- [ ] E2E test passes for toggle interactions
- [ ] `./scripts/check_quality.sh` passes

---

### PR5: Global Controls & Final Polish

**User Stories**: US2 (P1), US6 (P3) - Completion  
**Estimated Size**: ~150 LOC  
**Dependencies**: PR4 merged

**Scope**:
- Global "Expand All" / "Collapse All" buttons in EventStream header
- Buttons affect all tree nodes across all event blocks
- Delete `json_tree.py` entirely
- Update screenshot tests for new UI
- Final CSS polish and visual consistency

**Files Deleted**:
| File | Reason |
|------|--------|
| `adk_agent_sim/ui/components/json_tree.py` | Replaced by DevToolsTree, buggy code removed |

**Files Modified**:
| File | Changes |
|------|---------|
| `adk_agent_sim/ui/components/event_stream.py` | Add global expand/collapse controls (~50 LOC) |
| `tests/e2e/test_devtools_tree_e2e.py` | Add global control tests |
| `tests/e2e/test_component_screenshots.py` | Update screenshot baselines |

**Files Created**:
| File | Description |
|------|-------------|
| `docs/screenshots/components/devtools-tree-expanded.png` | Screenshot baseline |
| `docs/screenshots/components/devtools-tree-collapsed.png` | Screenshot baseline |

**Acceptance Criteria**:
- [ ] "Expand All" button expands all nodes in all event blocks
- [ ] "Collapse All" button collapses all nodes in all event blocks
- [ ] `json_tree.py` deleted from codebase
- [ ] No remaining imports of `JsonTree` or `render_json_tree`
- [ ] Screenshot tests capture new UI and pass review
- [ ] Full E2E test suite passes
- [ ] `./scripts/check_quality.sh` passes

---

## Complexity Tracking

> No Constitution violations requiring justification.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance issues with large datasets | Medium | High | Monitor render time in E2E tests; defer virtualization to future PR if needed |
| CSS thread lines break in edge cases | Low | Low | Test with various nesting depths; ensure last-child handling correct |
| Markdown detection false positives | Medium | Low | Toggle approach allows user to switch to RAW; acceptable per spec |
| NiceGUI limitations for custom CSS | Low | Medium | Research confirmed custom CSS via `.style()` works |

---

## Dependencies Graph

```
PR1 ─────────────────────────────────────┐
 │ (Core Tree)                           │
 ▼                                       │
PR2 ─────────────────────────────────────┤
 │ (Smart Blob Detection)                │
 ▼                                       │
PR3 ─────────────────────────────────────┤
 │ (View Mode Toggles)                   │
 ▼                                       │
PR4 ─────────────────────────────────────┤
 │ (Inline Expansion & Integration)      │
 ▼                                       │
PR5 ──────────────────────────────────────
   (Global Controls & Polish)
```

All PRs are sequential. Each must be merged before the next can begin.

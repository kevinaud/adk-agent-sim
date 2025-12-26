# Quickstart: DevTools-Style Event Stream Renderer

**Branch**: `004-devtools-event-renderer` | **Date**: 2025-12-26

## Overview

This feature replaces the accordion-based event stream renderer with a compact, DevTools-style hierarchical tree. The implementation is divided into **5 sequential pull requests** for easy code review.

> ⚠️ **CRITICAL CONSTRAINT**: The existing `json_tree.py` has multiple hard-to-diagnose bugs. This implementation is a **clean-room rewrite** — do NOT copy or reuse any code from `json_tree.py` or `text_presenter.py`. Build all components from scratch.

## PR Sequence

```
PR1: Core Tree Renderer     PR2: Smart Blob Detection    PR3: View Toggles
     (P1 foundation)             (P2 detection)              (P2 interaction)
         │                            │                            │
         ▼                            ▼                            │
┌─────────────────┐          ┌─────────────────┐                   │
│ DevToolsTree    │          │ SmartBlobDetector│                   │
│ TreeExpansionState│        │ BlobType enum    │                   │
│ Basic CSS       │          │ Detection logic  │                   │
└─────────────────┘          └─────────────────┘                   │
                                     │                             │
                                     ▼                             ▼
                             ┌─────────────────────────────────────────┐
                             │ PR4: Inline Expansion & Integration     │
                             │ SmartBlobRenderer, EventBlock integration│
                             └─────────────────────────────────────────┘
                                                │
                                                ▼
                             ┌─────────────────────────────────────────┐
                             │ PR5: Global Controls & Polish           │
                             │ Expand/Collapse All, screenshot tests   │
                             └─────────────────────────────────────────┘
```

## Development Sequence

### PR1: Core DevTools Tree Renderer (~200 LOC)

**Scope**: User Story 1 (P1) - Basic tree rendering

**Files**:
```
adk_agent_sim/ui/components/
├── devtools_tree.py          # NEW - Core tree component
├── tree_expansion_state.py   # NEW - Expansion state management

adk_agent_sim/ui/
├── styles.py                 # MODIFY - Add DEVTOOLS_TREE_STYLES

tests/unit/
├── test_devtools_tree.py     # NEW - Unit tests
├── test_tree_expansion_state.py  # NEW - State manager tests
```

**Deliverables**:
- `DevToolsTree` component renders JSON as hierarchical tree
- Monospace typography with syntax coloring
- Thread lines connecting parent-child nodes
- All nodes expanded by default
- Individual node expand/collapse via click
- `TreeExpansionState` dataclass with path-based state

**Test Commands**:
```bash
uv run pytest tests/unit/test_devtools_tree.py -v
uv run pytest tests/unit/test_tree_expansion_state.py -v
```

---

### PR2: Smart Blob Detection (~100 LOC)

**Scope**: User Stories 3-5 (P2) - Detection logic only

**Files**:
```
adk_agent_sim/ui/components/
├── smart_blob.py             # NEW - Detection utilities

tests/unit/
├── test_smart_blob.py        # NEW - Detection tests
```

**Deliverables**:
- `BlobType` enum: JSON, MARKDOWN, PLAIN
- `SmartBlobDetector.detect_type()` method
- `SmartBlobDetector.try_parse_json()` method
- `SmartBlobDetector.detect_markdown_patterns()` method
- Comprehensive test coverage for edge cases

**Test Commands**:
```bash
uv run pytest tests/unit/test_smart_blob.py -v
```

---

### PR3: View Mode Toggles (~150 LOC)

**Scope**: Toggle pill UI and view mode state

**Files**:
```
adk_agent_sim/ui/components/
├── smart_blob.py             # MODIFY - Add BlobViewState, ViewMode
├── blob_toggle_pills.py      # NEW - Toggle pill component

adk_agent_sim/ui/
├── styles.py                 # MODIFY - Add SMART_BLOB_STYLES

tests/unit/
├── test_blob_toggle_pills.py # NEW - Toggle behavior tests
```

**Deliverables**:
- `ViewMode` enum: RAW, JSON, MARKDOWN
- `BlobViewState` dataclass for mode tracking
- `BlobTogglePills` component with [RAW], [JSON], [MD] buttons
- Default mode selection based on detected type
- CSS styling for pill appearance

**Test Commands**:
```bash
uv run pytest tests/unit/test_smart_blob.py -v
uv run pytest tests/unit/test_blob_toggle_pills.py -v
```

---

### PR4: Inline Expansion & EventBlock Integration (~250 LOC)

**Scope**: Connect everything together

**Files**:
```
adk_agent_sim/ui/components/
├── smart_blob_renderer.py    # NEW - Full blob renderer
├── devtools_tree.py          # MODIFY - Integrate SmartBlobRenderer
├── event_block.py            # MODIFY - Replace JsonTree with DevToolsTree

tests/unit/
├── test_smart_blob_renderer.py  # NEW

tests/e2e/
├── test_devtools_tree_e2e.py    # NEW - Integration tests
```

**Deliverables**:
- `SmartBlobRenderer` renders string with toggles + content
- RAW view: Monospace with preserved whitespace
- JSON view: Recursive `DevToolsTree` for parsed content
- MARKDOWN view: `ui.markdown()` rendering
- Inline expansion (pushes tree content down)
- `EventBlock` classes use `DevToolsTree` instead of `JsonTree`
- Error handling for malformed JSON

**Test Commands**:
```bash
uv run pytest tests/unit/test_smart_blob_renderer.py -v
uv run pytest tests/e2e/test_devtools_tree_e2e.py -v
```

---

### PR5: Global Controls & Final Polish (~150 LOC)

**Scope**: User Story 2 (P1) completion + cleanup

**Files**:
```
adk_agent_sim/ui/components/
├── event_stream.py           # MODIFY - Add global expand/collapse
├── json_tree.py              # DELETE (not deprecate - remove entirely)

tests/e2e/
├── test_devtools_tree_e2e.py    # MODIFY - Add global control tests
├── test_component_screenshots.py # MODIFY - Update screenshots
```

**Deliverables**:
- Global "Expand All" button in EventStream header
- Global "Collapse All" button in EventStream header
- Buttons affect all tree nodes across all events
- **Delete** old `JsonTree` component entirely (do not deprecate)
- Update screenshot tests for new UI
- Final CSS polish and consistency

**Test Commands**:
```bash
uv run pytest tests/e2e/ -v
./scripts/check_quality.sh
```

---

## Local Development

### Run the Demo

```bash
# Start the dev server
uv run demo

# Open in browser
open http://localhost:8080
```

### Run All Tests

```bash
# Full test suite
uv run pytest -v

# Just this feature's tests
uv run pytest tests/unit/test_devtools*.py tests/unit/test_smart*.py -v
uv run pytest tests/e2e/test_devtools*.py -v
```

### Quality Checks

```bash
# Format and lint
uv run ruff format
uv run ruff check --fix

# Type checking
uv run pyright

# All quality gates
./scripts/check_quality.sh
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `devtools_tree.py` | Core tree rendering component |
| `tree_expansion_state.py` | Expand/collapse state management |
| `smart_blob.py` | Content detection utilities |
| `blob_toggle_pills.py` | Toggle pill UI component |
| `smart_blob_renderer.py` | Full blob renderer with all views |
| `styles.py` | CSS constants and colors |

---

## Success Validation

After all PRs merged, verify:

1. **SC-001**: Open any event with nested data → all nodes visible without clicks
2. **SC-002**: Click "Collapse All" → all nodes collapse; Click "Expand All" → all expand
3. **SC-003**: String with JSON → `[JSON]` toggle appears → click → tree renders inline
4. **SC-004**: String with Markdown → `[MD]` toggle appears → click → formatted text renders
5. **SC-005**: Visual comparison shows significant vertical space reduction
6. **SC-007**: Load event with 1000 nodes → renders within 500ms (check browser devtools)

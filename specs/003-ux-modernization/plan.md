# Implementation Plan: UX Modernization

**Branch**: `003-ux-modernization` | **Date**: 2025-12-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ux-modernization/spec.md`

## Summary

Modernize the ADK Agent Simulator UI from the current basic dropdown-and-split-pane layout to a polished, professional interface with:
1. Card grid for agent selection (replacing dropdown)
2. Structured event stream for history (replacing simple list)
3. Right sidebar for controls (replacing equal 50/50 split)
4. Collapsible JSON tree for tool outputs (replacing static code blocks)
5. Expandable header for system prompt (consistent with current collapsible approach)

This is a **UI-only refactor** with full feature parity—no backend changes required.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: NiceGUI 2.0+ (includes Quasar/Vue, Tailwind CSS)  
**Storage**: N/A (in-memory session only)  
**Testing**: pytest (visual testing via existing e2e infrastructure)  
**Target Platform**: Desktop browsers (Chrome, Firefox, Safari)  
**Project Type**: Single Python package with embedded web UI  
**Performance Goals**: Instant UI response (<100ms interaction feedback)  
**Constraints**: Must work within NiceGUI's component model; no custom JS frameworks  
**Scale/Scope**: 2 pages (Agent Select, Simulation), ~10 components to modify

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Library-First | ✅ PASS | UI changes don't affect installability or import pattern |
| II. Wrapper Integration | ✅ PASS | No changes to `AgentSimulator` entry point |
| III. Wizard of Oz Model | ✅ PASS | All wizard interactions preserved (tool invoke, final response) |
| IV. ADK Dependency | ✅ PASS | No changes to tool discovery/execution |
| V. Golden Trace Output | ✅ PASS | Export functionality unchanged |
| VI. Hermetic Dev Environment | ✅ PASS | NiceGUI already in deps; no new system dependencies |
| VII. Strict Standards | ✅ PASS | All code will use ruff, pyright strict, 2-space indent |
| VIII. Flexible UI Strategy | ✅ PASS | Staying with NiceGUI per existing choice |

**Result**: All gates pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-ux-modernization/
├── plan.md              # This file
├── research.md          # Phase 0 output - NiceGUI patterns research
├── data-model.md        # Phase 1 output - Component hierarchy
├── quickstart.md        # Phase 1 output - Development guide
├── contracts/           # Phase 1 output - Component interfaces
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
adk_agent_sim/
├── ui/
│   ├── app.py                    # Routes (minor changes)
│   ├── styles.py                 # Design tokens (UPDATE)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── action_panel.py       # Tool selection (UPDATE)
│   │   ├── agent_card.py         # NEW - Card component
│   │   ├── event_block.py        # NEW - Event stream block
│   │   ├── history_panel.py      # REPLACE with event_stream.py
│   │   ├── event_stream.py       # NEW - Event stream container
│   │   ├── json_tree.py          # NEW - Collapsible JSON tree
│   │   ├── schema_form.py        # Keep (form rendering)
│   │   ├── system_prompt.py      # UPDATE - Expandable header
│   │   └── tool_executor.py      # UPDATE - Loading states
│   └── pages/
│       ├── __init__.py
│       ├── agent_select.py       # REWRITE - Card grid
│       └── simulation.py         # UPDATE - Layout restructure

tests/
├── unit/
│   └── test_ui_components.py     # NEW - Component tests
└── e2e/
    └── test_ui_visual.py         # NEW - Visual regression (optional)
```

**Structure Decision**: Single Python package structure. All UI changes are contained within `adk_agent_sim/ui/`. No new top-level directories needed.

## Complexity Tracking

> No Constitution violations. Table not required.

# Implementation Plan: UX Modernization

**Branch**: `003-ux-modernization` | **Date**: 2025-12-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ux-modernization/spec.md`

## Summary

Modernize the UX of the ADK Agent Simulator while maintaining feature parity. Key improvements include:
- Agent selection dashboard with card grid showing actual agent descriptions
- Structured event stream with expand-by-default, session-only state persistence, and bulk expand/collapse controls
- Toggleable text presentation modes (Raw, JSON, Markdown) with auto-detection
- Tool catalog view showing full tool metadata (name, description, input/output schemas)

**Technical Approach**: UI-only changes using NiceGUI components with Tailwind CSS styling. No backend model changes required.

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: `nicegui` (UI), Tailwind CSS (styling)  
**Storage**: N/A (ephemeral in-memory sessions only)  
**Testing**: `pytest` with `pytest-playwright` for E2E visual verification  
**Target Platform**: Desktop browser (1280px+ width)
**Project Type**: Single project (Python library)  
**Performance Goals**: UI response <200ms, smooth expand/collapse animations  
**Constraints**: Feature parity with existing functionality, no backend changes  
**Scale/Scope**: ~10 UI components to modify/create

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Library-First | ✅ PASS | UI changes remain within library package |
| II. Wrapper Integration | ✅ PASS | No changes to agent configuration API |
| III. Wizard of Oz | ✅ PASS | Improves human decision-making context with better tool display |
| IV. ADK Dependency | ✅ PASS | No ADK integration changes |
| V. Golden Trace | ✅ PASS | Export functionality preserved (now via button to EvalSet) |
| VI. Hermetic Environment | ✅ PASS | No new system dependencies |
| VII. Strict Standards | ✅ PASS | All code must pass `ruff` (2-space) and `pyright` strict |
| VIII. Flexible UI | ✅ PASS | Continuing with NiceGUI as chosen framework |
| IX. Screenshot-Verified UX | ✅ PASS | E2E tests will capture screenshots for verification |

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/003-ux-modernization/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (component hierarchy)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
\`\`\`

### Source Code (changes to existing files)

\`\`\`text
adk_agent_sim/ui/
├── pages/
│   ├── agent_select.py        # MODIFY: Card grid with actual descriptions
│   └── simulation.py          # MODIFY: Layout changes
├── components/
│   ├── agent_card.py          # NEW: Individual agent card component
│   ├── event_stream.py        # NEW: Container for event blocks
│   ├── event_block.py         # MODIFY: Add expand/collapse state, bulk controls
│   ├── json_tree.py           # MODIFY: Used by text_presenter for JSON mode
│   ├── text_presenter.py      # NEW: Raw/JSON/Markdown toggle component
│   ├── action_panel.py        # MODIFY: Tool catalog view instead of dropdown
│   ├── tool_executor.py       # MODIFY: Updated to work with tool catalog
│   └── system_prompt.py       # Minor styling updates
└── styles.py                  # MODIFY: New style constants

docs/screenshots/              # Updated screenshots from E2E tests
\`\`\`

**Structure Decision**: Modifications to existing UI components. New \`agent_card.py\` and \`event_stream.py\` for better organization. No backend changes.

## Functional Requirements Mapping

### FR → Implementation Mapping

| FR | Component | Implementation |
|----|-----------|----------------|
| FR-001 | \`styles.py\` | Design system constants (colors, typography, spacing) |
| FR-002 | \`pages/agent_select.py\` | Card grid layout using \`ui.grid()\` |
| FR-002a | \`components/agent_card.py\` | Fetch description via \`agent.description\` property |
| FR-003 | \`pages/simulation.py\` | Event stream + sidebar layout |
| FR-004 | \`components/event_block.py\` | Distinct styling per \`HistoryEntry.type\` |
| FR-005 | \`components/json_tree.py\` | \`ui.tree()\` or custom collapsible component |
| FR-005a | \`components/event_block.py\` | \`expanded=True\` default for collapsible sections |
| FR-005b | `components/event_block.py` | State stored in component instance (session-only, not persisted) |
| FR-005c | `components/event_block.py` | "Expand All" / "Collapse All" buttons per block |
| FR-005d | `components/text_presenter.py` | New component with Raw/JSON/Markdown toggle |
| FR-005e | `components/text_presenter.py` | Auto-detect JSON, default to Raw otherwise |
| FR-005f | `components/text_presenter.py` | Truncate >500 chars in Raw mode with "Show More" |
| FR-006 | \`components/system_prompt.py\` | \`ui.expansion(value=False)\` by default |
| FR-007 | \`components/tool_executor.py\` | \`ui.spinner()\` during execution |
| FR-008 | All components | Feature parity verification via E2E tests |
| FR-009 | \`components/action_panel.py\` | Tool catalog with cards showing all metadata |
| FR-009a | \`components/action_panel.py\` | \`ui.expansion()\` for input/output schemas |
| FR-009b | \`components/action_panel.py\` | Remove dropdown, use clickable tool cards |

## Key Implementation Details

### 1. Agent Description Bug Fix

**Problem**: Agent cards show "No description available" even when agents have descriptions.

**Solution**: Access \`agent.description\` property correctly. The current code may be looking at the wrong attribute or not handling the case properly.

\`\`\`python
# In agent_card.py
def render_agent_card(config: SimulatedAgentConfig):
  # Use config.agent.description if available
  description = config.agent.description or "No description available"
\`\`\`

### 2. Expand/Collapse State Persistence

**Problem**: State resets when UI re-renders.

**Solution**: Store expand/collapse state in a dictionary keyed by event ID, not in transient UI state.

\`\`\`python
# In event_stream.py
class EventStream:
  def __init__(self):
    self._expand_states: dict[str, dict[str, bool]] = {}  # event_id -> section -> expanded
  
  def get_expanded(self, event_id: str, section: str) -> bool:
    return self._expand_states.get(event_id, {}).get(section, True)  # Default: expanded
  
  def set_expanded(self, event_id: str, section: str, expanded: bool):
    if event_id not in self._expand_states:
      self._expand_states[event_id] = {}
    self._expand_states[event_id][section] = expanded
\`\`\`

### 3. Text Presentation Toggle (TextPresenter Component)

**Solution**: Create a new `text_presenter.py` component that wraps text content with a mode toggle.

\`\`\`python
from enum import Enum

class PresentationMode(Enum):
  RAW = "raw"
  JSON = "json"
  MARKDOWN = "markdown"

def render_text_presenter(content: str, element_id: str) -> None:
  # Detect if content is valid JSON
  is_json = False
  try:
    parsed = json.loads(content)
    if isinstance(parsed, (dict, list)):
      is_json = True
  except json.JSONDecodeError:
    pass
  
  # Default mode: JSON if parseable, else Raw
  default_mode = PresentationMode.JSON if is_json else PresentationMode.RAW
  
  # Render toggle buttons
  with ui.button_group().classes('mb-2'):
    ui.button('Raw', on_click=lambda: set_mode(element_id, PresentationMode.RAW))
    ui.button('JSON', on_click=lambda: set_mode(element_id, PresentationMode.JSON))
    ui.button('Markdown', on_click=lambda: set_mode(element_id, PresentationMode.MARKDOWN))
  
  # Render content based on mode
  mode = get_mode(element_id, default_mode)
  if mode == PresentationMode.RAW:
    render_raw(content)  # Plain text, truncate >500 chars
  elif mode == PresentationMode.JSON:
    render_json_tree(parsed if is_json else content)
  else:
    ui.markdown(content)
\`\`\`

**Truncation**: In Raw mode, text >500 characters shows first 500 chars with "Show More" link.
      if isinstance(parsed, (dict, list)):  # Only if it's structured JSON
        render_json_tree(parsed)
        return
    except json.JSONDecodeError:
      pass
  # Fall through to normal string rendering
  ui.label(str(value))
\`\`\`

### 4. Tool Catalog View

**Solution**: Replace dropdown with a scrollable list of tool cards.

\`\`\`python
# In action_panel.py
def render_tool_catalog(tools: list[BaseTool]):
  with ui.scroll_area().classes('max-h-96'):
    for tool in tools:
      decl = tool._get_declaration()
      with ui.card().classes('cursor-pointer hover:shadow-lg'):
        ui.label(decl.name).classes('font-bold')
        if decl.description:
          ui.label(decl.description).classes('text-sm text-gray-600')
        with ui.expansion('Input Schema'):
          render_schema_preview(decl.parameters)
        # Output schema if available
\`\`\`

## Complexity Tracking

> No Constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | — | — |

---

## Phase 0: Research

### Research Tasks

1. **NiceGUI state management**: Best patterns for persisting UI state across re-renders.
2. **Tailwind CSS in NiceGUI**: How to apply consistent Tailwind classes.
3. **JSON tree component**: Existing NiceGUI components or need custom implementation.
4. **Scroll behavior**: How to maintain scroll position when adding new events.

### Decisions

| Topic | Decision | Rationale | Alternatives Rejected |
|-------|----------|-----------|----------------------|
| State Persistence | Component instance state | Simple, works with NiceGUI reactivity | Global store (overkill), session storage (unnecessary) |
| JSON Display | Custom collapsible tree | More control over styling | \`ui.json_editor\` (too heavy), raw text (poor UX) |
| Tool Catalog | Scrollable card list | Shows all metadata at once | Dropdown (hides info), tabs (extra clicks) |

---

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md) for component hierarchy and props.

**Key Components:**
- \`AgentCard\`: Displays agent name and description (fix bug)
- \`EventStream\`: Container with expand/collapse state management
- \`EventBlock\`: Individual event with bulk controls
- \`JsonTree\`: Auto-parsing JSON display
- \`ToolCatalog\`: Full metadata tool selection

### Contracts

See [contracts/README.md](contracts/README.md) for internal Python interface definitions.

**Key Interfaces:**
- \`ExpandCollapseState\`: Protocol for state persistence
- \`JsonRenderer\`: Protocol for value rendering with auto-parse

### Quickstart

See [quickstart.md](quickstart.md) for component usage examples.

---

## Dependencies

### New Dependencies

None required—all changes use existing NiceGUI features.

### Dev Container Updates

None required.

---

## Quality Gates Checklist

- [ ] All new/modified files use 2-space indentation (\`ruff format\`)
- [ ] All new/modified files pass \`ruff check\` with zero errors
- [ ] All new/modified files pass \`pyright --strict\` with zero errors
- [ ] Agent descriptions display correctly (bug fix verified)
- [ ] Event sections are expanded by default
- [ ] Expand/collapse state persists within session (resets on page refresh)
- [ ] Expand All / Collapse All buttons work
- [ ] Text presenter toggle switches between Raw/JSON/Markdown modes
- [ ] JSON auto-detection sets default mode to JSON for valid JSON content
- [ ] Raw mode truncates text >500 chars with "Show More"
- [ ] Tool catalog displays name, description, and schemas
- [ ] E2E tests pass with updated screenshots
- [ ] Screenshots reviewed and approved

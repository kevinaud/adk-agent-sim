# Data Model: UX Modernization

**Feature**: 003-ux-modernization  
**Date**: 2025-12-24  
**Status**: Complete

## Overview

This feature is UI-only. No new data models are required. This document describes the **component hierarchy** and **props/state** for the new UI components.

## Component Hierarchy

```text
SimulatorApp
├── AgentSelectPage (/)
│   └── AgentCardGrid
│       └── AgentCard[] (one per agent)
│
└── SimulationPage (/simulate)
    ├── PageHeader
    │   └── SessionStateBadge
    │
    ├── SystemPromptHeader (expandable)
    │
    └── MainLayout (row)
        ├── EventStream (2/3 width, scrollable)
        │   ├── EventBlock[] (one per history entry)
        │   │   ├── UserInputBlock
        │   │   ├── ToolExecutionBlock
        │   │   │   └── JsonTree (for args/result)
        │   │   ├── ToolErrorBlock
        │   │   └── AgentResponseBlock
        │   └── LoadingBlock (when executing)
        │
        └── ControlPanel (1/3 width, sidebar)
            ├── ActionPanel (tool selection)
            │   ├── ToolSelector
            │   └── FinalResponseButton
            └── ToolExecutor (when tool selected)
                ├── SchemaForm
                ├── ExecuteButton
                │   └── Spinner (when loading)
                └── CancelButton
```

## Component Specifications

### AgentCard

**Purpose**: Clickable card displaying agent name and description.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `name` | `str` | Yes | Agent display name |
| `description` | `str \| None` | No | Agent description (if available) |
| `on_click` | `Callable[[], Awaitable[None]]` | Yes | Click handler |

**Visual States**:
- Default: White background, subtle shadow
- Hover: Elevated shadow, slight scale
- Active/Clicked: Brief press effect

---

### AgentCardGrid

**Purpose**: Responsive grid container for agent cards.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `agents` | `list[AgentInfo]` | Yes | List of agents to display |
| `on_select` | `Callable[[str], Awaitable[None]]` | Yes | Selection callback (agent name) |

**AgentInfo** (inline type):
```python
class AgentInfo(TypedDict):
  name: str
  description: str | None
```

---

### EventStream

**Purpose**: Scrollable container for history events.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `history` | `list[HistoryEntry]` | Yes | Session history |
| `is_loading` | `bool` | No | Show loading block at bottom |
| `loading_tool` | `str \| None` | No | Name of tool being executed |

**Behavior**:
- Auto-scrolls to bottom on new entry
- Manual scroll allowed (disables auto-scroll until user scrolls to bottom)

---

### EventBlock

**Purpose**: Single event in the stream (abstract base).

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `entry` | `HistoryEntry` | Yes | The history entry to render |
| `event_id` | `str` | Yes | Unique ID for state tracking |
| `expand_states` | `dict[str, bool]` | No | Map of section -> expanded state |
| `on_expand_change` | `Callable[[str, bool], None]` | No | Callback when section expands/collapses |

**Visual Elements**:
- Header with event type badge and timestamp
- "Expand All" / "Collapse All" buttons (top-right of block)
- Content sections that remember their expand/collapse state

**Subtypes** (determined by `entry.type`):
- `UserInputBlock`: Shows user query text (no collapsible sections)
- `ToolExecutionBlock`: Shows tool name, args (JsonTree, collapsible), result (JsonTree, collapsible)
- `ToolErrorBlock`: Shows tool name, error message, traceback (collapsible)
- `AgentResponseBlock`: Shows final response text (no collapsible sections)

---

### JsonTree

**Purpose**: Interactive, collapsible JSON/dict viewer.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `data` | `Any` | Yes | JSON-serializable data to display |
| `label` | `str` | No | Root label (default: "root") |
| `expanded` | `bool` | No | Initial expansion state (default: True) |
| `max_depth` | `int` | No | Max auto-expand depth (default: 2) |

**Behavior**:
- Objects/dicts: Expandable with `{n keys}` indicator
- Arrays: Expandable with `[n items]` indicator
- Primitives: Inline display with type-appropriate formatting

---

### TextPresenter

**Purpose**: Text content viewer with toggleable presentation modes (Raw, JSON, Markdown).

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `content` | `str` | Yes | Text content to display |
| `element_id` | `str` | Yes | Unique ID for state tracking |
| `default_mode` | `PresentationMode \| None` | No | Override auto-detection (default: None = auto) |

**PresentationMode** (enum):
```python
class PresentationMode(Enum):
  RAW = "raw"
  JSON = "json"
  MARKDOWN = "markdown"
```

**Visual Elements**:
- Toggle button group (Raw | JSON | Markdown) with active state highlighting
- Content area that renders based on selected mode

**Behavior**:
- **Auto-detection**: If content is valid JSON (object `{}` or array `[]`), default mode is JSON; otherwise Raw
- **Raw mode**: Plain text, truncated at 500 chars with "Show More" link
- **JSON mode**: Renders using JsonTree component (pretty-printed, collapsible)
- **Markdown mode**: Renders using `ui.markdown()` for formatted display
- **State persistence**: Selected mode persists within session (in-memory)

---

### SystemPromptHeader

**Purpose**: Expandable header showing agent system instructions.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `content` | `str` | Yes | System prompt text |
| `agent_name` | `str` | Yes | Agent name for display |
| `expanded` | `bool` | No | Initial state (default: False) |

---

### ToolCatalog

**Purpose**: Read-only view of all tools available to the selected agent.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `tools` | `list[ToolInfo]` | Yes | List of all agent tools |
| `expanded` | `bool` | No | Initial state (default: False) |

**ToolInfo** (inline type):
```python
class ToolInfo(TypedDict):
  name: str
  description: str | None
  parameters: dict[str, Any]  # JSON Schema for parameters
```

**Visual Elements**:
- Collapsible section with "Tools" header and count badge
- Scrollable list of tool cards when expanded
- Each tool shows name, description preview, and parameter schema

**Behavior**:
- Click to expand/collapse entire catalog
- Individual tools are read-only (no interaction)
- Parameter schemas displayed as compact JSON trees

---

### ControlPanel

**Purpose**: Sidebar container for wizard controls.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `session` | `SimulationSession` | Yes | Current session |
| `on_tool_select` | `Callable[[str], None]` | Yes | Tool selection callback |
| `on_final_response` | `Callable[[str], Awaitable[None]]` | Yes | Final response callback |
| `on_execute_tool` | `Callable[[str, dict], Awaitable[None]]` | Yes | Tool execution callback |

---

### LoadingBlock

**Purpose**: Temporary event block shown during tool execution.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `tool_name` | `str` | Yes | Name of tool being executed |
| `elapsed_ms` | `int` | No | Elapsed time (for timer display) |

## Existing Models (Unchanged)

The following models from `adk_agent_sim.models` are used but **not modified**:

- `HistoryEntry` (base class)
- `UserQuery`
- `ToolCall`
- `ToolOutput`
- `ToolError`
- `FinalResponse`
- `SimulationSession`
- `SessionState`

## State Management

NiceGUI uses a reactive model where component state is managed via:
1. Instance variables on page/component classes
2. `ui.refreshable` decorators for selective re-rendering
3. Direct DOM updates via element references

**State Scope**: All UI state is **session-only** (in-memory). State is NOT persisted across page refreshes or browser sessions.

**Key State Locations**:
- `SimulationPage._selected_tool`: Currently selected tool (or None)
- `SimulationPage._is_executing`: Whether a tool is executing
- `EventStream._auto_scroll`: Whether to auto-scroll (disabled on manual scroll)
- `EventStream._expand_states`: Dict mapping `event_id` -> `section_name` -> `bool` for expand/collapse persistence
- `EventStream._presentation_modes`: Dict mapping `element_id` -> `PresentationMode` for text presenter state

### Expand/Collapse State Persistence (Session-Only)

```python
class ExpandCollapseStateManager:
  """Manages expand/collapse state for all event blocks (session-only, in-memory)."""
  
  def __init__(self):
    # event_id -> section_name -> expanded (bool)
    self._states: dict[str, dict[str, bool]] = {}
  
  def get_expanded(self, event_id: str, section: str, default: bool = True) -> bool:
    """Get expansion state. Default is expanded=True."""
    return self._states.get(event_id, {}).get(section, default)
  
  def set_expanded(self, event_id: str, section: str, expanded: bool) -> None:
    """Set expansion state for a section."""
    if event_id not in self._states:
      self._states[event_id] = {}
    self._states[event_id][section] = expanded
  
  def expand_all(self, event_id: str) -> None:
    """Expand all sections for an event."""
    if event_id in self._states:
      for section in self._states[event_id]:
        self._states[event_id][section] = True
  
  def collapse_all(self, event_id: str) -> None:
    """Collapse all sections for an event."""
    if event_id in self._states:
      for section in self._states[event_id]:
        self._states[event_id][section] = False
```

### Text Presentation Mode State (Session-Only)

```python
class PresentationModeManager:
  """Manages presentation mode state for text elements (session-only, in-memory)."""
  
  def __init__(self):
    # element_id -> PresentationMode
    self._modes: dict[str, PresentationMode] = {}
  
  def get_mode(self, element_id: str, default: PresentationMode) -> PresentationMode:
    """Get presentation mode for an element. Uses provided default if not set."""
    return self._modes.get(element_id, default)
  
  def set_mode(self, element_id: str, mode: PresentationMode) -> None:
    """Set presentation mode for an element."""
    self._modes[element_id] = mode
  
  @staticmethod
  def detect_default_mode(content: str) -> PresentationMode:
    \"\"\"Auto-detect default mode based on content. Returns JSON if valid JSON, else RAW.\"\"\"
    try:
      parsed = json.loads(content)
      if isinstance(parsed, (dict, list)):
        return PresentationMode.JSON
    except json.JSONDecodeError:
      pass
    return PresentationMode.RAW
```

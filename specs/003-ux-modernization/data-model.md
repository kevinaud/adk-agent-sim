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
| `expanded` | `bool` | No | Initial expansion state for collapsible content |

**Subtypes** (determined by `entry.type`):
- `UserInputBlock`: Shows user query text
- `ToolExecutionBlock`: Shows tool name, args (JsonTree), result (JsonTree)
- `ToolErrorBlock`: Shows tool name, error message, traceback (collapsible)
- `AgentResponseBlock`: Shows final response text

---

### JsonTree

**Purpose**: Interactive, collapsible JSON/dict viewer.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `data` | `Any` | Yes | JSON-serializable data to display |
| `label` | `str` | No | Root label (default: "root") |
| `expanded` | `bool` | No | Initial expansion state (default: True for first level) |
| `max_depth` | `int` | No | Max auto-expand depth (default: 2) |

**Behavior**:
- Objects/dicts: Expandable with `{n keys}` indicator
- Arrays: Expandable with `[n items]` indicator
- Primitives: Inline display with type-appropriate formatting
- Strings > 100 chars: Truncated with "show more"

---

### SystemPromptHeader

**Purpose**: Expandable header showing agent system instructions.

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `content` | `str` | Yes | System prompt text |
| `agent_name` | `str` | Yes | Agent name for display |
| `expanded` | `bool` | No | Initial state (default: False) |

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

**Key State Locations**:
- `SimulationPage._selected_tool`: Currently selected tool (or None)
- `SimulationPage._is_executing`: Whether a tool is executing
- `EventStream._auto_scroll`: Whether to auto-scroll (disabled on manual scroll)

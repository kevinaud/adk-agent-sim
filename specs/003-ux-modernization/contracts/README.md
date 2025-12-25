# Component Contracts

This directory contains interface definitions for the new UI components.

Since this is a Python/NiceGUI project (not a typed API), contracts are defined as:
1. **Type hints** in the component function signatures
2. **Docstrings** describing expected behavior
3. **Protocol classes** for callbacks (where applicable)

## Contract Files

- **None required** - All contracts are inline in the component files via type hints.

## Component Interface Summary

### `agent_card.py`

```python
def render_agent_card(
    name: str,
    description: str | None,
    on_click: Callable[[], Awaitable[None]],
) -> ui.card:
    """Render a clickable agent card."""
```

### `agent_card_grid.py` (or inline in `agent_select.py`)

```python
def render_agent_grid(
    agents: list[dict[str, str | None]],  # [{"name": str, "description": str | None}]
    on_select: Callable[[str], Awaitable[None]],
) -> ui.row:
    """Render a responsive grid of agent cards."""
```

### `event_stream.py`

```python
class EventStream:
    def __init__(
        self,
        history: list[HistoryEntry],
        is_loading: bool = False,
        loading_tool: str | None = None,
    ) -> None: ...
    
    def render(self) -> None: ...
    def refresh(self, history: list[HistoryEntry]) -> None: ...
    def set_loading(self, is_loading: bool, tool_name: str | None = None) -> None: ...
```

### `event_block.py`

```python
def render_event_block(entry: HistoryEntry, expanded: bool = True) -> ui.card:
    """Render a single event block based on entry type."""
```

### `json_tree.py`

```python
def render_json_tree(
    data: Any,
    label: str = "root",
    expanded: bool = True,
    max_depth: int = 2,
    _current_depth: int = 0,
) -> None:
    """Recursively render a collapsible JSON tree."""
```

### `system_prompt.py` (updated)

```python
def render_system_prompt_header(
    content: str,
    agent_name: str,
    expanded: bool = False,
) -> ui.expansion:
    """Render the system prompt as an expandable header."""
```

### `control_panel.py` (new, or refactor of action_panel)

```python
class ControlPanel:
    def __init__(
        self,
        tools: list[ToolInfo],
        on_tool_select: Callable[[str], None],
        on_final_response: Callable[[str], Awaitable[None]],
        on_execute_tool: Callable[[str, dict[str, Any]], Awaitable[None]],
        output_schema: type | None = None,
    ) -> None: ...
    
    def render(self) -> None: ...
    def show_tool_form(self, tool_name: str, schema: dict[str, Any]) -> None: ...
    def reset(self) -> None: ...
```

## Callback Protocols

```python
from typing import Protocol, Awaitable

class OnAgentSelect(Protocol):
    async def __call__(self, agent_name: str) -> None: ...

class OnToolSelect(Protocol):
    def __call__(self, tool_name: str) -> None: ...

class OnToolExecute(Protocol):
    async def __call__(self, tool_name: str, arguments: dict[str, Any]) -> None: ...

class OnFinalResponse(Protocol):
    async def __call__(self, response: str) -> None: ...
```

## Notes

- All components use NiceGUI's context manager pattern (`with ui.card(): ...`)
- Styling is applied via Tailwind classes (`.classes("...")`) and inline styles (`.style("...")`)
- Async callbacks are required where the operation involves controller methods
- Components return their root element for reference/manipulation

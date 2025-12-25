# Quickstart: UX Modernization

**Feature**: 003-ux-modernization  
**Date**: 2025-12-24

## Prerequisites

- Dev container running (all dependencies pre-installed)
- Virtual environment activated: `source .venv/bin/activate`

## Development Workflow

### 1. Run the Demo App

```bash
# Start the demo server (MCP tools)
demo-server &

# Run the simulator UI
demo
```

Open http://localhost:8080 to see the current UI.

### 2. File Locations

| Component | File | Action |
|-----------|------|--------|
| Styles/Colors | `adk_agent_sim/ui/styles.py` | Update design tokens |
| Agent Selection | `adk_agent_sim/ui/pages/agent_select.py` | Rewrite to card grid |
| Simulation Page | `adk_agent_sim/ui/pages/simulation.py` | Restructure layout |
| History Panel | `adk_agent_sim/ui/components/history_panel.py` | Replace with event stream |
| System Prompt | `adk_agent_sim/ui/components/system_prompt.py` | Update to expandable header |
| Action Panel | `adk_agent_sim/ui/components/action_panel.py` | Move to sidebar |
| Tool Executor | `adk_agent_sim/ui/components/tool_executor.py` | Add loading states |

### 3. New Files to Create

```bash
# Create new component files
touch adk_agent_sim/ui/components/agent_card.py
touch adk_agent_sim/ui/components/event_stream.py
touch adk_agent_sim/ui/components/event_block.py
touch adk_agent_sim/ui/components/json_tree.py
```

### 4. Quality Checks

```bash
# Run before every commit
./scripts/check_quality.sh

# Run tests
pytest tests/

# Run specific test file
pytest tests/unit/test_ui_components.py -v
```

### 5. Hot Reload

NiceGUI supports hot reload in development:

```bash
# Run with reload enabled
demo --reload
```

Changes to Python files will automatically refresh the browser.

## Implementation Order

Recommended sequence to minimize integration issues:

1. **styles.py** - Update design tokens (no breaking changes)
2. **json_tree.py** - New standalone component, testable in isolation
3. **event_block.py** - Depends on json_tree, renders single events
4. **event_stream.py** - Container using event_block
5. **agent_card.py** - New standalone component
6. **agent_select.py** - Rewrite page using agent_card
7. **system_prompt.py** - Update existing component
8. **simulation.py** - Final integration (depends on all above)

## Testing Strategy

### Manual Testing

1. Launch app, verify agent grid renders
2. Click agent card, verify navigation
3. Enter query, verify it appears in event stream
4. Execute tool, verify loading state and result display
5. Expand/collapse JSON tree, verify interaction
6. Send final response, verify completion state
7. Export trace, verify file downloads

### Automated Testing

```python
# Example unit test for JsonTree
def test_json_tree_renders_dict():
    """JsonTree should create expansion elements for dict keys."""
    # Test using NiceGUI's testing utilities
    ...
```

## Common Patterns

### Adding a New Event Block Type

```python
# In event_block.py
def _render_my_new_block(entry: MyNewEntry) -> None:
    with ui.row().classes("items-center gap-2"):
        ui.icon("my_icon").classes("text-blue-500")
        ui.label(entry.content).classes("text-sm")
```

### Styling with Tailwind

```python
# Common class patterns
".classes('w-full')"           # Full width
".classes('p-4')"              # Padding
".classes('mb-4')"             # Margin bottom
".classes('text-lg font-bold')" # Typography
".classes('bg-gray-50')"       # Background
".classes('hover:shadow-lg')"  # Hover effect
".classes('transition-all')"   # Smooth transitions
```

### Async Click Handlers

```python
async def on_click() -> None:
    await controller.do_something()
    ui.notify("Done!", type="positive")

ui.button("Click Me", on_click=on_click)
```

## Debugging

### NiceGUI Inspector

Press `F12` in browser to open DevTools. NiceGUI renders to real HTML elements.

### Python Debugging

```python
# Add breakpoints
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Logging

```python
import structlog
log = structlog.get_logger()
log.info("component_rendered", component="EventStream", entries=len(history))
```

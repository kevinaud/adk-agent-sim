# Research: UX Modernization

**Feature**: 003-ux-modernization  
**Date**: 2025-12-24  
**Status**: Complete

## Research Tasks

### R1: NiceGUI Card Grid Layout Patterns

**Question**: How to implement a responsive card grid in NiceGUI?

**Findings**:
- NiceGUI provides `ui.grid()` with configurable columns: `ui.grid(columns=3)`
- Cards are created with `ui.card()` and can include hover effects via Tailwind classes
- Responsive grids use Tailwind breakpoints: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Click handlers can be attached directly to cards via `card.on('click', handler)`

**Decision**: Use `ui.row()` with `flex-wrap` and fixed-width cards for simplicity. NiceGUI's grid is less flexible than raw Tailwind.

**Code Pattern**:
```python
with ui.row().classes("flex-wrap gap-4 justify-center"):
  for agent in agents:
    with ui.card().classes("w-64 cursor-pointer hover:shadow-lg transition-shadow"):
      ui.label(agent.name).classes("text-lg font-bold")
      ui.label(agent.description).classes("text-gray-600 text-sm")
```

---

### R2: NiceGUI Sidebar Layout Patterns

**Question**: How to implement a fixed right sidebar with scrollable main content?

**Findings**:
- NiceGUI uses Quasar's layout system under the hood
- `ui.left_drawer()` and `ui.right_drawer()` exist but are for collapsible drawers
- For fixed sidebars, use `ui.row()` with explicit width classes
- Main content should use `flex-grow` to fill remaining space
- Scroll areas: `ui.scroll_area()` with explicit height

**Decision**: Use `ui.row()` with `w-2/3` (main) and `w-1/3` (sidebar) split. Sidebar uses `sticky top-0` for fixed position.

**Code Pattern**:
```python
with ui.row().classes("w-full h-screen"):
  # Main content (scrollable)
  with ui.column().classes("w-2/3 h-full overflow-auto p-4"):
    render_event_stream()
  
  # Sidebar (fixed)
  with ui.column().classes("w-1/3 h-full border-l bg-gray-50 p-4"):
    render_control_panel()
```

---

### R3: Collapsible JSON Tree Component

**Question**: How to render interactive, collapsible JSON trees in NiceGUI?

**Findings**:
- NiceGUI has `ui.tree()` but it's designed for navigation trees, not JSON
- `ui.json_editor()` exists but is for editing, not display
- Best approach: use `ui.expansion()` recursively for nested structures
- Alternative: Use `ui.code()` with syntax highlighting (current approach) and add "expand/collapse" wrapper
- Quasar has `QTree` which NiceGUI wraps, but requires specific node format

**Decision**: Create a custom `JsonTree` component using recursive `ui.expansion()` calls. For primitives, display inline; for objects/arrays, create expandable sections.

**Code Pattern**:
```python
def render_json_tree(data: Any, label: str = "root") -> None:
  if isinstance(data, dict):
    with ui.expansion(label, icon="folder").classes("w-full"):
      for key, value in data.items():
        render_json_tree(value, key)
  elif isinstance(data, list):
    with ui.expansion(f"{label} [{len(data)}]", icon="list").classes("w-full"):
      for i, item in enumerate(data):
        render_json_tree(item, f"[{i}]")
  else:
    ui.label(f"{label}: {data}").classes("text-sm font-mono")
```

---

### R4: Event Stream Block Styling

**Question**: How to create visually distinct event blocks for different event types?

**Findings**:
- Current implementation uses `ui.card()` with border-left styling (works well)
- Can enhance with icons from Material Icons (already available via Quasar)
- Full-width blocks should use `w-full` class
- Background colors are already defined in `styles.py` - can reuse

**Decision**: Keep the existing color scheme but restructure layout:
- Full-width cards (not 50% split)
- Icon + Type badge in header row
- Content area with appropriate formatting per type
- Collapsible JSON tree for tool outputs (replacing static code block)

**Existing Colors** (from `styles.py`):
- User Query: `#E3F2FD` (light blue)
- Tool Call: `#FFF3E0` (light orange)
- Tool Output: `#E8F5E9` (light green)
- Tool Error: `#FFEBEE` (light red)
- Final Response: `#F3E5F5` (light purple)

---

### R5: Expandable Header Component

**Question**: How to implement an expandable header that pushes content down?

**Findings**:
- `ui.expansion()` is the NiceGUI primitive for collapsible content
- Can be styled to look like a header bar
- Default state can be collapsed: `ui.expansion(..., value=False)`
- Content inside will naturally push down when expanded

**Decision**: Wrap the system prompt in `ui.expansion()` styled as a header bar. Use `value=False` for collapsed by default.

**Code Pattern**:
```python
with ui.expansion(
  "System Instructions", 
  icon="psychology",
  value=False,  # Collapsed by default
).classes("w-full bg-blue-50 mb-4"):
  ui.markdown(system_prompt).classes("text-sm")
```

---

### R6: Loading States and Spinners

**Question**: How to show loading indicators during async operations?

**Findings**:
- NiceGUI provides `ui.spinner()` with various types: 'default', 'dots', 'bars', etc.
- Can wrap in conditional rendering
- `ui.notify()` can show toast messages for quick feedback
- For inline loading, add spinner next to the action button

**Decision**: Use inline spinners next to "Execute" buttons during tool execution. Add a "loading" event block in the stream while waiting.

**Code Pattern**:
```python
# During execution
with ui.row().classes("items-center gap-2"):
  ui.spinner("dots", size="sm")
  ui.label("Executing tool...").classes("text-gray-500")

# Or use a temporary event block
def render_loading_block(tool_name: str) -> ui.card:
  with ui.card().classes("w-full bg-gray-100") as card:
    with ui.row().classes("items-center gap-2"):
      ui.spinner("dots")
      ui.label(f"Executing {tool_name}...").classes("text-gray-600")
  return card
```

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Card Grid | `ui.row()` with flex-wrap | Simpler than `ui.grid()`, better control |
| Sidebar | Fixed width columns (2/3 + 1/3) | NiceGUI doesn't have true fixed sidebars |
| JSON Tree | Custom recursive `ui.expansion()` | Built-in tree not suited for JSON |
| Event Blocks | Keep existing colors, restructure layout | Colors work well, just need full-width |
| Header | `ui.expansion()` collapsed by default | Native NiceGUI component |
| Loading | Inline spinners + temporary blocks | Clear feedback without modal interruption |

## Alternatives Considered

1. **Custom Vue Components**: Rejected - adds complexity, breaks NiceGUI abstraction
2. **Third-party JSON viewer**: Rejected - would need custom JS integration
3. **Modal for System Prompt**: Rejected - user chose expandable header in clarification
4. **Chat bubble layout**: Rejected - user clarified this is an event stream, not chat

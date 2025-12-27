"""DevTools-style hierarchical JSON tree renderer.

This module provides a compact, Chrome DevTools-inspired tree component
for rendering JSON data with:
- Monospace typography with syntax coloring
- Thin vertical thread lines connecting parent-child nodes
- All nodes expanded by default
- Collapsible nodes with click-to-toggle behavior

Clean-room implementation: No code reused from json_tree.py.
"""

from enum import Enum
from typing import Any

from nicegui import ui

from adk_agent_sim.ui.components.devtools_tree.expansion_state import (
  TreeExpansionState,
)
from adk_agent_sim.ui.styles import DEVTOOLS_TREE_STYLES


class ValueType(Enum):
  """Type classification for JSON values."""

  OBJECT = "object"
  ARRAY = "array"
  STRING = "string"
  NUMBER = "number"
  BOOLEAN = "boolean"
  NULL = "null"


def _get_value_type(value: Any) -> ValueType:
  """Determine the ValueType for a given value.

  Args:
    value: Any JSON-serializable value

  Returns:
    The appropriate ValueType enum member
  """
  if value is None:
    return ValueType.NULL
  if isinstance(value, bool):  # Must check before int (bool is subclass of int)
    return ValueType.BOOLEAN
  if isinstance(value, (int, float)):
    return ValueType.NUMBER
  if isinstance(value, str):
    return ValueType.STRING
  if isinstance(value, dict):
    return ValueType.OBJECT
  if isinstance(value, list):
    return ValueType.ARRAY
  # Fallback for unknown types - render as string
  return ValueType.STRING


class DevToolsTree:
  """DevTools-style hierarchical JSON tree renderer.

  Renders JSON data with:
  - Monospace typography with syntax coloring
  - Thin vertical thread lines connecting parent-child nodes
  - All nodes expanded by default
  - Collapsible nodes with click-to-toggle behavior

  Example:
    ```python
    from adk_agent_sim.ui.components.devtools_tree import (
      DevToolsTree,
      TreeExpansionState,
    )

    data = {"name": "example", "items": [1, 2, 3]}
    tree = DevToolsTree(data, tree_id="my-tree")
    tree.render()
    ```
  """

  def __init__(
    self,
    data: Any,
    tree_id: str,
    expansion_state: TreeExpansionState | None = None,
  ) -> None:
    """Initialize the DevTools tree.

    Args:
      data: JSON-serializable data to display
      tree_id: Unique identifier for state tracking
      expansion_state: Optional expansion state manager (creates new if None)
    """
    self.data = data
    self.tree_id = tree_id
    self.expansion_state = expansion_state or TreeExpansionState(default_expanded=True)
    self._styles = DEVTOOLS_TREE_STYLES

  def render(self) -> None:
    """Render the tree component."""
    with (
      ui.element("div")
      .classes("devtools-tree")
      .style(
        f"font-family: {self._styles['font_family']}; "
        f"font-size: {self._styles['font_size']}; "
        f"line-height: {self._styles['line_height']}; "
      )
    ):
      self._render_node(
        value=self.data,
        key=None,
        path="root",
      )

  def _render_node(
    self,
    value: Any,
    key: str | int | None,
    path: str,
  ) -> None:
    """Recursively render a tree node.

    Args:
      value: The value at this node
      key: The key/index for this node (None for root)
      path: Unique path identifier for state tracking
    """
    value_type = _get_value_type(value)
    is_container = value_type in (ValueType.OBJECT, ValueType.ARRAY)
    is_expanded = self.expansion_state.is_expanded(path) if is_container else False

    with ui.element("div").classes("devtools-tree-node"):
      # Render the node row (toggle + key + value/opening brace)
      with (
        ui.element("div")
        .classes("devtools-tree-row")
        .style("display: flex; align-items: flex-start; min-height: 20px;")
      ):
        # Toggle chevron for containers
        if is_container:
          self._render_toggle(path, is_expanded)
        else:
          # Spacer for alignment
          ui.element("span").style("width: 16px; display: inline-block;")

        # Key label (if not root)
        if key is not None:
          self._render_key(key)
          ui.element("span").style(
            f"color: {self._styles['bracket_color']}; margin: 0 4px;"
          ).props('innerHTML=": "')

        # Value or container opening brace
        if is_container:
          self._render_opening_brace(value, value_type, is_expanded)
        else:
          self._render_primitive(value, value_type)

      # Render children and closing brace if expanded container
      if is_container and is_expanded:
        self._render_children_and_close(value, value_type, path)

  def _render_toggle(self, path: str, is_expanded: bool) -> None:
    """Render the expand/collapse toggle chevron.

    Args:
      path: Node path for state tracking
      is_expanded: Current expansion state
    """
    icon = "expand_more" if is_expanded else "chevron_right"
    ui.icon(icon).classes("devtools-tree-toggle").style(
      "cursor: pointer; font-size: 16px; width: 16px; color: #666; "
      "user-select: none; transition: transform 0.1s ease;"
    ).on("click", lambda _: self._toggle_node(path))

  def _toggle_node(self, path: str) -> None:
    """Handle click on toggle chevron.

    Args:
      path: Node path to toggle
    """
    self.expansion_state.toggle(path)
    # Force re-render by updating the UI
    # NiceGUI will handle the update through its reactive system

  def _render_key(self, key: str | int) -> None:
    """Render a key/property name.

    Args:
      key: The key or array index
    """
    if isinstance(key, int):
      # Array index - render as [0], [1], etc.
      display = f"[{key}]"
      color = self._styles["number_color"]
    else:
      # Object key - render as "key" with HTML entities for quotes
      escaped_key = str(key).replace("&", "&amp;")
      escaped_key = escaped_key.replace("<", "&lt;").replace(">", "&gt;")
      display = f"&quot;{escaped_key}&quot;"
      color = self._styles["key_color"]

    ui.element("span").classes("devtools-tree-key").style(f"color: {color};").props(
      f'innerHTML="{display}"'
    )

  def _render_opening_brace(
    self,
    value: Any,
    value_type: ValueType,
    is_expanded: bool,
  ) -> None:
    """Render the opening brace or collapsed preview for containers.

    Args:
      value: The container value
      value_type: OBJECT or ARRAY
      is_expanded: Whether the container is expanded
    """
    bracket_color = self._styles["bracket_color"]

    if value_type == ValueType.OBJECT:
      if is_expanded:
        ui.element("span").style(f"color: {bracket_color};").props('innerHTML="{"')
      else:
        count = len(value)
        style = "color: #999; font-size: 11px;"
        preview = f'{{...}} <span style="{style}">{count} items</span>'
        ui.element("span").style(f"color: {bracket_color};").props(
          f'innerHTML="{preview}"'
        )
    else:  # ARRAY
      if is_expanded:
        ui.element("span").style(f"color: {bracket_color};").props('innerHTML="["')
      else:
        count = len(value)
        style = "color: #999; font-size: 11px;"
        preview = f'[...] <span style="{style}">{count} items</span>'
        ui.element("span").style(f"color: {bracket_color};").props(
          f'innerHTML="{preview}"'
        )

  def _render_primitive(self, value: Any, value_type: ValueType) -> None:
    """Render a primitive value with syntax coloring.

    Args:
      value: The primitive value
      value_type: The value's type
    """
    if value_type == ValueType.STRING:
      # Escape HTML and quotes, replace newlines with visible indicator
      escaped = str(value).replace("&", "&amp;")
      escaped = escaped.replace("<", "&lt;").replace(">", "&gt;")
      # Use HTML entity for backslash to ensure it renders correctly
      escaped = escaped.replace("\n", "&#92;n")  # Show newlines as \n
      escaped = escaped.replace("\r", "&#92;r")  # Show carriage returns as \r
      escaped = escaped.replace("\t", "&#92;t")  # Show tabs as \t
      # Truncate long strings
      if len(escaped) > 100:
        escaped = escaped[:100] + "..."
      # Use HTML entities for surrounding quotes
      display = f"&quot;{escaped}&quot;"
      color = self._styles["string_color"]
    elif value_type == ValueType.NUMBER:
      display = str(value)
      color = self._styles["number_color"]
    elif value_type == ValueType.BOOLEAN:
      display = "true" if value else "false"
      color = self._styles["boolean_color"]
    elif value_type == ValueType.NULL:
      display = "null"
      color = self._styles["null_color"]
    else:
      display = str(value)
      color = self._styles["string_color"]

    ui.element("span").classes("devtools-tree-value").style(f"color: {color};").props(
      f'innerHTML="{display}"'
    )

  def _render_children_and_close(
    self,
    value: Any,
    value_type: ValueType,
    parent_path: str,
  ) -> None:
    """Render child nodes and closing brace for a container.

    Uses CSS margin-left on the children container for indentation.
    The closing brace is a sibling of the children container,
    ensuring it aligns with the opening brace.

    Args:
      value: The container (dict or list)
      value_type: OBJECT or ARRAY
      parent_path: Path of the parent node
    """
    bracket_color = self._styles["bracket_color"]
    indent = self._styles["indent_size"]

    # Children container - indented via margin-left
    with (
      ui.element("div")
      .classes("devtools-tree-children")
      .style(f"margin-left: {indent};")
    ):
      if value_type == ValueType.OBJECT:
        items = list(value.items())
        for child_key, child_value in items:
          child_path = f"{parent_path}.{child_key}"
          self._render_node(
            value=child_value,
            key=child_key,
            path=child_path,
          )
      else:  # ARRAY
        for i, child_value in enumerate(value):
          child_path = f"{parent_path}[{i}]"
          self._render_node(
            value=child_value,
            key=i,
            path=child_path,
          )

    # Closing bracket - sibling of children, same level as opening brace
    closing = "}" if value_type == ValueType.OBJECT else "]"
    ui.element("div").style(f"color: {bracket_color}; padding-left: 16px;").props(
      f'innerHTML="{closing}"'
    )

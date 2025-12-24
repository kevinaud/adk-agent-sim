"""Interactive collapsible JSON tree component."""

from __future__ import annotations

from typing import Any

from nicegui import ui

from adk_agent_sim.ui.styles import (
  JSON_TREE_KEY_STYLE,
  JSON_TREE_PRIMITIVE_COLORS,
  JSON_TREE_VALUE_STYLE,
)


class JsonTree:
  """Component for displaying JSON data as an interactive, collapsible tree."""

  MAX_STRING_LENGTH = 100
  DEFAULT_MAX_DEPTH = 2

  def __init__(
    self,
    data: Any,
    label: str = "root",
    expanded: bool = True,
    max_depth: int = DEFAULT_MAX_DEPTH,
  ) -> None:
    """
    Initialize the JSON tree.

    Args:
      data: JSON-serializable data to display
      label: Root label for the tree
      expanded: Initial expansion state
      max_depth: Maximum depth to auto-expand (default: 2)
    """
    self.data = data
    self.label = label
    self.expanded = expanded
    self.max_depth = max_depth

  def render(self) -> None:
    """Render the JSON tree component."""
    self._render_node(self.data, self.label, depth=0)

  def _render_node(self, data: Any, label: str, depth: int) -> None:
    """Recursively render a JSON node."""
    should_expand = depth < self.max_depth if self.expanded else False

    if isinstance(data, dict):
      self._render_dict(data, label, depth, should_expand)
    elif isinstance(data, list):
      self._render_list(data, label, depth, should_expand)
    else:
      self._render_primitive(data, label)

  def _render_dict(
    self,
    data: dict[str, Any],
    label: str,
    depth: int,
    expanded: bool,
  ) -> None:
    """Render a dictionary node."""
    key_count = len(data)
    header = f"{label} {{{key_count} key{'s' if key_count != 1 else ''}}}"

    if key_count == 0:
      with ui.row().classes("items-center gap-1"):
        ui.label(label).style(JSON_TREE_KEY_STYLE).classes("text-sm")
        ui.label("{ }").style(JSON_TREE_VALUE_STYLE).classes("text-sm")
      return

    with ui.expansion(header, icon="folder", value=expanded).classes("w-full text-sm"):
      for key, value in data.items():
        self._render_node(value, key, depth + 1)

  def _render_list(
    self,
    data: list[Any],
    label: str,
    depth: int,
    expanded: bool,
  ) -> None:
    """Render a list/array node."""
    item_count = len(data)
    header = f"{label} [{item_count} item{'s' if item_count != 1 else ''}]"

    if item_count == 0:
      with ui.row().classes("items-center gap-1"):
        ui.label(label).style(JSON_TREE_KEY_STYLE).classes("text-sm")
        ui.label("[ ]").style(JSON_TREE_VALUE_STYLE).classes("text-sm")
      return

    with ui.expansion(header, icon="list", value=expanded).classes("w-full text-sm"):
      for i, item in enumerate(data):
        self._render_node(item, f"[{i}]", depth + 1)

  def _render_primitive(self, data: Any, label: str) -> None:
    """Render a primitive value (string, number, boolean, null)."""
    with ui.row().classes("items-center gap-1 py-1"):
      ui.label(f"{label}:").style(JSON_TREE_KEY_STYLE).classes("text-sm")
      value_str, color = self._format_primitive(data)
      ui.label(value_str).style(f"{JSON_TREE_VALUE_STYLE} color: {color};").classes(
        "text-sm"
      )

  def _format_primitive(self, data: Any) -> tuple[str, str]:
    """Format a primitive value and return (formatted_string, color)."""
    if data is None:
      return "null", JSON_TREE_PRIMITIVE_COLORS["null"]
    elif isinstance(data, bool):
      return str(data).lower(), JSON_TREE_PRIMITIVE_COLORS["boolean"]
    elif isinstance(data, (int, float)):
      return str(data), JSON_TREE_PRIMITIVE_COLORS["number"]
    elif isinstance(data, str):
      color = JSON_TREE_PRIMITIVE_COLORS["string"]
      if len(data) > self.MAX_STRING_LENGTH:
        return f'"{data[: self.MAX_STRING_LENGTH]}..."', color
      return f'"{data}"', color
    else:
      # Fallback for other types
      return str(data), JSON_TREE_PRIMITIVE_COLORS["null"]


class TruncatedJsonTree(JsonTree):
  """JSON tree with 'Show More' functionality for large string values."""

  def __init__(
    self,
    data: Any,
    label: str = "root",
    expanded: bool = True,
    max_depth: int = JsonTree.DEFAULT_MAX_DEPTH,
    show_more_threshold: int = 100,
  ) -> None:
    """
    Initialize with truncation support.

    Args:
      data: JSON-serializable data to display
      label: Root label for the tree
      expanded: Initial expansion state
      max_depth: Maximum depth to auto-expand
      show_more_threshold: Character threshold for "Show More" button
    """
    super().__init__(data, label, expanded, max_depth)
    self.show_more_threshold = show_more_threshold

  def _render_primitive(self, data: Any, label: str) -> None:
    """Render primitive with 'Show More' for long strings."""
    if isinstance(data, str) and len(data) > self.show_more_threshold:
      self._render_truncated_string(data, label)
    else:
      super()._render_primitive(data, label)

  def _render_truncated_string(self, data: str, label: str) -> None:
    """Render a truncated string with Show More button."""
    truncated = data[: self.show_more_threshold]
    color = JSON_TREE_PRIMITIVE_COLORS["string"]
    is_expanded = {"value": False}

    with ui.column().classes("w-full gap-1"):
      with ui.row().classes("items-center gap-1"):
        ui.label(f"{label}:").style(JSON_TREE_KEY_STYLE).classes("text-sm")

      container = ui.column().classes("w-full pl-4")
      with container:

        @ui.refreshable
        def render_content() -> None:
          if is_expanded["value"]:
            ui.label(f'"{data}"').style(
              f"{JSON_TREE_VALUE_STYLE} color: {color}; white-space: pre-wrap;"
            ).classes("text-sm break-words")
            ui.button(
              "Show Less",
              icon="expand_less",
              on_click=lambda: toggle_expand(),
            ).props("flat dense size=xs").classes("text-blue-600")
          else:
            ui.label(f'"{truncated}..."').style(
              f"{JSON_TREE_VALUE_STYLE} color: {color};"
            ).classes("text-sm")
            ui.button(
              "Show More",
              icon="expand_more",
              on_click=lambda: toggle_expand(),
            ).props("flat dense size=xs").classes("text-blue-600")

        def toggle_expand() -> None:
          is_expanded["value"] = not is_expanded["value"]
          render_content.refresh()

        render_content()


def render_json_tree(
  data: Any,
  label: str = "root",
  expanded: bool = True,
  max_depth: int = 2,
  truncate: bool = False,
) -> JsonTree | TruncatedJsonTree:
  """
  Render a JSON tree component.

  Args:
    data: JSON-serializable data to display
    label: Root label for the tree
    expanded: Initial expansion state
    max_depth: Maximum depth to auto-expand
    truncate: Whether to enable truncation with "Show More" for long strings

  Returns:
    The JsonTree instance
  """
  if truncate:
    tree = TruncatedJsonTree(data, label, expanded, max_depth)
  else:
    tree = JsonTree(data, label, expanded, max_depth)
  tree.render()
  return tree

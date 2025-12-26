"""Interactive collapsible JSON tree component."""

from typing import TYPE_CHECKING, Any

from nicegui import ui

from adk_agent_sim.ui.styles import (
  JSON_TREE_KEY_STYLE,
  JSON_TREE_PRIMITIVE_COLORS,
  JSON_TREE_VALUE_STYLE,
)

if TYPE_CHECKING:
  from adk_agent_sim.ui.components.text_presenter import PresentationModeManager


class JsonTree:
  """Component for displaying JSON data as an interactive, collapsible tree."""

  MAX_STRING_LENGTH = 100
  DEFAULT_MAX_DEPTH = 2
  # Threshold for showing text presenter toggle (for longer strings)
  TEXT_PRESENTER_THRESHOLD = 50

  def __init__(
    self,
    data: Any,
    label: str = "root",
    expanded: bool = True,
    max_depth: int = DEFAULT_MAX_DEPTH,
    tree_id: str | None = None,
    mode_manager: PresentationModeManager | None = None,
  ) -> None:
    """
    Initialize the JSON tree.

    Args:
      data: JSON-serializable data to display
      label: Root label for the tree
      expanded: Initial expansion state
      max_depth: Maximum depth to auto-expand (default: 2)
      tree_id: Unique ID for tracking presentation modes within this tree
      mode_manager: Optional mode manager for text presentation toggles
    """
    self.data = data
    self.label = label
    self.expanded = expanded
    self.max_depth = max_depth
    self.tree_id = tree_id or "tree"
    self.mode_manager = mode_manager
    self._element_counter = 0

  def _get_element_id(self, label: str) -> str:
    """Generate a unique element ID for text presenter tracking."""
    self._element_counter += 1
    return f"{self.tree_id}_{label}_{self._element_counter}"

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
    """Render a primitive value (string, number, boolean, null).

    For strings longer than TEXT_PRESENTER_THRESHOLD, render with
    presentation toggle (Raw/JSON/Markdown).
    """
    # Use text presenter for longer strings
    if isinstance(data, str) and len(data) > self.TEXT_PRESENTER_THRESHOLD:
      self._render_string_with_presenter(data, label)
    else:
      with ui.row().classes("items-center gap-1 py-1"):
        ui.label(f"{label}:").style(JSON_TREE_KEY_STYLE).classes("text-sm")
        value_str, color = self._format_primitive(data)
        ui.label(value_str).style(f"{JSON_TREE_VALUE_STYLE} color: {color};").classes(
          "text-sm"
        )

  def _render_string_with_presenter(self, data: str, label: str) -> None:
    """Render a string value with presentation toggle."""
    # Import here to avoid circular import
    from adk_agent_sim.ui.components.text_presenter import render_text_presenter

    with ui.column().classes("w-full py-1"):
      ui.label(f"{label}:").style(JSON_TREE_KEY_STYLE).classes("text-sm mb-1")
      element_id = self._get_element_id(label)
      render_text_presenter(data, element_id, mode_manager=self.mode_manager)

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
    tree_id: str | None = None,
    mode_manager: PresentationModeManager | None = None,
  ) -> None:
    """
    Initialize with truncation support.

    Args:
      data: JSON-serializable data to display
      label: Root label for the tree
      expanded: Initial expansion state
      max_depth: Maximum depth to auto-expand
      show_more_threshold: Character threshold for "Show More" button
      tree_id: Unique ID for tracking presentation modes within this tree
      mode_manager: Optional mode manager for text presentation toggles
    """
    super().__init__(data, label, expanded, max_depth, tree_id, mode_manager)
    self.show_more_threshold = show_more_threshold

  def _render_primitive(self, data: Any, label: str) -> None:
    """Render primitive with text presenter for longer strings."""
    # Use text presenter for strings over threshold (replaces Show More)
    if isinstance(data, str) and len(data) > self.show_more_threshold:
      self._render_string_with_presenter(data, label)
    else:
      super()._render_primitive(data, label)


def render_json_tree(
  data: Any,
  label: str = "root",
  expanded: bool = True,
  max_depth: int = 2,
  truncate: bool = False,
  tree_id: str | None = None,
  mode_manager: PresentationModeManager | None = None,
) -> JsonTree | TruncatedJsonTree:
  """
  Render a JSON tree component.

  Args:
    data: JSON-serializable data to display
    label: Root label for the tree
    expanded: Initial expansion state
    max_depth: Maximum depth to auto-expand
    truncate: Whether to enable text presenter for long strings
    tree_id: Unique ID for tracking presentation modes
    mode_manager: Optional mode manager for text presentation toggles

  Returns:
    The JsonTree instance
  """
  if truncate:
    tree = TruncatedJsonTree(
      data, label, expanded, max_depth, tree_id=tree_id, mode_manager=mode_manager
    )
  else:
    tree = JsonTree(
      data, label, expanded, max_depth, tree_id=tree_id, mode_manager=mode_manager
    )
  tree.render()
  return tree

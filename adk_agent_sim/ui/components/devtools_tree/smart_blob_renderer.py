"""Smart blob renderer for string values with format toggles.

Provides inline expansion of structured content with RAW/JSON/MD view toggles.
Content is rendered inline, pushing the tree content down (no modals).

Clean-room implementation: No code reused from existing components.
"""

from typing import TYPE_CHECKING

from nicegui import ui

from adk_agent_sim.ui.components.devtools_tree.blob_toggle_pills import (
  BlobTogglePills,
)
from adk_agent_sim.ui.components.devtools_tree.smart_blob import (
  BlobType,
  BlobViewState,
  SmartBlobDetector,
)
from adk_agent_sim.ui.styles import DEVTOOLS_TREE_STYLES

if TYPE_CHECKING:
  from adk_agent_sim.ui.components.devtools_tree.expansion_state import (
    TreeExpansionState,
  )


class SmartBlobRenderer:
  """Renders string values with RAW/JSON/MD toggle pills.

  Provides inline expansion of structured content:
  - RAW: Monospace text with preserved whitespace
  - JSON: Recursive DevToolsTree rendering
  - MARKDOWN: Rendered Markdown via ui.markdown()

  When a string is detected as JSON or Markdown, toggle pills appear
  allowing the user to switch between views. Content expands inline,
  respecting parent indentation.

  Example:
    ```python
    from adk_agent_sim.ui.components.devtools_tree import (
      BlobType,
      BlobViewState,
      SmartBlobRenderer,
      TreeExpansionState,
    )

    blob_state = BlobViewState()
    expansion_state = TreeExpansionState()
    renderer = SmartBlobRenderer(
      value='{"key": "value"}',
      blob_id="result_0",
      detected_type=BlobType.JSON,
      blob_view_state=blob_state,
      expansion_state=expansion_state,
    )
    renderer.render()
    ```
  """

  def __init__(
    self,
    value: str,
    blob_id: str,
    detected_type: BlobType,
    blob_view_state: BlobViewState,
    expansion_state: "TreeExpansionState",
  ) -> None:
    """Initialize the smart blob renderer.

    Args:
      value: Raw string content to render
      blob_id: Unique identifier for state tracking
      detected_type: Auto-detected content type (JSON, MARKDOWN, PLAIN_TEXT)
      blob_view_state: State manager for view modes
      expansion_state: State manager for nested tree expansion
    """
    self.value = value
    self.blob_id = blob_id
    self.detected_type = detected_type
    self.blob_view_state = blob_view_state
    self.expansion_state = expansion_state
    self._styles = DEVTOOLS_TREE_STYLES
    self._container: ui.element | None = None

  def render(self) -> None:
    """Render the blob with toggle pills and content.

    For PLAIN_TEXT content, just renders the raw string.
    For JSON/MARKDOWN content, shows toggle pills and renders
    content based on the active view mode.
    """
    # Only show toggles for structured content
    has_toggles = self.detected_type != BlobType.PLAIN_TEXT

    with ui.element("div").classes("smart-blob") as container:
      self._container = container

      if has_toggles:
        # Render toggle pills
        pills = BlobTogglePills(
          blob_id=self.blob_id,
          detected_type=self.detected_type,
          state=self.blob_view_state,
          on_change=lambda _: self._refresh_content(),
        )
        pills.render()

      # Render content based on current mode
      self._render_content()

  def _refresh_content(self) -> None:
    """Refresh the content view when mode changes."""
    # NiceGUI handles reactivity through its binding system
    # For now, we rely on page refresh or parent component updates
    pass

  def _render_content(self) -> None:
    """Render content based on current view mode."""
    current_mode = self._get_current_mode()

    with ui.element("div").classes("smart-blob-content"):
      if current_mode == BlobType.PLAIN_TEXT:
        self._render_raw_view()
      elif current_mode == BlobType.JSON:
        self._render_json_view()
      elif current_mode == BlobType.MARKDOWN:
        self._render_markdown_view()
      else:
        # Fallback to raw
        self._render_raw_view()

  def _get_current_mode(self) -> BlobType:
    """Get the current view mode for this blob.

    Returns:
      The current BlobType mode (defaults based on detected type)
    """
    default_mode = BlobViewState.default_mode_for_type(self.detected_type)
    return self.blob_view_state.get_mode(self.blob_id, default_mode) or default_mode

  def _render_raw_view(self) -> None:
    """Render raw text with monospace font and preserved whitespace."""
    # Use pre-wrap to preserve whitespace and line breaks
    style = (
      f"font-family: {self._styles['font_family']}; "
      f"font-size: {self._styles['font_size']}; "
      "white-space: pre-wrap; "
      "word-break: break-word; "
      f"color: {self._styles['string_color']}; "
      "padding: 4px 0; "
    )

    # Escape HTML entities and render
    escaped = self._escape_html(self.value)
    ui.element("div").classes("smart-blob-raw").style(style).props(
      f'innerHTML="{escaped}"'
    )

  def _render_json_view(self) -> None:
    """Render parsed JSON as a DevToolsTree.

    If JSON parsing fails, falls back to raw view with error indication.
    """
    parsed, error = SmartBlobDetector.try_parse_json(self.value)

    if error is not None or parsed is None:
      # Malformed JSON - show raw with error indicator
      self._render_raw_with_error(error or "Invalid JSON")
      return

    # Import here to avoid circular dependency
    from adk_agent_sim.ui.components.devtools_tree.renderer import DevToolsTree

    # Create a nested tree for the parsed JSON
    nested_tree = DevToolsTree(
      data=parsed,
      tree_id=f"{self.blob_id}_json",
      expansion_state=self.expansion_state,
    )
    nested_tree.render()

  def _render_markdown_view(self) -> None:
    """Render Markdown content using NiceGUI's markdown component."""
    # Render using NiceGUI's built-in Markdown support
    ui.markdown(self.value).classes("smart-blob-markdown").style(
      "padding: 4px 0; font-size: 13px; line-height: 1.5; "
    )

  def _render_raw_with_error(self, error: str) -> None:
    """Render raw view with an error indicator for malformed content.

    Args:
      error: Error message describing the parsing failure
    """
    with ui.element("div").classes("smart-blob-error"):
      # Error indicator
      ui.element("div").style(
        "color: #F57C00; font-size: 11px; margin-bottom: 4px; "
      ).props(f'innerHTML="⚠ {self._escape_html(error)}"')

      # Render raw content
      self._render_raw_view()

  def _escape_html(self, text: str) -> str:
    """Escape HTML entities in text.

    Args:
      text: Raw text to escape

    Returns:
      HTML-escaped text safe for innerHTML
    """
    escaped = text.replace("&", "&amp;")
    escaped = escaped.replace("<", "&lt;")
    escaped = escaped.replace(">", "&gt;")
    escaped = escaped.replace('"', "&quot;")
    escaped = escaped.replace("\n", "<br>")
    escaped = escaped.replace("\t", "&nbsp;&nbsp;")
    return escaped


def render_smart_blob(
  value: str,
  blob_id: str,
  blob_view_state: BlobViewState | None = None,
  expansion_state: "TreeExpansionState | None" = None,
) -> None:
  """Convenience function to render a smart blob.

  Automatically detects content type and renders with appropriate toggles.

  Args:
    value: String content to render
    blob_id: Unique identifier for state tracking
    blob_view_state: Optional state manager (creates new if None)
    expansion_state: Optional expansion state (creates new if None)
  """
  from adk_agent_sim.ui.components.devtools_tree.expansion_state import (
    TreeExpansionState,
  )

  detected_type = SmartBlobDetector.detect_type(value)
  state = blob_view_state or BlobViewState()
  exp_state = expansion_state or TreeExpansionState()

  renderer = SmartBlobRenderer(
    value=value,
    blob_id=blob_id,
    detected_type=detected_type,
    blob_view_state=state,
    expansion_state=exp_state,
  )
  renderer.render()

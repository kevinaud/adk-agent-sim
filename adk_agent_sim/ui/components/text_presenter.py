"""Text presenter component with toggleable presentation modes (Raw/JSON/Markdown)."""

import ast
import json
from enum import Enum
from typing import Any

from nicegui import ui


class PresentationMode(Enum):
  """Presentation mode for text content."""

  RAW = "raw"
  JSON = "json"
  MARKDOWN = "markdown"


def _try_parse_as_data(content: str) -> tuple[Any, bool]:
  """Try to parse content as JSON or Python literal.

  Returns:
    Tuple of (parsed_data, success). If parsing fails, returns (None, False).
  """
  # First try standard JSON
  try:
    parsed = json.loads(content)
    if isinstance(parsed, (dict, list)):
      return parsed, True
  except (json.JSONDecodeError, TypeError):
    pass

  # Then try Python literal (handles single quotes, True/False/None)
  try:
    parsed = ast.literal_eval(content)
    if isinstance(parsed, (dict, list)):
      return parsed, True
  except (ValueError, SyntaxError, TypeError):
    pass

  return None, False


class PresentationModeManager:
  """Manages presentation mode state for text elements (session-only, in-memory).

  State is NOT persisted across page refreshes - resets to auto-detected default.
  """

  def __init__(self) -> None:
    """Initialize the mode manager with empty state."""
    # element_id -> PresentationMode
    self._modes: dict[str, PresentationMode] = {}

  def get_mode(self, element_id: str, default: PresentationMode) -> PresentationMode:
    """Get presentation mode for an element. Uses provided default if not set."""
    return self._modes.get(element_id, default)

  def set_mode(self, element_id: str, mode: PresentationMode) -> None:
    """Set presentation mode for an element."""
    self._modes[element_id] = mode

  def clear(self) -> None:
    """Clear all state (e.g., when starting new session)."""
    self._modes.clear()

  @staticmethod
  def detect_default_mode(content: str) -> PresentationMode:
    """Auto-detect default mode based on content.

    Returns JSON if content is valid JSON or Python literal (dict/list), else RAW.
    """
    _, success = _try_parse_as_data(content)
    return PresentationMode.JSON if success else PresentationMode.RAW


# Global mode manager instance (session-only)
_mode_manager = PresentationModeManager()


def get_mode_manager() -> PresentationModeManager:
  """Get the global presentation mode manager."""
  return _mode_manager


class TextPresenter:
  """Text content viewer with toggleable presentation modes (Raw/JSON/Markdown).

  Supports three modes:
  - Raw: Plain text, truncated at 500 chars with "Show More" link
  - JSON: Renders using DevToolsTree component (pretty-printed, collapsible)
  - Markdown: Renders using ui.markdown() for formatted display

  Auto-detection defaults to JSON if content is valid JSON, otherwise Raw.
  Selected mode persists within session (resets on page refresh).
  """

  TRUNCATE_THRESHOLD = 500

  def __init__(
    self,
    content: str,
    element_id: str,
    default_mode: PresentationMode | None = None,
    mode_manager: PresentationModeManager | None = None,
  ) -> None:
    """
    Initialize the text presenter.

    Args:
      content: Text content to display
      element_id: Unique ID for state tracking
      default_mode: Override auto-detection (default: None = auto)
      mode_manager: Optional custom mode manager (uses global if not provided)
    """
    self.content = content
    self.element_id = element_id
    self._mode_manager = mode_manager or get_mode_manager()

    # Determine initial mode
    auto_mode = PresentationModeManager.detect_default_mode(content)
    self._default_mode = default_mode if default_mode is not None else auto_mode
    self._current_mode = self._mode_manager.get_mode(element_id, self._default_mode)

    # State for "Show More" in Raw mode
    self._show_full_content = False
    self._content_container: ui.column | None = None

  def _set_mode(self, mode: PresentationMode) -> None:
    """Change the presentation mode and re-render."""
    self._current_mode = mode
    self._mode_manager.set_mode(self.element_id, mode)
    self._show_full_content = False  # Reset show more state
    if self._content_container:
      self._content_container.clear()
      with self._content_container:
        self._render_content()

  def _render_mode_toggle(self) -> None:
    """Render the mode toggle button group."""
    with ui.row().classes("items-center gap-1 mb-2"):
      # Raw button
      raw_selected = self._current_mode == PresentationMode.RAW
      ui.button(
        "Raw",
        on_click=lambda: self._set_mode(PresentationMode.RAW),
      ).props(
        f"{'flat' if not raw_selected else ''} dense size=sm"
        f"{' color=primary' if raw_selected else ''}"
      ).classes("text-xs")

      # JSON button
      json_selected = self._current_mode == PresentationMode.JSON
      ui.button(
        "JSON",
        on_click=lambda: self._set_mode(PresentationMode.JSON),
      ).props(
        f"{'flat' if not json_selected else ''} dense size=sm"
        f"{' color=primary' if json_selected else ''}"
      ).classes("text-xs")

      # Markdown button
      md_selected = self._current_mode == PresentationMode.MARKDOWN
      ui.button(
        "Markdown",
        on_click=lambda: self._set_mode(PresentationMode.MARKDOWN),
      ).props(
        f"{'flat' if not md_selected else ''} dense size=sm"
        f"{' color=primary' if md_selected else ''}"
      ).classes("text-xs")

  def _render_raw_content(self) -> None:
    """Render content in Raw mode with truncation."""
    if len(self.content) <= self.TRUNCATE_THRESHOLD or self._show_full_content:
      # Show full content
      ui.code(self.content).classes("w-full text-xs whitespace-pre-wrap")
    else:
      # Show truncated content with "Show More" link
      truncated = self.content[: self.TRUNCATE_THRESHOLD]
      ui.code(truncated + "...").classes("w-full text-xs whitespace-pre-wrap")

      def show_more() -> None:
        self._show_full_content = True
        if self._content_container:
          self._content_container.clear()
          with self._content_container:
            self._render_content()

      ui.button("Show More", on_click=show_more).props("flat dense size=xs").classes(
        "text-xs text-blue-600 mt-1"
      )

  def _render_json_content(self) -> None:
    """Render content in JSON mode.

    First tries to parse as JSON, then as Python literal.
    Shows pretty-printed JSON with 2-space indentation.
    """
    parsed, success = _try_parse_as_data(self.content)
    if success:
      # Pretty-print with 2-space indentation
      pretty_json = json.dumps(parsed, indent=2, ensure_ascii=False)
      ui.code(pretty_json, language="json").classes(
        "w-full text-xs whitespace-pre-wrap"
      )
    else:
      # Fallback to raw if parsing fails
      ui.label("Invalid JSON - showing raw content:").classes(
        "text-xs text-amber-600 mb-1"
      )
      ui.code(self.content).classes("w-full text-xs whitespace-pre-wrap")

  def _render_markdown_content(self) -> None:
    """Render content in Markdown mode."""
    ui.markdown(self.content).classes("text-sm prose prose-sm max-w-none")

  def _render_content(self) -> None:
    """Render the content area based on current mode."""
    if self._current_mode == PresentationMode.RAW:
      self._render_raw_content()
    elif self._current_mode == PresentationMode.JSON:
      self._render_json_content()
    else:  # MARKDOWN
      self._render_markdown_content()

  def render(self) -> None:
    """Render the complete text presenter component."""
    with ui.column().classes("w-full"):
      # Mode toggle buttons
      self._render_mode_toggle()

      # Content area (refreshable on mode change)
      self._content_container = ui.column().classes("w-full")
      with self._content_container:
        self._render_content()


def render_text_presenter(
  content: str,
  element_id: str,
  default_mode: PresentationMode | None = None,
  mode_manager: PresentationModeManager | None = None,
) -> TextPresenter:
  """
  Render a text presenter component.

  Args:
    content: Text content to display
    element_id: Unique ID for state tracking
    default_mode: Override auto-detection (default: None = auto)
    mode_manager: Optional custom mode manager

  Returns:
    The TextPresenter instance
  """
  presenter = TextPresenter(content, element_id, default_mode, mode_manager)
  presenter.render()
  return presenter

"""Toggle pill component for switching between blob view modes.

This module provides a compact pill-based toggle UI for switching
between PLAIN_TEXT, JSON, and MARKDOWN view modes for string content.

Clean-room implementation: No code reused from existing components.
"""

from collections.abc import Callable
from typing import Any

from nicegui import ui

from adk_agent_sim.ui.components.devtools_tree.smart_blob import (
  BlobType,
  BlobViewState,
)
from adk_agent_sim.ui.styles import SMART_BLOB_STYLES


class BlobTogglePills:
  """Toggle pill component for switching blob view modes.

  Renders a horizontal row of pill buttons [RAW] [JSON] [MD]
  with visual indication of the active mode.

  Example:
    ```python
    from adk_agent_sim.ui.components.devtools_tree import (
      BlobTogglePills,
      BlobViewState,
      BlobType,
    )

    state = BlobViewState()
    pills = BlobTogglePills(
      blob_id="my-blob",
      detected_type=BlobType.JSON,
      state=state,
      on_change=lambda mode: print(f"Switched to {mode}"),
    )
    pills.render()
    ```
  """

  def __init__(
    self,
    blob_id: str,
    detected_type: BlobType,
    state: BlobViewState,
    on_change: Callable[[BlobType], None] | None = None,
  ) -> None:
    """Initialize the toggle pills.

    Args:
      blob_id: Unique identifier for the blob
      detected_type: Detected content type of the blob
      state: BlobViewState for tracking current mode
      on_change: Optional callback when mode changes
    """
    self.blob_id = blob_id
    self.detected_type = detected_type
    self.state = state
    self.on_change = on_change
    self._styles = SMART_BLOB_STYLES
    self._container: Any = None  # NiceGUI element reference

  def get_available_modes(self) -> list[BlobType]:
    """Get the list of available view modes for this blob type.

    PLAIN_TEXT (RAW) is always available. JSON is available if blob is JSON.
    MARKDOWN is available if blob is MARKDOWN.

    Returns:
      List of BlobType values that are available as view modes
    """
    modes = [BlobType.PLAIN_TEXT]
    if self.detected_type == BlobType.JSON:
      modes.append(BlobType.JSON)
    if self.detected_type == BlobType.MARKDOWN:
      modes.append(BlobType.MARKDOWN)
    return modes

  def get_current_mode(self) -> BlobType:
    """Get the current view mode, initializing to default if needed.

    Returns:
      Current BlobType as view mode for this blob
    """
    mode = self.state.get_mode(self.blob_id)
    if mode is None:
      # Initialize to default based on detected type
      mode = BlobViewState.default_mode_for_type(self.detected_type)
      self.state.set_mode(self.blob_id, mode)
    return mode

  def _handle_click(self, mode: BlobType) -> None:
    """Handle pill click to switch mode.

    Args:
      mode: BlobType to switch to
    """
    current = self.get_current_mode()
    if mode != current:
      self.state.set_mode(self.blob_id, mode)
      if self.on_change:
        self.on_change(mode)
      # Re-render to update active states
      self._update_styles()

  def _get_pill_style(self, mode: BlobType, is_active: bool) -> str:
    """Generate CSS style for a pill button.

    Args:
      mode: The BlobType this pill represents
      is_active: Whether this pill is currently active

    Returns:
      CSS style string
    """
    s = self._styles
    base_style = (
      f"padding: {s['pill_padding']}; "
      f"border-radius: {s['pill_border_radius']}; "
      f"font-size: {s['pill_font_size']}; "
      f"font-family: {s['pill_font_family']}; "
      f"cursor: pointer; "
      f"border: 1px solid; "
      f"transition: all 0.15s ease; "
      f"user-select: none; "
    )

    if is_active:
      return (
        base_style
        + f"background-color: {s['active_bg']}; "
        + f"color: {s['active_text']}; "
        + f"border-color: {s['active_border']}; "
      )
    else:
      return (
        base_style
        + f"background-color: {s['inactive_bg']}; "
        + f"color: {s['inactive_text']}; "
        + f"border-color: {s['inactive_border']}; "
      )

  def _update_styles(self) -> None:
    """Update pill styles after mode change."""
    if self._container is not None:
      self._container.clear()
      with self._container:
        self._render_pills()

  def _render_pills(self) -> None:
    """Render the individual pill buttons."""
    current_mode = self.get_current_mode()
    available_modes = self.get_available_modes()

    for mode in available_modes:
      is_active = mode == current_mode
      label = mode.label  # Use BlobType's label property
      style = self._get_pill_style(mode, is_active)

      ui.element("span").props(f'innerHTML="{label}"').style(style).on(
        "click", lambda _, m=mode: self._handle_click(m)
      )

  def render(self) -> None:
    """Render the toggle pills component."""
    s = self._styles
    container_style = (
      f"display: inline-flex; "
      f"gap: {s['pill_container_gap']}; "
      f"margin: {s['pill_container_margin']}; "
      f"align-items: center; "
    )

    self._container = ui.element("div").style(container_style)
    with self._container:
      self._render_pills()

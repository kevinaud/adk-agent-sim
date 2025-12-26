"""Event stream component for displaying session history."""

from nicegui import ui

from adk_agent_sim.models.history import HistoryEntry
from adk_agent_sim.ui.components.event_block import LoadingBlock, render_event_block
from adk_agent_sim.ui.components.expansion_state import ExpansionStateManager
from adk_agent_sim.ui.styles import LAYOUT


class EventStream:
  """Scrollable container for history events with auto-scroll behavior."""

  def __init__(
    self,
    history: list[HistoryEntry],
    is_loading: bool = False,
    loading_tool: str | None = None,
  ) -> None:
    """
    Initialize the event stream.

    Args:
      history: List of history entries to display
      is_loading: Whether to show loading block at bottom
      loading_tool: Name of tool being executed (shown in loading block)
    """
    self.history = history
    self.is_loading = is_loading
    self.loading_tool = loading_tool
    self._container: ui.column | None = None
    self._scroll_area: ui.scroll_area | None = None
    self._auto_scroll = True
    # State manager persists expand/collapse state across refreshes
    self._state_manager = ExpansionStateManager(default_expanded=True)

  def _generate_event_id(self, entry: HistoryEntry, index: int) -> str:
    """Generate a stable event ID for state tracking."""
    # Use timestamp + type + index to ensure uniqueness
    return f"{entry.timestamp.isoformat()}_{entry.type}_{index}"

  def render(self) -> None:
    """Render the event stream component."""
    with ui.column().classes("w-full h-full"):
      # Stream header
      with ui.row().classes("w-full items-center justify-between mb-2 px-1"):
        ui.label("Event Stream").classes("text-lg font-semibold text-gray-700")
        if self.history:
          ui.badge(f"{len(self.history)} events", color="blue-3").props("outline")

      # Scrollable event container
      self._scroll_area = (
        ui.scroll_area()
        .style(f"height: {LAYOUT['event_stream_height']}")
        .classes("w-full border rounded-lg bg-white")
      )

      with self._scroll_area:
        self._container = ui.column().classes("w-full gap-2 p-3")
        with self._container:
          self._render_events()

  def _render_events(self) -> None:
    """Render all history entries."""
    if not self.history:
      self._render_empty_state()
      return

    # Render each history entry with state tracking
    for index, entry in enumerate(self.history):
      event_id = self._generate_event_id(entry, index)
      render_event_block(
        entry,
        expanded=True,
        event_id=event_id,
        state_manager=self._state_manager,
      )

    # Show loading block if executing
    if self.is_loading and self.loading_tool:
      loading = LoadingBlock(self.loading_tool)
      loading.render()

    # Trigger auto-scroll to bottom
    if self._auto_scroll and self._scroll_area:
      self._scroll_to_bottom()

  def _render_empty_state(self) -> None:
    """Render empty state when no history exists."""
    with ui.column().classes("w-full items-center justify-center py-12"):
      ui.icon("history", size="3xl").classes("text-gray-300 mb-4")
      ui.label("No events yet").classes("text-lg text-gray-500 font-medium")
      ui.label("Events will appear here as the simulation progresses.").classes(
        "text-sm text-gray-400"
      )

  def _scroll_to_bottom(self) -> None:
    """Scroll the event stream to the bottom."""
    if self._scroll_area:
      self._scroll_area.scroll_to(percent=1.0)

  def refresh(
    self,
    history: list[HistoryEntry],
    is_loading: bool = False,
    loading_tool: str | None = None,
  ) -> None:
    """
    Refresh the event stream with new data.

    Args:
      history: Updated history entries
      is_loading: Whether currently loading
      loading_tool: Tool being executed
    """
    self.history = history
    self.is_loading = is_loading
    self.loading_tool = loading_tool

    if self._container:
      self._container.clear()
      with self._container:
        self._render_events()


class RefreshableEventStream:
  """Event stream with built-in refresh capability using NiceGUI's refreshable."""

  def __init__(self) -> None:
    """Initialize the refreshable event stream."""
    self._history: list[HistoryEntry] = []
    self._is_loading = False
    self._loading_tool: str | None = None
    self._scroll_area: ui.scroll_area | None = None
    # State manager persists expand/collapse state across refreshes
    self._state_manager = ExpansionStateManager(default_expanded=True)

  def _generate_event_id(self, entry: HistoryEntry, index: int) -> str:
    """Generate a stable event ID for state tracking."""
    return f"{entry.timestamp.isoformat()}_{entry.type}_{index}"

  def set_state(
    self,
    history: list[HistoryEntry],
    is_loading: bool = False,
    loading_tool: str | None = None,
  ) -> None:
    """
    Update the stream state and refresh.

    Args:
      history: New history entries
      is_loading: Loading state
      loading_tool: Tool being executed
    """
    self._history = history
    self._is_loading = is_loading
    self._loading_tool = loading_tool
    self._render_stream.refresh()

  @ui.refreshable
  def _render_stream(self) -> None:
    """Render the stream content (refreshable)."""
    with ui.column().classes("w-full gap-2 p-3"):
      if not self._history:
        # Empty state
        with ui.column().classes("w-full items-center justify-center py-12"):
          ui.icon("history", size="3xl").classes("text-gray-300 mb-4")
          ui.label("No events yet").classes("text-lg text-gray-500 font-medium")
          ui.label("Events will appear here as the simulation progresses.").classes(
            "text-sm text-gray-400"
          )
        return

      # Render events with state tracking
      for index, entry in enumerate(self._history):
        event_id = self._generate_event_id(entry, index)
        render_event_block(
          entry,
          expanded=True,
          event_id=event_id,
          state_manager=self._state_manager,
        )

      # Loading block
      if self._is_loading and self._loading_tool:
        loading = LoadingBlock(self._loading_tool)
        loading.render()

  def render(self) -> None:
    """Render the complete event stream."""
    with ui.column().classes("w-full h-full"):
      # Header
      with ui.row().classes("w-full items-center justify-between mb-2 px-1"):
        ui.label("Event Stream").classes("text-lg font-semibold text-gray-700")

        @ui.refreshable
        def render_badge() -> None:
          if self._history:
            ui.badge(f"{len(self._history)} events", color="blue-3").props("outline")

        render_badge()

      # Scroll area
      self._scroll_area = (
        ui.scroll_area()
        .style(f"height: {LAYOUT['event_stream_height']}")
        .classes("w-full border rounded-lg bg-white")
      )

      with self._scroll_area:
        self._render_stream()  # pyright: ignore[reportCallIssue]


def render_event_stream(
  history: list[HistoryEntry],
  is_loading: bool = False,
  loading_tool: str | None = None,
) -> EventStream:
  """
  Render an event stream component.

  Args:
    history: List of history entries
    is_loading: Whether to show loading state
    loading_tool: Name of tool being executed

  Returns:
    The EventStream instance
  """
  stream = EventStream(history, is_loading, loading_tool)
  stream.render()
  return stream

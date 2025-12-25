"""History panel component for displaying session history."""

from __future__ import annotations

import json

from nicegui import ui

from adk_agent_sim.models.history import (
  FinalResponse,
  HistoryEntry,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.ui.styles import (
  HISTORY_BORDER_COLORS,
  HISTORY_COLORS,
  HISTORY_ENTRY_STYLE,
  HISTORY_PANEL_HEIGHT,
)


class HistoryPanel:
  """Component for displaying the session history."""

  def __init__(self, history: list[HistoryEntry]) -> None:
    """
    Initialize the history panel.

    Args:
      history: List of history entries to display
    """
    self.history = history
    self._container: ui.column | None = None

  def render(self) -> None:
    """Render the history panel component."""
    with ui.card().classes("w-full"):
      ui.label("Session History").classes("text-lg font-semibold mb-4")

      with ui.scroll_area().style(f"height: {HISTORY_PANEL_HEIGHT}"):
        self._container = ui.column().classes("w-full gap-2")
        self._render_entries()

  def _render_entries(self) -> None:
    """Render all history entries."""
    if self._container is None:
      return

    with self._container:
      if not self.history:
        ui.label("No history yet").classes("text-gray-500 italic")
        return

      for entry in self.history:
        self._render_entry(entry)

  def _render_entry(self, entry: HistoryEntry) -> None:
    """Render a single history entry with appropriate styling."""
    entry_type = entry.type
    bg_color = HISTORY_COLORS.get(entry_type, "#F5F5F5")
    border_color = HISTORY_BORDER_COLORS.get(entry_type, "#9E9E9E")

    style = (
      f"{HISTORY_ENTRY_STYLE} background-color: {bg_color}; "
      f"border-left-color: {border_color};"
    )

    with ui.card().style(style).classes("w-full"):
      # Entry header with type and timestamp
      with ui.row().classes("w-full items-center justify-between mb-2"):
        self._render_entry_badge(entry_type)
        timestamp_str = entry.timestamp.strftime("%H:%M:%S")
        ui.label(timestamp_str).classes("text-xs text-gray-500")

      # Entry content based on type
      if isinstance(entry, UserQuery):
        self._render_user_query(entry)
      elif isinstance(entry, ToolCall):
        self._render_tool_call(entry)
      elif isinstance(entry, ToolOutput):
        self._render_tool_output(entry)
      elif isinstance(entry, ToolError):
        self._render_tool_error(entry)
      else:
        self._render_final_response(entry)

  def _render_entry_badge(self, entry_type: str) -> None:
    """Render a badge for the entry type."""
    labels = {
      "user_query": ("User Query", "blue"),
      "tool_call": ("Tool Call", "orange"),
      "tool_output": ("Tool Output", "green"),
      "tool_error": ("Tool Error", "red"),
      "final_response": ("Final Response", "purple"),
    }
    label, color = labels.get(entry_type, (entry_type, "gray"))
    ui.badge(label, color=color)

  def _render_user_query(self, entry: UserQuery) -> None:
    """Render a user query entry."""
    ui.label(entry.content).classes("text-sm")

  def _render_tool_call(self, entry: ToolCall) -> None:
    """Render a tool call entry."""
    ui.label(f"Tool: {entry.tool_name}").classes("font-medium")

    if entry.arguments:
      with ui.expansion("Arguments", icon="code").classes("w-full"):
        ui.code(
          json.dumps(entry.arguments, indent=2, default=str),
          language="json",
        ).classes("w-full text-xs")

  def _render_tool_output(self, entry: ToolOutput) -> None:
    """Render a tool output entry."""
    duration_str = f"{entry.duration_ms:.0f}ms"
    ui.label(f"Duration: {duration_str}").classes("text-xs text-gray-500 mb-1")

    # Truncate large outputs for display
    result_str = json.dumps(entry.result, indent=2, default=str)
    max_display_len = 1000

    if len(result_str) > max_display_len:
      with ui.expansion("Result (truncated)", icon="code").classes("w-full"):
        ui.code(
          result_str[:max_display_len] + "\n... (truncated)",
          language="json",
        ).classes("w-full text-xs")
    else:
      with ui.expansion("Result", icon="code").classes("w-full"):
        ui.code(result_str, language="json").classes("w-full text-xs")

  def _render_tool_error(self, entry: ToolError) -> None:
    """Render a tool error entry."""
    duration_str = f"{entry.duration_ms:.0f}ms"
    ui.label(f"Duration: {duration_str}").classes("text-xs text-gray-500 mb-1")

    ui.label(f"{entry.error_type}: {entry.error_message}").classes(
      "text-sm text-red-700"
    )

    if entry.traceback:
      with ui.expansion("Traceback", icon="error").classes("w-full"):
        ui.code(entry.traceback, language="python").classes("w-full text-xs")

  def _render_final_response(self, entry: FinalResponse) -> None:
    """Render a final response entry."""
    ui.label(entry.content).classes("text-sm")

  def refresh(self, history: list[HistoryEntry]) -> None:
    """Refresh the history display with new entries."""
    self.history = history
    if self._container:
      self._container.clear()
      with self._container:
        self._render_entries()


def render_history_panel(history: list[HistoryEntry]) -> HistoryPanel:
  """
  Render a history panel component.

  Args:
    history: List of history entries

  Returns:
    HistoryPanel instance
  """
  panel = HistoryPanel(history)
  panel.render()
  return panel

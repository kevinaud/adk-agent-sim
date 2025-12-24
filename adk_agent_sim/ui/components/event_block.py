"""Event block components for rendering history entries in the event stream."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from nicegui import ui

from adk_agent_sim.models.history import (
  FinalResponse,
  HistoryEntry,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.ui.components.json_tree import render_json_tree
from adk_agent_sim.ui.components.text_presenter import render_text_presenter
from adk_agent_sim.ui.styles import (
  EVENT_BLOCK_STYLE,
  EVENT_ICONS,
  HISTORY_BORDER_COLORS,
  HISTORY_COLORS,
)


class EventBlock(ABC):
  """Abstract base class for event blocks in the event stream."""

  def __init__(self, entry: HistoryEntry, expanded: bool = False) -> None:
    """
    Initialize the event block.

    Args:
      entry: The history entry to render
      expanded: Initial expansion state for collapsible content
    """
    self.entry = entry
    self.expanded = expanded
    self._card: ui.card | None = None

  @abstractmethod
  def render_content(self) -> None:
    """Render the block-specific content. Implemented by subclasses."""
    pass

  def _expand_all(self) -> None:
    """Expand all collapsible sections in this event block."""
    if self._card:
      # Use JavaScript to expand all q-expansion-item elements
      self._card.run_method(
        "querySelectorAll",
        ".q-expansion-item:not(.q-expansion-item--expanded) "
        "> .q-expansion-item__container > .q-item",
      )
      ui.run_javascript(
        f'''
        document.querySelectorAll(
          '[id="{self._card.id}"] .q-expansion-item:not(.q-expansion-item--expanded)'
        ).forEach(el => el.querySelector('.q-item')?.click());
        '''
      )

  def _collapse_all(self) -> None:
    """Collapse all collapsible sections in this event block."""
    if self._card:
      ui.run_javascript(
        f'''
        document.querySelectorAll(
          '[id="{self._card.id}"] .q-expansion-item--expanded'
        ).forEach(el => el.querySelector('.q-item')?.click());
        '''
      )

  def render(self) -> None:
    """Render the complete event block."""
    entry_type = self.entry.type
    bg_color = HISTORY_COLORS.get(entry_type, "#F5F5F5")
    border_color = HISTORY_BORDER_COLORS.get(entry_type, "#9E9E9E")
    icon = EVENT_ICONS.get(entry_type, "help")

    style = (
      f"{EVENT_BLOCK_STYLE} background-color: {bg_color}; "
      f"border-left-color: {border_color};"
    )

    self._card = ui.card().style(style).classes("w-full")
    with self._card:
      # Header row with icon, badge, expand/collapse buttons, and timestamp
      with ui.row().classes("w-full items-center justify-between mb-2"):
        with ui.row().classes("items-center gap-2"):
          ui.icon(icon).classes("text-lg")
          self._render_badge(entry_type)

        with ui.row().classes("items-center gap-1"):
          # Expand/Collapse All buttons
          ui.button(
            icon="unfold_more",
            on_click=self._expand_all,
          ).props("flat dense size=xs").tooltip("Expand All")
          ui.button(
            icon="unfold_less",
            on_click=self._collapse_all,
          ).props("flat dense size=xs").tooltip("Collapse All")

          timestamp_str = self.entry.timestamp.strftime("%H:%M:%S")
          ui.label(timestamp_str).classes("text-xs text-gray-500 ml-2")

      # Content area
      self.render_content()

  def _render_badge(self, entry_type: str) -> None:
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


class UserInputBlock(EventBlock):
  """Event block for user query entries."""

  def __init__(self, entry: UserQuery, expanded: bool = False) -> None:
    """Initialize user input block."""
    super().__init__(entry, expanded)
    self.entry: UserQuery = entry

  def render_content(self) -> None:
    """Render user query content."""
    ui.label(self.entry.content).classes("text-sm")


class ToolExecutionBlock(EventBlock):
  """Event block for tool call and output entries."""

  def __init__(
    self,
    call: ToolCall,
    output: ToolOutput | None = None,
    expanded: bool = False,
  ) -> None:
    """
    Initialize tool execution block.

    Args:
      call: The tool call entry
      output: Optional tool output entry
      expanded: Initial expansion state
    """
    super().__init__(call, expanded)
    self.call: ToolCall = call
    self.output = output

  def render_content(self) -> None:
    """Render tool call and output content."""
    # Tool name
    ui.label(f"Tool: {self.call.tool_name}").classes("font-medium mb-2")

    # Arguments section
    if self.call.arguments:
      with ui.expansion("Arguments", icon="code", value=self.expanded).classes(
        "w-full mb-2"
      ):
        render_json_tree(
          self.call.arguments,
          label="args",
          expanded=True,
          max_depth=2,
        )

    # Result section (if output available)
    if self.output:
      duration_str = f"{self.output.duration_ms:.0f}ms"
      ui.label(f"Duration: {duration_str}").classes("text-xs text-gray-500 mb-1")

      with ui.expansion("Result", icon="check_circle", value=self.expanded).classes(
        "w-full"
      ):
        # Use TextPresenter for string results (supports Raw/JSON/Markdown toggle)
        if isinstance(self.output.result, str):
          element_id = f"tool_exec_{self.call.call_id}_result"
          render_text_presenter(self.output.result, element_id)
        else:
          render_json_tree(
            self.output.result,
            label="result",
            expanded=True,
            max_depth=2,
            truncate=True,
          )


class ToolCallBlock(EventBlock):
  """Event block for tool call entries (without output)."""

  def __init__(self, entry: ToolCall, expanded: bool = False) -> None:
    """Initialize tool call block."""
    super().__init__(entry, expanded)
    self.entry: ToolCall = entry

  def render_content(self) -> None:
    """Render tool call content."""
    ui.label(f"Tool: {self.entry.tool_name}").classes("font-medium mb-2")

    if self.entry.arguments:
      with ui.expansion("Arguments", icon="code", value=self.expanded).classes(
        "w-full"
      ):
        render_json_tree(
          self.entry.arguments,
          label="args",
          expanded=True,
          max_depth=2,
        )


class ToolOutputBlock(EventBlock):
  """Event block for tool output entries."""

  def __init__(self, entry: ToolOutput, expanded: bool = False) -> None:
    """Initialize tool output block."""
    super().__init__(entry, expanded)
    self.entry: ToolOutput = entry

  def render_content(self) -> None:
    """Render tool output content."""
    duration_str = f"{self.entry.duration_ms:.0f}ms"
    ui.label(f"Duration: {duration_str}").classes("text-xs text-gray-500 mb-1")

    with ui.expansion("Result", icon="check_circle", value=self.expanded).classes(
      "w-full"
    ):
      # Use TextPresenter for string results (supports Raw/JSON/Markdown toggle)
      if isinstance(self.entry.result, str):
        element_id = f"tool_output_{self.entry.call_id}_result"
        render_text_presenter(self.entry.result, element_id)
      else:
        render_json_tree(
          self.entry.result,
          label="result",
          expanded=True,
          max_depth=2,
          truncate=True,
        )


class ToolErrorBlock(EventBlock):
  """Event block for tool error entries."""

  def __init__(self, entry: ToolError, expanded: bool = False) -> None:
    """Initialize tool error block."""
    super().__init__(entry, expanded)
    self.entry: ToolError = entry

  def render_content(self) -> None:
    """Render tool error content."""
    duration_str = f"{self.entry.duration_ms:.0f}ms"
    ui.label(f"Duration: {duration_str}").classes("text-xs text-gray-500 mb-1")

    # Error message
    ui.label(f"{self.entry.error_type}: {self.entry.error_message}").classes(
      "text-sm text-red-700 font-medium mb-2"
    )

    # Collapsible traceback
    if self.entry.traceback:
      with ui.expansion("Traceback", icon="error", value=self.expanded).classes(
        "w-full"
      ):
        ui.code(self.entry.traceback, language="python").classes("w-full text-xs")


class AgentResponseBlock(EventBlock):
  """Event block for final response entries."""

  def __init__(self, entry: FinalResponse, expanded: bool = False) -> None:
    """Initialize agent response block."""
    super().__init__(entry, expanded)
    self.entry: FinalResponse = entry

  def render_content(self) -> None:
    """Render final response content."""
    content = self.entry.content

    # Try to parse as JSON for structured display
    try:
      parsed = json.loads(content)
      if isinstance(parsed, (dict, list)):
        render_json_tree(
          parsed,
          label="response",
          expanded=True,
          max_depth=3,
        )
        return
    except (json.JSONDecodeError, TypeError):
      pass

    # Plain text display
    ui.markdown(content).classes("text-sm")


class LoadingBlock:
  """Temporary block shown during tool execution."""

  def __init__(self, tool_name: str, elapsed_ms: int = 0) -> None:
    """
    Initialize loading block.

    Args:
      tool_name: Name of the tool being executed
      elapsed_ms: Elapsed time in milliseconds
    """
    self.tool_name = tool_name
    self.elapsed_ms = elapsed_ms

  def render(self) -> ui.card:
    """Render the loading block."""
    with ui.card().classes("w-full bg-gray-100") as card:
      with ui.row().classes("items-center gap-3 p-2"):
        ui.spinner("dots", size="sm")
        ui.label(f"Executing {self.tool_name}...").classes("text-gray-600")
        if self.elapsed_ms > 0:
          ui.label(f"({self.elapsed_ms}ms)").classes("text-xs text-gray-400")
    return card


def create_event_block(entry: HistoryEntry, expanded: bool = False) -> EventBlock:
  """
  Factory function to create the appropriate EventBlock for a history entry.

  Args:
    entry: The history entry
    expanded: Initial expansion state

  Returns:
    The appropriate EventBlock subclass instance
  """
  if isinstance(entry, UserQuery):
    return UserInputBlock(entry, expanded)
  elif isinstance(entry, ToolCall):
    return ToolCallBlock(entry, expanded)
  elif isinstance(entry, ToolOutput):
    return ToolOutputBlock(entry, expanded)
  elif isinstance(entry, ToolError):
    return ToolErrorBlock(entry, expanded)
  else:
    # FinalResponse is the only remaining type in the union
    return AgentResponseBlock(entry, expanded)


def render_event_block(
  entry: HistoryEntry,
  expanded: bool = False,
  event_id: str | None = None,
  state_manager: object | None = None,
) -> None:
  """
  Render an event block for a history entry.

  Args:
    entry: The history entry to render
    expanded: Initial expansion state for collapsible content
    event_id: Optional unique ID for state tracking
    state_manager: Optional state manager for expand/collapse persistence
  """
  # Note: event_id and state_manager are accepted for API compatibility
  # but not yet used - expand/collapse state is managed per-block currently
  block = create_event_block(entry, expanded)
  block.render()

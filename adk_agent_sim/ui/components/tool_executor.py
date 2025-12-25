"""Tool executor component with form, timer, and cancel functionality."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable

from nicegui import ui

from adk_agent_sim.ui.components.schema_form import (
  render_schema_form,
  validate_required_fields,
)
from adk_agent_sim.ui.styles import (
  DANGER_BUTTON_STYLE,
  PRIMARY_BUTTON_STYLE,
  TIMER_STYLE,
)

if TYPE_CHECKING:
  from google.genai.types import FunctionDeclaration

  from adk_agent_sim.execution.tool_runner import ToolRunner


class ToolExecutor:
  """Component for executing a tool with form input."""

  def __init__(
    self,
    tool_name: str,
    declaration: FunctionDeclaration | None,
    tool_runner: ToolRunner,
    on_execute: Callable[[str, dict[str, Any]], Any],
    on_cancel: Callable[[], None],
  ) -> None:
    """
    Initialize the tool executor component.

    Args:
      tool_name: Name of the tool to execute
      declaration: Tool's FunctionDeclaration for schema
      tool_runner: ToolRunner instance for execution status
      on_execute: Callback when execute is clicked (tool_name, arguments)
      on_cancel: Callback when cancel is clicked
    """
    self.tool_name = tool_name
    self.declaration = declaration
    self.tool_runner = tool_runner
    self.on_execute = on_execute
    self.on_cancel = on_cancel

    self._form_values: dict[str, Any] = {}
    self._timer_label: ui.label | None = None
    self._timer_task: asyncio.Task[None] | None = None
    self._execute_button: ui.button | None = None
    self._cancel_button: ui.button | None = None
    self._spinner: ui.spinner | None = None
    self._executing_label: ui.label | None = None

  def render(self) -> None:
    """Render the tool executor component."""
    with ui.card().classes("w-full"):
      # Header
      ui.label(f"Execute: {self.tool_name}").classes("text-lg font-semibold mb-2")

      # Tool description
      if self.declaration and self.declaration.description:
        ui.label(self.declaration.description).classes("text-sm text-gray-600 mb-4")

      # Parameter form
      if self.declaration and self.declaration.parameters:
        ui.label("Parameters").classes("font-medium mb-2")
        self._form_values = render_schema_form(
          self.declaration.parameters,
          on_change=self._on_form_change,
        )
      else:
        ui.label("No parameters required").classes("text-gray-500 italic")

      ui.separator()

      # Execution status row (hidden initially)
      with ui.row().classes("w-full items-center gap-2 py-2") as status_row:
        self._spinner = ui.spinner("dots", size="sm")
        self._executing_label = ui.label("Executing...").classes("text-gray-600")
      status_row.set_visibility(False)
      self._status_row = status_row

      # Action row with timer
      with ui.row().classes("w-full items-center justify-between mt-4"):
        # Timer display
        with ui.row().classes("items-center gap-2"):
          ui.icon("timer").classes("text-gray-500")
          self._timer_label = ui.label("0.00s").style(TIMER_STYLE)

        # Buttons
        with ui.row().classes("gap-2"):
          self._cancel_button = (
            ui.button(
              "Cancel",
              icon="cancel",
              on_click=self._handle_cancel,
            )
            .style(DANGER_BUTTON_STYLE)
            .props("flat")
          )
          self._cancel_button.set_visibility(False)

          self._execute_button = ui.button(
            "Execute",
            icon="play_arrow",
            on_click=self._handle_execute,
          ).style(PRIMARY_BUTTON_STYLE)

  def _on_form_change(self, values: dict[str, Any]) -> None:
    """Handle form value changes."""
    self._form_values.update(values)

  async def _handle_execute(self) -> None:
    """Handle execute button click."""
    # Validate required fields
    if self.declaration and self.declaration.parameters:
      errors = validate_required_fields(
        self.declaration.parameters,
        self._form_values,
      )
      if errors:
        ui.notify(
          f"Validation errors: {', '.join(errors)}",
          type="negative",
        )
        return

    # Show executing state
    if self._execute_button:
      self._execute_button.set_visibility(False)
    if self._cancel_button:
      self._cancel_button.set_visibility(True)
    if hasattr(self, "_status_row") and self._status_row:
      self._status_row.set_visibility(True)

    # Start timer
    self._start_timer()

    try:
      # Execute tool (this is async)
      await self.on_execute(self.tool_name, self._form_values)
    finally:
      # Stop timer and restore buttons
      self._stop_timer()
      if self._execute_button:
        self._execute_button.set_visibility(True)
      if self._cancel_button:
        self._cancel_button.set_visibility(False)
      if hasattr(self, "_status_row") and self._status_row:
        self._status_row.set_visibility(False)

  def _handle_cancel(self) -> None:
    """Handle cancel button click."""
    self.on_cancel()
    ui.notify("Cancellation requested...", type="warning")

  def _start_timer(self) -> None:
    """Start the execution timer."""

    async def update_timer() -> None:
      while self.tool_runner.is_running:
        elapsed_s = self.tool_runner.elapsed_ms / 1000
        if self._timer_label:
          self._timer_label.set_text(f"{elapsed_s:.2f}s")
        await asyncio.sleep(0.1)

    self._timer_task = asyncio.create_task(update_timer())

  def _stop_timer(self) -> None:
    """Stop the execution timer."""
    if self._timer_task and not self._timer_task.done():
      self._timer_task.cancel()
    # Show final time
    if self._timer_label:
      elapsed_s = self.tool_runner.elapsed_ms / 1000
      self._timer_label.set_text(f"{elapsed_s:.2f}s")


def render_tool_executor(
  tool_name: str,
  declaration: FunctionDeclaration | None,
  tool_runner: ToolRunner,
  on_execute: Callable[[str, dict[str, Any]], Any],
  on_cancel: Callable[[], None],
) -> ToolExecutor:
  """
  Render a tool executor component.

  Args:
    tool_name: Name of the tool
    declaration: Tool's FunctionDeclaration
    tool_runner: ToolRunner instance
    on_execute: Execute callback
    on_cancel: Cancel callback

  Returns:
    ToolExecutor instance
  """
  executor = ToolExecutor(
    tool_name=tool_name,
    declaration=declaration,
    tool_runner=tool_runner,
    on_execute=on_execute,
    on_cancel=on_cancel,
  )
  executor.render()
  return executor

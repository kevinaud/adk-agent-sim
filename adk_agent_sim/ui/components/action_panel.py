"""Action panel component for tool selection and final response."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from nicegui import ui

from adk_agent_sim.ui.components.tool_catalog import render_selectable_tool_catalog
from adk_agent_sim.ui.styles import PRIMARY_BUTTON_STYLE, SUCCESS_BUTTON_STYLE

if TYPE_CHECKING:
  from google.adk.tools import BaseTool


class ActionPanel:
  """Component for selecting actions (tool calls or final response)."""

  def __init__(
    self,
    tools: list[BaseTool],
    on_tool_select: Callable[[str], None],
    on_final_response: Callable[[str], Awaitable[None]],
    has_output_schema: bool = False,
    output_schema: type | None = None,
  ) -> None:
    """
    Initialize the action panel.

    Args:
      tools: List of available tools
      on_tool_select: Callback when a tool is selected
      on_final_response: Async callback when final response is submitted
      has_output_schema: Whether the agent has an output schema
      output_schema: The Pydantic model for output schema (if any)
    """
    self.tools = tools
    self.on_tool_select = on_tool_select
    self.on_final_response = on_final_response
    self.has_output_schema = has_output_schema
    self.output_schema = output_schema

    self._selected_tool: str | None = None
    self._response_text: str = ""
    self._form_values: dict[str, Any] = {}

  def render(self) -> None:
    """Render the action panel component."""
    with ui.card().classes("w-full"):
      ui.label("Choose Action").classes("text-lg font-semibold mb-4")

      with ui.tabs().classes("w-full") as tabs:
        tool_tab = ui.tab("Call Tool", icon="build")
        response_tab = ui.tab("Final Response", icon="send")

      with ui.tab_panels(tabs, value=tool_tab).classes("w-full"):
        # Tool selection panel
        with ui.tab_panel(tool_tab):
          self._render_tool_panel()

        # Final response panel
        with ui.tab_panel(response_tab):
          self._render_response_panel()

  def _render_tool_panel(self) -> None:
    """Render the tool selection panel using ToolCatalog."""
    if not self.tools:
      ui.label("No tools available").classes("text-gray-500 italic")
      return

    # Track selected tool within this panel
    self._selected_tool = None

    @ui.refreshable
    def render_catalog() -> None:
      def on_tool_click(tool_name: str) -> None:
        self._selected_tool = tool_name
        render_catalog.refresh()

      render_selectable_tool_catalog(
        tools=self.tools,
        on_tool_select=on_tool_click,
        selected_tool=self._selected_tool,
      )

    render_catalog()

    def on_select_click() -> None:
      if self._selected_tool:
        self.on_tool_select(self._selected_tool)
      else:
        ui.notify("Please select a tool first", type="warning")

    ui.button(
      "Select Tool",
      icon="arrow_forward",
      on_click=on_select_click,
    ).style(PRIMARY_BUTTON_STYLE).classes("mt-4")

  def _render_response_panel(self) -> None:
    """Render the final response panel."""
    ui.label("Enter your final response:").classes("mb-2")

    if self.has_output_schema and self.output_schema:
      # Render structured form for output schema
      ui.label("This agent expects structured output. Fill in the form below.").classes(
        "text-sm text-amber-600 mb-2"
      )

      from adk_agent_sim.ui.components.schema_form import (
        pydantic_to_schema,
        render_schema_form,
        validate_required_fields,
      )

      # Convert Pydantic model to Schema
      schema = pydantic_to_schema(self.output_schema)

      def on_form_change(values: dict[str, Any]) -> None:
        self._form_values = values

      self._form_values = render_schema_form(schema, on_form_change)

      async def on_submit_structured() -> None:
        errors = validate_required_fields(schema, self._form_values)
        if errors:
          ui.notify(f"Validation errors: {', '.join(errors)}", type="warning")
          return
        # Validate against Pydantic model
        try:
          if self.output_schema:
            self.output_schema(**self._form_values)  # Validate
          response_str = json.dumps(self._form_values)
          await self.on_final_response(response_str)
        except Exception as e:
          ui.notify(f"Validation error: {e}", type="negative")

      ui.button(
        "Submit Response",
        icon="send",
        on_click=on_submit_structured,
      ).style(SUCCESS_BUTTON_STYLE)
    else:
      # Plain text response
      if self.has_output_schema:
        ui.label(
          "Note: This agent has an output schema. "
          "Your response should match the expected format."
        ).classes("text-sm text-amber-600 mb-2")

      response_input = ui.textarea(
        label="Final Response",
        placeholder="Enter the agent's final response to the user...",
      ).classes("w-full mb-4")
      response_input.props("rows=4")

      async def on_submit_click() -> None:
        if response_input.value:
          await self.on_final_response(response_input.value)
        else:
          ui.notify("Please enter a response", type="warning")

      ui.button(
        "Submit Response",
        icon="send",
        on_click=on_submit_click,
      ).style(SUCCESS_BUTTON_STYLE)


def render_action_panel(
  tools: list[BaseTool],
  on_tool_select: Callable[[str], None],
  on_final_response: Callable[[str], Awaitable[None]],
  has_output_schema: bool = False,
  output_schema: type | None = None,
) -> ActionPanel:
  """
  Render the action panel component.

  Args:
    tools: List of available tools
    on_tool_select: Tool selection callback
    on_final_response: Final response async callback
    has_output_schema: Whether agent has output schema
    output_schema: The Pydantic model for output schema (if any)

  Returns:
    ActionPanel instance
  """
  panel = ActionPanel(
    tools=tools,
    on_tool_select=on_tool_select,
    on_final_response=on_final_response,
    has_output_schema=has_output_schema,
    output_schema=output_schema,
  )
  panel.render()
  return panel

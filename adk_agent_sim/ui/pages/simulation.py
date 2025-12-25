"""Main simulation page component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nicegui import ui

from adk_agent_sim.models.session import SessionState
from adk_agent_sim.ui.components.action_panel import render_action_panel
from adk_agent_sim.ui.components.event_stream import EventStream
from adk_agent_sim.ui.components.system_prompt import render_system_prompt
from adk_agent_sim.ui.components.tool_executor import render_tool_executor
from adk_agent_sim.ui.styles import (
  CONTROL_PANEL_CLASSES,
  LAYOUT,
  PRIMARY_BUTTON_STYLE,
  SUCCESS_BUTTON_STYLE,
)

if TYPE_CHECKING:
  from adk_agent_sim.controller import SimulationController


class SimulationPage:
  """Main page for running the agent simulation with 2/3 + 1/3 layout."""

  def __init__(self, controller: SimulationController) -> None:
    """
    Initialize the simulation page.

    Args:
      controller: The simulation controller
    """
    self.controller = controller
    self._event_stream: EventStream | None = None
    self._sidebar_content: ui.column | None = None
    self._selected_tool: str | None = None
    self._is_executing: bool = False
    self._state_badge_refresh: Any | None = None  # Function to refresh state badge

  async def render(self) -> None:
    """Render the simulation page."""
    await self.render_async()

  async def render_async(self) -> None:
    """Render the simulation page with new layout."""
    session = self.controller.current_session
    if session is None:
      ui.label("No active session").classes("text-red-500")
      return

    # Header
    self._render_header(session.agent_name)

    # Main layout container
    with ui.column().classes("w-full h-screen pt-16"):
      # System prompt header (expandable, collapsed by default)
      with ui.column().classes("w-full px-4 pt-4"):
        instruction = await self.controller.get_system_instruction()
        render_system_prompt(instruction, session.agent_name, expanded=False)

      # Main content: 2/3 event stream + 1/3 sidebar
      with ui.row().classes("w-full flex-grow gap-0 px-4 pb-4"):
        # Left: Event Stream (2/3 width)
        with ui.column().classes(f"{LAYOUT['main_content_width']} h-full pr-4"):
          self._event_stream = EventStream(
            history=session.history,
            is_loading=self._is_executing,
            loading_tool=self._selected_tool if self._is_executing else None,
          )
          self._event_stream.render()

        # Right: Control Panel Sidebar (1/3 width)
        with ui.column().classes(f"{LAYOUT['sidebar_width']} {CONTROL_PANEL_CLASSES}"):
          self._sidebar_content = ui.column().classes("w-full h-full")
          with self._sidebar_content:
            self._render_sidebar_content()

  def _render_header(self, agent_name: str) -> None:
    """Render the page header with agent name and session state."""
    with ui.header().classes("bg-blue-700 text-white"):
      with ui.row().classes("w-full items-center justify-between px-4"):
        # Left: Agent name and icon
        with ui.row().classes("items-center gap-2"):
          ui.icon("smart_toy", size="sm")
          ui.label(f"Simulating: {agent_name}").classes("text-xl font-semibold")

        # Right: Session state badge (refreshable)
        @ui.refreshable  # type: ignore[reportArgumentType]
        def render_state_badge() -> None:
          session = self.controller.current_session
          if session:
            state_config = {
              SessionState.AWAITING_QUERY: (
                "Awaiting Query",
                "yellow",
                "text-yellow-900",
              ),
              SessionState.ACTIVE: ("Active", "green", "text-green-900"),
              SessionState.COMPLETED: ("Completed", "blue", "text-blue-900"),
            }
            label, color, text_class = state_config.get(
              session.state, ("Unknown", "gray", "text-gray-900")
            )
            ui.badge(label, color=color).classes(f"{text_class} font-semibold")

        render_state_badge()
        self._state_badge_refresh = render_state_badge.refresh  # Store refresh function

  def _render_sidebar_content(self) -> None:
    """Render the sidebar content based on session state."""
    session = self.controller.current_session
    if session is None:
      return

    if session.state == SessionState.AWAITING_QUERY:
      self._render_query_input()
    elif session.state == SessionState.ACTIVE:
      if self._selected_tool:
        self._render_tool_executor()
      else:
        self._render_action_panel()
    elif session.state == SessionState.COMPLETED:
      self._render_completed()

  def _render_query_input(self) -> None:
    """Render the initial query input form in the sidebar."""
    session = self.controller.current_session
    if session is None:
      return

    # Check if agent has input schema
    has_input_schema = False
    input_schema = None
    if session.agent:
      try:
        input_schema = getattr(session.agent, "input_schema", None)
        has_input_schema = input_schema is not None
      except Exception:
        pass

    with ui.card().classes("w-full"):
      ui.label("Enter User Query").classes("text-lg font-semibold mb-4")

      if has_input_schema:
        # Render structured form for input schema
        ui.label("This agent expects structured input.").classes(
          "text-gray-600 mb-4 text-sm"
        )

        from adk_agent_sim.ui.components.schema_form import (
          pydantic_to_schema,
          render_schema_form,
          validate_required_fields,
        )

        assert input_schema is not None
        schema = pydantic_to_schema(input_schema)
        form_values: dict[str, Any] = {}

        def on_form_change(values: dict[str, Any]) -> None:
          nonlocal form_values
          form_values = values

        form_values = render_schema_form(schema, on_form_change)

        async def on_start_structured() -> None:
          errors = validate_required_fields(schema, form_values)
          if errors:
            ui.notify(f"Validation errors: {', '.join(errors)}", type="warning")
            return
          import json

          query_str = json.dumps(form_values)
          await self.controller.start_session(query_str)
          self._refresh_ui()

        ui.button(
          "Start Session",
          icon="play_arrow",
          on_click=on_start_structured,
        ).classes("w-full mt-4").style(PRIMARY_BUTTON_STYLE)
      else:
        # Plain text input
        ui.label("Provide the initial query for the agent.").classes(
          "text-gray-600 mb-4 text-sm"
        )

        query_input = ui.textarea(
          label="User Query",
          placeholder="Enter the user's question or request...",
        ).classes("w-full mb-4")
        query_input.props("rows=4")

        async def on_start() -> None:
          if query_input.value:
            await self.controller.start_session(query_input.value)
            self._refresh_ui()
          else:
            ui.notify("Please enter a query", type="warning")

        ui.button(
          "Start Session",
          icon="play_arrow",
          on_click=on_start,
        ).classes("w-full").style(PRIMARY_BUTTON_STYLE)

  def _render_action_panel(self) -> None:
    """Render the action selection panel in the sidebar."""
    session = self.controller.current_session
    if session is None:
      return

    # Check if agent has output schema
    has_output_schema = False
    output_schema = None
    if session.agent:
      try:
        output_schema = getattr(session.agent, "output_schema", None)
        has_output_schema = output_schema is not None
      except Exception:
        pass

    render_action_panel(
      tools=session.tools,
      on_tool_select=self._on_tool_select,
      on_final_response=self._on_final_response,
      has_output_schema=has_output_schema,
      output_schema=output_schema,
    )

  def _render_tool_executor(self) -> None:
    """Render the tool executor for the selected tool in the sidebar."""
    if not self._selected_tool:
      return

    declaration = self.controller.get_tool_declaration(self._selected_tool)

    # Back button
    ui.button(
      "← Back to Actions",
      on_click=self._clear_tool_selection,
    ).props("flat dense").classes("mb-4")

    render_tool_executor(
      tool_name=self._selected_tool,
      declaration=declaration,
      tool_runner=self.controller.tool_runner,
      on_execute=self._on_execute_tool,
      on_cancel=self._on_cancel_tool,
    )

  def _render_completed(self) -> None:
    """Render the completed session view in the sidebar."""
    with ui.card().classes("w-full"):
      with ui.column().classes("w-full items-center"):
        ui.icon("check_circle", color="green", size="xl").classes("mb-4")
        ui.label("Session Completed").classes("text-lg font-semibold mb-2")

        ui.label("Export the Golden Trace to save this simulation.").classes(
          "text-gray-600 text-sm text-center mb-4"
        )

        async def on_export() -> None:
          try:
            json_str = self.controller.export_trace()
            session = self.controller.current_session
            session_id = session.session_id if session else "unknown"
            ui.download(
              json_str.encode("utf-8"),
              filename=f"golden_trace_{session_id}.json",
            )
            ui.notify("Golden Trace exported!", type="positive")
          except Exception as e:
            ui.notify(f"Export failed: {e}", type="negative")

        ui.button(
          "Export Golden Trace",
          icon="download",
          on_click=on_export,
        ).classes("w-full").style(SUCCESS_BUTTON_STYLE)

  def _on_tool_select(self, tool_name: str) -> None:
    """Handle tool selection."""
    self._selected_tool = tool_name
    self._refresh_ui()

  def _clear_tool_selection(self) -> None:
    """Clear tool selection and return to action panel."""
    self._selected_tool = None
    self._refresh_ui()

  async def _on_execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> None:
    """Handle tool execution with loading state."""
    try:
      # Set loading state
      self._is_executing = True
      self._refresh_event_stream()

      result = await self.controller.execute_tool(tool_name, arguments)
      if result.success:
        ui.notify(f"Tool '{tool_name}' executed successfully", type="positive")
      else:
        ui.notify(f"Tool error: {result.error_message}", type="negative")
    except Exception as e:
      ui.notify(f"Execution failed: {e}", type="negative")
    finally:
      self._selected_tool = None
      self._is_executing = False
      self._refresh_ui()

  def _on_cancel_tool(self) -> None:
    """Handle tool cancellation."""
    self.controller.cancel_tool()

  async def _on_final_response(self, response: str) -> None:
    """Handle final response submission."""
    try:
      await self.controller.submit_final_response(response)
      ui.notify("Final response submitted!", type="positive")
      self._refresh_ui()
    except Exception as e:
      ui.notify(f"Failed to submit response: {e}", type="negative")

  def _refresh_event_stream(self) -> None:
    """Refresh just the event stream component."""
    session = self.controller.current_session
    if session and self._event_stream:
      self._event_stream.refresh(
        history=session.history,
        is_loading=self._is_executing,
        loading_tool=self._selected_tool if self._is_executing else None,
      )

  def _refresh_ui(self) -> None:
    """Refresh the UI after state changes."""
    # Refresh state badge
    if self._state_badge_refresh:
      self._state_badge_refresh()  # type: ignore[reportUnknownMemberType]

    # Refresh event stream
    self._refresh_event_stream()

    # Refresh sidebar content
    if self._sidebar_content:
      self._sidebar_content.clear()
      with self._sidebar_content:
        self._render_sidebar_content()


async def render_simulation_page(controller: SimulationController) -> SimulationPage:
  """
  Render the simulation page.

  Args:
    controller: The simulation controller

  Returns:
    SimulationPage instance
  """
  page = SimulationPage(controller)
  await page.render()
  return page

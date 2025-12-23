"""Agent selection page component."""

from __future__ import annotations

from typing import Callable

from nicegui import ui

from adk_agent_sim.ui.styles import PRIMARY_BUTTON_STYLE


class AgentSelectPage:
  """Page for selecting an agent to simulate."""

  def __init__(
    self,
    agent_names: list[str],
    on_select: Callable[[str], None],
  ) -> None:
    """
    Initialize the agent selection page.

    Args:
      agent_names: List of available agent names
      on_select: Callback when an agent is selected
    """
    self.agent_names = agent_names
    self.on_select = on_select
    self._selected: str | None = None

  def render(self) -> None:
    """Render the agent selection page."""
    with ui.column().classes("w-full h-screen items-center justify-center"):
      with ui.card().classes("w-96 p-8"):
        # Header
        ui.label("ADK Agent Simulator").classes("text-2xl font-bold text-center mb-2")
        ui.label("Select an agent to begin simulation").classes(
          "text-gray-600 text-center mb-6"
        )

        # Agent selection
        if not self.agent_names:
          ui.label("No agents available").classes("text-red-500 text-center")
          return

        select = ui.select(
          options=self.agent_names,
          label="Agent",
          value=self.agent_names[0],
        ).classes("w-full mb-6")

        def on_click() -> None:
          if select.value:
            self.on_select(select.value)

        ui.button(
          "Start Simulation",
          icon="play_arrow",
          on_click=on_click,
        ).classes("w-full").style(PRIMARY_BUTTON_STYLE)

        # Footer info
        ui.separator().classes("my-4")
        ui.label(f"{len(self.agent_names)} agent(s) available").classes(
          "text-xs text-gray-500 text-center"
        )


def render_agent_select_page(
  agent_names: list[str],
  on_select: Callable[[str], None],
) -> AgentSelectPage:
  """
  Render the agent selection page.

  Args:
    agent_names: List of available agent names
    on_select: Selection callback

  Returns:
    AgentSelectPage instance
  """
  page = AgentSelectPage(agent_names, on_select)
  page.render()
  return page

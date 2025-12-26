"""Agent selection page component."""

from typing import Awaitable, Callable, TypedDict

from nicegui import ui

from adk_agent_sim.ui.components.agent_card import AgentCard


class AgentInfo(TypedDict):
  """Type definition for agent info dictionary."""

  name: str
  description: str | None


class AgentSelectPage:
  """Page for selecting an agent to simulate using a card grid dashboard."""

  def __init__(
    self,
    agents_info: list[AgentInfo],
    on_select: Callable[[str], Awaitable[None]],
  ) -> None:
    """
    Initialize the agent selection page.

    Args:
      agents_info: List of agent info dicts with 'name' and 'description' keys
      on_select: Async callback when an agent is selected
    """
    self.agents_info = agents_info
    self.on_select = on_select

  def render(self) -> None:
    """Render the agent selection page with card grid layout."""
    with ui.column().classes("w-full min-h-screen bg-gray-50"):
      # Header section
      self._render_header()

      # Main content - card grid
      self._render_card_grid()

      # Footer
      self._render_footer()

  def _render_header(self) -> None:
    """Render the page header with title and description."""
    with ui.column().classes("w-full items-center py-12 bg-white shadow-sm"):
      # Logo/icon
      with ui.element("div").classes(
        "w-20 h-20 rounded-full bg-blue-600 flex items-center justify-center mb-4"
      ):
        ui.icon("smart_toy", size="2xl").classes("text-white")

      # Title
      ui.label("ADK Agent Simulator").classes("text-3xl font-bold text-gray-800 mb-2")

      # Subtitle
      ui.label("Select an agent to begin simulation").classes("text-lg text-gray-600")

  def _render_card_grid(self) -> None:
    """Render the agent cards in a responsive grid."""
    with ui.column().classes("w-full items-center py-8 px-4 flex-grow"):
      if not self.agents_info:
        # Empty state
        with ui.card().classes("p-8 text-center"):
          ui.icon("warning", size="xl").classes("text-yellow-500 mb-4")
          ui.label("No Agents Available").classes("text-xl font-semibold mb-2")
          ui.label("Please configure agents in your project to get started.").classes(
            "text-gray-600"
          )
        return

      # Card grid container
      with ui.row().classes("flex-wrap gap-6 justify-center"):
        for agent_info in self.agents_info:
          self._render_agent_card(agent_info)

  def _render_agent_card(self, agent_info: AgentInfo) -> None:
    """Render a single agent card."""
    agent_name = agent_info["name"]

    # Create closure for click handler
    async def on_card_click() -> None:
      await self.on_select(agent_name)

    card = AgentCard(
      name=agent_name,
      description=agent_info.get("description"),
      on_click=on_card_click,
    )
    card.render()

  def _render_footer(self) -> None:
    """Render the page footer with agent count info."""
    with ui.column().classes("w-full items-center py-6 bg-white border-t"):
      count = len(self.agents_info)
      ui.label(f"{count} agent{'s' if count != 1 else ''} available").classes(
        "text-sm text-gray-500"
      )


def render_agent_select_page(
  agents_info: list[AgentInfo],
  on_select: Callable[[str], Awaitable[None]],
) -> AgentSelectPage:
  """
  Render the agent selection page.

  Args:
    agents_info: List of agent info dicts with 'name' and 'description' keys
    on_select: Async selection callback

  Returns:
    AgentSelectPage instance
  """
  page = AgentSelectPage(agents_info, on_select)
  page.render()
  return page

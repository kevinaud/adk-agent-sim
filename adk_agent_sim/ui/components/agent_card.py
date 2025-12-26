"""Agent card component for the agent selection dashboard."""

from typing import Awaitable, Callable

from nicegui import ui

from adk_agent_sim.ui.styles import AGENT_CARD_HOVER_CLASSES, AGENT_CARD_STYLE


class AgentCard:
  """Clickable card component displaying agent name and description."""

  def __init__(
    self,
    name: str,
    description: str | None = None,
    on_click: Callable[[], Awaitable[None]] | None = None,
  ) -> None:
    """
    Initialize the agent card.

    Args:
      name: Agent display name
      description: Agent description (optional)
      on_click: Async click handler
    """
    self.name = name
    self.description = description
    self.on_click = on_click

  def render(self) -> ui.card:
    """
    Render the agent card.

    Returns:
      The card element
    """
    with (
      ui.card()
      .style(AGENT_CARD_STYLE)
      .classes(f"shadow-md {AGENT_CARD_HOVER_CLASSES}") as card
    ):
      # Agent icon/avatar area
      with ui.row().classes("w-full justify-center mb-3"):
        with ui.element("div").classes(
          "w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center"
        ):
          ui.icon("smart_toy", size="xl").classes("text-blue-600")

      # Agent name
      ui.label(self.name).classes("text-lg font-bold text-center w-full text-gray-800")

      # Description (if available)
      if self.description:
        ui.label(self.description).classes(
          "text-sm text-gray-600 text-center mt-2 line-clamp-2"
        )
      else:
        ui.label("No description available").classes(
          "text-sm text-gray-400 text-center mt-2 italic"
        )

      # Visual indicator for clickability
      with ui.row().classes("w-full justify-center mt-4"):
        ui.badge("Click to start", color="blue-3").props("outline")

    # Attach click handler
    if self.on_click is not None:
      handler = self.on_click
      card.on("click", lambda: handler())

    return card


class AgentCardGrid:
  """Responsive grid container for agent cards."""

  def __init__(
    self,
    agents: list[dict[str, str | None]],
    on_select: Callable[[str], Awaitable[None]],
  ) -> None:
    """
    Initialize the agent card grid.

    Args:
      agents: List of agent info dicts with 'name' and optional 'description'
      on_select: Selection callback (receives agent name)
    """
    self.agents = agents
    self.on_select = on_select

  def render(self) -> None:
    """Render the agent card grid."""
    with ui.row().classes("flex-wrap gap-6 justify-center p-4"):
      for agent in self.agents:
        name = str(agent.get("name", "Unknown"))
        description = agent.get("description")

        # Create the click handler closure properly
        agent_name = name

        async def on_card_click(n: str = agent_name) -> None:
          await self.on_select(n)

        card = AgentCard(
          name=name,
          description=str(description) if description else None,
          on_click=on_card_click,
        )
        card.render()


def render_agent_card(
  name: str,
  description: str | None = None,
  on_click: Callable[[], Awaitable[None]] | None = None,
) -> AgentCard:
  """
  Render an agent card.

  Args:
    name: Agent display name
    description: Agent description
    on_click: Click handler

  Returns:
    The AgentCard instance
  """
  card = AgentCard(name, description, on_click)
  card.render()
  return card


def render_agent_card_grid(
  agents: list[dict[str, str | None]],
  on_select: Callable[[str], Awaitable[None]],
) -> AgentCardGrid:
  """
  Render an agent card grid.

  Args:
    agents: List of agent info dicts
    on_select: Selection callback

  Returns:
    The AgentCardGrid instance
  """
  grid = AgentCardGrid(agents, on_select)
  grid.render()
  return grid

"""NiceGUI application setup and routing."""

from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
  from adk_agent_sim.controller import SimulationController


class SimulatorApp:
  """NiceGUI application for the agent simulator."""

  def __init__(self, controller: SimulationController) -> None:
    """
    Initialize the simulator application.

    Args:
      controller: The simulation controller with agents
    """
    self.controller = controller
    self._setup_routes()

  def _setup_routes(self) -> None:
    """Set up the application routes."""

    @ui.page("/")
    async def index() -> None:  # pyright: ignore[reportUnusedFunction]
      """Agent selection page."""
      from adk_agent_sim.ui.pages.agent_select import (
        AgentInfo,
        render_agent_select_page,
      )

      # Build list of agent info with names and descriptions
      agents_info: list[AgentInfo] = []
      for name, agent in self.controller.available_agents.items():
        agents_info.append(
          AgentInfo(
            name=name,
            description=agent.description,
          )
        )

      async def on_select(agent_name: str) -> None:
        # Create session and select agent
        self.controller.create_session()
        try:
          await self.controller.select_agent(agent_name)
          # Navigate to simulation page
          ui.navigate.to("/simulate")
        except (ConnectionError, BaseExceptionGroup) as e:
          # Show user-friendly error for connection failures
          # BaseExceptionGroup can come from anyio/asyncio MCP client
          error_msg = str(e)
          if isinstance(e, BaseExceptionGroup):
            # Extract first meaningful error
            msgs = [str(exc) for exc in e.exceptions[:2]]
            error_msg = "; ".join(msgs)
          ui.notify(
            f"Failed to connect: {error_msg}",
            type="negative",
            position="top",
            close_button=True,
            timeout=0,  # Don't auto-close
          )
        except Exception as e:
          # Show generic error for other failures
          ui.notify(
            f"Failed to start simulation: {e}",
            type="negative",
            position="top",
            close_button=True,
            timeout=0,
          )

      render_agent_select_page(agents_info, on_select)

    @ui.page("/simulate")
    async def simulate() -> None:  # pyright: ignore[reportUnusedFunction]
      """Main simulation page."""
      from adk_agent_sim.ui.pages.simulation import render_simulation_page

      # Ensure we have an active session
      if self.controller.current_session is None:
        ui.navigate.to("/")
        return

      await render_simulation_page(self.controller)  # type: ignore

  def run(
    self,
    host: str = "127.0.0.1",
    port: int = 8080,
    title: str = "ADK Agent Simulator",
    reload: bool = False,
  ) -> None:
    """
    Run the NiceGUI application.

    Args:
      host: Host to bind to
      port: Port to listen on
      title: Browser window title
      reload: Enable auto-reload for development
    """
    ui.run(  # type: ignore
      host=host,
      port=port,
      title=title,
      reload=reload,
      show=True,
    )


def create_app(controller: SimulationController) -> SimulatorApp:
  """
  Create a simulator application instance.

  Args:
    controller: The simulation controller

  Returns:
    SimulatorApp instance
  """
  return SimulatorApp(controller)

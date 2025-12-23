"""AgentSimulator entry point class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from adk_agent_sim.controller import SimulationController
from adk_agent_sim.ui.app import SimulatorApp

if TYPE_CHECKING:
  from google.adk.agents import Agent


class AgentSimulator:
  """
  Main entry point for the ADK Agent Simulator.

  Usage:
    ```python
    from adk_agent_sim import AgentSimulator
    from my_project.agents import my_agent

    simulator = AgentSimulator(agents={"MyAgent": my_agent})
    simulator.run()  # Opens browser at http://localhost:8080
    ```
  """

  def __init__(
    self,
    agents: dict[str, Agent],
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
    title: str = "ADK Agent Simulator",
  ) -> None:
    """
    Initialize the agent simulator.

    Args:
      agents: Dictionary mapping agent names to Agent instances
      host: Host to bind the web server to
      port: Port to listen on
      title: Browser window title
    """
    if not agents:
      raise ValueError("At least one agent must be provided")

    self._agents = agents
    self._host = host
    self._port = port
    self._title = title

    # Create controller and app
    self._controller = SimulationController(agents)
    self._app = SimulatorApp(self._controller)

  @property
  def controller(self) -> SimulationController:
    """Get the simulation controller."""
    return self._controller

  def run(self, *, reload: bool = False) -> None:
    """
    Start the simulator web interface.

    This will open a browser window at the configured host/port.

    Args:
      reload: Enable auto-reload for development
    """
    self._app.run(
      host=self._host,
      port=self._port,
      title=self._title,
      reload=reload,
    )

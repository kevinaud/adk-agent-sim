"""Session state and model for simulation runs."""

import time
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
  from google.adk.agents import Agent
  from google.adk.tools import BaseTool

  from adk_agent_sim.models.history import HistoryEntry


class SessionState(Enum):
  """Session lifecycle states."""

  SELECTING_AGENT = "selecting_agent"  # Initial state, choosing agent
  AWAITING_QUERY = "awaiting_query"  # Agent selected, waiting for user query
  ACTIVE = "active"  # In simulation loop
  COMPLETED = "completed"  # Final response submitted


class SimulationSession(BaseModel):
  """Tracks state for a single simulation run."""

  model_config = {"arbitrary_types_allowed": True}

  session_id: str = Field(
    default_factory=lambda: str(uuid.uuid4()),
    description="Unique session identifier",
  )
  agent_name: str = Field(default="", description="Display name of selected agent")
  agent: Any = Field(default=None, description="Reference to ADK Agent instance")
  tools: list[Any] = Field(default_factory=list, description="Cached tools from agent")
  state: SessionState = Field(default=SessionState.SELECTING_AGENT)
  history: list[Any] = Field(default_factory=list)
  start_timestamp: float = Field(
    default_factory=time.time, description="Session start time (epoch)"
  )

  # For ADK context construction
  adk_session: Any = Field(default=None, description="ADK Session for ToolContext")
  adk_session_service: Any = Field(
    default=None, description="ADK SessionService for InvocationContext"
  )

  def add_history_entry(self, entry: HistoryEntry) -> None:
    """Add an entry to the session history."""
    self.history.append(entry)

  def select_agent(self, name: str, agent: Agent, tools: list[BaseTool]) -> None:
    """Select an agent and transition to AWAITING_QUERY state."""
    if self.state != SessionState.SELECTING_AGENT:
      raise ValueError(
        f"Cannot select agent from state {self.state.value}. "
        "Must be in SELECTING_AGENT state."
      )
    self.agent_name = name
    self.agent = agent
    self.tools = list(tools)
    self.state = SessionState.AWAITING_QUERY

  def start_session(self) -> None:
    """Start the simulation session (transition to ACTIVE)."""
    if self.state != SessionState.AWAITING_QUERY:
      raise ValueError(
        f"Cannot start session from state {self.state.value}. "
        "Must be in AWAITING_QUERY state."
      )
    self.state = SessionState.ACTIVE
    self.start_timestamp = time.time()

  def complete_session(self) -> None:
    """Mark session as completed."""
    if self.state != SessionState.ACTIVE:
      raise ValueError(
        f"Cannot complete session from state {self.state.value}. "
        "Must be in ACTIVE state."
      )
    self.state = SessionState.COMPLETED

  def get_tool_by_name(self, name: str) -> BaseTool | None:
    """Find a tool by name."""
    for tool in self.tools:
      if tool.name == name:
        return tool
    return None

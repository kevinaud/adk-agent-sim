"""Simulation controller for orchestrating the agent simulation workflow."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from adk_agent_sim.execution.tool_runner import ExecutionResult, ToolRunner
from adk_agent_sim.models.history import (
  FinalResponse,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.models.session import SessionState, SimulationSession

if TYPE_CHECKING:
  from google.adk.agents import Agent
  from google.genai.types import FunctionDeclaration


class SimulationController:
  """Orchestrates the simulation flow between UI and business logic."""

  def __init__(self, agents: dict[str, Agent]) -> None:
    """
    Initialize the controller with available agents.

    Args:
      agents: Dictionary mapping agent names to Agent instances
    """
    self._agents = agents
    self._session: SimulationSession | None = None
    self._tool_runner = ToolRunner()
    self._tool_declarations: dict[str, FunctionDeclaration] = {}

  @property
  def available_agents(self) -> dict[str, Agent]:
    """Dictionary of agent_name → Agent instance."""
    return self._agents

  @property
  def current_session(self) -> SimulationSession | None:
    """Active session or None if not started."""
    return self._session

  @property
  def tool_runner(self) -> ToolRunner:
    """The tool runner instance for execution status."""
    return self._tool_runner

  def create_session(self) -> SimulationSession:
    """Create a new simulation session."""
    self._session = SimulationSession()
    self._tool_declarations = {}
    return self._session

  async def select_agent(self, agent_name: str) -> None:
    """
    Select an agent and initialize tools.

    Args:
      agent_name: Key from available_agents dict

    Raises:
      KeyError: If agent_name not found
      ValueError: If no session is active
    """
    if self._session is None:
      raise ValueError("No active session. Call create_session() first.")

    if agent_name not in self._agents:
      raise KeyError(f"Agent '{agent_name}' not found")

    agent = self._agents[agent_name]

    # Get tools from agent
    tools = await agent.canonical_tools()

    # Cache tool declarations for form rendering
    self._tool_declarations = {}
    for tool in tools:
      try:
        declaration = tool._get_declaration()
        if declaration:
          self._tool_declarations[tool.name] = declaration
      except Exception:
        # Some tools may not have declarations
        pass

    # Update session state
    self._session.select_agent(agent_name, agent, tools)

  def get_tool_declaration(self, tool_name: str) -> FunctionDeclaration | None:
    """Get the cached FunctionDeclaration for a tool."""
    return self._tool_declarations.get(tool_name)

  async def get_system_instruction(self) -> str:
    """Get the agent's system instruction/prompt."""
    if self._session is None or self._session.agent is None:
      return ""
    try:
      instruction = await self._session.agent.canonical_instruction()
      if isinstance(instruction, tuple):
        return instruction[0]
      return instruction or ""
    except Exception:
      return ""

  async def start_session(self, user_query: str | dict[str, Any]) -> None:
    """
    Start a new session with the given user query.

    Args:
      user_query: Plain text or structured input (if input_schema defined)

    Raises:
      ValueError: If session not in AWAITING_QUERY state
    """
    if self._session is None:
      raise ValueError("No active session")

    if self._session.state != SessionState.AWAITING_QUERY:
      raise ValueError(
        f"Session not in AWAITING_QUERY state (current: {self._session.state})"
      )

    # Convert structured input to JSON string if needed
    content = user_query if isinstance(user_query, str) else str(user_query)

    # Add user query to history
    self._session.add_history_entry(UserQuery(content=content))
    self._session.start_session()

  async def execute_tool(
    self, tool_name: str, arguments: dict[str, Any]
  ) -> ExecutionResult:
    """
    Execute a tool and record results in session history.

    Args:
      tool_name: Name of the tool to execute
      arguments: Arguments for the tool

    Returns:
      ExecutionResult with success/failure details

    Raises:
      ValueError: If session not active or tool not found
    """
    if self._session is None:
      raise ValueError("No active session")

    if self._session.state != SessionState.ACTIVE:
      raise ValueError("Session not in ACTIVE state")

    tool = self._session.get_tool_by_name(tool_name)
    if tool is None:
      raise ValueError(f"Tool '{tool_name}' not found")

    # Create tool call entry
    tool_call = ToolCall(tool_name=tool_name, arguments=arguments)
    self._session.add_history_entry(tool_call)

    # Execute the tool
    result = await self._tool_runner.execute(tool, arguments, self._session)

    # Record result in history
    if result.success:
      self._session.add_history_entry(
        ToolOutput(
          call_id=tool_call.call_id,
          result=result.result,
          duration_ms=result.duration_ms,
        )
      )
    else:
      self._session.add_history_entry(
        ToolError(
          call_id=tool_call.call_id,
          error_type=result.error_type or "Unknown",
          error_message=result.error_message or "Unknown error",
          traceback=result.error_traceback,
          duration_ms=result.duration_ms,
        )
      )

    return result

  def cancel_tool(self) -> None:
    """Cancel the currently executing tool (if any)."""
    self._tool_runner.cancel()

  async def submit_final_response(self, response: str | dict[str, Any]) -> None:
    """
    Submit final response and transition to COMPLETED state.

    Args:
      response: Plain text or structured output (if output_schema defined)

    Raises:
      ValueError: If session not active
    """
    if self._session is None:
      raise ValueError("No active session")

    if self._session.state != SessionState.ACTIVE:
      raise ValueError("Session not in ACTIVE state")

    # Convert structured output to JSON string if needed
    content = response if isinstance(response, str) else str(response)

    # Add final response to history
    self._session.add_history_entry(FinalResponse(content=content))
    self._session.complete_session()

  def export_trace(self) -> str:
    """
    Export current session as Golden Trace JSON.

    Returns:
      JSON string of EvalCase

    Raises:
      ValueError: If session not completed
    """
    if self._session is None:
      raise ValueError("No active session")

    if self._session.state != SessionState.COMPLETED:
      raise ValueError("Session not completed")

    from adk_agent_sim.export.golden_trace import GoldenTraceBuilder

    builder = GoldenTraceBuilder(self._session)
    eval_case = builder.build()
    return builder.export_json(eval_case)

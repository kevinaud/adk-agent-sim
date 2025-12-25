"""Factory functions for creating ADK execution contexts."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from google.adk.agents.invocation_context import InvocationContext
  from google.adk.tools import BaseTool
  from google.adk.tools.tool_context import ToolContext

  from adk_agent_sim.models.session import SimulationSession


async def create_invocation_context(
  session: SimulationSession,
) -> InvocationContext:
  """
  Create a valid InvocationContext for tool execution.

  Args:
    session: The current simulation session with agent and ADK session

  Returns:
    InvocationContext suitable for tool execution
  """
  # Import here to avoid circular imports and allow type checking
  from google.adk.agents.invocation_context import InvocationContext

  return InvocationContext(
    invocation_id=f"{session.session_id}_inv",
    agent=session.agent,
    session=session.adk_session,
    session_service=None,  # type: ignore
  )


async def create_tool_context(
  session: SimulationSession,
  tool: BaseTool,
  invocation_context: InvocationContext | None = None,
) -> ToolContext:
  """
  Create a valid ToolContext for executing a specific tool.

  Args:
    session: The current simulation session
    tool: The tool to be executed
    invocation_context: Optional pre-created invocation context

  Returns:
    ToolContext suitable for tool.run_async()
  """
  # Import here to avoid circular imports
  from google.adk.tools.tool_context import ToolContext

  if invocation_context is None:
    invocation_context = await create_invocation_context(session)

  return ToolContext(
    invocation_context=invocation_context,
    function_call_id=str(uuid.uuid4()),
  )


async def ensure_adk_session(session: SimulationSession) -> Any:
  """
  Ensure the simulation session has a valid ADK Session.

  Creates an in-memory ADK session if one doesn't exist.

  Args:
    session: The simulation session to update

  Returns:
    The ADK Session object
  """
  if session.adk_session is not None:
    return session.adk_session

  # Create an in-memory session for the simulation
  from google.adk.sessions import InMemorySessionService

  session_service = InMemorySessionService()
  adk_session = await session_service.create_session(
    app_name="adk_agent_sim",
    user_id="wizard",
  )
  session.adk_session = adk_session
  return adk_session

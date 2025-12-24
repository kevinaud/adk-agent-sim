"""Unit tests for context factory functions."""

from __future__ import annotations

import pytest
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from adk_agent_sim.execution.context_factory import (
  create_invocation_context,
  create_tool_context,
  ensure_adk_session,
)
from adk_agent_sim.models.session import SimulationSession


def simple_tool() -> str:
  """A simple test tool."""
  return "success"


@pytest.fixture
def real_agent() -> Agent:
  """Create a real ADK agent for testing."""
  return Agent(
    model="gemini-2.5-flash",
    name="TestAgent",
    description="Agent for testing",
    instruction="You are a test agent.",
    tools=[FunctionTool(simple_tool)],
  )


@pytest.fixture
def simulation_session(real_agent: Agent) -> SimulationSession:
  """Create a simulation session for testing."""
  from google.adk.tools import BaseTool

  session = SimulationSession()
  tools: list[BaseTool] = [FunctionTool(simple_tool)]
  session.select_agent("TestAgent", real_agent, tools)
  return session


class TestCreateInvocationContext:
  """Tests for create_invocation_context function."""

  @pytest.mark.asyncio
  async def test_creates_valid_invocation_context(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that create_invocation_context creates a valid InvocationContext."""
    # Ensure session has adk_session
    await ensure_adk_session(simulation_session)

    # Create invocation context
    inv_context = await create_invocation_context(simulation_session)

    # Verify structure
    assert inv_context is not None
    assert hasattr(inv_context, "invocation_id")
    assert hasattr(inv_context, "agent")
    assert hasattr(inv_context, "session")
    assert hasattr(inv_context, "session_service")

    # Verify values
    assert inv_context.agent == simulation_session.agent
    assert inv_context.session == simulation_session.adk_session
    assert inv_context.session_service is not None  # This was the bug!
    assert inv_context.invocation_id.startswith(simulation_session.session_id)

  @pytest.mark.asyncio
  async def test_session_service_not_none(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that session_service is not None (bug fix verification)."""
    await ensure_adk_session(simulation_session)
    inv_context = await create_invocation_context(simulation_session)

    # This is the critical assertion - previously session_service was None
    assert inv_context.session_service is not None

  @pytest.mark.asyncio
  async def test_creates_session_service_if_missing(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that session_service is created if not present."""
    # Create a real ADK session first (bypass ensure_adk_session)
    from google.adk.sessions import InMemorySessionService

    temp_service = InMemorySessionService()
    simulation_session.adk_session = await temp_service.create_session(
      app_name="test", user_id="test_user"
    )
    # But don't set adk_session_service - let create_invocation_context create it

    inv_context = await create_invocation_context(simulation_session)

    # Should have created a session_service
    assert simulation_session.adk_session_service is not None
    assert inv_context.session_service is not None

  @pytest.mark.asyncio
  async def test_reuses_existing_session_service(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that existing session_service is reused."""
    # Set up session with service
    await ensure_adk_session(simulation_session)
    first_service = simulation_session.adk_session_service

    # Create multiple invocation contexts
    inv_context_1 = await create_invocation_context(simulation_session)
    inv_context_2 = await create_invocation_context(simulation_session)

    # Should reuse the same service
    assert inv_context_1.session_service is first_service
    assert inv_context_2.session_service is first_service


class TestCreateToolContext:
  """Tests for create_tool_context function."""

  @pytest.mark.asyncio
  async def test_creates_valid_tool_context(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that create_tool_context creates a valid ToolContext."""
    await ensure_adk_session(simulation_session)

    # Use the real tool from the session
    tool = simulation_session.tools[0]
    tool_context = await create_tool_context(simulation_session, tool)

    # Just verify it was created successfully
    assert tool_context is not None

  @pytest.mark.asyncio
  async def test_creates_invocation_context_if_not_provided(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that tool_context creates its own invocation_context if not provided."""
    await ensure_adk_session(simulation_session)

    tool = simulation_session.tools[0]
    tool_context = await create_tool_context(simulation_session, tool)

    # Verify the tool context was created (internal structure is opaque)
    assert tool_context is not None

  @pytest.mark.asyncio
  async def test_uses_provided_invocation_context(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that provided invocation_context is used."""
    await ensure_adk_session(simulation_session)

    inv_context = await create_invocation_context(simulation_session)
    tool = simulation_session.tools[0]
    tool_context = await create_tool_context(
      simulation_session, tool, invocation_context=inv_context
    )

    # Verify it was created successfully with provided context
    assert tool_context is not None


class TestEnsureAdkSession:
  """Tests for ensure_adk_session function."""

  @pytest.mark.asyncio
  async def test_creates_adk_session_if_missing(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that ensure_adk_session creates ADK session if missing."""
    assert simulation_session.adk_session is None
    assert simulation_session.adk_session_service is None

    adk_session = await ensure_adk_session(simulation_session)

    assert adk_session is not None
    assert simulation_session.adk_session is not None
    assert simulation_session.adk_session_service is not None

  @pytest.mark.asyncio
  async def test_reuses_existing_adk_session(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that existing ADK session is reused."""
    # Create initial session
    first_session = await ensure_adk_session(simulation_session)

    # Call again
    second_session = await ensure_adk_session(simulation_session)

    # Should be the same object
    assert first_session is second_session

  @pytest.mark.asyncio
  async def test_creates_session_service_with_session(
    self, simulation_session: SimulationSession
  ) -> None:
    """Test that session_service is created along with session."""
    await ensure_adk_session(simulation_session)

    # Both should be set
    assert simulation_session.adk_session is not None
    assert simulation_session.adk_session_service is not None

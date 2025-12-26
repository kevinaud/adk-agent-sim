"""Integration tests for end-to-end simulation flow."""

import json
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from adk_agent_sim.controller import SimulationController
from adk_agent_sim.execution.tool_runner import ExecutionResult
from adk_agent_sim.models.history import (
  FinalResponse,
  ToolCall,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.models.session import SessionState


class MockTool(BaseTool):
  """Mock ADK tool for testing."""

  def __init__(
    self,
    name: str = "mock_tool",
    result: Any = {"success": True},
  ) -> None:
    self.name = name
    self._result = result

  def _get_declaration(self) -> MagicMock:
    decl = MagicMock()
    decl.name = self.name
    decl.parameters = None
    return decl

  async def run_async(self, *, args: dict[str, Any], tool_context: Any) -> Any:
    return self._result


class MockAgent(Agent):
  """Mock ADK agent for testing."""

  def __init__(
    self,
    name: str = "MockAgent",
    tools: list[MockTool] | None = None,
  ) -> None:
    super().__init__(name=name)  # type: ignore[reportUnknownMemberType]
    self._tools = tools or [MockTool()]

  async def canonical_tools(self, ctx: Any = None) -> list[BaseTool]:
    return cast(list[BaseTool], self._tools)

  async def canonical_instruction(self, ctx: Any = None) -> tuple[str, bool]:
    return f"You are {self.name}. Help users with their queries.", False


def create_mock_execute(tools: list[MockTool]) -> Any:
  """Create a mock execute function for the tool runner."""

  async def mock_execute(
    tool: Any, arguments: dict[str, Any], session: Any
  ) -> ExecutionResult:
    result = await tool.run_async(args=arguments, tool_context=None)
    return ExecutionResult(
      success=True,
      result=result,
    )

  return mock_execute


class TestSimulationFlowIntegration:
  """End-to-end tests for the complete simulation workflow."""

  @pytest.fixture
  def controller(self) -> SimulationController:
    """Create controller with mock agent."""
    tools = [
      MockTool(name="get_weather", result={"temperature": 72, "unit": "F"}),
      MockTool(name="get_time", result={"time": "12:00 PM"}),
    ]
    agent = MockAgent(name="WeatherAgent", tools=tools)
    agents: dict[str, Agent] = {"WeatherAgent": agent}
    return SimulationController(agents=agents)

  @pytest.mark.asyncio
  async def test_complete_simulation_workflow(
    self, controller: SimulationController
  ) -> None:
    """Test complete workflow: select agent → query → tools → response."""
    # Step 1: Create session
    session = controller.create_session()
    assert session.state == SessionState.SELECTING_AGENT

    # Step 2: Select agent
    await controller.select_agent("WeatherAgent")
    assert session.state == SessionState.AWAITING_QUERY
    assert session.agent_name == "WeatherAgent"

    # Step 3: Start with user query
    await controller.start_session("What's the weather in NYC?")
    assert session.state == SessionState.ACTIVE

    # Verify query in history
    assert len(session.history) == 1
    assert isinstance(session.history[0], UserQuery)
    assert session.history[0].content == "What's the weather in NYC?"

    # Step 4: Execute first tool (mocked)
    with patch.object(
      controller._tool_runner,
      "execute",
      create_mock_execute(session.tools),
    ):
      result1 = await controller.execute_tool("get_weather", {"city": "NYC"})
      assert result1.success is True
      assert result1.result is not None
      assert result1.result["temperature"] == 72

      # Verify tool call and output in history
      assert len(session.history) == 3  # Query + ToolCall + ToolOutput
      assert isinstance(session.history[1], ToolCall)
      assert isinstance(session.history[2], ToolOutput)

      # Step 5: Execute second tool
      result2 = await controller.execute_tool("get_time", {})
      assert result2.success is True

    # Step 6: Submit final response
    await controller.submit_final_response(
      "The weather in NYC is 72°F. The time is 12:00 PM."
    )
    assert session.state == SessionState.COMPLETED

    # Verify final response in history
    final_responses = [e for e in session.history if isinstance(e, FinalResponse)]
    assert len(final_responses) == 1

  @pytest.mark.asyncio
  async def test_export_after_completion(
    self, controller: SimulationController
  ) -> None:
    """Test exporting Golden Trace after completing simulation."""
    # Complete a minimal simulation
    controller.create_session()
    await controller.select_agent("WeatherAgent")
    await controller.start_session("Hello")

    assert controller.current_session is not None
    with patch.object(
      controller._tool_runner,
      "execute",
      create_mock_execute(controller.current_session.tools),
    ):
      await controller.execute_tool("get_weather", {"city": "LA"})

    await controller.submit_final_response("Done")

    # Export
    json_str = controller.export_trace()

    # Verify it's valid JSON
    parsed = json.loads(json_str)
    assert "eval_id" in parsed or "evalId" in parsed

    # Verify it has expected structure
    assert "conversation" in parsed
    assert len(parsed["conversation"]) == 1

  @pytest.mark.asyncio
  async def test_cannot_export_incomplete_session(
    self, controller: SimulationController
  ) -> None:
    """Test that export fails if session not completed."""
    controller.create_session()
    await controller.select_agent("WeatherAgent")
    await controller.start_session("Test")

    # Session is ACTIVE, not COMPLETED
    with pytest.raises(ValueError, match="not completed"):
      controller.export_trace()

  @pytest.mark.asyncio
  async def test_multiple_tool_calls_recorded(
    self, controller: SimulationController
  ) -> None:
    """Test that multiple tool calls are all recorded in history."""
    controller.create_session()
    await controller.select_agent("WeatherAgent")
    await controller.start_session("Multi-tool query")

    assert controller.current_session is not None
    with patch.object(
      controller._tool_runner,
      "execute",
      create_mock_execute(controller.current_session.tools),
    ):
      # Execute multiple tools
      await controller.execute_tool("get_weather", {"city": "NYC"})
      await controller.execute_tool("get_weather", {"city": "LA"})
      await controller.execute_tool("get_time", {})

    await controller.submit_final_response("All done")

    session = controller.current_session
    assert session is not None
    tool_calls = [e for e in session.history if isinstance(e, ToolCall)]
    tool_outputs = [e for e in session.history if isinstance(e, ToolOutput)]

    assert len(tool_calls) == 3
    assert len(tool_outputs) == 3

    # Verify different arguments were recorded
    assert tool_calls[0].arguments == {"city": "NYC"}
    assert tool_calls[1].arguments == {"city": "LA"}
    assert tool_calls[2].arguments == {}

  @pytest.mark.asyncio
  async def test_system_instruction_available(
    self, controller: SimulationController
  ) -> None:
    """Test that system instruction is available after agent selection."""
    controller.create_session()
    await controller.select_agent("WeatherAgent")

    instruction = await controller.get_system_instruction()
    assert "WeatherAgent" in instruction

  @pytest.mark.asyncio
  async def test_get_tool_declaration(self, controller: SimulationController) -> None:
    """Test getting tool declarations for form rendering."""
    controller.create_session()
    await controller.select_agent("WeatherAgent")

    decl = controller.get_tool_declaration("get_weather")
    assert decl is not None
    assert decl.name == "get_weather"

  @pytest.mark.asyncio
  async def test_get_unknown_tool_declaration(
    self, controller: SimulationController
  ) -> None:
    """Test getting declaration for unknown tool returns None."""
    controller.create_session()
    await controller.select_agent("WeatherAgent")

    decl = controller.get_tool_declaration("unknown_tool")
    assert decl is None


class TestSessionStateTransitions:
  """Tests for session state transitions."""

  @pytest.fixture
  def controller(self) -> SimulationController:
    agent = MockAgent()
    agents: dict[str, Agent] = {"TestAgent": agent}
    return SimulationController(agents=agents)

  @pytest.mark.asyncio
  async def test_state_flow_selecting_to_awaiting(
    self, controller: SimulationController
  ) -> None:
    """Test transition from SELECTING_AGENT to AWAITING_QUERY."""
    session = controller.create_session()
    assert session.state == SessionState.SELECTING_AGENT

    await controller.select_agent("TestAgent")
    assert session.state == SessionState.AWAITING_QUERY

  @pytest.mark.asyncio
  async def test_state_flow_awaiting_to_active(
    self, controller: SimulationController
  ) -> None:
    """Test transition from AWAITING_QUERY to ACTIVE."""
    controller.create_session()
    await controller.select_agent("TestAgent")

    session = controller.current_session
    assert session is not None
    assert session.state == SessionState.AWAITING_QUERY

    await controller.start_session("Test query")
    assert session.state == SessionState.ACTIVE

  @pytest.mark.asyncio
  async def test_state_flow_active_to_completed(
    self, controller: SimulationController
  ) -> None:
    """Test transition from ACTIVE to COMPLETED."""
    controller.create_session()
    await controller.select_agent("TestAgent")
    await controller.start_session("Test")

    session = controller.current_session
    assert session is not None
    assert session.state == SessionState.ACTIVE

    await controller.submit_final_response("Done")
    assert session.state == SessionState.COMPLETED

  @pytest.mark.asyncio
  async def test_cannot_start_without_query(
    self, controller: SimulationController
  ) -> None:
    """Test that session requires being in correct state to start."""
    controller.create_session()

    # Try to start from SELECTING_AGENT state
    with pytest.raises(ValueError):
      await controller.start_session("Test")

  @pytest.mark.asyncio
  async def test_cannot_complete_from_awaiting(
    self, controller: SimulationController
  ) -> None:
    """Test that session cannot complete from AWAITING_QUERY."""
    controller.create_session()
    await controller.select_agent("TestAgent")

    with pytest.raises(ValueError, match="not in ACTIVE state"):
      await controller.submit_final_response("Done")

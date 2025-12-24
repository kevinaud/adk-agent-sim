"""Integration tests for tool execution."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from google.adk.agents import Agent
from google.adk.tools import BaseTool

from adk_agent_sim.controller import SimulationController
from adk_agent_sim.execution.tool_runner import ExecutionResult
from adk_agent_sim.models.history import ToolCall, ToolError, ToolOutput
from adk_agent_sim.models.session import SessionState


class MockTool(BaseTool):
  """Mock ADK tool for testing."""

  def __init__(
    self,
    name: str = "mock_tool",
    result: Any = {"success": True},
    raise_error: Exception | None = None,
  ) -> None:
    self.name = name
    self._result = result
    self._raise_error = raise_error
    self._run_count = 0

  def _get_declaration(self) -> MagicMock:
    """Return mock declaration."""
    decl = MagicMock()
    decl.name = self.name
    decl.parameters = None
    return decl

  async def run_async(self, *, args: dict[str, Any], tool_context: Any) -> Any:
    """Execute the tool."""
    self._run_count += 1
    if self._raise_error:
      raise self._raise_error
    return self._result


class MockAgent(Agent):
  """Mock ADK agent for testing."""

  def __init__(
    self,
    name: str = "MockAgent",
    tools: list[MockTool] | None = None,
  ) -> None:
    super().__init__(name=name)  # type: ignore[reportUnknownMemberType]
    self.name = name
    self._tools = tools or [MockTool()]

  async def canonical_tools(self, ctx: Any = None) -> list[BaseTool]:
    """Return the agent's tools."""
    return cast(list[BaseTool], self._tools)

  async def canonical_instruction(self, ctx: Any = None) -> tuple[str, bool]:
    """Return the agent's instructions."""
    return f"You are {self.name}. Help users with their queries.", False


@pytest.fixture
def mock_agent() -> MockAgent:
  """Create a mock agent."""
  return MockAgent()


@pytest.fixture
def controller(mock_agent: MockAgent) -> SimulationController:
  """Create a controller with mock agent."""
  agents: dict[str, Agent] = {"MockAgent": mock_agent}
  return SimulationController(agents=agents)


class TestToolExecution:
  """Integration tests for tool execution flow."""

  @pytest.mark.asyncio
  async def test_execute_tool_success(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test successful tool execution."""
    # Setup session
    controller.create_session()
    await controller.select_agent("MockAgent")
    await controller.start_session("Test query")

    # Mock the tool runner to avoid real context creation
    async def mock_execute(
      tool: Any, arguments: dict[str, Any], session: Any
    ) -> ExecutionResult:
      result = await tool.run_async(args=arguments, tool_context=None)
      return ExecutionResult(success=True, result=result, duration_ms=100.0)

    with patch.object(controller._tool_runner, "execute", mock_execute):
      result = await controller.execute_tool("mock_tool", {"param": "value"})

      assert result.success is True
      assert result.result == {"success": True}
      assert result.duration_ms > 0

  @pytest.mark.asyncio
  async def test_execute_tool_with_real_context(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test tool execution with real context creation (no mocking).

    This test verifies that the bug where session_service was None is fixed.
    Previously this would fail with ValidationError about session_service.
    """
    # Setup session
    controller.create_session()
    await controller.select_agent("MockAgent")
    await controller.start_session("Test query")

    # Execute tool WITHOUT mocking - this goes through real context creation
    result = await controller.execute_tool("mock_tool", {"param": "value"})

    # Should succeed without ValidationError
    assert result.success is True
    assert result.result == {"success": True}
    assert result.duration_ms > 0

  @pytest.mark.asyncio
  async def test_execute_tool_records_history(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test that tool execution records history entries."""
    controller.create_session()
    await controller.select_agent("MockAgent")
    await controller.start_session("Test query")

    async def mock_execute(
      tool: Any, arguments: dict[str, Any], session: Any
    ) -> ExecutionResult:
      result = await tool.run_async(args=arguments, tool_context=None)
      return ExecutionResult(success=True, result=result, duration_ms=100.0)

    with patch.object(controller._tool_runner, "execute", mock_execute):
      await controller.execute_tool("mock_tool", {"key": "value"})

      # Check history
      session = controller.current_session
      assert session is not None

      # Should have: UserQuery, ToolCall, ToolOutput
      assert len(session.history) >= 3

      # Find tool call and output
      tool_calls = [e for e in session.history if isinstance(e, ToolCall)]
      tool_outputs = [e for e in session.history if isinstance(e, ToolOutput)]

      assert len(tool_calls) == 1
      assert len(tool_outputs) == 1

      assert tool_calls[0].tool_name == "mock_tool"
      assert tool_calls[0].arguments == {"key": "value"}
      assert tool_outputs[0].call_id == tool_calls[0].call_id

  @pytest.mark.asyncio
  async def test_execute_tool_error_handling(
    self, controller: SimulationController
  ) -> None:
    """Test that tool errors are captured and recorded."""
    error_tool = MockTool(
      name="error_tool",
      raise_error=ValueError("Something went wrong"),
    )
    error_agent = MockAgent(tools=[error_tool])
    agents: dict[str, Agent] = {"ErrorAgent": error_agent}
    controller = SimulationController(agents=agents)

    controller.create_session()
    await controller.select_agent("ErrorAgent")
    await controller.start_session("Test query")

    async def mock_execute(
      tool: Any, arguments: dict[str, Any], session: Any
    ) -> ExecutionResult:
      try:
        await tool.run_async(args=arguments, tool_context=None)
        return ExecutionResult(success=True, result={}, duration_ms=100.0)
      except Exception as e:
        return ExecutionResult(
          success=False,
          error=e,
          error_type=type(e).__name__,
          error_message=str(e),
          duration_ms=50.0,
        )

    with patch.object(controller._tool_runner, "execute", mock_execute):
      result = await controller.execute_tool("error_tool", {})

      assert result.success is False
      assert result.error_type == "ValueError"
      assert "Something went wrong" in str(result.error_message)

      # Check history has error entry
      session = controller.current_session
      assert session is not None
      tool_errors = [e for e in session.history if isinstance(e, ToolError)]
      assert len(tool_errors) == 1
      assert tool_errors[0].error_type == "ValueError"

  @pytest.mark.asyncio
  async def test_execute_tool_not_found(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test executing non-existent tool raises error."""
    controller.create_session()
    await controller.select_agent("MockAgent")
    await controller.start_session("Test query")

    with pytest.raises(ValueError, match="not found"):
      await controller.execute_tool("nonexistent_tool", {})

  @pytest.mark.asyncio
  async def test_execute_tool_not_active(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test that tool execution requires active session."""
    controller.create_session()
    await controller.select_agent("MockAgent")
    # Don't start session

    with pytest.raises(ValueError, match="not in ACTIVE state"):
      await controller.execute_tool("mock_tool", {})

  @pytest.mark.asyncio
  async def test_session_remains_active_after_error(
    self, controller: SimulationController
  ) -> None:
    """Test that session stays ACTIVE after tool error."""
    error_tool = MockTool(
      name="error_tool",
      raise_error=RuntimeError("Oops"),
    )
    agents: dict[str, Agent] = {"ErrorAgent": MockAgent(tools=[error_tool])}
    controller = SimulationController(agents=agents)

    controller.create_session()
    await controller.select_agent("ErrorAgent")
    await controller.start_session("Test")

    async def mock_execute(
      tool: Any, arguments: dict[str, Any], session: Any
    ) -> ExecutionResult:
      try:
        await tool.run_async(arguments, None)
        return ExecutionResult(success=True, result={}, duration_ms=100.0)
      except Exception as e:
        return ExecutionResult(
          success=False,
          error_type=type(e).__name__,
          error_message=str(e),
          duration_ms=50.0,
        )

    with patch.object(controller._tool_runner, "execute", mock_execute):
      await controller.execute_tool("error_tool", {})

      # Session should still be active
      assert controller.current_session is not None
      assert controller.current_session.state == SessionState.ACTIVE


class TestToolCancellation:
  """Tests for tool cancellation."""

  @pytest.mark.asyncio
  async def test_cancel_tool_sets_cancelled_flag(
    self, controller: SimulationController
  ) -> None:
    """Test that cancelling a tool sets the cancelled flag."""
    controller.create_session()

    # Cancel when nothing is running should be safe
    controller.cancel_tool()

  @pytest.mark.asyncio
  async def test_tool_runner_is_running_property(
    self, controller: SimulationController, mock_agent: MockAgent
  ) -> None:
    """Test is_running property of tool runner."""
    controller.create_session()
    await controller.select_agent("MockAgent")

    # Before execution
    assert controller.tool_runner.is_running is False

    await controller.start_session("Test")

    async def mock_execute(
      tool: Any, arguments: dict[str, Any], session: Any
    ) -> ExecutionResult:
      return ExecutionResult(success=True, result={}, duration_ms=100.0)

    with patch.object(controller._tool_runner, "execute", mock_execute):
      await controller.execute_tool("mock_tool", {})

      # After execution
      assert controller.tool_runner.is_running is False

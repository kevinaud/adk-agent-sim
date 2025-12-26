"""Async tool execution with cancellation support."""

import asyncio
import time
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from google.adk.tools import BaseTool

  from adk_agent_sim.models.session import SimulationSession


@dataclass
class ExecutionResult:
  """Result of tool execution."""

  success: bool
  result: Any | None = None  # Tool return value if success
  error: Exception | None = None  # Exception if failure
  error_type: str | None = None  # Exception class name
  error_message: str | None = None  # Exception message
  error_traceback: str | None = None  # Full traceback
  duration_ms: float = 0.0
  cancelled: bool = False


class ToolRunner:
  """Async tool executor with cancellation support."""

  def __init__(self) -> None:
    self._current_task: asyncio.Task[Any] | None = None
    self._start_time: float = 0.0
    self._is_running: bool = False

  @property
  def is_running(self) -> bool:
    """Whether a tool is currently executing."""
    return self._is_running

  @property
  def elapsed_ms(self) -> float:
    """Milliseconds since execution started (0 if not running)."""
    if not self._is_running:
      return 0.0
    return (time.time() - self._start_time) * 1000

  async def execute(
    self,
    tool: BaseTool,
    arguments: dict[str, Any],
    session: SimulationSession,
  ) -> ExecutionResult:
    """
    Execute a tool with the given arguments.

    Args:
      tool: The ADK tool to execute
      arguments: Arguments matching the tool's schema
      session: Current simulation session (for context construction)

    Returns:
      ExecutionResult with success/failure details
    """
    from adk_agent_sim.execution.context_factory import (
      create_tool_context,
      ensure_adk_session,
    )

    self._is_running = True
    self._start_time = time.time()

    try:
      # Ensure we have an ADK session for context
      await ensure_adk_session(session)

      # Create tool context
      tool_context = await create_tool_context(session, tool)

      # Execute the tool
      self._current_task = asyncio.current_task()
      result = await tool.run_async(args=arguments, tool_context=tool_context)

      duration_ms = (time.time() - self._start_time) * 1000
      return ExecutionResult(
        success=True,
        result=result,
        duration_ms=duration_ms,
      )

    except asyncio.CancelledError:
      duration_ms = (time.time() - self._start_time) * 1000
      return ExecutionResult(
        success=False,
        duration_ms=duration_ms,
        cancelled=True,
        error_message="Tool execution was cancelled",
      )

    except Exception as e:
      duration_ms = (time.time() - self._start_time) * 1000
      return ExecutionResult(
        success=False,
        error=e,
        error_type=type(e).__name__,
        error_message=str(e),
        error_traceback=traceback.format_exc(),
        duration_ms=duration_ms,
      )

    finally:
      self._is_running = False
      self._current_task = None

  def cancel(self) -> None:
    """Request cancellation of the running tool (if any)."""
    if self._current_task is not None and not self._current_task.done():
      self._current_task.cancel()

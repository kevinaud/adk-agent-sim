"""History entry types for simulation sessions."""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Union

from pydantic import BaseModel, Field


def _now() -> datetime:
  """Return current UTC datetime."""
  return datetime.now(timezone.utc)


def _new_call_id() -> str:
  """Generate a unique call ID."""
  return str(uuid.uuid4())


class UserQuery(BaseModel):
  """Initial user query to start the session."""

  type: Literal["user_query"] = "user_query"
  content: str = Field(description="User's input text or structured data as JSON")
  timestamp: datetime = Field(default_factory=_now)


class ToolCall(BaseModel):
  """Records a tool invocation request."""

  type: Literal["tool_call"] = "tool_call"
  tool_name: str
  arguments: dict[str, Any]
  call_id: str = Field(
    default_factory=_new_call_id,
    description="Unique ID for correlating with response",
  )
  timestamp: datetime = Field(default_factory=_now)


class ToolOutput(BaseModel):
  """Records a successful tool execution result."""

  type: Literal["tool_output"] = "tool_output"
  call_id: str = Field(description="Correlates with ToolCall.call_id")
  result: Any = Field(description="Tool return value")
  duration_ms: float = Field(description="Execution time in milliseconds")
  timestamp: datetime = Field(default_factory=_now)


class ToolError(BaseModel):
  """Records a failed tool execution."""

  type: Literal["tool_error"] = "tool_error"
  call_id: str = Field(description="Correlates with ToolCall.call_id")
  error_type: str = Field(description="Exception class name")
  error_message: str = Field(description="Exception message")
  traceback: str | None = Field(default=None, description="Full traceback if available")
  duration_ms: float = Field(description="Time until failure in milliseconds")
  timestamp: datetime = Field(default_factory=_now)


class FinalResponse(BaseModel):
  """Records the human's final answer."""

  type: Literal["final_response"] = "final_response"
  content: str = Field(description="Final response text or structured data as JSON")
  timestamp: datetime = Field(default_factory=_now)


# Discriminated union for type-safe history handling
HistoryEntry = Union[UserQuery, ToolCall, ToolOutput, ToolError, FinalResponse]

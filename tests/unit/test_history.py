"""Unit tests for history entry models."""

from __future__ import annotations

from datetime import datetime, timezone

from adk_agent_sim.models.history import (
  FinalResponse,
  HistoryEntry,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)


class TestUserQuery:
  """Tests for UserQuery history entry."""

  def test_user_query_creation(self) -> None:
    """Test creating a UserQuery entry."""
    entry = UserQuery(content="What is the weather?")
    assert entry.content == "What is the weather?"
    assert entry.type == "user_query"

  def test_user_query_has_timestamp(self) -> None:
    """Test that UserQuery gets a timestamp."""
    before = datetime.now(timezone.utc)
    entry = UserQuery(content="Test")
    after = datetime.now(timezone.utc)
    assert before <= entry.timestamp <= after


class TestToolCall:
  """Tests for ToolCall history entry."""

  def test_tool_call_creation(self) -> None:
    """Test creating a ToolCall entry."""
    entry = ToolCall(tool_name="get_weather", arguments={"city": "NYC"})
    assert entry.tool_name == "get_weather"
    assert entry.arguments == {"city": "NYC"}
    assert entry.type == "tool_call"

  def test_tool_call_has_unique_id(self) -> None:
    """Test that ToolCall gets a unique call_id."""
    entry1 = ToolCall(tool_name="tool1", arguments={})
    entry2 = ToolCall(tool_name="tool2", arguments={})
    assert entry1.call_id != entry2.call_id

  def test_tool_call_empty_arguments(self) -> None:
    """Test ToolCall with no arguments."""
    entry = ToolCall(tool_name="no_args_tool", arguments={})
    assert entry.arguments == {}


class TestToolOutput:
  """Tests for ToolOutput history entry."""

  def test_tool_output_creation(self) -> None:
    """Test creating a ToolOutput entry."""
    entry = ToolOutput(
      call_id="abc123",
      result={"temperature": 72},
      duration_ms=150.5,
    )
    assert entry.call_id == "abc123"
    assert entry.result == {"temperature": 72}
    assert entry.duration_ms == 150.5
    assert entry.type == "tool_output"

  def test_tool_output_string_result(self) -> None:
    """Test ToolOutput with string result."""
    entry = ToolOutput(call_id="xyz", result="Success", duration_ms=100.0)
    assert entry.result == "Success"

  def test_tool_output_none_result(self) -> None:
    """Test ToolOutput with None result."""
    entry = ToolOutput(call_id="xyz", result=None, duration_ms=50.0)
    assert entry.result is None


class TestToolError:
  """Tests for ToolError history entry."""

  def test_tool_error_creation(self) -> None:
    """Test creating a ToolError entry."""
    entry = ToolError(
      call_id="abc123",
      error_type="ValueError",
      error_message="Invalid argument",
      duration_ms=75.0,
    )
    assert entry.call_id == "abc123"
    assert entry.error_type == "ValueError"
    assert entry.error_message == "Invalid argument"
    assert entry.duration_ms == 75.0
    assert entry.type == "tool_error"

  def test_tool_error_with_traceback(self) -> None:
    """Test ToolError with traceback."""
    entry = ToolError(
      call_id="xyz",
      error_type="RuntimeError",
      error_message="Something failed",
      traceback="Traceback (most recent call last):\n...",
      duration_ms=100.0,
    )
    assert entry.traceback is not None
    assert "Traceback" in entry.traceback

  def test_tool_error_without_traceback(self) -> None:
    """Test ToolError without traceback."""
    entry = ToolError(
      call_id="xyz",
      error_type="KeyError",
      error_message="Key not found",
      duration_ms=25.0,
    )
    assert entry.traceback is None


class TestFinalResponse:
  """Tests for FinalResponse history entry."""

  def test_final_response_creation(self) -> None:
    """Test creating a FinalResponse entry."""
    entry = FinalResponse(content="The weather in NYC is 72°F")
    assert entry.content == "The weather in NYC is 72°F"
    assert entry.type == "final_response"

  def test_final_response_has_timestamp(self) -> None:
    """Test that FinalResponse gets a timestamp."""
    before = datetime.now(timezone.utc)
    entry = FinalResponse(content="Done")
    after = datetime.now(timezone.utc)
    assert before <= entry.timestamp <= after


class TestHistoryEntryUnion:
  """Tests for the HistoryEntry discriminated union."""

  def test_all_types_are_valid_history_entries(self) -> None:
    """Test that all entry types are valid HistoryEntry instances."""
    entries: list[HistoryEntry] = [
      UserQuery(content="Test query"),
      ToolCall(tool_name="test_tool", arguments={}),
      ToolOutput(call_id="id1", result="result", duration_ms=100.0),
      ToolError(
        call_id="id2",
        error_type="Error",
        error_message="msg",
        duration_ms=50.0,
      ),
      FinalResponse(content="Final"),
    ]

    # All should be processable as HistoryEntry
    for entry in entries:
      assert hasattr(entry, "type")
      assert hasattr(entry, "timestamp")

  def test_discriminated_by_type_field(self) -> None:
    """Test that entries can be discriminated by type field."""
    entries = [
      UserQuery(content="Q"),
      ToolCall(tool_name="T", arguments={}),
      ToolOutput(call_id="C", result=None, duration_ms=0.0),
      ToolError(call_id="C", error_type="E", error_message="M", duration_ms=0.0),
      FinalResponse(content="F"),
    ]

    types = [e.type for e in entries]
    assert types == [
      "user_query",
      "tool_call",
      "tool_output",
      "tool_error",
      "final_response",
    ]

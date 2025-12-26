"""Unit tests for Golden Trace export."""

import json
from unittest.mock import MagicMock

from adk_agent_sim.export.golden_trace import GoldenTraceBuilder
from adk_agent_sim.models.history import (
  FinalResponse,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.models.session import SimulationSession


class TestGoldenTraceBuilder:
  """Tests for GoldenTraceBuilder."""

  def _create_completed_session(
    self,
    agent_name: str = "TestAgent",
    query: str = "What is 2+2?",
    response: str = "The answer is 4.",
  ) -> SimulationSession:
    """Create a completed session for testing."""
    session = SimulationSession()
    session.select_agent(agent_name, MagicMock(), [])
    session.add_history_entry(UserQuery(content=query))
    session.start_session()
    session.add_history_entry(FinalResponse(content=response))
    session.complete_session()
    return session

  def test_generate_eval_id_snake_case(self) -> None:
    """Test that eval_id uses snake_case agent name."""
    session = self._create_completed_session(agent_name="MyTestAgent")
    builder = GoldenTraceBuilder(session)
    eval_id = builder._generate_eval_id()

    assert "my_test_agent" in eval_id
    # Should have timestamp suffix
    assert "_" in eval_id
    # Should match pattern: snake_name_timestamp
    parts = eval_id.rsplit("_", 1)
    assert len(parts) == 2

  def test_generate_eval_id_handles_special_characters(self) -> None:
    """Test that eval_id handles special characters."""
    session = self._create_completed_session(agent_name="Test-Agent 123!")
    builder = GoldenTraceBuilder(session)
    eval_id = builder._generate_eval_id()

    # Should not contain special chars
    assert "-" not in eval_id.split("_")[0]  # Before timestamp
    assert " " not in eval_id
    assert "!" not in eval_id

  def test_extract_user_query(self) -> None:
    """Test extracting user query from history."""
    session = self._create_completed_session(query="Hello, world!")
    builder = GoldenTraceBuilder(session)
    content = builder._extract_user_query()

    assert content.role == "user"
    assert content.parts is not None
    assert len(content.parts) == 1
    assert content.parts[0].text == "Hello, world!"

  def test_extract_final_response(self) -> None:
    """Test extracting final response from history."""
    session = self._create_completed_session(response="Goodbye!")
    builder = GoldenTraceBuilder(session)
    content = builder._extract_final_response()

    assert content.role == "model"
    assert content.parts is not None
    assert len(content.parts) == 1
    assert content.parts[0].text == "Goodbye!"

  def test_extract_tool_data_empty(self) -> None:
    """Test extracting tool data when no tools were called."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    tool_uses, tool_responses = builder._extract_tool_data()

    assert tool_uses == []
    assert tool_responses == []

  def test_extract_tool_data_with_tool_call(self) -> None:
    """Test extracting tool data with tool calls."""
    session = SimulationSession()
    session.select_agent("TestAgent", MagicMock(), [])
    session.add_history_entry(UserQuery(content="Test"))
    session.start_session()

    # Add a tool call and output
    tool_call = ToolCall(tool_name="add", arguments={"a": 1, "b": 2})
    session.add_history_entry(tool_call)
    session.add_history_entry(
      ToolOutput(call_id=tool_call.call_id, result={"sum": 3}, duration_ms=100.0)
    )

    session.add_history_entry(FinalResponse(content="Done"))
    session.complete_session()

    builder = GoldenTraceBuilder(session)
    tool_uses, tool_responses = builder._extract_tool_data()

    assert len(tool_uses) == 1
    assert tool_uses[0].name == "add"
    assert tool_uses[0].args == {"a": 1, "b": 2}

    assert len(tool_responses) == 1
    assert tool_responses[0].response == {"sum": 3}

  def test_extract_tool_data_with_tool_error(self) -> None:
    """Test extracting tool data with tool errors."""
    session = SimulationSession()
    session.select_agent("TestAgent", MagicMock(), [])
    session.add_history_entry(UserQuery(content="Test"))
    session.start_session()

    # Add a tool call that failed
    tool_call = ToolCall(tool_name="fail_tool", arguments={})
    session.add_history_entry(tool_call)
    session.add_history_entry(
      ToolError(
        call_id=tool_call.call_id,
        error_type="ValueError",
        error_message="Something failed",
        duration_ms=50.0,
      )
    )

    session.add_history_entry(FinalResponse(content="Error handled"))
    session.complete_session()

    builder = GoldenTraceBuilder(session)
    tool_uses, tool_responses = builder._extract_tool_data()

    assert len(tool_uses) == 1
    assert len(tool_responses) == 1

    # Error should be in response format
    error_resp = tool_responses[0].response
    assert error_resp is not None
    assert error_resp["error"] is True
    assert error_resp["error_type"] == "ValueError"
    assert error_resp["error_message"] == "Something failed"

  def test_build_creates_eval_case(self) -> None:
    """Test that build() creates a valid EvalCase."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    eval_case = builder.build()

    assert eval_case.eval_id is not None
    assert eval_case.conversation is not None
    assert len(eval_case.conversation) == 1
    assert eval_case.creation_timestamp is not None

  def test_export_json_returns_valid_json(self) -> None:
    """Test that export_json returns valid JSON."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    json_str = builder.export_json()

    # Should be parseable
    parsed = json.loads(json_str)
    assert "eval_id" in parsed or "evalId" in parsed

  def test_serialize_result_dict(self) -> None:
    """Test serializing dict result."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    result = builder._serialize_result({"key": "value"})
    assert result == {"key": "value"}

  def test_serialize_result_primitive(self) -> None:
    """Test serializing primitive results."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)

    assert builder._serialize_result("string") == {"result": "string"}
    assert builder._serialize_result(42) == {"result": 42}
    assert builder._serialize_result(3.14) == {"result": 3.14}
    assert builder._serialize_result(True) == {"result": True}

  def test_serialize_result_none(self) -> None:
    """Test serializing None result."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    assert builder._serialize_result(None) == {"result": None}

  def test_serialize_result_list(self) -> None:
    """Test serializing list result."""
    session = self._create_completed_session()
    builder = GoldenTraceBuilder(session)
    result = builder._serialize_result([1, 2, 3])
    assert result == {"result": [1, 2, 3]}

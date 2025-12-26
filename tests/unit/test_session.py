"""Unit tests for SimulationSession state machine."""

from unittest.mock import MagicMock

import pytest
from google.adk.agents import Agent

from adk_agent_sim.models.history import UserQuery
from adk_agent_sim.models.session import SessionState, SimulationSession


class TestSessionState:
  """Tests for the SessionState enum."""

  def test_session_states_exist(self) -> None:
    """Test that all expected session states exist."""
    assert SessionState.SELECTING_AGENT is not None
    assert SessionState.AWAITING_QUERY is not None
    assert SessionState.ACTIVE is not None
    assert SessionState.COMPLETED is not None

  def test_session_state_values(self) -> None:
    """Test session state string values."""
    assert SessionState.SELECTING_AGENT.value == "selecting_agent"
    assert SessionState.AWAITING_QUERY.value == "awaiting_query"
    assert SessionState.ACTIVE.value == "active"
    assert SessionState.COMPLETED.value == "completed"


class TestSimulationSession:
  """Tests for the SimulationSession model."""

  def test_initial_state(self) -> None:
    """Test that new sessions start in SELECTING_AGENT state."""
    session = SimulationSession()
    assert session.state == SessionState.SELECTING_AGENT

  def test_session_has_unique_id(self) -> None:
    """Test that each session gets a unique ID."""
    session1 = SimulationSession()
    session2 = SimulationSession()
    assert session1.session_id != session2.session_id

  def test_initial_history_is_empty(self) -> None:
    """Test that new sessions have empty history."""
    session = SimulationSession()
    assert session.history == []

  def test_select_agent_transitions_state(self) -> None:
    """Test that selecting an agent transitions to AWAITING_QUERY."""
    session = SimulationSession()
    # Create mock agent and tools
    mock_agent = MagicMock(spec=Agent)
    session.select_agent("TestAgent", mock_agent, [])
    assert session.state == SessionState.AWAITING_QUERY
    assert session.agent_name == "TestAgent"

  def test_start_session_transitions_state(self) -> None:
    """Test that starting session transitions to ACTIVE."""
    session = SimulationSession()
    mock_agent = MagicMock(spec=Agent)
    session.select_agent("TestAgent", mock_agent, [])
    session.start_session()
    assert session.state == SessionState.ACTIVE

  def test_complete_session_transitions_state(self) -> None:
    """Test that completing session transitions to COMPLETED."""
    session = SimulationSession()
    mock_agent = MagicMock(spec=Agent)
    session.select_agent("TestAgent", mock_agent, [])
    session.start_session()
    session.complete_session()
    assert session.state == SessionState.COMPLETED

  def test_add_history_entry(self) -> None:
    """Test adding entries to history."""
    session = SimulationSession()
    entry = UserQuery(content="Hello")
    session.add_history_entry(entry)
    assert len(session.history) == 1
    assert session.history[0] == entry

  def test_get_tool_by_name_returns_none_when_empty(self) -> None:
    """Test get_tool_by_name returns None for unknown tool."""
    session = SimulationSession()
    assert session.get_tool_by_name("unknown") is None

  def test_invalid_state_transition_select_agent(self) -> None:
    """Test that selecting agent from wrong state raises error."""
    session = SimulationSession()
    mock_agent = MagicMock(spec=Agent)
    session.select_agent("TestAgent", mock_agent, [])
    session.start_session()
    with pytest.raises(ValueError, match="Cannot select agent"):
      session.select_agent("Another", mock_agent, [])

  def test_invalid_state_transition_start_session(self) -> None:
    """Test that starting session from wrong state raises error."""
    session = SimulationSession()
    # Try to start without selecting agent
    with pytest.raises(ValueError, match="Cannot start session"):
      session.start_session()

  def test_invalid_state_transition_complete_session(self) -> None:
    """Test that completing session from wrong state raises error."""
    session = SimulationSession()
    # Try to complete without starting
    with pytest.raises(ValueError, match="Cannot complete session"):
      session.complete_session()

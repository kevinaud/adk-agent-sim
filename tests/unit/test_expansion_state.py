"""Unit tests for expansion state management."""

from adk_agent_sim.ui.components.expansion_state import ExpansionStateManager


class TestExpansionStateManager:
  """Tests for ExpansionStateManager."""

  def test_default_state_is_expanded(self) -> None:
    """Verify default state matches spec requirement (expanded).

    Acceptance Scenario 4: Tool outputs expanded by default.
    """
    manager = ExpansionStateManager()
    assert manager.get("event-1", "Arguments") is True
    assert manager.get("event-1", "Result") is True

  def test_custom_default_state(self) -> None:
    """Verify custom default can be set."""
    manager = ExpansionStateManager(default_expanded=False)
    assert manager.get("event-1", "Arguments") is False

  def test_set_and_get_state(self) -> None:
    """Verify state can be set and retrieved."""
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    assert manager.get("event-1", "Arguments") is False
    # Unset section should return default (True)
    assert manager.get("event-1", "Result") is True

  def test_set_preserves_other_sections(self) -> None:
    """Verify setting one section doesn't affect others."""
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    manager.set("event-1", "Result", True)
    assert manager.get("event-1", "Arguments") is False
    assert manager.get("event-1", "Result") is True

  def test_expand_all(self) -> None:
    """Verify expand_all expands all tracked sections.

    Acceptance Scenario 8: Expand All button works.
    """
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    manager.set("event-1", "Result", False)
    manager.expand_all("event-1")
    assert manager.get("event-1", "Arguments") is True
    assert manager.get("event-1", "Result") is True

  def test_collapse_all(self) -> None:
    """Verify collapse_all collapses all tracked sections.

    Acceptance Scenario 9: Collapse All button works.
    """
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", True)
    manager.set("event-1", "Result", True)
    manager.collapse_all("event-1")
    assert manager.get("event-1", "Arguments") is False
    assert manager.get("event-1", "Result") is False

  def test_expand_all_untracked_event(self) -> None:
    """Verify expand_all on untracked event is a no-op."""
    manager = ExpansionStateManager()
    # Should not raise
    manager.expand_all("nonexistent")
    # Default should still apply
    assert manager.get("nonexistent", "Arguments") is True

  def test_collapse_all_untracked_event(self) -> None:
    """Verify collapse_all on untracked event is a no-op."""
    manager = ExpansionStateManager()
    # Should not raise
    manager.collapse_all("nonexistent")
    # Default should still apply
    assert manager.get("nonexistent", "Arguments") is True

  def test_independent_events(self) -> None:
    """Verify different events have independent state.

    Acceptance Scenarios 5-6: State preserved per event.
    """
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    manager.set("event-2", "Arguments", True)
    assert manager.get("event-1", "Arguments") is False
    assert manager.get("event-2", "Arguments") is True

  def test_get_sections(self) -> None:
    """Verify get_sections returns tracked sections."""
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    manager.set("event-1", "Result", True)
    sections = manager.get_sections("event-1")
    assert "Arguments" in sections
    assert "Result" in sections
    assert len(sections) == 2

  def test_get_sections_untracked_event(self) -> None:
    """Verify get_sections returns empty list for untracked event."""
    manager = ExpansionStateManager()
    assert manager.get_sections("nonexistent") == []

  def test_clear(self) -> None:
    """Verify clear removes all tracked state."""
    manager = ExpansionStateManager()
    manager.set("event-1", "Arguments", False)
    manager.set("event-2", "Result", False)
    manager.clear()
    # After clear, should return defaults
    assert manager.get("event-1", "Arguments") is True
    assert manager.get("event-2", "Result") is True
    assert manager.get_sections("event-1") == []

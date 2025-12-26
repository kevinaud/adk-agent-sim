"""Unit tests for TreeExpansionState.

Tests state management for DevTools tree node expand/collapse behavior.
"""

from adk_agent_sim.ui.components.tree_expansion_state import (
  GlobalMode,
  TreeExpansionState,
)


class TestTreeExpansionStateInit:
  """Tests for TreeExpansionState initialization."""

  def test_default_values(self) -> None:
    """State initializes with sensible defaults."""
    state = TreeExpansionState()

    assert state.global_mode == GlobalMode.DEFAULT
    assert state.node_overrides == {}
    assert state.default_expanded is True

  def test_custom_default_expanded(self) -> None:
    """Can initialize with custom default_expanded value."""
    state = TreeExpansionState(default_expanded=False)

    assert state.default_expanded is False


class TestIsExpanded:
  """Tests for is_expanded() method."""

  def test_returns_default_when_no_override(self) -> None:
    """Returns default_expanded when no override exists."""
    state = TreeExpansionState(default_expanded=True)

    assert state.is_expanded("root.some.path") is True

  def test_returns_default_false_when_configured(self) -> None:
    """Respects default_expanded=False."""
    state = TreeExpansionState(default_expanded=False)

    assert state.is_expanded("root.some.path") is False

  def test_override_takes_precedence(self) -> None:
    """Node override takes precedence over default."""
    state = TreeExpansionState(default_expanded=True)
    state.node_overrides["root.specific.path"] = False

    assert state.is_expanded("root.specific.path") is False
    assert state.is_expanded("root.other.path") is True

  def test_global_all_expanded_overrides_default(self) -> None:
    """ALL_EXPANDED mode overrides default."""
    state = TreeExpansionState(default_expanded=False)
    state.global_mode = GlobalMode.ALL_EXPANDED

    assert state.is_expanded("root.any.path") is True

  def test_global_all_collapsed_overrides_default(self) -> None:
    """ALL_COLLAPSED mode overrides default."""
    state = TreeExpansionState(default_expanded=True)
    state.global_mode = GlobalMode.ALL_COLLAPSED

    assert state.is_expanded("root.any.path") is False

  def test_node_override_beats_global_mode(self) -> None:
    """Node override has highest priority over global mode."""
    state = TreeExpansionState()
    state.global_mode = GlobalMode.ALL_COLLAPSED
    state.node_overrides["root.special"] = True

    assert state.is_expanded("root.special") is True
    assert state.is_expanded("root.other") is False


class TestToggle:
  """Tests for toggle() method."""

  def test_toggle_creates_override_from_default(self) -> None:
    """Toggle creates override inverting default state."""
    state = TreeExpansionState(default_expanded=True)

    state.toggle("root.node")

    assert state.node_overrides["root.node"] is False
    assert state.is_expanded("root.node") is False

  def test_toggle_inverts_existing_override(self) -> None:
    """Toggle inverts existing override."""
    state = TreeExpansionState()
    state.node_overrides["root.node"] = False

    state.toggle("root.node")

    assert state.node_overrides["root.node"] is True
    assert state.is_expanded("root.node") is True

  def test_toggle_respects_global_mode(self) -> None:
    """Toggle creates override inverting global mode state."""
    state = TreeExpansionState()
    state.global_mode = GlobalMode.ALL_COLLAPSED

    state.toggle("root.node")

    # Was collapsed (due to global mode), now expanded
    assert state.node_overrides["root.node"] is True
    assert state.is_expanded("root.node") is True


class TestExpandAll:
  """Tests for expand_all() method."""

  def test_sets_global_mode_to_all_expanded(self) -> None:
    """expand_all() sets global mode."""
    state = TreeExpansionState()

    state.expand_all()

    assert state.global_mode == GlobalMode.ALL_EXPANDED

  def test_clears_node_overrides(self) -> None:
    """expand_all() clears existing overrides."""
    state = TreeExpansionState()
    state.node_overrides["root.a"] = False
    state.node_overrides["root.b"] = True

    state.expand_all()

    assert state.node_overrides == {}

  def test_all_nodes_expanded_after_call(self) -> None:
    """All nodes report expanded after expand_all()."""
    state = TreeExpansionState()
    state.node_overrides["root.collapsed"] = False

    state.expand_all()

    assert state.is_expanded("root.collapsed") is True
    assert state.is_expanded("root.any.path") is True


class TestCollapseAll:
  """Tests for collapse_all() method."""

  def test_sets_global_mode_to_all_collapsed(self) -> None:
    """collapse_all() sets global mode."""
    state = TreeExpansionState()

    state.collapse_all()

    assert state.global_mode == GlobalMode.ALL_COLLAPSED

  def test_clears_node_overrides(self) -> None:
    """collapse_all() clears existing overrides."""
    state = TreeExpansionState()
    state.node_overrides["root.a"] = True
    state.node_overrides["root.b"] = False

    state.collapse_all()

    assert state.node_overrides == {}

  def test_all_nodes_collapsed_after_call(self) -> None:
    """All nodes report collapsed after collapse_all()."""
    state = TreeExpansionState(default_expanded=True)
    state.node_overrides["root.expanded"] = True

    state.collapse_all()

    assert state.is_expanded("root.expanded") is False
    assert state.is_expanded("root.any.path") is False


class TestReset:
  """Tests for reset() method."""

  def test_resets_global_mode_to_default(self) -> None:
    """reset() sets global mode to DEFAULT."""
    state = TreeExpansionState()
    state.global_mode = GlobalMode.ALL_EXPANDED

    state.reset()

    assert state.global_mode == GlobalMode.DEFAULT

  def test_clears_node_overrides(self) -> None:
    """reset() clears existing overrides."""
    state = TreeExpansionState()
    state.node_overrides["root.a"] = True

    state.reset()

    assert state.node_overrides == {}

  def test_nodes_return_to_default_after_reset(self) -> None:
    """Nodes use default_expanded after reset()."""
    state = TreeExpansionState(default_expanded=True)
    state.global_mode = GlobalMode.ALL_COLLAPSED

    state.reset()

    assert state.is_expanded("root.any") is True


class TestPathBasedSparseStorage:
  """Tests for path-based sparse state storage (T017)."""

  def test_different_paths_independent(self) -> None:
    """Different paths maintain independent state."""
    state = TreeExpansionState(default_expanded=True)

    state.toggle("root.items[0]")
    state.toggle("root.items[1]")
    state.toggle("root.items[1]")  # Toggle back

    assert state.is_expanded("root.items[0]") is False
    assert state.is_expanded("root.items[1]") is True
    assert state.is_expanded("root.items[2]") is True  # Default

  def test_sparse_storage_efficiency(self) -> None:
    """Only toggled nodes are stored, not all possible nodes."""
    state = TreeExpansionState()

    # Simulate many potential nodes but only toggle a few
    state.toggle("root.a")
    state.toggle("root.deeply.nested.path")

    # Only 2 entries in overrides, not all possible paths
    assert len(state.node_overrides) == 2
    assert "root.a" in state.node_overrides
    assert "root.deeply.nested.path" in state.node_overrides

  def test_nested_path_notation(self) -> None:
    """Supports dot and bracket notation for paths."""
    state = TreeExpansionState(default_expanded=True)

    # Various path formats
    state.node_overrides["root.config.settings"] = False
    state.node_overrides["root.items[0].name"] = False
    state.node_overrides["root.data[5][2]"] = False

    assert state.is_expanded("root.config.settings") is False
    assert state.is_expanded("root.items[0].name") is False
    assert state.is_expanded("root.data[5][2]") is False

  def test_expand_all_then_individual_collapse(self) -> None:
    """Can collapse individual nodes after expand_all."""
    state = TreeExpansionState()
    state.expand_all()

    state.toggle("root.specific.node")

    # Most nodes expanded, one collapsed
    assert state.is_expanded("root.any.path") is True
    assert state.is_expanded("root.specific.node") is False

  def test_collapse_all_then_individual_expand(self) -> None:
    """Can expand individual nodes after collapse_all."""
    state = TreeExpansionState()
    state.collapse_all()

    state.toggle("root.important.node")

    # Most nodes collapsed, one expanded
    assert state.is_expanded("root.any.path") is False
    assert state.is_expanded("root.important.node") is True

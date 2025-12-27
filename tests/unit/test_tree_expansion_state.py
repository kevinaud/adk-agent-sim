"""Unit tests for TreeExpansionState.

Tests state management for DevTools tree node expand/collapse behavior.
"""

from adk_agent_sim.ui.components.devtools_tree import TreeExpansionState


class TestTreeExpansionStateInit:
  """Tests for TreeExpansionState initialization."""

  def test_default_values(self) -> None:
    """State initializes with sensible defaults."""
    state = TreeExpansionState()

    assert state.node_states == {}
    assert state.default_expanded is True

  def test_custom_default_expanded(self) -> None:
    """Can initialize with custom default_expanded value."""
    state = TreeExpansionState(default_expanded=False)

    assert state.default_expanded is False


class TestIsExpanded:
  """Tests for is_expanded() method."""

  def test_returns_default_when_no_state(self) -> None:
    """Returns default_expanded when no state exists."""
    state = TreeExpansionState(default_expanded=True)

    assert state.is_expanded("root.some.path") is True

  def test_returns_default_false_when_configured(self) -> None:
    """Respects default_expanded=False."""
    state = TreeExpansionState(default_expanded=False)

    assert state.is_expanded("root.some.path") is False

  def test_explicit_state_takes_precedence(self) -> None:
    """Explicit state takes precedence over default."""
    state = TreeExpansionState(default_expanded=True)
    state.node_states["root.specific.path"] = False

    assert state.is_expanded("root.specific.path") is False
    assert state.is_expanded("root.other.path") is True


class TestToggle:
  """Tests for toggle() method."""

  def test_toggle_creates_state_from_default(self) -> None:
    """Toggle creates state inverting default."""
    state = TreeExpansionState(default_expanded=True)

    state.toggle("root.node")

    assert state.node_states["root.node"] is False
    assert state.is_expanded("root.node") is False

  def test_toggle_inverts_existing_state(self) -> None:
    """Toggle inverts existing state."""
    state = TreeExpansionState()
    state.node_states["root.node"] = False

    state.toggle("root.node")

    assert state.node_states["root.node"] is True
    assert state.is_expanded("root.node") is True


class TestExpandAll:
  """Tests for expand_all() method."""

  def test_expands_all_specified_paths(self) -> None:
    """expand_all() sets all specified paths to expanded."""
    state = TreeExpansionState()
    paths = ["root.a", "root.b", "root.c"]

    state.expand_all(paths)

    for path in paths:
      assert state.is_expanded(path) is True

  def test_overwrites_existing_collapsed_state(self) -> None:
    """expand_all() overwrites existing collapsed states."""
    state = TreeExpansionState()
    state.node_states["root.collapsed"] = False

    state.expand_all(["root.collapsed", "root.other"])

    assert state.is_expanded("root.collapsed") is True
    assert state.is_expanded("root.other") is True


class TestCollapseAll:
  """Tests for collapse_all() method."""

  def test_collapses_all_specified_paths(self) -> None:
    """collapse_all() sets all specified paths to collapsed."""
    state = TreeExpansionState(default_expanded=True)
    paths = ["root.a", "root.b", "root.c"]

    state.collapse_all(paths)

    for path in paths:
      assert state.is_expanded(path) is False

  def test_overwrites_existing_expanded_state(self) -> None:
    """collapse_all() overwrites existing expanded states."""
    state = TreeExpansionState()
    state.node_states["root.expanded"] = True

    state.collapse_all(["root.expanded", "root.other"])

    assert state.is_expanded("root.expanded") is False
    assert state.is_expanded("root.other") is False


class TestReset:
  """Tests for reset() method."""

  def test_clears_node_states(self) -> None:
    """reset() clears existing states."""
    state = TreeExpansionState()
    state.node_states["root.a"] = True
    state.node_states["root.b"] = False

    state.reset()

    assert state.node_states == {}

  def test_nodes_return_to_default_after_reset(self) -> None:
    """Nodes use default_expanded after reset()."""
    state = TreeExpansionState(default_expanded=True)
    state.node_states["root.any"] = False

    state.reset()

    assert state.is_expanded("root.any") is True


class TestPathBasedStorage:
  """Tests for path-based state storage."""

  def test_different_paths_independent(self) -> None:
    """Different paths maintain independent state."""
    state = TreeExpansionState(default_expanded=True)

    state.toggle("root.items[0]")
    state.toggle("root.items[1]")
    state.toggle("root.items[1]")  # Toggle back

    assert state.is_expanded("root.items[0]") is False
    assert state.is_expanded("root.items[1]") is True
    assert state.is_expanded("root.items[2]") is True  # Default

  def test_storage_efficiency(self) -> None:
    """Only toggled nodes are stored."""
    state = TreeExpansionState()

    state.toggle("root.a")
    state.toggle("root.deeply.nested.path")

    assert len(state.node_states) == 2
    assert "root.a" in state.node_states
    assert "root.deeply.nested.path" in state.node_states

  def test_nested_path_notation(self) -> None:
    """Supports dot and bracket notation for paths."""
    state = TreeExpansionState(default_expanded=True)

    state.node_states["root.config.settings"] = False
    state.node_states["root.items[0].name"] = False
    state.node_states["root.data[5][2]"] = False

    assert state.is_expanded("root.config.settings") is False
    assert state.is_expanded("root.items[0].name") is False
    assert state.is_expanded("root.data[5][2]") is False

  def test_expand_all_then_individual_collapse(self) -> None:
    """Can collapse individual nodes after expand_all."""
    state = TreeExpansionState()
    state.expand_all(["root.a", "root.b", "root.specific.node"])

    state.toggle("root.specific.node")

    assert state.is_expanded("root.a") is True
    assert state.is_expanded("root.specific.node") is False

  def test_collapse_all_then_individual_expand(self) -> None:
    """Can expand individual nodes after collapse_all."""
    state = TreeExpansionState()
    state.collapse_all(["root.a", "root.b", "root.important.node"])

    state.toggle("root.important.node")

    assert state.is_expanded("root.a") is False
    assert state.is_expanded("root.important.node") is True

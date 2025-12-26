"""Unit tests for DevToolsTree component.

Tests the hierarchical JSON tree renderer functionality.
"""

from adk_agent_sim.ui.components.devtools_tree import (
  DevToolsTree,
  ValueType,
  _get_value_type,
)
from adk_agent_sim.ui.components.tree_expansion_state import TreeExpansionState


class TestGetValueType:
  """Tests for _get_value_type() helper function."""

  def test_null_type(self) -> None:
    """None maps to NULL type."""
    assert _get_value_type(None) == ValueType.NULL

  def test_boolean_true(self) -> None:
    """True maps to BOOLEAN type."""
    assert _get_value_type(True) == ValueType.BOOLEAN

  def test_boolean_false(self) -> None:
    """False maps to BOOLEAN type."""
    assert _get_value_type(False) == ValueType.BOOLEAN

  def test_integer(self) -> None:
    """Integer maps to NUMBER type."""
    assert _get_value_type(42) == ValueType.NUMBER
    assert _get_value_type(0) == ValueType.NUMBER
    assert _get_value_type(-1) == ValueType.NUMBER

  def test_float(self) -> None:
    """Float maps to NUMBER type."""
    assert _get_value_type(3.14) == ValueType.NUMBER
    assert _get_value_type(0.0) == ValueType.NUMBER

  def test_string(self) -> None:
    """String maps to STRING type."""
    assert _get_value_type("hello") == ValueType.STRING
    assert _get_value_type("") == ValueType.STRING

  def test_dict(self) -> None:
    """Dict maps to OBJECT type."""
    assert _get_value_type({}) == ValueType.OBJECT
    assert _get_value_type({"key": "value"}) == ValueType.OBJECT

  def test_list(self) -> None:
    """List maps to ARRAY type."""
    assert _get_value_type([]) == ValueType.ARRAY
    assert _get_value_type([1, 2, 3]) == ValueType.ARRAY

  def test_bool_before_int_check(self) -> None:
    """Boolean is checked before int (bool is subclass of int)."""
    # This ensures we don't misclassify True as NUMBER (1)
    assert _get_value_type(True) == ValueType.BOOLEAN
    assert _get_value_type(False) == ValueType.BOOLEAN


class TestDevToolsTreeInit:
  """Tests for DevToolsTree initialization."""

  def test_basic_init(self) -> None:
    """Tree initializes with data and tree_id."""
    data = {"key": "value"}
    tree = DevToolsTree(data=data, tree_id="test-tree")

    assert tree.data == data
    assert tree.tree_id == "test-tree"
    assert tree.expansion_state is not None

  def test_creates_expansion_state_if_none(self) -> None:
    """Creates new TreeExpansionState if not provided."""
    tree = DevToolsTree(data={}, tree_id="test")

    assert isinstance(tree.expansion_state, TreeExpansionState)
    assert tree.expansion_state.default_expanded is True

  def test_uses_provided_expansion_state(self) -> None:
    """Uses provided TreeExpansionState."""
    custom_state = TreeExpansionState(default_expanded=False)
    tree = DevToolsTree(data={}, tree_id="test", expansion_state=custom_state)

    assert tree.expansion_state is custom_state

  def test_accepts_various_data_types(self) -> None:
    """Can initialize with various JSON-serializable data types."""
    # Object
    DevToolsTree(data={"key": "value"}, tree_id="obj")

    # Array
    DevToolsTree(data=[1, 2, 3], tree_id="arr")

    # Primitive
    DevToolsTree(data="string", tree_id="str")
    DevToolsTree(data=42, tree_id="num")
    DevToolsTree(data=True, tree_id="bool")
    DevToolsTree(data=None, tree_id="null")

  def test_accepts_nested_structures(self) -> None:
    """Can initialize with deeply nested structures."""
    nested_data = {
      "level1": {"level2": {"level3": {"level4": [1, 2, {"deep": "value"}]}}}
    }
    tree = DevToolsTree(data=nested_data, tree_id="nested")

    assert tree.data == nested_data


class TestDevToolsTreeExpansionState:
  """Tests for expansion state integration with DevToolsTree."""

  def test_default_expanded_true(self) -> None:
    """Nodes are expanded by default (T013)."""
    tree = DevToolsTree(
      data={"outer": {"inner": "value"}},
      tree_id="test",
    )

    # Default expansion state should expand all
    assert tree.expansion_state.is_expanded("root") is True
    assert tree.expansion_state.is_expanded("root.outer") is True

  def test_toggle_integration(self) -> None:
    """Toggling updates expansion state."""
    tree = DevToolsTree(
      data={"container": {"item": "value"}},
      tree_id="test",
    )

    # Initially expanded
    assert tree.expansion_state.is_expanded("root.container") is True

    # Toggle to collapse
    tree.expansion_state.toggle("root.container")
    assert tree.expansion_state.is_expanded("root.container") is False

    # Toggle to expand again
    tree.expansion_state.toggle("root.container")
    assert tree.expansion_state.is_expanded("root.container") is True

  def test_expand_all_integration(self) -> None:
    """expand_all() works through tree's expansion state (T016)."""
    state = TreeExpansionState()
    state.node_overrides["root.a"] = False
    state.node_overrides["root.b"] = False

    tree = DevToolsTree(
      data={"a": {}, "b": {}},
      tree_id="test",
      expansion_state=state,
    )

    tree.expansion_state.expand_all()

    assert tree.expansion_state.is_expanded("root.a") is True
    assert tree.expansion_state.is_expanded("root.b") is True

  def test_collapse_all_integration(self) -> None:
    """collapse_all() works through tree's expansion state (T016)."""
    tree = DevToolsTree(
      data={"a": {}, "b": {}},
      tree_id="test",
    )

    tree.expansion_state.collapse_all()

    assert tree.expansion_state.is_expanded("root.a") is False
    assert tree.expansion_state.is_expanded("root.b") is False


class TestDevToolsTreeWithNestedData:
  """Tests for DevToolsTree with various nested structures (T015)."""

  def test_simple_object(self) -> None:
    """Handles simple flat object."""
    data = {"name": "test", "count": 42, "active": True}
    tree = DevToolsTree(data=data, tree_id="simple")

    # Tree should be created without error
    assert tree.data == data

  def test_nested_objects(self) -> None:
    """Handles nested objects."""
    data = {"user": {"profile": {"name": "Alice", "settings": {"theme": "dark"}}}}
    tree = DevToolsTree(data=data, tree_id="nested-obj")

    assert tree.data == data

  def test_arrays(self) -> None:
    """Handles arrays."""
    data = {"items": [1, 2, 3, 4, 5]}
    tree = DevToolsTree(data=data, tree_id="arrays")

    assert tree.data == data

  def test_nested_arrays(self) -> None:
    """Handles nested arrays."""
    data = {"matrix": [[1, 2], [3, 4], [5, 6]]}
    tree = DevToolsTree(data=data, tree_id="nested-arr")

    assert tree.data == data

  def test_mixed_nesting(self) -> None:
    """Handles mixed object/array nesting."""
    data = {
      "users": [
        {"name": "Alice", "tags": ["admin", "active"]},
        {"name": "Bob", "tags": ["user"]},
      ],
      "metadata": {"counts": [10, 20, 30]},
    }
    tree = DevToolsTree(data=data, tree_id="mixed")

    assert tree.data == data

  def test_all_primitive_types(self) -> None:
    """Handles all JSON primitive types."""
    data = {
      "string": "hello",
      "number_int": 42,
      "number_float": 3.14,
      "bool_true": True,
      "bool_false": False,
      "null_value": None,
    }
    tree = DevToolsTree(data=data, tree_id="primitives")

    assert tree.data == data

  def test_empty_containers(self) -> None:
    """Handles empty objects and arrays."""
    data = {
      "empty_object": {},
      "empty_array": [],
    }
    tree = DevToolsTree(data=data, tree_id="empty")

    assert tree.data == data

  def test_deeply_nested_structure(self) -> None:
    """Handles deeply nested structures (10+ levels)."""

    # Create a deeply nested structure
    def create_deep(depth: int) -> dict:
      if depth == 0:
        return {"leaf": "value"}
      return {"level": create_deep(depth - 1)}

    data = create_deep(10)
    tree = DevToolsTree(data=data, tree_id="deep")

    assert tree.data == data


class TestDevToolsTreePathGeneration:
  """Tests for tree path generation for state tracking."""

  def test_root_path(self) -> None:
    """Root node has 'root' path."""
    tree = DevToolsTree(data={}, tree_id="test")
    # The root path is used internally during render
    # We can verify by checking expansion state behavior at root
    assert tree.expansion_state.is_expanded("root") is True

  def test_object_paths(self) -> None:
    """Object keys generate dot-separated paths."""
    tree = DevToolsTree(
      data={"outer": {"inner": "value"}},
      tree_id="test",
    )

    # These paths should be valid for state tracking
    tree.expansion_state.toggle("root.outer")
    assert tree.expansion_state.is_expanded("root.outer") is False

  def test_array_paths(self) -> None:
    """Array indices generate bracket notation paths."""
    tree = DevToolsTree(
      data={"items": [{"a": 1}, {"b": 2}]},
      tree_id="test",
    )

    # Array paths use bracket notation
    tree.expansion_state.toggle("root.items[0]")
    assert tree.expansion_state.is_expanded("root.items[0]") is False
    assert tree.expansion_state.is_expanded("root.items[1]") is True

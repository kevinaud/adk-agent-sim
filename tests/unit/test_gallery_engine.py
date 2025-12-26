from typing import Callable, Dict, List, cast
from unittest.mock import Mock, call, patch

import pytest
from starlette.datastructures import QueryParams

# Adjust import based on your actual file structure
from adk_agent_sim.ui.components.gallery_engine import ComponentRegistry, GalleryEngine

# --- 1. Test Components (Mocks) ---


class SimpleComponent:
  """A simple component with basic types."""

  def __init__(self, title: str, count: int = 1, is_visible: bool = False):
    self.title = title
    self.count = count
    self.is_visible = is_visible
    self.rendered = False

  def render(self):
    self.rendered = True


class ComplexComponent:
  """A component expecting complex types (Lists, Dicts, Callables)."""

  def __init__(
    self, items: List[str], config: Dict[str, str], on_click: Callable[[], None]
  ):
    self.items = items
    self.config = config
    self.on_click = on_click
    self.rendered = False

  def render(self):
    self.rendered = True


class BrokenComponent:
  """A component that crashes on render."""

  def render(self):
    raise ValueError("Simulated Render Crash")


def factory_component():
  """A factory function that returns a SimpleComponent."""
  return SimpleComponent(title="Factory Created")


# --- 2. Fixtures ---


@pytest.fixture
def mock_ui():
  """Patches the 'ui' object in gallery_engine to prevent actual GUI calls."""
  with patch("adk_agent_sim.ui.components.gallery_engine.ui") as mock:
    yield mock


@pytest.fixture
def registry() -> ComponentRegistry:
  return {
    "Simple": SimpleComponent,
    "Complex": ComplexComponent,
    "Broken": BrokenComponent,
    "Factory": factory_component,
  }


@pytest.fixture
def engine(registry: ComponentRegistry):
  return GalleryEngine(registry)


# --- 3. Tests ---


def test_render_index(engine: GalleryEngine, mock_ui: Mock):
  """Test that the index renders links for all registry items."""
  engine.render_index()

  # Check that labels and links were created
  assert mock_ui.label.call_count > 0

  # Check that links to sub-routes were generated
  # expected calls: ui.link("Simple", "/_gallery/Simple"), etc.
  expected_calls = [
    call("Broken", "/_gallery/Broken"),
    call("Complex", "/_gallery/Complex"),
    call("Factory", "/_gallery/Factory"),
    call("Simple", "/_gallery/Simple"),
  ]

  # We inspect the calls to ui.link to ensure URLs are correct
  mock_ui.link.assert_has_calls(expected_calls, any_order=True)


def test_render_component_simple_class(engine: GalleryEngine, mock_ui: Mock):
  """Test instantiating a class with primitive types from QueryParams."""
  params = QueryParams({"title": "Hello World", "count": "42", "is_visible": "true"})

  # Execution
  engine.render_component("Simple", params)

  # Verification:
  # Since we can't easily grab the instance from the black box,
  # we verify that the UI wrapper was created and no errors were shown.
  mock_ui.element.assert_called_with("div")

  # To strictly verify the instantiation arguments, we can patch the class
  # in the registry. But for this integration test, let's trust the instance
  # logic below in `test_instantiate_component_logic`


def test_instantiate_component_logic(engine: GalleryEngine) -> None:
  """Unit test specifically for _instantiate_component logic (Type Casting)."""
  params = QueryParams({"title": "Test", "count": "10", "is_visible": "true"})

  instance = cast(
    SimpleComponent, engine._instantiate_component(SimpleComponent, params)
  )

  assert isinstance(instance, SimpleComponent)
  assert instance.title == "Test"
  assert instance.count == 10  # Casted to int
  assert instance.is_visible is True  # Casted to bool


def test_instantiate_component_defaults(engine: GalleryEngine) -> None:
  """Test that default values in __init__ are respected if param is missing."""
  params = QueryParams({"title": "Only Title"})

  instance = cast(
    SimpleComponent, engine._instantiate_component(SimpleComponent, params)
  )

  assert instance.title == "Only Title"
  assert instance.count == 1  # Default
  assert instance.is_visible is False  # Default


def test_instantiate_component_mocking(engine: GalleryEngine) -> None:
  """Test that missing required args are auto-mocked (Complex types)."""
  # No params provided for ComplexComponent, which requires lists/dicts/callables
  params = QueryParams({})

  instance = cast(
    ComplexComponent, engine._instantiate_component(ComplexComponent, params)
  )

  assert isinstance(instance, ComplexComponent)
  assert isinstance(instance.items, list)
  assert isinstance(instance.config, dict)
  assert callable(instance.on_click)


def test_render_component_factory(engine: GalleryEngine, mock_ui: Mock):
  """Test that factory functions are called directly."""
  params = QueryParams({})

  # Test that the factory function is called without error
  engine.render_component("Factory", params)

  # Verify render was called (no error UI shown)
  assert mock_ui.column.call_count >= 1
  # Ensure error was NOT called
  assert mock_ui.label.call_args_list[-1] != call("Failed to render component")


def test_render_not_found(engine: GalleryEngine, mock_ui: Mock):
  """Test rendering a non-existent component."""
  engine.render_component("NonExistent", QueryParams({}))

  # Should show an error icon/text
  mock_ui.label.assert_any_call("Component 'NonExistent' not found.")


def test_render_error_handling(engine: GalleryEngine, mock_ui: Mock):
  """Test that exceptions during render are caught and displayed."""
  params = QueryParams({})

  engine.render_component("Broken", params)

  # Should catch ValueError and display it
  mock_ui.label.assert_any_call("Failed to render component")
  # Using string containment for the exception message check
  found_msg = False
  for call_args in mock_ui.label.call_args_list:
    if "Simulated Render Crash" in str(call_args):
      found_msg = True
      break
  assert found_msg, "Did not find exception message in UI labels"


def test_json_casting(engine: GalleryEngine) -> None:
  """Test casting JSON strings to Dict/List."""
  params = QueryParams(
    {
      "items": '["a", "b"]',
      "config": '{"key": "val"}',
      "on_click": "ignore",  # Required arg
    }
  )

  instance = cast(
    ComplexComponent, engine._instantiate_component(ComplexComponent, params)
  )

  assert isinstance(instance, ComplexComponent)
  assert instance.items == ["a", "b"]
  assert instance.config == {"key": "val"}

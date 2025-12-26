"""
Core logic for the component gallery.
Handles dynamic instantiation and argument mocking.
"""

import inspect
import json
from enum import Enum
from typing import (
  Any,
  Callable,
  Dict,
  Protocol,
  Type,
  Union,
  get_type_hints,
  runtime_checkable,
)

from nicegui import ui
from starlette.datastructures import QueryParams


# 1. The Contract: What is a "Component"?
@runtime_checkable
class Renderable(Protocol):
  def render(self) -> Any:
    """Renders the component to the UI."""
    ...


# 2. The Building Blocks
ComponentClass = Type[Renderable]
ComponentFactory = Callable[[], Renderable]

# 3. The Registry Entry
GalleryEntry = Union[ComponentClass, ComponentFactory]

# 4. The Registry
ComponentRegistry = Dict[str, GalleryEntry]


class GalleryEngine:
  """Reflective engine to render components based on URL parameters."""

  def __init__(self, registry: ComponentRegistry) -> None:
    """
    Initialize the gallery engine.

    Args:
      registry: Dictionary mapping names to Component Classes or Factories.
    """
    self.registry = registry

  def render_index(self) -> None:
    """Render the list of available components."""
    ui.label("Component Gallery").classes("text-3xl font-bold mb-6 text-gray-800")

    with ui.row().classes("flex-wrap gap-4"):
      for name in sorted(self.registry.keys()):
        # Interactive card for each component
        with ui.card().classes("w-64 hover:shadow-lg transition-shadow cursor-pointer"):
          with ui.column().classes("w-full items-center p-4"):
            ui.icon("extension", size="lg").classes("text-blue-500 mb-2")
            # Link points to the sub-route /_gallery/{name}
            ui.link(name, f"/_gallery/{name}").classes(
              "text-lg font-medium text-gray-700 hover:text-blue-600 stretch "
              "text-center"
            )

  def render_component(self, name: str, query_params: QueryParams) -> None:
    """
    Render the specific component in an isolated container.

    Args:
      name: The component name (from URL path).
      query_params: Dictionary of query parameters from the request.
    """
    item = self.registry.get(name)

    if item is None:
      with ui.column().classes("p-4 text-red-600"):
        ui.icon("error", size="xl")
        ui.label(f"Component '{name}' not found.").classes("font-bold")
        ui.link("← Back to Gallery", "/_gallery").classes("mt-4 text-blue-600")
      return

    # 1. Back Navigation
    ui.link("← Back to Gallery", "/_gallery").classes(
      "mb-4 inline-block text-gray-500 hover:text-gray-800"
    )

    # 2. Component Container (Target for Playwright)
    with ui.column().classes("w-full items-center"):
      ui.label(f"Viewing: {name}").classes("text-sm text-gray-400 mb-2")

      with (
        ui.element("div")
        .props("data-testid=gallery-component-wrapper")
        .classes(
          "p-4 border-2 border-dashed border-gray-200 rounded-lg "
          "w-full flex justify-center bg-white"
        )
      ):
        try:
          instance: Renderable

          # Case A: It's a Class -> Use reflection with Request params
          if isinstance(item, type):
            instance = self._instantiate_component(item, query_params)
          # Case B: It's a Factory -> Call directly
          else:
            instance = item()

          instance.render()

        except Exception as e:
          self._render_error(e)

  def _instantiate_component(
    self, cls: ComponentClass, query_params: QueryParams
  ) -> Renderable:
    """
    Instantiate a class by mapping query params to __init__ arguments.
    """
    sig = inspect.signature(cls.__init__)

    # Try to get type hints, but handle failures from TYPE_CHECKING imports
    try:
      type_hints = get_type_hints(cls.__init__)
    except NameError:
      # Fall back to empty hints if forward references can't be resolved
      type_hints = {}

    kwargs: Dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
      if param_name == "self":
        continue

      # Skip *args and **kwargs parameters
      if param.kind in (
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
      ):
        continue

      # 1. Check Query Parameters
      url_value = query_params.get(param_name)

      if url_value is not None:
        target_type = type_hints.get(param_name, str)
        kwargs[param_name] = self._cast_value(url_value, target_type)

      # 2. Check for defaults or mock if required
      elif param.default == inspect.Parameter.empty:
        kwargs[param_name] = self._mock_value(
          param_name, type_hints.get(param_name, Any)
        )

    return cls(**kwargs)

  def _cast_value(self, value: str, target_type: Type[Any]) -> Any:
    """Cast string URL params to Python types."""
    if target_type is bool:
      return value.lower() == "true"
    if target_type is int:
      return int(value)
    if target_type is float:
      return float(value)

    # Handle Enum types
    origin = getattr(target_type, "__origin__", None)
    if inspect.isclass(target_type) and issubclass(target_type, Enum):
      # Try by value first, then by name
      for member in target_type:
        if member.value == value or member.name == value:
          return member
      raise ValueError(f"Invalid enum value '{value}' for {target_type}")

    # Check for dict/list types including generics like Dict[str, str], List[str]
    if target_type is dict or origin is dict:
      try:
        return json.loads(value)
      except json.JSONDecodeError:
        return {}
    if target_type is list or origin is list:
      try:
        return json.loads(value)
      except json.JSONDecodeError:
        return []
    return value

  def _mock_value(self, name: str, target_type: Type[Any]) -> Any:
    """Generate mock values for required arguments missing from URL."""
    type_str = str(target_type)

    if "Callable" in type_str or "Awaitable" in type_str:

      async def mock_handler(*args: Any, **kwargs: Any) -> None:
        ui.notify(f"Mock Handler: '{name}' called with {args}")

      return mock_handler

    if "list" in type_str.lower() or target_type is list:
      return []
    if "dict" in type_str.lower() or target_type is dict:
      return {}

    return f"[Mock {name}]"

  def _render_error(self, e: Exception) -> None:
    """Render a friendly error message if component crashes."""
    with ui.column().classes("bg-red-50 p-4 rounded text-red-700 w-full"):
      ui.label("Failed to render component").classes("font-bold")
      ui.label(str(e)).classes("font-mono text-sm break-all")

"""Universal Schema → Form renderer for NiceGUI."""

from __future__ import annotations

from typing import Any, Callable, cast

from nicegui import ui
from pydantic import BaseModel

from adk_agent_sim.ui.styles import FIELD_STYLE


def render_schema_form(
  schema: Any,
  on_change: Callable[[dict[str, Any]], None] | None = None,
  prefix: str = "",
) -> dict[str, Any]:
  """
  Render a google.genai.types.Schema as a NiceGUI form.

  Args:
    schema: The Schema object to render
    on_change: Optional callback when any field value changes
    prefix: Path prefix for nested fields

  Returns:
    Dictionary to collect form values (will be populated as user inputs)
  """
  values: dict[str, Any] = {}

  if schema is None:
    return values

  # Handle OBJECT type with properties
  if hasattr(schema, "properties") and schema.properties:
    required_fields = set(schema.required or [])

    for field_name, field_schema in schema.properties.items():
      field_path = f"{prefix}.{field_name}" if prefix else field_name
      is_required = field_name in required_fields

      # Render the field
      field_value = _render_field(
        field_name=field_name,
        schema=field_schema,
        is_required=is_required,
        on_change=lambda v, fn=field_name: _update_value(values, fn, v, on_change),
        prefix=field_path,
        values=values,
      )
      values[field_name] = field_value

  return values


def _update_value(
  values: dict[str, Any],
  field_name: str,
  value: Any,
  on_change: Callable[[dict[str, Any]], None] | None,
) -> None:
  """Update a value in the values dict and notify callback."""
  values[field_name] = value
  if on_change:
    on_change(values)


def _render_field(
  field_name: str,
  schema: Any,
  is_required: bool,
  on_change: Callable[[Any], None],
  prefix: str,
  values: dict[str, Any],
) -> Any:
  """
  Render a single field based on its schema type.

  Returns the initial/default value for the field.
  """
  from google.genai.types import Type

  # Get field metadata
  description = getattr(schema, "description", None) or ""
  schema_type = getattr(schema, "type", None)
  enum_values = getattr(schema, "enum", None)

  # Build label
  label = field_name.replace("_", " ").title()
  if is_required:
    label += " *"

  with ui.column().classes("w-full").style(FIELD_STYLE):
    # Handle enum (dropdown)
    if enum_values:
      default_val = enum_values[0] if enum_values else ""
      select = ui.select(
        options=enum_values,
        value=default_val,
        label=label,
      ).classes("w-full")
      select.on_value_change(lambda e: on_change(e.value))
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      return default_val

    # Handle by type
    if schema_type == Type.STRING:
      input_field = ui.input(label=label, value="").classes("w-full")
      input_field.on_value_change(lambda e: on_change(e.value))
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      return ""

    elif schema_type in (Type.INTEGER, Type.NUMBER):
      is_float = schema_type == Type.NUMBER
      number_field = ui.number(
        label=label,
        value=0.0 if is_float else 0,
        format="%.2f" if is_float else "%.0f",
      ).classes("w-full")
      number_field.on_value_change(lambda e: on_change(e.value))
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      return 0.0 if is_float else 0

    elif schema_type == Type.BOOLEAN:
      checkbox = ui.checkbox(label, value=False)
      checkbox.on_value_change(lambda e: on_change(e.value))
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      return False

    elif schema_type == Type.OBJECT:
      # Recursively render nested object
      ui.label(label).classes("font-semibold")
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      with ui.card().classes("w-full p-2 ml-4"):
        nested_values = render_schema_form(schema, None, prefix)
        on_change(nested_values)
        return nested_values

    elif schema_type == Type.ARRAY:
      # Render array with add/remove functionality
      ui.label(label).classes("font-semibold")
      if description:
        ui.label(description).classes("text-xs text-gray-500")

      items_schema = getattr(schema, "items", None)
      array_values: list[Any] = []

      with ui.column().classes("w-full ml-4"):
        items_container = ui.column().classes("w-full")

        def add_item() -> None:
          with items_container:
            idx = len(array_values)
            with ui.row().classes("w-full items-center"):
              if items_schema:
                item_val = _render_array_item(
                  items_schema,
                  idx,
                  lambda v, i=idx: _update_array_item(array_values, i, v, on_change),
                )
                array_values.append(item_val)
              else:
                # Default to string input
                inp = ui.input(label=f"Item {idx + 1}").classes("flex-grow")
                inp.on_value_change(
                  lambda e, i=idx: _update_array_item(
                    array_values, i, e.value, on_change
                  )
                )
                array_values.append("")

              def create_remove_handler(index: int) -> Any:
                def handler() -> None:
                  remove_item(index)

                return handler

              ui.button(
                icon="delete",
                on_click=create_remove_handler(idx),
              ).props("flat dense")

          on_change(array_values)

        def remove_item(idx: int) -> None:
          if idx < len(array_values):
            array_values.pop(idx)
            on_change(array_values)
            # Rebuild UI would require more complex state management
            # For now, mark as removed

        ui.button("Add Item", icon="add", on_click=add_item).props("flat")

      return array_values

    else:
      # Fallback to text input
      input_field = ui.input(label=label, value="").classes("w-full")
      input_field.on_value_change(lambda e: on_change(e.value))
      if description:
        ui.label(description).classes("text-xs text-gray-500")
      return ""


def _render_array_item(
  items_schema: Any,
  index: int,
  on_change: Callable[[Any], None],
) -> Any:
  """Render a single array item based on its schema."""
  from google.genai.types import Type

  schema_type = getattr(items_schema, "type", None)

  if schema_type == Type.STRING:
    inp = ui.input(label=f"Item {index + 1}").classes("flex-grow")
    inp.on_value_change(lambda e: on_change(e.value))
    return ""

  elif schema_type in (Type.INTEGER, Type.NUMBER):
    is_float = schema_type == Type.NUMBER
    num = ui.number(
      label=f"Item {index + 1}",
      value=0.0 if is_float else 0,
    ).classes("flex-grow")
    num.on_value_change(lambda e: on_change(e.value))
    return 0.0 if is_float else 0

  elif schema_type == Type.OBJECT:
    # Nested object in array
    nested = render_schema_form(items_schema, on_change, f"item_{index}")
    return nested

  else:
    inp = ui.input(label=f"Item {index + 1}").classes("flex-grow")
    inp.on_value_change(lambda e: on_change(e.value))
    return ""


def _update_array_item(
  array_values: list[Any],
  index: int,
  value: Any,
  on_change: Callable[[Any], None],
) -> None:
  """Update an array item value."""
  if index < len(array_values):
    array_values[index] = value
  on_change(array_values)


def validate_required_fields(
  schema: Any,
  values: dict[str, Any],
) -> list[str]:
  """
  Validate that required fields have values.

  Returns:
    List of validation error messages (empty if valid)
  """
  errors: list[str] = []

  if schema is None:
    return errors

  required_fields = set(getattr(schema, "required", None) or [])

  for field_name in required_fields:
    value = values.get(field_name)
    if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
      errors.append(f"'{field_name}' is required")

  return errors


def pydantic_to_schema(model: type[BaseModel]) -> Any:
  """
  Convert a Pydantic model to google.genai.types.Schema.

  Args:
    model: A Pydantic BaseModel class

  Returns:
    Schema instance for form rendering
  """
  from google.genai.types import Schema

  # Get JSON schema from Pydantic model
  json_schema = model.model_json_schema()

  # Convert to genai Schema
  return Schema.from_json_schema(json_schema=cast(Any, json_schema))

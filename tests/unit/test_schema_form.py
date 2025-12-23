"""Unit tests for schema form rendering utilities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from adk_agent_sim.ui.components.schema_form import (
  pydantic_to_schema,
  validate_required_fields,
)


class TestValidateRequiredFields:
  """Tests for validate_required_fields function."""

  def test_no_required_fields(self) -> None:
    """Test schema with no required fields."""
    schema = MagicMock()
    schema.required = None
    errors = validate_required_fields(schema, {"field": "value"})
    assert errors == []

  def test_empty_required_fields(self) -> None:
    """Test schema with empty required list."""
    schema = MagicMock()
    schema.required = []
    errors = validate_required_fields(schema, {})
    assert errors == []

  def test_required_field_present(self) -> None:
    """Test required field that is present."""
    schema = MagicMock()
    schema.required = ["name"]
    errors = validate_required_fields(schema, {"name": "John"})
    assert errors == []

  def test_required_field_missing(self) -> None:
    """Test required field that is missing."""
    schema = MagicMock()
    schema.required = ["name"]
    errors = validate_required_fields(schema, {})
    assert len(errors) == 1
    assert "'name' is required" in errors[0]

  def test_required_field_empty_string(self) -> None:
    """Test required field with empty string value."""
    schema = MagicMock()
    schema.required = ["name"]
    errors = validate_required_fields(schema, {"name": ""})
    assert len(errors) == 1
    assert "'name' is required" in errors[0]

  def test_required_field_none(self) -> None:
    """Test required field with None value."""
    schema = MagicMock()
    schema.required = ["name"]
    errors = validate_required_fields(schema, {"name": None})
    assert len(errors) == 1
    assert "'name' is required" in errors[0]

  def test_required_field_empty_list(self) -> None:
    """Test required field with empty list value."""
    schema = MagicMock()
    schema.required = ["items"]
    errors = validate_required_fields(schema, {"items": []})
    assert len(errors) == 1
    assert "'items' is required" in errors[0]

  def test_multiple_required_fields(self) -> None:
    """Test multiple required fields."""
    schema = MagicMock()
    schema.required = ["name", "email", "age"]
    errors = validate_required_fields(schema, {"name": "John", "email": "", "age": 25})
    assert len(errors) == 1
    assert "'email' is required" in errors[0]

  def test_all_required_fields_missing(self) -> None:
    """Test all required fields missing."""
    schema = MagicMock()
    schema.required = ["name", "email"]
    errors = validate_required_fields(schema, {})
    assert len(errors) == 2

  def test_none_schema(self) -> None:
    """Test with None schema."""
    errors = validate_required_fields(None, {"field": "value"})
    assert errors == []

  def test_zero_is_valid_value(self) -> None:
    """Test that zero is a valid value for required fields."""
    schema = MagicMock()
    schema.required = ["count"]
    errors = validate_required_fields(schema, {"count": 0})
    # Zero should be valid (not empty)
    assert errors == []

  def test_false_is_valid_value(self) -> None:
    """Test that False is a valid value for required fields."""
    schema = MagicMock()
    schema.required = ["active"]
    errors = validate_required_fields(schema, {"active": False})
    # False should be valid (not empty)
    assert errors == []


class TestPydanticToSchema:
  """Tests for pydantic_to_schema function."""

  def test_converts_simple_model(self) -> None:
    """Test converting a simple Pydantic model."""
    from pydantic import BaseModel

    class SimpleModel(BaseModel):
      name: str
      age: int

    with patch("google.genai.types.Schema") as MockSchema:
      MockSchema.from_json_schema = MagicMock(return_value=MockSchema)
      pydantic_to_schema(SimpleModel)

      # Should call from_json_schema with the model's JSON schema
      MockSchema.from_json_schema.assert_called_once()
      call_args = MockSchema.from_json_schema.call_args.kwargs["json_schema"]
      assert "name" in call_args.get("properties", {})
      assert "age" in call_args.get("properties", {})

  def test_includes_required_fields(self) -> None:
    """Test that required fields are included in schema."""
    from pydantic import BaseModel

    class RequiredModel(BaseModel):
      required_field: str
      optional_field: str | None = None

    with patch("google.genai.types.Schema") as MockSchema:
      MockSchema.from_json_schema = MagicMock(return_value=MockSchema)
      pydantic_to_schema(RequiredModel)

      call_args = MockSchema.from_json_schema.call_args.kwargs["json_schema"]
      required = call_args.get("required", [])
      assert "required_field" in required

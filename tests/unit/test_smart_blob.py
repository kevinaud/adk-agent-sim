"""Unit tests for SmartBlobDetector.

Tests content type detection for JSON and Markdown patterns.
"""

from adk_agent_sim.ui.components.smart_blob import (
  BlobType,
  SmartBlobDetector,
)


class TestBlobTypeEnum:
  """Tests for BlobType enumeration."""

  def test_json_value(self) -> None:
    """JSON type has correct value."""
    assert BlobType.JSON.value == "json"

  def test_markdown_value(self) -> None:
    """MARKDOWN type has correct value."""
    assert BlobType.MARKDOWN.value == "markdown"

  def test_plain_value(self) -> None:
    """PLAIN type has correct value."""
    assert BlobType.PLAIN.value == "plain"


class TestTryParseJson:
  """Tests for SmartBlobDetector.try_parse_json()."""

  def test_valid_json_object(self) -> None:
    """Parses valid JSON objects."""
    value = '{"name": "Alice", "age": 30}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == {"name": "Alice", "age": 30}

  def test_valid_json_array(self) -> None:
    """Parses valid JSON arrays."""
    value = '[1, 2, 3, "four"]'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == [1, 2, 3, "four"]

  def test_nested_json(self) -> None:
    """Parses nested JSON structures."""
    value = '{"users": [{"name": "Bob"}, {"name": "Carol"}]}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == {"users": [{"name": "Bob"}, {"name": "Carol"}]}

  def test_empty_object(self) -> None:
    """Parses empty JSON object."""
    value = "{}"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == {}

  def test_empty_array(self) -> None:
    """Parses empty JSON array."""
    value = "[]"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == []

  def test_json_with_whitespace(self) -> None:
    """Parses JSON with leading/trailing whitespace."""
    value = '  \n  {"key": "value"}  \n  '
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == {"key": "value"}

  def test_json_primitive_string_rejected(self) -> None:
    """Rejects JSON primitive strings."""
    value = '"just a string"'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Not a JSON object or array"

  def test_json_primitive_number_rejected(self) -> None:
    """Rejects JSON primitive numbers."""
    value = "42"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Not a JSON object or array"

  def test_json_primitive_boolean_rejected(self) -> None:
    """Rejects JSON primitive booleans."""
    value = "true"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Not a JSON object or array"

  def test_json_primitive_null_rejected(self) -> None:
    """Rejects JSON primitive null."""
    value = "null"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Not a JSON object or array"

  def test_malformed_json_missing_quote(self) -> None:
    """Returns error for malformed JSON missing quote."""
    value = '{"name: "Alice"}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error is not None

  def test_malformed_json_trailing_comma(self) -> None:
    """Returns error for malformed JSON with trailing comma."""
    value = '{"a": 1, "b": 2,}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error is not None

  def test_malformed_json_single_quotes(self) -> None:
    """Returns error for JSON with single quotes."""
    value = "{'name': 'Alice'}"
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error is not None

  def test_empty_string(self) -> None:
    """Returns error for empty string."""
    value = ""
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Empty string"

  def test_whitespace_only(self) -> None:
    """Returns error for whitespace-only string."""
    value = "   \n\t   "
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert parsed is None
    assert error == "Empty string"


class TestDetectMarkdownPatterns:
  """Tests for SmartBlobDetector.detect_markdown_patterns()."""

  def test_header_h1(self) -> None:
    """Detects H1 headers."""
    value = "# Main Title\nSome content"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_header_h2(self) -> None:
    """Detects H2 headers."""
    value = "## Section Title\nSome content"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_header_h3(self) -> None:
    """Detects H3 headers."""
    value = "### Subsection\nSome content"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_header_h6(self) -> None:
    """Detects H6 headers."""
    value = "###### Deep header\nContent"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_bold_text(self) -> None:
    """Detects bold text with **."""
    value = "This has **bold** text"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_unordered_list_dash(self) -> None:
    """Detects unordered lists with dash."""
    value = "Items:\n- First\n- Second"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_unordered_list_asterisk(self) -> None:
    """Detects unordered lists with asterisk."""
    value = "Items:\n* First\n* Second"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_ordered_list(self) -> None:
    """Detects ordered lists."""
    value = "Steps:\n1. First step\n2. Second step"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_code_block(self) -> None:
    """Detects code blocks with triple backticks."""
    value = "Example:\n```python\nprint('hello')\n```"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_inline_code_not_detected(self) -> None:
    """Does not detect single backtick inline code."""
    # Single backticks alone don't trigger markdown detection
    value = "Use `code` here"
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_plain_text_no_patterns(self) -> None:
    """Returns False for plain text."""
    value = "This is just regular text without any formatting."
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_empty_string(self) -> None:
    """Returns False for empty string."""
    value = ""
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_whitespace_only(self) -> None:
    """Returns False for whitespace-only string."""
    value = "   \n\t   "
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_very_short_string(self) -> None:
    """Returns False for very short strings."""
    value = "ab"
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_single_char(self) -> None:
    """Returns False for single character."""
    value = "#"
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_hash_without_space(self) -> None:
    """Does not match # without following space."""
    value = "#hashtag is not a header"
    assert SmartBlobDetector.detect_markdown_patterns(value) is False

  def test_header_in_middle_of_line(self) -> None:
    """Header at start of line is detected."""
    value = "Some text\n## Header Here\nMore text"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True

  def test_list_at_start_of_content(self) -> None:
    """List at start of content is detected."""
    value = "- First item"
    assert SmartBlobDetector.detect_markdown_patterns(value) is True


class TestDetectType:
  """Tests for SmartBlobDetector.detect_type()."""

  def test_json_object(self) -> None:
    """Detects JSON objects."""
    value = '{"key": "value"}'
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_json_array(self) -> None:
    """Detects JSON arrays."""
    value = "[1, 2, 3]"
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_markdown_header(self) -> None:
    """Detects Markdown content."""
    value = "## Section\nContent here"
    assert SmartBlobDetector.detect_type(value) == BlobType.MARKDOWN

  def test_markdown_list(self) -> None:
    """Detects Markdown lists."""
    value = "- Item one\n- Item two"
    assert SmartBlobDetector.detect_type(value) == BlobType.MARKDOWN

  def test_plain_text(self) -> None:
    """Detects plain text."""
    value = "Just some regular text."
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_empty_string(self) -> None:
    """Returns PLAIN for empty string."""
    value = ""
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_whitespace_only(self) -> None:
    """Returns PLAIN for whitespace-only string."""
    value = "   \n\t   "
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_json_takes_priority_over_markdown(self) -> None:
    """JSON detection takes priority over Markdown.

    If a string is valid JSON that happens to contain markdown-like
    patterns in its values, it should be detected as JSON.
    """
    value = '{"title": "## Header", "list": "- item"}'
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_malformed_json_with_markdown_detected_as_markdown(self) -> None:
    """Malformed JSON with Markdown patterns becomes MARKDOWN."""
    value = '{"title": ## Not valid JSON\n- But has markdown'
    assert SmartBlobDetector.detect_type(value) == BlobType.MARKDOWN

  def test_malformed_json_plain_text_detected_as_plain(self) -> None:
    """Malformed JSON without Markdown becomes PLAIN."""
    value = '{"title": Not valid JSON and no markdown patterns'
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN


class TestEdgeCases:
  """Tests for edge cases and boundary conditions."""

  def test_json_with_unicode(self) -> None:
    """Handles JSON with Unicode characters."""
    value = '{"emoji": "🎉", "japanese": "日本語"}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed == {"emoji": "🎉", "japanese": "日本語"}
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_deeply_nested_json(self) -> None:
    """Handles deeply nested JSON."""
    value = '{"a": {"b": {"c": {"d": {"e": "deep"}}}}}'
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert parsed is not None
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_large_json_array(self) -> None:
    """Handles JSON arrays with many elements."""
    elements = list(range(100))
    value = str(elements).replace("'", "")  # Python list to JSON array format
    # Actually use proper JSON
    import json

    value = json.dumps(elements)
    parsed, error = SmartBlobDetector.try_parse_json(value)

    assert error is None
    assert len(parsed) == 100
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_markdown_with_multiple_patterns(self) -> None:
    """Detects Markdown with multiple pattern types."""
    value = """# Title

## Section

This has **bold** and:

- List item 1
- List item 2

```python
code block
```
"""
    assert SmartBlobDetector.detect_markdown_patterns(value) is True
    assert SmartBlobDetector.detect_type(value) == BlobType.MARKDOWN

  def test_almost_json_not_quite(self) -> None:
    """Handles strings that look like JSON but aren't."""
    value = "{'this': 'looks like JSON but uses single quotes'}"
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_json_string_literal(self) -> None:
    """JSON string literals are PLAIN, not JSON blobs."""
    value = '"This is a JSON string literal"'
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_number_as_json(self) -> None:
    """Numbers alone are PLAIN, not JSON blobs."""
    value = "3.14159"
    assert SmartBlobDetector.detect_type(value) == BlobType.PLAIN

  def test_multiline_json(self) -> None:
    """Handles pretty-printed multiline JSON."""
    value = """{
  "name": "Test",
  "items": [
    "one",
    "two"
  ]
}"""
    assert SmartBlobDetector.detect_type(value) == BlobType.JSON

  def test_markdown_header_only(self) -> None:
    """Header alone is detected as Markdown."""
    value = "## Just a Header"
    assert SmartBlobDetector.detect_type(value) == BlobType.MARKDOWN

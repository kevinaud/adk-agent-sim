"""Unit tests for SmartBlobRenderer.

Tests cover:
- RAW view rendering
- JSON view rendering with nested structure
- MARKDOWN view rendering
- Malformed JSON fallback
- State management integration
"""

from adk_agent_sim.ui.components.devtools_tree import (
  BlobType,
  BlobViewState,
  SmartBlobDetector,
  TreeExpansionState,
)
from adk_agent_sim.ui.components.devtools_tree.smart_blob_renderer import (
  SmartBlobRenderer,
)

# ============================================================================
# SmartBlobRenderer Initialization Tests
# ============================================================================


class TestSmartBlobRendererInit:
  """Tests for SmartBlobRenderer initialization."""

  def test_stores_value(self) -> None:
    """Constructor stores the value."""
    renderer = SmartBlobRenderer(
      value="test content",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert renderer.value == "test content"

  def test_stores_blob_id(self) -> None:
    """Constructor stores the blob_id."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="my-blob-id",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert renderer.blob_id == "my-blob-id"

  def test_stores_detected_type(self) -> None:
    """Constructor stores the detected_type."""
    renderer = SmartBlobRenderer(
      value='{"key": "value"}',
      blob_id="test-1",
      detected_type=BlobType.JSON,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert renderer.detected_type == BlobType.JSON

  def test_stores_blob_view_state(self) -> None:
    """Constructor stores the blob_view_state."""
    state = BlobViewState()
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    assert renderer.blob_view_state is state

  def test_stores_expansion_state(self) -> None:
    """Constructor stores the expansion_state."""
    exp_state = TreeExpansionState()
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=exp_state,
    )
    assert renderer.expansion_state is exp_state


# ============================================================================
# SmartBlobRenderer Mode Selection Tests
# ============================================================================


class TestSmartBlobRendererModeSelection:
  """Tests for view mode selection."""

  def test_plain_text_defaults_to_raw(self) -> None:
    """PLAIN_TEXT content defaults to RAW mode."""
    state = BlobViewState()
    renderer = SmartBlobRenderer(
      value="plain text",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    mode = renderer._get_current_mode()
    assert mode == BlobType.PLAIN_TEXT

  def test_json_defaults_to_json(self) -> None:
    """JSON content defaults to JSON mode."""
    state = BlobViewState()
    renderer = SmartBlobRenderer(
      value='{"key": "value"}',
      blob_id="test-1",
      detected_type=BlobType.JSON,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    mode = renderer._get_current_mode()
    assert mode == BlobType.JSON

  def test_markdown_defaults_to_markdown(self) -> None:
    """MARKDOWN content defaults to MARKDOWN mode."""
    state = BlobViewState()
    renderer = SmartBlobRenderer(
      value="# Heading",
      blob_id="test-1",
      detected_type=BlobType.MARKDOWN,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    mode = renderer._get_current_mode()
    assert mode == BlobType.MARKDOWN

  def test_respects_preset_mode(self) -> None:
    """Respects mode set in state."""
    state = BlobViewState()
    state.set_mode("test-1", BlobType.PLAIN_TEXT)
    renderer = SmartBlobRenderer(
      value='{"key": "value"}',
      blob_id="test-1",
      detected_type=BlobType.JSON,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    mode = renderer._get_current_mode()
    assert mode == BlobType.PLAIN_TEXT


# ============================================================================
# SmartBlobRenderer HTML Escaping Tests
# ============================================================================


class TestSmartBlobRendererHtmlEscaping:
  """Tests for HTML escaping."""

  def test_escapes_ampersand(self) -> None:
    """Ampersand is escaped."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    result = renderer._escape_html("foo & bar")
    assert "&amp;" in result

  def test_escapes_less_than(self) -> None:
    """Less than is escaped."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    result = renderer._escape_html("foo < bar")
    assert "&lt;" in result

  def test_escapes_greater_than(self) -> None:
    """Greater than is escaped."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    result = renderer._escape_html("foo > bar")
    assert "&gt;" in result

  def test_escapes_quotes(self) -> None:
    """Double quotes are escaped."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    result = renderer._escape_html('foo "bar" baz')
    assert "&quot;" in result

  def test_converts_newlines_to_br(self) -> None:
    """Newlines are converted to <br>."""
    renderer = SmartBlobRenderer(
      value="test",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    result = renderer._escape_html("line1\nline2")
    assert "<br>" in result


# ============================================================================
# SmartBlobRenderer Blob Detection Integration Tests
# ============================================================================


class TestSmartBlobRendererDetection:
  """Tests for integration with SmartBlobDetector."""

  def test_json_object_detected(self) -> None:
    """JSON object is detected correctly."""
    value = '{"name": "test", "count": 42}'
    detected = SmartBlobDetector.detect_type(value)
    assert detected == BlobType.JSON

  def test_json_array_detected(self) -> None:
    """JSON array is detected correctly."""
    value = '[1, 2, 3, "four"]'
    detected = SmartBlobDetector.detect_type(value)
    assert detected == BlobType.JSON

  def test_markdown_heading_detected(self) -> None:
    """Markdown heading is detected."""
    value = "# Main Heading\n\nSome content here."
    detected = SmartBlobDetector.detect_type(value)
    assert detected == BlobType.MARKDOWN

  def test_plain_text_detected(self) -> None:
    """Plain text is detected correctly."""
    value = "Just some plain text without special formatting."
    detected = SmartBlobDetector.detect_type(value)
    assert detected == BlobType.PLAIN_TEXT

  def test_malformed_json_fallback(self) -> None:
    """Malformed JSON falls back to PLAIN_TEXT."""
    value = '{"key": "value"'  # Missing closing brace
    detected = SmartBlobDetector.detect_type(value)
    assert detected == BlobType.PLAIN_TEXT


# ============================================================================
# SmartBlobRenderer State Management Tests
# ============================================================================


class TestSmartBlobRendererStateManagement:
  """Tests for state management across multiple blobs."""

  def test_multiple_blobs_independent_state(self) -> None:
    """Multiple blobs have independent state."""
    state = BlobViewState()

    renderer1 = SmartBlobRenderer(
      value='{"a": 1}',
      blob_id="blob-1",
      detected_type=BlobType.JSON,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )

    renderer2 = SmartBlobRenderer(
      value="# Header",
      blob_id="blob-2",
      detected_type=BlobType.MARKDOWN,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )

    # Each has its own default
    assert renderer1._get_current_mode() == BlobType.JSON
    assert renderer2._get_current_mode() == BlobType.MARKDOWN

  def test_shared_state_between_renderers(self) -> None:
    """Renderers with same blob_id share state."""
    state = BlobViewState()

    renderer1 = SmartBlobRenderer(
      value='{"a": 1}',
      blob_id="shared-blob",
      detected_type=BlobType.JSON,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )

    # First renderer initializes to JSON
    assert renderer1._get_current_mode() == BlobType.JSON

    # Set mode to RAW
    state.set_mode("shared-blob", BlobType.PLAIN_TEXT)

    # Second renderer with same ID should see RAW
    renderer2 = SmartBlobRenderer(
      value='{"a": 1}',
      blob_id="shared-blob",
      detected_type=BlobType.JSON,
      blob_view_state=state,
      expansion_state=TreeExpansionState(),
    )
    assert renderer2._get_current_mode() == BlobType.PLAIN_TEXT


# ============================================================================
# SmartBlobRenderer Edge Cases
# ============================================================================


class TestSmartBlobRendererEdgeCases:
  """Tests for edge cases."""

  def test_empty_string(self) -> None:
    """Handles empty string."""
    renderer = SmartBlobRenderer(
      value="",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert renderer.value == ""
    assert renderer._get_current_mode() == BlobType.PLAIN_TEXT

  def test_whitespace_only(self) -> None:
    """Handles whitespace-only string."""
    renderer = SmartBlobRenderer(
      value="   \n\t  ",
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert renderer._get_current_mode() == BlobType.PLAIN_TEXT

  def test_nested_json_string(self) -> None:
    """Handles nested JSON (double-encoded)."""
    import json

    # This is a JSON string containing an escaped JSON string as a value
    inner_json = '{"nested": true}'
    outer = {"data": inner_json}
    outer_json = json.dumps(outer)

    # The outer is detected as JSON
    detected = SmartBlobDetector.detect_type(outer_json)
    assert detected == BlobType.JSON

  def test_very_long_content(self) -> None:
    """Handles very long content."""
    long_content = "x" * 10000
    renderer = SmartBlobRenderer(
      value=long_content,
      blob_id="test-1",
      detected_type=BlobType.PLAIN_TEXT,
      blob_view_state=BlobViewState(),
      expansion_state=TreeExpansionState(),
    )
    assert len(renderer.value) == 10000

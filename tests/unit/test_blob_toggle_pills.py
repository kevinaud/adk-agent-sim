"""Unit tests for BlobTogglePills and BlobViewState.

Tests cover:
- BlobType enum values and labels
- BlobViewState get/set/reset operations
- BlobViewState default mode selection
- BlobTogglePills mode availability
- BlobTogglePills click handling and state management
"""

from adk_agent_sim.ui.components.devtools_tree import (
  BlobTogglePills,
  BlobType,
  BlobViewState,
)

# ============================================================================
# BlobType Enum Tests
# ============================================================================


class TestBlobType:
  """Tests for BlobType enum."""

  def test_plain_text_value(self) -> None:
    """PLAIN_TEXT has correct value."""
    assert BlobType.PLAIN_TEXT.value == "plain_text"

  def test_plain_text_label(self) -> None:
    """PLAIN_TEXT has RAW label for UI display."""
    assert BlobType.PLAIN_TEXT.label == "RAW"

  def test_json_value(self) -> None:
    """JSON has correct value."""
    assert BlobType.JSON.value == "json"

  def test_json_label(self) -> None:
    """JSON has JSON label for UI display."""
    assert BlobType.JSON.label == "JSON"

  def test_markdown_value(self) -> None:
    """MARKDOWN has correct value."""
    assert BlobType.MARKDOWN.value == "markdown"

  def test_markdown_label(self) -> None:
    """MARKDOWN has MD label for UI display."""
    assert BlobType.MARKDOWN.label == "MD"

  def test_all_types_exist(self) -> None:
    """All expected types exist."""
    types = list(BlobType)
    assert len(types) == 3
    assert BlobType.PLAIN_TEXT in types
    assert BlobType.JSON in types
    assert BlobType.MARKDOWN in types


# ============================================================================
# BlobViewState Tests
# ============================================================================


class TestBlobViewState:
  """Tests for BlobViewState dataclass."""

  def test_initial_state_empty(self) -> None:
    """New state has no modes set."""
    state = BlobViewState()
    assert state.get_mode("any-id") is None

  def test_get_mode_with_default(self) -> None:
    """get_mode returns default when mode not set."""
    state = BlobViewState()
    assert state.get_mode("blob-1", BlobType.PLAIN_TEXT) == BlobType.PLAIN_TEXT
    assert state.get_mode("blob-1", BlobType.JSON) == BlobType.JSON

  def test_set_mode_basic(self) -> None:
    """set_mode stores mode for blob."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.JSON)
    assert state.get_mode("blob-1") == BlobType.JSON

  def test_set_mode_override(self) -> None:
    """set_mode overrides previous mode."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.PLAIN_TEXT)
    state.set_mode("blob-1", BlobType.MARKDOWN)
    assert state.get_mode("blob-1") == BlobType.MARKDOWN

  def test_multiple_blobs_independent(self) -> None:
    """Different blobs have independent modes."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.PLAIN_TEXT)
    state.set_mode("blob-2", BlobType.JSON)
    state.set_mode("blob-3", BlobType.MARKDOWN)

    assert state.get_mode("blob-1") == BlobType.PLAIN_TEXT
    assert state.get_mode("blob-2") == BlobType.JSON
    assert state.get_mode("blob-3") == BlobType.MARKDOWN

  def test_reset_single_blob(self) -> None:
    """reset with blob_id clears only that blob."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.JSON)
    state.set_mode("blob-2", BlobType.MARKDOWN)

    state.reset("blob-1")

    assert state.get_mode("blob-1") is None
    assert state.get_mode("blob-2") == BlobType.MARKDOWN

  def test_reset_all_blobs(self) -> None:
    """reset without blob_id clears all blobs."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.JSON)
    state.set_mode("blob-2", BlobType.MARKDOWN)

    state.reset()

    assert state.get_mode("blob-1") is None
    assert state.get_mode("blob-2") is None

  def test_reset_nonexistent_blob_no_error(self) -> None:
    """reset with nonexistent blob_id doesn't raise."""
    state = BlobViewState()
    state.reset("nonexistent")  # Should not raise


class TestBlobViewStateDefaultMode:
  """Tests for BlobViewState.default_mode_for_type."""

  def test_json_type_defaults_to_json(self) -> None:
    """JSON detected type defaults to JSON view mode."""
    mode = BlobViewState.default_mode_for_type(BlobType.JSON)
    assert mode == BlobType.JSON

  def test_markdown_type_defaults_to_markdown(self) -> None:
    """MARKDOWN detected type defaults to MARKDOWN view mode."""
    mode = BlobViewState.default_mode_for_type(BlobType.MARKDOWN)
    assert mode == BlobType.MARKDOWN

  def test_plain_text_type_defaults_to_plain_text(self) -> None:
    """PLAIN_TEXT detected type defaults to PLAIN_TEXT view mode."""
    mode = BlobViewState.default_mode_for_type(BlobType.PLAIN_TEXT)
    assert mode == BlobType.PLAIN_TEXT


# ============================================================================
# BlobTogglePills Tests - Basic Initialization
# ============================================================================


class TestBlobTogglePillsInit:
  """Tests for BlobTogglePills initialization."""

  def test_stores_blob_id(self) -> None:
    """Constructor stores blob_id."""
    state = BlobViewState()
    pills = BlobTogglePills("my-blob", BlobType.PLAIN_TEXT, state)
    assert pills.blob_id == "my-blob"

  def test_stores_detected_type(self) -> None:
    """Constructor stores detected_type."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    assert pills.detected_type == BlobType.JSON

  def test_stores_state(self) -> None:
    """Constructor stores state reference."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.PLAIN_TEXT, state)
    assert pills.state is state

  def test_stores_callback(self) -> None:
    """Constructor stores on_change callback."""
    state = BlobViewState()

    def callback(m: BlobType) -> None:
      pass

    pills = BlobTogglePills("blob-1", BlobType.PLAIN_TEXT, state, on_change=callback)
    assert pills.on_change is callback

  def test_callback_default_none(self) -> None:
    """on_change defaults to None."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.PLAIN_TEXT, state)
    assert pills.on_change is None


# ============================================================================
# BlobTogglePills Tests - Available Modes
# ============================================================================


class TestBlobTogglePillsAvailableModes:
  """Tests for get_available_modes method."""

  def test_plain_text_blob_only_plain_text(self) -> None:
    """PLAIN_TEXT blob only has PLAIN_TEXT mode available."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.PLAIN_TEXT, state)
    modes = pills.get_available_modes()
    assert modes == [BlobType.PLAIN_TEXT]

  def test_json_blob_has_plain_text_and_json(self) -> None:
    """JSON blob has PLAIN_TEXT and JSON modes available."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    modes = pills.get_available_modes()
    assert modes == [BlobType.PLAIN_TEXT, BlobType.JSON]

  def test_markdown_blob_has_plain_text_and_markdown(self) -> None:
    """MARKDOWN blob has PLAIN_TEXT and MARKDOWN modes available."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.MARKDOWN, state)
    modes = pills.get_available_modes()
    assert modes == [BlobType.PLAIN_TEXT, BlobType.MARKDOWN]


# ============================================================================
# BlobTogglePills Tests - Current Mode
# ============================================================================


class TestBlobTogglePillsCurrentMode:
  """Tests for get_current_mode method."""

  def test_initializes_to_default_for_json(self) -> None:
    """JSON blob initializes to JSON mode."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    mode = pills.get_current_mode()
    assert mode == BlobType.JSON

  def test_initializes_to_default_for_markdown(self) -> None:
    """MARKDOWN blob initializes to MARKDOWN mode."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.MARKDOWN, state)
    mode = pills.get_current_mode()
    assert mode == BlobType.MARKDOWN

  def test_initializes_to_default_for_plain_text(self) -> None:
    """PLAIN_TEXT blob initializes to PLAIN_TEXT mode."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.PLAIN_TEXT, state)
    mode = pills.get_current_mode()
    assert mode == BlobType.PLAIN_TEXT

  def test_respects_preset_mode(self) -> None:
    """get_current_mode returns preset mode."""
    state = BlobViewState()
    state.set_mode("blob-1", BlobType.PLAIN_TEXT)
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    mode = pills.get_current_mode()
    assert mode == BlobType.PLAIN_TEXT

  def test_sets_mode_on_first_access(self) -> None:
    """get_current_mode sets mode in state on first access."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    assert state.get_mode("blob-1") is None  # Not set yet
    pills.get_current_mode()
    assert state.get_mode("blob-1") == BlobType.JSON  # Now set


# ============================================================================
# BlobTogglePills Tests - Click Handler
# ============================================================================


class TestBlobTogglePillsClickHandler:
  """Tests for _handle_click method."""

  def test_updates_state_on_click(self) -> None:
    """Click updates state to new mode."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    pills.get_current_mode()  # Initialize to JSON

    pills._handle_click(BlobType.PLAIN_TEXT)

    assert state.get_mode("blob-1") == BlobType.PLAIN_TEXT

  def test_calls_callback_on_change(self) -> None:
    """Click calls on_change callback with new mode."""
    state = BlobViewState()
    received_modes: list[BlobType] = []
    pills = BlobTogglePills(
      "blob-1", BlobType.JSON, state, on_change=lambda m: received_modes.append(m)
    )
    pills.get_current_mode()  # Initialize to JSON

    pills._handle_click(BlobType.PLAIN_TEXT)

    assert received_modes == [BlobType.PLAIN_TEXT]

  def test_no_callback_if_same_mode(self) -> None:
    """Click on current mode doesn't call callback."""
    state = BlobViewState()
    received_modes: list[BlobType] = []
    pills = BlobTogglePills(
      "blob-1", BlobType.JSON, state, on_change=lambda m: received_modes.append(m)
    )
    pills.get_current_mode()  # Initialize to JSON

    pills._handle_click(BlobType.JSON)  # Click on already-active mode

    assert received_modes == []  # No callback

  def test_no_error_without_callback(self) -> None:
    """Click works without on_change callback."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    pills.get_current_mode()

    # Should not raise
    pills._handle_click(BlobType.PLAIN_TEXT)

    assert state.get_mode("blob-1") == BlobType.PLAIN_TEXT


# ============================================================================
# BlobTogglePills Tests - Style Generation
# ============================================================================


class TestBlobTogglePillsStyles:
  """Tests for style generation."""

  def test_active_pill_has_solid_background(self) -> None:
    """Active pill has solid background color."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.JSON, is_active=True)
    assert "background-color: #1976D2" in style  # Primary blue

  def test_inactive_pill_has_transparent_background(self) -> None:
    """Inactive pill has transparent background."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.PLAIN_TEXT, is_active=False)
    assert "background-color: transparent" in style

  def test_active_pill_has_white_text(self) -> None:
    """Active pill has white text."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.JSON, is_active=True)
    assert "color: #FFFFFF" in style

  def test_inactive_pill_has_gray_text(self) -> None:
    """Inactive pill has gray text."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.PLAIN_TEXT, is_active=False)
    assert "color: #616161" in style

  def test_pill_has_border(self) -> None:
    """Pill style includes border."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.PLAIN_TEXT, is_active=False)
    assert "border: 1px solid" in style

  def test_pill_has_padding(self) -> None:
    """Pill style includes padding."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.PLAIN_TEXT, is_active=False)
    assert "padding:" in style

  def test_pill_has_border_radius(self) -> None:
    """Pill style includes border-radius."""
    state = BlobViewState()
    pills = BlobTogglePills("blob-1", BlobType.JSON, state)
    style = pills._get_pill_style(BlobType.PLAIN_TEXT, is_active=False)
    assert "border-radius:" in style


# ============================================================================
# Integration Tests
# ============================================================================


class TestBlobTogglePillsIntegration:
  """Integration tests for BlobTogglePills."""

  def test_multiple_blobs_with_shared_state(self) -> None:
    """Multiple pills can share state."""
    state = BlobViewState()
    pills1 = BlobTogglePills("blob-1", BlobType.JSON, state)
    pills2 = BlobTogglePills("blob-2", BlobType.MARKDOWN, state)

    # Initialize both
    pills1.get_current_mode()
    pills2.get_current_mode()

    # Each has correct default
    assert state.get_mode("blob-1") == BlobType.JSON
    assert state.get_mode("blob-2") == BlobType.MARKDOWN

    # Changing one doesn't affect the other
    pills1._handle_click(BlobType.PLAIN_TEXT)
    assert state.get_mode("blob-1") == BlobType.PLAIN_TEXT
    assert state.get_mode("blob-2") == BlobType.MARKDOWN

  def test_full_click_cycle(self) -> None:
    """Full cycle of clicking through modes."""
    state = BlobViewState()
    changes: list[BlobType] = []
    pills = BlobTogglePills(
      "blob-1", BlobType.JSON, state, on_change=lambda m: changes.append(m)
    )

    # Initialize
    assert pills.get_current_mode() == BlobType.JSON

    # Switch to PLAIN_TEXT
    pills._handle_click(BlobType.PLAIN_TEXT)
    assert pills.get_current_mode() == BlobType.PLAIN_TEXT
    assert changes[-1] == BlobType.PLAIN_TEXT

    # Switch back to JSON
    pills._handle_click(BlobType.JSON)
    assert pills.get_current_mode() == BlobType.JSON
    assert changes[-1] == BlobType.JSON

    # Clicking same mode doesn't trigger callback
    pills._handle_click(BlobType.JSON)
    assert len(changes) == 2  # Still just 2 changes

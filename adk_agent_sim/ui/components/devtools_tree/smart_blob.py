"""Smart blob detection for structured content in strings.

This module provides utilities for detecting JSON and Markdown content
in string values, enabling appropriate rendering.

Clean-room implementation: No code reused from existing components.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from markdown_it import MarkdownIt


class BlobType(Enum):
  """Content type for string values, also used as view mode.

  Each type has a value (for serialization) and a label (for UI display).
  PLAIN_TEXT is always available as a view mode. JSON and MARKDOWN are available
  when the content is detected as that type.
  """

  PLAIN_TEXT = ("plain_text", "RAW")  # Plain text / raw view
  JSON = ("json", "JSON")  # Valid JSON object or array
  MARKDOWN = ("markdown", "MD")  # Contains Markdown formatting patterns

  def __init__(self, value: str, label: str) -> None:
    self._value_ = value
    self._label = label

  @property
  def label(self) -> str:
    """Display label for UI."""
    return self._label


@dataclass
class BlobViewState:
  """Manages view mode state for individual blob values.

  Tracks the current view mode for each blob, with support
  for default mode selection based on detected content type.
  """

  # Map from blob_id to current BlobType (used as view mode)
  _modes: dict[str, BlobType] = field(default_factory=dict)

  def get_mode(self, blob_id: str, default: BlobType | None = None) -> BlobType | None:
    """Get the current view mode for a blob.

    Args:
      blob_id: Unique identifier for the blob
      default: Default mode to return if not set

    Returns:
      Current BlobType or default if not set
    """
    return self._modes.get(blob_id, default)

  def set_mode(self, blob_id: str, mode: BlobType) -> None:
    """Set the view mode for a blob.

    Args:
      blob_id: Unique identifier for the blob
      mode: BlobType to set as view mode
    """
    self._modes[blob_id] = mode

  def reset(self, blob_id: str | None = None) -> None:
    """Reset view mode(s) to unset state.

    Args:
      blob_id: If provided, reset only this blob. Otherwise reset all.
    """
    if blob_id is not None:
      self._modes.pop(blob_id, None)
    else:
      self._modes.clear()

  @staticmethod
  def default_mode_for_type(detected_type: BlobType) -> BlobType:
    """Determine the default view mode based on detected blob type.

    This provides smart defaults: JSON content shows as JSON tree,
    Markdown shows as rendered Markdown, plain/raw text shows raw.

    Args:
      detected_type: The detected BlobType

    Returns:
      Recommended default BlobType as view mode
    """
    # For detected types, show in their native format
    # RAW content stays RAW
    return detected_type


class SmartBlobDetector:
  """Detects JSON and Markdown content in string values.

  Provides static methods to analyze string content and determine
  the most appropriate rendering format.
  """

  @staticmethod
  def try_parse_json(value: str) -> tuple[Any, str | None]:
    """Attempt to parse string as JSON.

    Args:
      value: String to parse

    Returns:
      Tuple of (parsed_data, error_message)
      If successful: (data, None)
      If failed: (None, error_message)
    """
    if not value or not value.strip():
      return None, "Empty string"

    try:
      parsed = json.loads(value)
      # Only consider objects and arrays as JSON blobs
      # Primitives (strings, numbers, booleans, null) are not JSON blobs
      if isinstance(parsed, (dict, list)):
        return parsed, None
      return None, "Not a JSON object or array"
    except json.JSONDecodeError as e:
      return None, str(e)

  @staticmethod
  def detect_markdown_patterns(value: str) -> bool:
    """Check if string contains Markdown patterns.

    Uses markdown-it-py to parse the string and check for structural elements.

    Args:
      value: String to analyze

    Returns:
      True if Markdown patterns detected
    """
    if not value or not value.strip():
      return False

    # Need at least some meaningful content
    if len(value.strip()) < 3:
      return False

    md = MarkdownIt()
    tokens = md.parse(value)

    # Check if any token is a "structural" markdown element
    # We ignore 'paragraph_open', 'inline', and 'text' as they exist in plain text
    markdown_indicators = {
      "heading_open",
      "fence",
      "blockquote_open",
      "list_item_open",
      "table_open",
      "hr",
      "link_open",
      "em_open",
      "strong_open",
    }

    for token in tokens:
      if token.type in markdown_indicators:
        return True
      # Also check inline children for formatting (bold/italics/links)
      if token.type == "inline" and token.children:
        for child in token.children:
          if child.type in markdown_indicators:
            return True
    return False

  @staticmethod
  def detect_type(value: str) -> BlobType:
    """Detect the type of structured content in a string.

    Detection priority:
    1. JSON (if valid JSON object or array)
    2. Markdown (if contains Markdown patterns)
    3. RAW (default for plain text)

    Args:
      value: String to analyze

    Returns:
      BlobType indicating the detected content type
    """
    if not value or not value.strip():
      return BlobType.PLAIN_TEXT

    # Try JSON first (higher priority)
    parsed, _ = SmartBlobDetector.try_parse_json(value)
    if parsed is not None:
      return BlobType.JSON

    # Check for Markdown patterns
    if SmartBlobDetector.detect_markdown_patterns(value):
      return BlobType.MARKDOWN

    # Default to plain text
    return BlobType.PLAIN_TEXT

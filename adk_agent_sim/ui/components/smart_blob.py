"""Smart blob detection for structured content in strings.

This module provides utilities for detecting JSON and Markdown content
in string values, enabling appropriate rendering.

Clean-room implementation: No code reused from existing components.
"""

import json
import re
from enum import Enum
from typing import Any


class BlobType(Enum):
  """Detected content type for string values."""

  JSON = "json"  # Valid JSON object or array
  MARKDOWN = "markdown"  # Contains Markdown formatting patterns
  PLAIN = "plain"  # Plain text, no detected structure


class SmartBlobDetector:
  """Detects JSON and Markdown content in string values.

  Provides static methods to analyze string content and determine
  the most appropriate rendering format.
  """

  # Markdown patterns to detect
  # - Headers: ## or ### at start of line
  # - Bold: **text**
  # - Lists: - item or 1. item at start of line
  # - Code blocks: ``` at start of line
  _MARKDOWN_PATTERNS = [
    re.compile(r"^#{1,6}\s", re.MULTILINE),  # Headers
    re.compile(r"\*\*[^*]+\*\*"),  # Bold
    re.compile(r"^[-*]\s", re.MULTILINE),  # Unordered lists
    re.compile(r"^\d+\.\s", re.MULTILINE),  # Ordered lists
    re.compile(r"^```", re.MULTILINE),  # Code blocks
  ]

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

    Detects: headers (##), bold (**), lists (- or 1.), code blocks (```)

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

    for pattern in SmartBlobDetector._MARKDOWN_PATTERNS:
      if pattern.search(value):
        return True

    return False

  @staticmethod
  def detect_type(value: str) -> BlobType:
    """Detect the type of structured content in a string.

    Detection priority:
    1. JSON (if valid JSON object or array)
    2. Markdown (if contains Markdown patterns)
    3. Plain (default)

    Args:
      value: String to analyze

    Returns:
      BlobType indicating the detected content type
    """
    if not value or not value.strip():
      return BlobType.PLAIN

    # Try JSON first (higher priority)
    parsed, _ = SmartBlobDetector.try_parse_json(value)
    if parsed is not None:
      return BlobType.JSON

    # Check for Markdown patterns
    if SmartBlobDetector.detect_markdown_patterns(value):
      return BlobType.MARKDOWN

    # Default to plain text
    return BlobType.PLAIN

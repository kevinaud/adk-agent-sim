"""Data-driven screenshot tests for UI components via the Component Gallery.

This module uses a declarative configuration to generate screenshot tests
for each component registered in the gallery. Tests navigate to the gallery
URL with specific query parameters to control component state.

Screenshots are saved to: docs/screenshots/components/{component}_{test_name}.png

Usage:
  uv run pytest tests/e2e/test_component_screenshots.py -v
  uv run pytest tests/e2e/test_component_screenshots.py -k "AgentCard" -v
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
  from playwright.sync_api import Page

# =============================================================================
# Constants
# =============================================================================

ELEMENT_TIMEOUT = 10000  # Playwright uses milliseconds
GALLERY_PATH = "/_gallery"
COMPONENT_SCREENSHOT_DIR = (
  Path(__file__).parent.parent.parent / "docs" / "screenshots" / "components"
)

# Viewport dimensions for consistent screenshots
SCREENSHOT_WIDTH = 800
SCREENSHOT_HEIGHT = 600


# =============================================================================
# Test Configuration
# =============================================================================


@dataclass
class ComponentScreenshot:
  """Configuration for a single component screenshot test case."""

  # Component name as registered in the gallery
  component: str

  # Test case name (used in screenshot filename)
  test_name: str

  # Query parameters to pass to the gallery URL
  params: dict[str, str] = field(default_factory=dict)

  # Optional: selector to wait for before capturing screenshot
  wait_for_selector: str | None = None

  # Optional: viewport override (width, height)
  viewport: tuple[int, int] | None = None

  # Optional: description for documentation
  description: str = ""

  @property
  def screenshot_path(self) -> Path:
    """Generate the screenshot file path."""
    return COMPONENT_SCREENSHOT_DIR / f"{self.component}_{self.test_name}.png"

  @property
  def gallery_url(self) -> str:
    """Generate the full gallery URL with query params."""
    url = f"{GALLERY_PATH}/{self.component}"
    if self.params:
      query = "&".join(f"{k}={v}" for k, v in self.params.items())
      url = f"{url}?{query}"
    return url

  @property
  def test_id(self) -> str:
    """Generate a unique test ID for pytest parametrization."""
    return f"{self.component}_{self.test_name}"


# =============================================================================
# Screenshot Test Cases Configuration
# =============================================================================

# Define all screenshot test cases here.
# Each entry creates one test that navigates to the gallery and captures a screenshot.

SCREENSHOT_TESTS: list[ComponentScreenshot] = [
  # -------------------------------------------------------------------------
  # AgentCard variations
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="AgentCard",
    test_name="default",
    params={"name": "Support Bot", "description": "A helpful customer support agent"},
    description="Standard agent card with name and description",
  ),
  ComponentScreenshot(
    component="AgentCard",
    test_name="long_description",
    params={
      "name": "Research Assistant",
      "description": (
        "An advanced AI agent that helps with research tasks including "
        "literature review, data analysis, and citation management"
      ),
    },
    description="Agent card with longer description text",
  ),
  ComponentScreenshot(
    component="AgentCard",
    test_name="no_description",
    params={"name": "Minimal Agent"},
    description="Agent card without description",
  ),
  # -------------------------------------------------------------------------
  # JsonTree variations
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="JsonTree",
    test_name="simple_object",
    params={
      "data": '{"name": "Alice", "age": 30, "active": true}',
      "label": "user",
      "expanded": "true",
    },
    description="Simple JSON object with primitive values",
  ),
  ComponentScreenshot(
    component="JsonTree",
    test_name="nested_object",
    params={
      "data": '{"user": {"name": "Bob", "settings": {"theme": "dark"}}, "count": 42}',
      "label": "config",
      "expanded": "true",
      "max_depth": "3",
    },
    description="Nested JSON object structure",
  ),
  ComponentScreenshot(
    component="JsonTree",
    test_name="array_data",
    params={
      "data": '[{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]',
      "label": "items",
      "expanded": "true",
    },
    description="JSON array with objects",
  ),
  ComponentScreenshot(
    component="JsonTree",
    test_name="collapsed",
    params={
      "data": '{"nested": {"deep": {"value": 123}}}',
      "label": "data",
      "expanded": "false",
    },
    description="Collapsed JSON tree",
  ),
  # -------------------------------------------------------------------------
  # DevToolsTree variations (new component - clean-room implementation)
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="DevToolsTree",
    test_name="simple_object",
    params={
      "data": '{"name": "Alice", "age": 30, "active": true}',
      "tree_id": "simple-demo",
    },
    description="Simple JSON object with DevTools styling",
  ),
  ComponentScreenshot(
    component="DevToolsTree_Nested",
    test_name="default",
    description="DevToolsTree with nested execution trace data",
    viewport=(800, 700),
  ),
  ComponentScreenshot(
    component="DevToolsTree_Collapsed",
    test_name="default",
    description="DevToolsTree with all nodes collapsed",
  ),
  ComponentScreenshot(
    component="DevToolsTree_Primitives",
    test_name="default",
    description="DevToolsTree showcasing all JSON primitive types",
    viewport=(800, 400),
  ),
  ComponentScreenshot(
    component="DevToolsTree_ArrayRoot",
    test_name="default",
    description="DevToolsTree with array as root element",
    viewport=(800, 350),
  ),
  ComponentScreenshot(
    component="DevToolsTree_DeeplyNested",
    test_name="default",
    description="DevToolsTree with deeply nested structure showing indentation",
    viewport=(800, 400),
  ),
  ComponentScreenshot(
    component="DevToolsTree_LongStrings",
    test_name="default",
    description="DevToolsTree with long strings showing truncation behavior",
    viewport=(800, 350),
  ),
  ComponentScreenshot(
    component="DevToolsTree_ToolOutput",
    test_name="default",
    description="DevToolsTree displaying realistic tool output data",
    viewport=(800, 700),
  ),
  # -------------------------------------------------------------------------
  # TextPresenter variations
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="TextPresenter",
    test_name="raw_text",
    params={
      "content": "This is plain text content without any special formatting.",
      "element_id": "raw_demo",
    },
    description="Text presenter in raw mode",
  ),
  ComponentScreenshot(
    component="TextPresenter",
    test_name="json_content",
    params={
      "content": '{"status": "success", "data": {"id": 123, "items": ["a", "b"]}}',
      "element_id": "json_demo",
      "default_mode": "json",
    },
    description="Text presenter showing JSON content",
  ),
  ComponentScreenshot(
    component="TextPresenter",
    test_name="markdown_content",
    params={
      "content": (
        "# Heading\\n\\n**Bold** and *italic* text.\\n\\n- List item 1\\n- List item 2"
      ),
      "element_id": "md_demo",
      "default_mode": "markdown",
    },
    description="Text presenter rendering markdown",
  ),
  # -------------------------------------------------------------------------
  # LoadingBlock variations
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="LoadingBlock",
    test_name="default",
    params={"tool_name": "search_database"},
    description="Loading block with tool name",
  ),
  ComponentScreenshot(
    component="LoadingBlock",
    test_name="with_elapsed_time",
    params={"tool_name": "analyze_data", "elapsed_ms": "2500"},
    description="Loading block showing elapsed time",
  ),
  # -------------------------------------------------------------------------
  # EventBlock variations (factory-based)
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="EventBlock_UserQuery",
    test_name="default",
    description="User query event block",
  ),
  ComponentScreenshot(
    component="EventBlock_ToolCall",
    test_name="default",
    description="Tool call event block",
  ),
  ComponentScreenshot(
    component="EventBlock_ToolOutput_String",
    test_name="default",
    description="Tool output with string result",
  ),
  ComponentScreenshot(
    component="EventBlock_ToolOutput_Complex",
    test_name="default",
    description="Tool output with complex nested data",
    viewport=(800, 800),  # Taller for complex content
  ),
  ComponentScreenshot(
    component="EventBlock_ToolError",
    test_name="default",
    description="Tool error event block",
  ),
  ComponentScreenshot(
    component="EventBlock_FinalResponse",
    test_name="default",
    description="Final response event block with markdown",
  ),
  ComponentScreenshot(
    component="EventBlock_Loading",
    test_name="default",
    description="Loading state event block",
  ),
  # -------------------------------------------------------------------------
  # ToolCatalog and ActionPanel (factory-based)
  # -------------------------------------------------------------------------
  ComponentScreenshot(
    component="ToolCatalog_Default",
    test_name="default",
    description="Tool catalog with sample tools",
    viewport=(800, 700),
  ),
  ComponentScreenshot(
    component="ActionPanel_Default",
    test_name="default",
    description="Action panel with tool selection and response input",
    viewport=(800, 700),
  ),
]


# =============================================================================
# Test Implementation
# =============================================================================


def _get_test_ids() -> list[str]:
  """Generate test IDs for pytest parametrization."""
  return [test.test_id for test in SCREENSHOT_TESTS]


@pytest.mark.parametrize(
  "screenshot_config",
  SCREENSHOT_TESTS,
  ids=_get_test_ids(),
)
class TestComponentScreenshots:
  """Data-driven screenshot tests for gallery components."""

  def test_capture_screenshot(
    self,
    page: "Page",
    base_url: str,
    screenshot_config: ComponentScreenshot,
  ) -> None:
    """Capture a screenshot of a component in the gallery.

    This test:
    1. Navigates to the component gallery URL with query params
    2. Waits for the component to render
    3. Captures a screenshot to the components directory
    """
    # Set viewport size
    width, height = screenshot_config.viewport or (SCREENSHOT_WIDTH, SCREENSHOT_HEIGHT)
    page.set_viewport_size({"width": width, "height": height})

    # Navigate to the gallery component URL
    full_url = f"{base_url}{screenshot_config.gallery_url}"
    page.goto(full_url)
    page.wait_for_load_state("networkidle")

    # Wait for the component wrapper to be present
    wrapper_selector = "[data-testid='gallery-component-wrapper']"
    page.wait_for_selector(wrapper_selector, timeout=ELEMENT_TIMEOUT)

    # Optional: wait for additional selector if specified
    if screenshot_config.wait_for_selector:
      page.wait_for_selector(
        screenshot_config.wait_for_selector, timeout=ELEMENT_TIMEOUT
      )

    # Small delay to ensure animations complete
    page.wait_for_timeout(200)

    # Ensure screenshot directory exists
    COMPONENT_SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Capture screenshot of just the component wrapper
    wrapper = page.locator(wrapper_selector)
    wrapper.screenshot(path=screenshot_config.screenshot_path)

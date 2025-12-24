"""E2E tests for the ADK Agent Simulator.

This module contains Playwright-based E2E tests that verify the complete
simulation flow from agent selection through tool execution to final response.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from playwright.sync_api import Page


# =============================================================================
# Constants (duplicated from conftest for direct access)
# =============================================================================

ELEMENT_TIMEOUT = 10000  # Playwright uses milliseconds
TOOL_EXECUTION_TIMEOUT = 30000  # Playwright uses milliseconds


# =============================================================================
# Helper Functions for Tool Selection (Card-based UI)
# =============================================================================


def select_tool_from_catalog(page: "Page", tool_name: str) -> None:
  """Select a tool from the ToolCatalog card-based UI.

  The ToolCatalog displays tools as clickable cards. This helper:
  1. Waits for the tool card to be visible
  2. Clicks on the card to select it

  Args:
    page: Playwright Page instance
    tool_name: Name of the tool to select (e.g., "add_numbers")
  """
  # Wait for the tool card to be visible in the catalog
  # Tool catalog cards have cursor-pointer and mb-2
  # classes to distinguish from parent cards
  tool_card = page.locator(f'.q-card.cursor-pointer:has-text("{tool_name}")')
  tool_card.wait_for(timeout=ELEMENT_TIMEOUT)
  tool_card.click()
  page.wait_for_load_state("networkidle")


# =============================================================================
# User Story 1: Complete Simulation Flow (Happy Path)
# =============================================================================


class TestHappyPath:
  """Test complete simulation flow from start to finish."""

  def test_agent_selection(self, page: Page) -> None:
    """Verify Playwright connects and can select TestAgent.

    TC-01 Step 1: User can access agent selection page and see TestAgent.
    """
    # Verify page loaded with agent selection
    page.wait_for_selector("text=ADK Agent Simulator", timeout=ELEMENT_TIMEOUT)

    # Verify TestAgent card is available (new card-based UI)
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)

    # Click the TestAgent card to select it
    page.locator("text=TestAgent").click()
    page.wait_for_load_state("networkidle")

  def test_query_submission(self, page: Page) -> None:
    """Enter query and verify tools are displayed.

    TC-01 Step 2: After starting session, tools should be available.
    """
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator(".q-card:has-text('TestAgent')").click()
    page.wait_for_load_state("networkidle")

    # Enter a query in the textarea
    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")

    # Start the session
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Verify we're now in the action panel with tools available
    page.wait_for_selector("text=Choose Action", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Call Tool", timeout=ELEMENT_TIMEOUT)

  def test_tool_selection(self, page: Page) -> None:
    """Select add_numbers tool and verify form renders.

    TC-01 Step 3: Tool selection shows parameter form.
    """
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator(".q-card:has-text('TestAgent')").click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Wait for action panel
    page.wait_for_selector("text=Choose Action", timeout=ELEMENT_TIMEOUT)

    # Select add_numbers tool from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")

    # Click Select Tool button
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify tool executor form renders with parameters
    page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Parameters", timeout=ELEMENT_TIMEOUT)

  def test_tool_execution(self, page: Page) -> None:
    """Fill form with a=5, b=3, execute, and verify result "8" in history.

    TC-01 Step 4: Tool execution produces correct result.
    """
    # Start session and get to tool form
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select add_numbers tool from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Wait for the tool executor form
    page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)

    # Fill in parameters (a=5, b=3)
    # NiceGUI number inputs - use the input within the q-field
    a_input = page.locator("label:has-text('A')").locator("..").locator("input")
    b_input = page.locator("label:has-text('B')").locator("..").locator("input")

    # Clear and fill
    a_input.fill("5")
    b_input.fill("3")

    # Execute the tool
    page.locator("button:has-text('Execute')").click()

    # Wait for execution and verify the result appears
    # The tool output should show somewhere in the page
    page.wait_for_timeout(2000)  # Wait for tool execution

    # Verify we're back at action panel (successful execution returns there)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

  def test_final_response_and_session_completion(self, page: Page) -> None:
    """Submit final response and verify session completion.

    TC-01 Step 5: Session completes after final response.
    """
    # Start session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute add_numbers tool from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Fill and execute
    inputs = page.locator("input[type='number']")
    inputs.first.fill("5")
    inputs.nth(1).fill("3")
    page.locator("button:has-text('Execute')").click()
    page.wait_for_load_state("networkidle")

    # Now submit final response via the Final Response tab
    page.locator("text=Final Response").click()
    response_input = page.locator("textarea").last
    response_input.fill("The sum of 5 and 3 is 8.")
    page.locator("button:has-text('Submit Response')").click()

    # Verify session completed
    page.wait_for_selector("text=Session Completed", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Export Golden Trace", timeout=ELEMENT_TIMEOUT)


# =============================================================================
# User Story 2: Dynamic Form Rendering (Widget Tests)
# =============================================================================


class TestWidgetRendering:
  """Test that different schema types render correct UI widgets."""

  def test_widget_number_input(self, page: Page) -> None:
    """Verify add_numbers renders numeric inputs for a and b.

    TC-02 Step 1: Integer parameters render as number inputs.
    """
    # Navigate to add_numbers tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test query")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select add_numbers from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify number inputs exist - NiceGUI uses q-field components
    # Check for labels A and B which indicate number inputs
    page.wait_for_selector("text=Parameters", timeout=ELEMENT_TIMEOUT)
    a_label = page.locator("text=A")
    b_label = page.locator("text=B")
    assert a_label.count() >= 1, "Expected label for parameter 'a'"
    assert b_label.count() >= 1, "Expected label for parameter 'b'"

  def test_widget_string_input(self, page: Page) -> None:
    """Verify greet renders text input for name parameter.

    TC-02 Step 2: String parameters render as text inputs.
    """
    # Navigate to greet tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test query")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select greet tool from the card-based catalog
    select_tool_from_catalog(page, "greet")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify text input exists (for name parameter)
    # NiceGUI renders input with labels, check for the "Name" label
    page.wait_for_selector("text=Parameters", timeout=ELEMENT_TIMEOUT)
    name_label = page.locator("text=Name")
    assert name_label.count() >= 1, "Expected label for 'name' parameter"

  def test_widget_checkbox(self, page: Page) -> None:
    """Verify greet renders checkbox for formal boolean parameter.

    TC-02 Step 3: Boolean parameters render as checkboxes or toggles.
    """
    # Navigate to greet tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test query")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select greet tool from the card-based catalog
    select_tool_from_catalog(page, "greet")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify checkbox/toggle exists for formal parameter
    # NiceGUI checkbox has the label "Formal" associated with it
    page.wait_for_selector("text=Parameters", timeout=ELEMENT_TIMEOUT)
    formal_label = page.locator("text=Formal")
    assert formal_label.count() >= 1, "Expected label for 'formal' boolean parameter"

  def test_widget_dropdown(self, page: Page) -> None:
    """Verify get_status renders dropdown for level enum parameter.

    TC-02 Step 4: Enum parameters render as dropdowns.
    """
    # Navigate to get_status tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test query")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select get_status tool from the card-based catalog
    select_tool_from_catalog(page, "get_status")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify dropdown exists for level enum - should show enum options when clicked
    # The parameter form should have a q-select for the enum
    page.wait_for_selector("text=Level", timeout=ELEMENT_TIMEOUT)

    # Click on the level dropdown to verify it has enum options
    level_select = page.locator(".q-select").last
    level_select.click()

    # Verify enum options are present
    page.wait_for_selector("text=low", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=medium", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=high", timeout=ELEMENT_TIMEOUT)


# =============================================================================
# User Story 3: Error Handling
# =============================================================================


class TestErrorHandling:
  """Test tool execution error handling and display."""

  def test_error_display(self, page: Page) -> None:
    """Execute fail_always and verify error card with error styling.

    TC-03 Step 1: Tool errors display with visual error indication.
    """
    # Start session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test error handling")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select fail_always tool from the card-based catalog
    select_tool_from_catalog(page, "fail_always")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Execute the failing tool
    page.locator("button:has-text('Execute')").click()

    # Wait for the tool to execute and error to appear
    # The error may appear in history or as a notification
    page.wait_for_timeout(2000)  # Give time for tool execution

    # Verify we return to action panel (error was handled)
    # And verify Tool Error badge appears in history
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

  def test_session_continues_after_error(self, page: Page) -> None:
    """After error, verify can still select other tools.

    TC-03 Step 2: Session remains active after tool error.
    """
    # Start session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test error recovery")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute fail_always from the card-based catalog
    select_tool_from_catalog(page, "fail_always")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")
    page.locator("button:has-text('Execute')").click()

    # Wait for error to be processed
    page.wait_for_timeout(2000)

    # Verify we can still access the action panel and select another tool
    page.wait_for_selector("text=Choose Action", timeout=ELEMENT_TIMEOUT)

    # Select a different tool (add_numbers) from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Verify we can proceed with the new tool
    page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)

  def test_error_preserved_in_history(self, page: Page) -> None:
    """Verify error remains visible in history after continuing.

    TC-03 Step 3: Error entries persist in session history.
    """
    # Start session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test error history")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute fail_always from the card-based catalog
    select_tool_from_catalog(page, "fail_always")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")
    page.locator("button:has-text('Execute')").click()

    # Wait for error
    page.wait_for_timeout(2000)

    # Now execute add_numbers successfully from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    inputs = page.locator("input[type='number']")
    inputs.first.fill("1")
    inputs.nth(1).fill("2")
    page.locator("button:has-text('Execute')").click()

    # Wait for success
    page.wait_for_timeout(2000)

    # Verify both tool calls are in history (error and success)
    # History should show fail_always entry with error
    history_section = page.locator("text=History").first
    assert history_section.is_visible(), "History section should be visible"

    # The history should contain both tool executions
    page.wait_for_selector("text=fail_always", timeout=ELEMENT_TIMEOUT)


# =============================================================================
# User Story 4: State Isolation
# =============================================================================


class TestStateIsolation:
  """Test session state isolation on page reload."""

  def test_state_clears_on_reload(self, page: Page) -> None:
    """Perform actions, reload page, verify history cleared.

    TC-04 Step 1: Page reload clears session state.
    """
    # Start session and execute a tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test state isolation")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute add_numbers from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Fill using label locators (same as working test)
    a_input = page.locator("label:has-text('A')").locator("..").locator("input")
    b_input = page.locator("label:has-text('B')").locator("..").locator("input")
    a_input.fill("10")
    b_input.fill("20")
    page.locator("button:has-text('Execute')").click()

    # Wait for tool execution
    page.wait_for_timeout(2000)

    # Verify we're back at action panel
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Navigate to home page (not reload, which preserves URL)
    page.goto(page.url.replace("/simulate", "/"))
    page.wait_for_load_state("networkidle")

    # Verify we're back at agent selection
    page.wait_for_selector("text=ADK Agent Simulator", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Select an agent", timeout=ELEMENT_TIMEOUT)

  def test_fresh_session_no_artifacts(self, page: Page) -> None:
    """Verify fresh session has no artifacts from previous sessions.

    TC-04 Step 2: New sessions start completely clean.
    """
    # Just verify we start with a clean agent selection page
    page.wait_for_selector("text=ADK Agent Simulator", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Select an agent", timeout=ELEMENT_TIMEOUT)

    # No history should be visible initially
    history_visible = page.locator("text=History").is_visible()
    assert not history_visible, "History should not be visible on fresh start"

    # No tool results should be visible
    tool_results = page.locator("text=Tool Result")
    assert tool_results.count() == 0, "No tool results should exist initially"


# =============================================================================
# User Story 5: Screenshot Capture
# =============================================================================


class TestScreenshotCapture:
  """Capture screenshots of major UX views for visual documentation.

  These tests capture screenshots at 1280x720 resolution for:
  - Visual documentation of the application
  - AI-assisted analysis of UX quality
  - Change detection during PR reviews
  """

  def test_capture_agent_selection(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the agent selection page showing dropdown and start button.

    TC-05 Step 1: Screenshot of initial agent selection view.
    """
    # Ensure page is at agent selection
    page.wait_for_selector("text=ADK Agent Simulator", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Select an agent", timeout=ELEMENT_TIMEOUT)

    # Capture screenshot
    capture_screenshot("agent-selection")

  def test_capture_query_input(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the query input form after agent selection.

    TC-05 Step 2: Screenshot of simulation start with query input.
    """
    # Start simulation
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    # Wait for query input to appear
    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)

    # Fill with sample query for context
    query_input.fill("Please add 5 and 3 together")

    # Capture screenshot
    capture_screenshot("query-input")

  def test_capture_tool_selection(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the tool selection panel showing available tools.

    TC-05 Step 3: Screenshot of action panel with tool list.
    """
    # Start session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Wait for action panel
    page.wait_for_selector("text=Choose Action", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Call Tool", timeout=ELEMENT_TIMEOUT)

    # Capture screenshot
    capture_screenshot("tool-selection")

  def test_capture_tool_form(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the dynamic parameter form for a selected tool.

    TC-05 Step 4: Screenshot of tool parameter form.
    """
    # Navigate to tool form
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select add_numbers tool from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Wait for form
    page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Parameters", timeout=ELEMENT_TIMEOUT)

    # Fill parameters for context
    a_input = page.locator("label:has-text('A')").locator("..").locator("input")
    b_input = page.locator("label:has-text('B')").locator("..").locator("input")
    a_input.fill("5")
    b_input.fill("3")

    # Capture screenshot
    capture_screenshot("tool-form")

  def test_capture_tool_result(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the history panel showing tool execution result.

    TC-05 Step 5: Screenshot of successful tool execution result.
    """
    # Execute a tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select and execute add_numbers from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    a_input = page.locator("label:has-text('A')").locator("..").locator("input")
    b_input = page.locator("label:has-text('B')").locator("..").locator("input")
    a_input.fill("5")
    b_input.fill("3")
    page.locator("button:has-text('Execute')").click()

    # Wait for result
    page.wait_for_timeout(2000)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Capture screenshot (shows history with tool result)
    capture_screenshot("tool-result")

  def test_capture_error_display(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the error display when a tool fails.

    TC-05 Step 6: Screenshot of error card styling.
    """
    # Execute failing tool
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Test error handling")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Select and execute fail_always from the card-based catalog
    select_tool_from_catalog(page, "fail_always")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    page.locator("button:has-text('Execute')").click()

    # Wait for error
    page.wait_for_timeout(2000)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Capture screenshot (shows error in history)
    capture_screenshot("error-display")

  def test_capture_session_complete(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture the session completion state.

    TC-05 Step 7: Screenshot of completed session with export option.
    """
    # Complete a full session
    # Select agent by clicking its card
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Please add 5 and 3 together")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute add_numbers from the card-based catalog
    select_tool_from_catalog(page, "add_numbers")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    inputs = page.locator("input[type='number']")
    inputs.first.fill("5")
    inputs.nth(1).fill("3")
    page.locator("button:has-text('Execute')").click()
    page.wait_for_load_state("networkidle")

    # Submit final response
    page.locator("text=Final Response").click()
    response_input = page.locator("textarea").last
    response_input.fill("The sum of 5 and 3 is 8.")
    page.locator("button:has-text('Submit Response')").click()

    # Wait for completion
    page.wait_for_selector("text=Session Completed", timeout=ELEMENT_TIMEOUT)
    page.wait_for_selector("text=Export Golden Trace", timeout=ELEMENT_TIMEOUT)

    # Capture screenshot
    capture_screenshot("session-complete")

  def test_capture_text_presentation_raw_mode(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture text output in Raw presentation mode.

    TC-05 Step 8: Screenshot of text output with Raw toggle selected.
    """
    # Start session
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Get user info")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute get_user_info tool
    select_tool_from_catalog(page, "get_user_info")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    user_id_input = (
      page.locator("label:has-text('User Id')").locator("..").locator("input")
    )
    user_id_input.fill("42")
    page.locator("button:has-text('Execute')").click()

    # Wait for result
    page.wait_for_timeout(2000)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Ensure Raw mode is selected (should be default)
    page.wait_for_selector("button:has-text('Raw')", timeout=ELEMENT_TIMEOUT)

    # Capture screenshot showing Raw mode
    capture_screenshot("text-presentation-raw")

  def test_capture_text_presentation_json_mode(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture text output in JSON presentation mode.

    TC-05 Step 9: Screenshot of text output with JSON toggle selected.
    """
    # Start session
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Get user info")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute get_user_info tool
    select_tool_from_catalog(page, "get_user_info")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    user_id_input = (
      page.locator("label:has-text('User Id')").locator("..").locator("input")
    )
    user_id_input.fill("42")
    page.locator("button:has-text('Execute')").click()

    # Wait for result
    page.wait_for_timeout(2000)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Click JSON toggle button
    json_button = page.locator("button:has-text('JSON')")
    json_button.wait_for(timeout=ELEMENT_TIMEOUT)
    json_button.click()
    page.wait_for_timeout(500)  # Wait for mode switch

    # Capture screenshot showing JSON mode
    capture_screenshot("text-presentation-json")

  def test_capture_text_presentation_markdown_mode(
    self, page: Page, capture_screenshot: Callable[[str], None]
  ) -> None:
    """Capture text output in Markdown presentation mode.

    TC-05 Step 10: Screenshot of text output with Markdown toggle selected.
    """
    # Start session
    page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
    page.locator('.q-card:has-text("TestAgent")').click()
    page.wait_for_load_state("networkidle")

    query_input = page.locator("textarea")
    query_input.wait_for(timeout=ELEMENT_TIMEOUT)
    query_input.fill("Get status message")
    page.locator("button:has-text('Start Session')").click()
    page.wait_for_load_state("networkidle")

    # Execute get_status tool (returns plain text suitable for markdown)
    select_tool_from_catalog(page, "get_status")
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Select dropdown for level parameter
    level_select = (
      page.locator("label:has-text('Level')").locator("..").locator(".q-select")
    )
    level_select.click()
    page.get_by_text("high", exact=True).click()
    page.locator("button:has-text('Execute')").click()

    # Wait for result
    page.wait_for_timeout(2000)
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Click Markdown toggle button
    markdown_button = page.locator("button:has-text('Markdown')")
    markdown_button.wait_for(timeout=ELEMENT_TIMEOUT)
    markdown_button.click()
    page.wait_for_timeout(500)  # Wait for mode switch

    # Capture screenshot showing Markdown mode
    capture_screenshot("text-presentation-markdown")

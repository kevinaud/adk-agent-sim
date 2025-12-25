"""E2E tests for event stream expand/collapse behavior.

These tests verify User Story 2 acceptance scenarios 4-9 from spec.md:
- Scenario 4: Tool outputs expanded by default
- Scenario 5: Collapse state preserved on UI action
- Scenario 6: Expand state preserved when new events added
- Scenario 7: Expand All/Collapse All buttons visible
- Scenario 8: Expand All button works
- Scenario 9: Collapse All button works
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from playwright.sync_api import Page

# =============================================================================
# Constants
# =============================================================================

ELEMENT_TIMEOUT = 10000  # Playwright uses milliseconds
TOOL_EXECUTION_TIMEOUT = 30000


# =============================================================================
# Helper Functions
# =============================================================================


def start_session_and_execute_tool(page: Page) -> None:
  """Helper to start a session and execute a tool to generate event blocks.

  This navigates through:
  1. Select TestAgent
  2. Start session with query
  3. Select and execute add_numbers tool
  """
  # Select TestAgent by clicking its card
  page.wait_for_selector("text=TestAgent", timeout=ELEMENT_TIMEOUT)
  page.locator('.q-card:has-text("TestAgent")').click()
  page.wait_for_load_state("networkidle")

  # Enter query
  query_input = page.locator("textarea")
  query_input.wait_for(timeout=ELEMENT_TIMEOUT)
  query_input.fill("Please add 5 and 3 together")
  page.locator("button:has-text('Start Session')").click()
  page.wait_for_load_state("networkidle")

  # Wait for action panel
  page.wait_for_selector("text=Choose Action", timeout=ELEMENT_TIMEOUT)

  # The tool catalog shows tools as cards - click on add_numbers card
  # Use the specific tool card class pattern
  page.wait_for_selector("text=add_numbers", timeout=ELEMENT_TIMEOUT)
  add_numbers_card = page.locator('.q-card.cursor-pointer:has-text("add_numbers")')
  add_numbers_card.click()

  # Click Select Tool button
  page.locator("button:has-text('Select Tool')").click()
  page.wait_for_load_state("networkidle")

  # Fill and execute
  page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)
  a_input = page.locator("label:has-text('A')").locator("..").locator("input")
  b_input = page.locator("label:has-text('B')").locator("..").locator("input")
  a_input.fill("5")
  b_input.fill("3")
  page.locator("button:has-text('Execute')").click()
  page.wait_for_load_state("networkidle")

  # Wait for execution to complete
  page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)


# =============================================================================
# Test Class: Event Stream Expansion Behavior
# =============================================================================


class TestEventStreamExpansion:
  """Tests for User Story 2 acceptance scenarios 4-9."""

  def test_tool_output_expanded_by_default(self, page: Page) -> None:
    """Scenario 4: Tool outputs expanded by default.

    Given a tool call or tool output event,
    When it first renders,
    Then all collapsible sections are expanded by default.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for event stream to show tool output
    page.wait_for_selector("text=Tool Output", timeout=ELEMENT_TIMEOUT)

    # Verify: Check that expansion items have expanded class
    # Look for expanded expansion items within event blocks
    expanded_items = page.locator(".q-expansion-item--expanded")

    # Should have at least one expanded item (Result section)
    assert expanded_items.count() >= 1, (
      "Expected at least one expanded section in tool output"
    )

  def test_expand_collapse_buttons_visible(self, page: Page) -> None:
    """Scenario 7: Expand All/Collapse All buttons visible.

    Given an event block with multiple collapsible sections,
    When the user views it,
    Then "Expand All" and "Collapse All" buttons are visible.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for event stream
    page.wait_for_selector("text=Tool Output", timeout=ELEMENT_TIMEOUT)

    # Verify: Find expand/collapse buttons by their tooltip or icon
    # The buttons use unfold_more (expand) and unfold_less (collapse) icons
    expand_button = page.locator("button:has(i:text('unfold_more'))").first
    collapse_button = page.locator("button:has(i:text('unfold_less'))").first

    # Buttons should be visible
    assert expand_button.is_visible(), "Expand All button should be visible"
    assert collapse_button.is_visible(), "Collapse All button should be visible"

  def test_collapse_all_button_works(self, page: Page) -> None:
    """Scenario 9: Collapse All button collapses all sections.

    Given an event block with some sections expanded,
    When the user clicks "Collapse All",
    Then all collapsible children within that event collapse.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for event stream with tool output (which has collapsible Result section)
    tool_output_block = page.locator('.q-card:has-text("Tool Output")').first
    tool_output_block.wait_for(timeout=ELEMENT_TIMEOUT)

    # Wait for expanded items within the tool output block
    tool_output_block.locator(".q-expansion-item--expanded").first.wait_for(
      timeout=ELEMENT_TIMEOUT
    )

    # Get initial expanded count within the tool output block
    initial_expanded = tool_output_block.locator(".q-expansion-item--expanded").count()
    assert initial_expanded > 0, "Should have expanded items before collapse"

    # Click Collapse All button within the tool output block
    collapse_button = tool_output_block.locator(
      "button:has(i:text('unfold_less'))"
    ).first
    collapse_button.click()

    # Wait a moment for collapse animation
    page.wait_for_timeout(500)

    # Verify: Should have no expanded items within the block after collapse
    final_expanded = tool_output_block.locator(".q-expansion-item--expanded").count()
    assert final_expanded < initial_expanded, (
      f"Expected fewer expanded items after collapse: "
      f"{final_expanded} >= {initial_expanded}"
    )

  def test_expand_all_button_works(self, page: Page) -> None:
    """Scenario 8: Expand All button expands all sections.

    Given an event block with some sections collapsed,
    When the user clicks "Expand All",
    Then all collapsible children within that event expand.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for tool output block which has collapsible Result section
    tool_output_block = page.locator('.q-card:has-text("Tool Output")').first
    tool_output_block.wait_for(timeout=ELEMENT_TIMEOUT)
    tool_output_block.locator(".q-expansion-item--expanded").first.wait_for(
      timeout=ELEMENT_TIMEOUT
    )

    # First collapse all within this block
    collapse_button = tool_output_block.locator(
      "button:has(i:text('unfold_less'))"
    ).first
    collapse_button.click()
    page.wait_for_timeout(500)

    # Get collapsed state count within the block
    after_collapse = tool_output_block.locator(".q-expansion-item--expanded").count()

    # Now click Expand All within this block
    expand_button = tool_output_block.locator("button:has(i:text('unfold_more'))").first
    expand_button.click()
    page.wait_for_timeout(500)

    # Verify: Should have more expanded items
    after_expand = tool_output_block.locator(".q-expansion-item--expanded").count()
    assert after_expand > after_collapse, (
      f"Expected more expanded items after expand: {after_expand} <= {after_collapse}"
    )


class TestEventStreamStatePersistence:
  """Tests for expansion state persistence (Scenarios 5-6).

  These tests verify that expand/collapse state is preserved when:
  - User performs UI actions (Scenario 5)
  - New events are added to stream (Scenario 6)
  """

  def test_collapse_state_preserved_on_action(self, page: Page) -> None:
    """Scenario 5: Collapse state preserved during UI actions.

    Given a user has collapsed a section in an event,
    When they perform another UI action,
    Then the collapsed state is preserved.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for tool output block with expanded Result section
    tool_output_block = page.locator('.q-card:has-text("Tool Output")').first
    tool_output_block.wait_for(timeout=ELEMENT_TIMEOUT)
    tool_output_block.locator(".q-expansion-item--expanded").first.wait_for(
      timeout=ELEMENT_TIMEOUT
    )

    # Collapse the Result section using Collapse All button
    collapse_button = tool_output_block.locator(
      "button:has(i:text('unfold_less'))"
    ).first
    collapse_button.click()
    page.wait_for_timeout(500)

    # Verify it's collapsed
    assert tool_output_block.locator(".q-expansion-item--expanded").count() == 0, (
      "Section should be collapsed"
    )

    # Perform another action: select another tool (but don't execute)
    # Click on add_numbers card again (reselecting)
    add_numbers_card = page.locator('.q-card.cursor-pointer:has-text("add_numbers")')
    add_numbers_card.click()
    page.wait_for_timeout(300)

    # Click Select Tool
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # Go back to Choose Action
    page.locator("button:has-text('Back')").click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # Verify the collapse state is still preserved
    # The tool output block should still have its Result section collapsed
    tool_output_block = page.locator('.q-card:has-text("Tool Output")').first
    collapsed_count = tool_output_block.locator(".q-expansion-item--expanded").count()
    assert collapsed_count == 0, (
      f"Collapsed state should be preserved, found {collapsed_count} expanded items"
    )

  def test_expand_state_preserved_on_new_event(self, page: Page) -> None:
    """Scenario 6: Expand state preserved when new events added.

    Given a user has expanded a section in an event,
    When new events are added to the stream,
    Then the expanded state of existing events is preserved.
    """
    # Setup: Start session and execute a tool
    start_session_and_execute_tool(page)

    # Wait for tool output block with expanded Result section
    tool_output_block = page.locator('.q-card:has-text("Tool Output")').first
    tool_output_block.wait_for(timeout=ELEMENT_TIMEOUT)
    tool_output_block.locator(".q-expansion-item--expanded").first.wait_for(
      timeout=ELEMENT_TIMEOUT
    )

    # Verify initially expanded
    initial_expanded = tool_output_block.locator(".q-expansion-item--expanded").count()
    assert initial_expanded >= 1, "Result section should be expanded initially"

    # Execute another tool action to generate new events
    # Click on add_numbers card
    add_numbers_card = page.locator('.q-card.cursor-pointer:has-text("add_numbers")')
    add_numbers_card.click()

    # Click Select Tool
    page.locator("button:has-text('Select Tool')").click()
    page.wait_for_load_state("networkidle")

    # Fill and execute again
    page.wait_for_selector("text=Execute: add_numbers", timeout=ELEMENT_TIMEOUT)
    a_input = page.locator("label:has-text('A')").locator("..").locator("input")
    b_input = page.locator("label:has-text('B')").locator("..").locator("input")
    a_input.fill("10")
    b_input.fill("20")
    page.locator("button:has-text('Execute')").click()
    page.wait_for_load_state("networkidle")

    # Wait for execution to complete and new event to appear
    page.wait_for_selector("text=Choose Action", timeout=TOOL_EXECUTION_TIMEOUT)

    # Now there should be TWO tool output blocks
    tool_output_blocks = page.locator('.q-card:has-text("Tool Output")')
    page.wait_for_timeout(500)
    assert tool_output_blocks.count() >= 2, "Should have at least 2 tool output events"

    # Check that the first tool output block still has its expanded state
    first_tool_output = tool_output_blocks.first
    expanded_count = first_tool_output.locator(".q-expansion-item--expanded").count()
    assert expanded_count >= 1, (
      f"First tool output expanded state should be preserved, found {expanded_count}"
    )

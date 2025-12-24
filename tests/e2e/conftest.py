"""E2E test fixtures for Playwright-based browser testing.

This module provides pytest fixtures for running E2E tests against the
ADK Agent Simulator using Playwright for browser automation.
"""

from __future__ import annotations

import os
import socket
import threading
import time
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
  from playwright.sync_api import Page

# =============================================================================
# Constants
# =============================================================================

TEST_SERVER_PORT = 8081
TEST_BASE_URL = f"http://127.0.0.1:{TEST_SERVER_PORT}"

# Screenshot directory (relative to repo root)
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "docs" / "screenshots"

# Screenshot viewport dimensions
SCREENSHOT_WIDTH = 1280
SCREENSHOT_HEIGHT = 720

# Timeout constants (in seconds)
SERVER_STARTUP_TIMEOUT = 10
ELEMENT_TIMEOUT = 10000  # Playwright uses milliseconds
TOOL_EXECUTION_TIMEOUT = 30000  # Playwright uses milliseconds


# =============================================================================
# Helper Functions
# =============================================================================


def _wait_for_port(port: int, timeout: float = SERVER_STARTUP_TIMEOUT) -> bool:
  """Wait for a port to become available.

  Args:
    port: The port number to check.
    timeout: Maximum time to wait in seconds.

  Returns:
    True if the port is accepting connections, False if timeout reached.
  """
  start_time = time.time()
  while time.time() - start_time < timeout:
    try:
      with socket.create_connection(("127.0.0.1", port), timeout=1):
        return True
    except OSError:
      time.sleep(0.1)
  return False


def _run_server() -> None:
  """Run the NiceGUI server in the current thread.

  This function is designed to be run in a daemon thread. It imports
  the test agent and starts the simulator server directly using NiceGUI.
  """
  # Import here to avoid circular imports and ensure fresh state
  from nicegui import ui

  from adk_agent_sim.simulator import AgentSimulator
  from tests.fixtures.agents.test_agent.agent import get_test_agent

  agent = get_test_agent()
  _simulator = AgentSimulator(  # noqa: F841 - Side effect: registers routes
    agents={"TestAgent": agent},
    host="127.0.0.1",
    port=TEST_SERVER_PORT,
  )

  # Create the app pages but don't start yet
  # The simulator's _app has already set up the routes

  # Run NiceGUI directly with server-mode settings
  ui.run(  # pyright: ignore[reportUnknownMemberType]
    host="127.0.0.1",
    port=TEST_SERVER_PORT,
    title="E2E Test Simulator",
    reload=False,
    show=False,  # Don't open browser
    native=False,  # Don't use native mode
  )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def run_server() -> Generator[str, None, None]:
  """Start the NiceGUI server in a background thread.

  This session-scoped fixture starts the server once for all E2E tests
  and yields the base URL. The daemon thread automatically terminates
  when pytest exits.

  Yields:
    The base URL of the running server.
  """
  # Set environment variables
  os.environ["ADK_AGENT_MODULE"] = "tests.fixtures.agents.test_agent"
  # NiceGUI requires this when running under pytest
  os.environ["NICEGUI_SCREEN_TEST_PORT"] = str(TEST_SERVER_PORT)

  # Start server in daemon thread
  server_thread = threading.Thread(target=_run_server, daemon=True)
  server_thread.start()

  # Wait for server to be ready
  if not _wait_for_port(TEST_SERVER_PORT, SERVER_STARTUP_TIMEOUT):
    pytest.fail(
      f"Server failed to start on port {TEST_SERVER_PORT} "
      f"within {SERVER_STARTUP_TIMEOUT} seconds"
    )

  yield TEST_BASE_URL

  # Daemon thread auto-terminates when pytest exits


@pytest.fixture(scope="session")
def base_url(run_server: str) -> str:
  """Get the base URL of the running test server.

  This fixture has session scope to match pytest-base-url expectations.

  Args:
    run_server: The session-scoped server fixture.

  Returns:
    The base URL string.
  """
  return run_server


@pytest.fixture(scope="function")
def test_page(page: Page, base_url: str) -> Page:
  """Navigate to the base URL and return a fresh page.

  This fixture uses the pytest-playwright provided page fixture,
  navigates to the test server, and waits for the page to be ready.

  Args:
    page: The Playwright page fixture.
    base_url: The base URL of the test server.

  Returns:
    The Playwright page object ready for testing.
  """
  page.set_default_timeout(ELEMENT_TIMEOUT)
  page.goto(base_url)
  # Wait for NiceGUI to initialize
  page.wait_for_load_state("networkidle")
  return page


# Override the pytest-playwright page fixture to auto-navigate
@pytest.fixture(scope="function")
def page(page: Page, base_url: str) -> Page:  # type: ignore[misc]  # noqa: F811
  """Override default page fixture to navigate to base_url.

  This ensures all tests start at the correct URL without
  needing to manually navigate.

  Args:
    page: The Playwright page fixture.
    base_url: The base URL of the test server.

  Returns:
    The Playwright page object at base_url.
  """
  page.set_default_timeout(ELEMENT_TIMEOUT)
  page.goto(base_url)
  page.wait_for_load_state("networkidle")
  return page


@pytest.fixture(scope="function")
def capture_screenshot(page: Page) -> Callable[[str], None]:
  """Provide a function to capture screenshots during tests.

  Screenshots are saved to docs/screenshots/ at 1280x720 resolution
  for visual documentation and AI-assisted analysis.

  Args:
    page: The Playwright page fixture.

  Returns:
    A callable that takes a screenshot name (without extension) and
    saves it to the screenshots directory.
  """
  # Set viewport to consistent size for screenshots
  page.set_viewport_size({"width": SCREENSHOT_WIDTH, "height": SCREENSHOT_HEIGHT})

  def _capture(name: str) -> None:
    """Capture a screenshot with the given name.

    Args:
      name: The screenshot filename (without .png extension).
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=screenshot_path)

  return _capture

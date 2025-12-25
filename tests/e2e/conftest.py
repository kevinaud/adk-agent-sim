"""E2E test fixtures for Playwright-based browser testing.

This module provides pytest fixtures for running E2E tests against the
ADK Agent Simulator using Playwright for browser automation.

Supports parallel execution with pytest-xdist:
  uv run pytest tests/e2e/ -n 4  # Run with 4 parallel workers

Each xdist worker gets its own server instance on a unique port.
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

# Base port for test servers (workers use BASE_PORT + worker_id)
BASE_SERVER_PORT = 8081
MAX_WORKERS = 8  # Maximum parallel workers supported

# Screenshot directory (relative to repo root)
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "docs" / "screenshots"

# Screenshot viewport dimensions
SCREENSHOT_WIDTH = 1280
SCREENSHOT_HEIGHT = 720

# Timeout constants (in seconds)
SERVER_STARTUP_TIMEOUT = 15
ELEMENT_TIMEOUT = 10000  # Playwright uses milliseconds
TOOL_EXECUTION_TIMEOUT = 30000  # Playwright uses milliseconds


# =============================================================================
# Helper Functions
# =============================================================================


def _get_worker_id(request: pytest.FixtureRequest) -> int:
  """Get the xdist worker ID, or 0 if not running with xdist.

  Args:
    request: The pytest fixture request object.

  Returns:
    Integer worker ID (0-based), or 0 for non-parallel runs.
  """
  # xdist sets worker_id like "gw0", "gw1", etc.
  worker_id = getattr(request.config, "workerinput", {}).get("workerid", "master")
  if worker_id == "master":
    return 0
  # Extract number from "gwN"
  return int(worker_id.replace("gw", ""))


def _get_server_port(worker_id: int) -> int:
  """Get the server port for a given worker.

  Args:
    worker_id: The xdist worker ID (0-based).

  Returns:
    The port number for this worker's server.
  """
  return BASE_SERVER_PORT + worker_id


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


def _make_server_runner(port: int) -> Callable[[], None]:
  """Create a server runner function for a specific port.

  Args:
    port: The port to run the server on.

  Returns:
    A callable that starts the NiceGUI server on the specified port.
  """

  def _run_server() -> None:
    """Run the NiceGUI server in the current thread."""
    # Import here to avoid circular imports and ensure fresh state
    from nicegui import ui

    from adk_agent_sim.simulator import AgentSimulator
    from tests.fixtures.agents.test_agent.agent import get_test_agent

    agent = get_test_agent()
    _simulator = AgentSimulator(  # noqa: F841 - Side effect: registers routes
      agents={"TestAgent": agent},
      host="127.0.0.1",
      port=port,
    )

    # Run NiceGUI directly with server-mode settings
    ui.run(  # pyright: ignore[reportUnknownMemberType]
      host="127.0.0.1",
      port=port,
      title=f"E2E Test Simulator (port {port})",
      reload=False,
      show=False,  # Don't open browser
      native=False,  # Don't use native mode
    )

  return _run_server


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> int:
  """Get the current xdist worker ID.

  Args:
    request: The pytest fixture request object.

  Returns:
    Integer worker ID (0-based).
  """
  return _get_worker_id(request)


@pytest.fixture(scope="session")
def server_port(worker_id: int) -> int:
  """Get the server port for this worker.

  Args:
    worker_id: The xdist worker ID.

  Returns:
    The port number for this worker's server.
  """
  return _get_server_port(worker_id)


@pytest.fixture(scope="session")
def run_server(server_port: int) -> Generator[str, None, None]:
  """Start the NiceGUI server in a background thread.

  This session-scoped fixture starts a server instance for each xdist
  worker. When running with `-n N`, N separate servers are started
  on ports BASE_SERVER_PORT through BASE_SERVER_PORT + N - 1.

  Yields:
    The base URL of the running server.
  """
  base_url = f"http://127.0.0.1:{server_port}"

  # Set environment variables
  os.environ["ADK_AGENT_MODULE"] = "tests.fixtures.agents.test_agent"
  # NiceGUI requires this when running under pytest
  os.environ["NICEGUI_SCREEN_TEST_PORT"] = str(server_port)

  # Start server in daemon thread
  server_runner = _make_server_runner(server_port)
  server_thread = threading.Thread(target=server_runner, daemon=True)
  server_thread.start()

  # Wait for server to be ready
  if not _wait_for_port(server_port, SERVER_STARTUP_TIMEOUT):
    pytest.fail(
      f"Server failed to start on port {server_port} "
      f"within {SERVER_STARTUP_TIMEOUT} seconds"
    )

  yield base_url

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

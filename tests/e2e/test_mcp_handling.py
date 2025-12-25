"""E2E tests for MCP tool handling in the ADK Agent Simulator.

This module tests scenarios involving MCP (Model Context Protocol) tools,
specifically verifying that the simulator handles MCP server connectivity
issues gracefully rather than crashing with unhandled exceptions.

These tests are run in isolation with subprocess-based server management
to avoid conflicts with NiceGUI's global state.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
  pass

# =============================================================================
# Constants
# =============================================================================

MCP_TEST_SERVER_PORT = 8095  # Different port from regular E2E tests (8081-8088)
MCP_SERVER_PORT = 9001  # Port for the MCP server
MCP_TEST_BASE_URL = f"http://127.0.0.1:{MCP_TEST_SERVER_PORT}"

# Timeout constants
SERVER_STARTUP_TIMEOUT = 15
ELEMENT_TIMEOUT = 15000  # Longer timeout for MCP operations


# =============================================================================
# Helper Functions
# =============================================================================


def _wait_for_port(port: int, timeout: float = SERVER_STARTUP_TIMEOUT) -> bool:
  """Wait for a port to become available."""
  start_time = time.time()
  while time.time() - start_time < timeout:
    try:
      with socket.create_connection(("127.0.0.1", port), timeout=1):
        return True
    except OSError:
      time.sleep(0.1)
  return False


def _is_port_in_use(port: int) -> bool:
  """Check if a port is currently in use."""
  try:
    with socket.create_connection(("127.0.0.1", port), timeout=0.5):
      return True
  except OSError:
    return False


# =============================================================================
# Tests: MCP Server Unavailable (TC-05)
# =============================================================================


class TestMCPServerUnavailable:
  """Test handling when MCP server is not running.

  TC-05: Verify that the simulator handles MCP connection failures gracefully
  rather than crashing with unhandled exceptions.
  """

  @pytest.mark.skipif(
    _is_port_in_use(MCP_TEST_SERVER_PORT),
    reason=f"Port {MCP_TEST_SERVER_PORT} already in use",
  )
  def test_start_simulation_shows_error_not_crash(self) -> None:
    """Verify that starting simulation with unavailable MCP server shows error.

    When the MCP server is not running, clicking "Start Simulation" should:
    1. NOT crash the application with unhandled exceptions
    2. Display a user-friendly error message
    3. Allow the user to retry or select a different agent

    This test captures the bug where MCP connection failures caused
    RuntimeError exceptions that were not properly caught.

    Note: This test runs Playwright in a subprocess to avoid conflicts with
    pytest-xdist's event loop.
    """
    # Start the simulator in a subprocess with MCP agent
    # This avoids NiceGUI global state issues
    server_script = f"""
import sys
sys.path.insert(0, '/workspaces/adk-agent-sim')

from nicegui import ui
from adk_agent_sim.simulator import AgentSimulator
from tests.fixtures.agents.mcp_agent.agent import get_mcp_agent

agent = get_mcp_agent()
simulator = AgentSimulator(
    agents={{"MCPAgent": agent}},
    host="127.0.0.1",
    port={MCP_TEST_SERVER_PORT},
)

ui.run(
    host="127.0.0.1",
    port={MCP_TEST_SERVER_PORT},
    title="MCP E2E Test Simulator",
    reload=False,
    show=False,
    native=False,
)
"""
    # Start server subprocess
    env = os.environ.copy()
    env["NICEGUI_SCREEN_TEST_PORT"] = str(MCP_TEST_SERVER_PORT)

    server_proc = subprocess.Popen(
      [sys.executable, "-c", server_script],
      env=env,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    )

    try:
      # Wait for server to start
      if not _wait_for_port(MCP_TEST_SERVER_PORT, SERVER_STARTUP_TIMEOUT):
        stdout, stderr = server_proc.communicate(timeout=5)
        pytest.fail(
          f"Simulator failed to start on port {MCP_TEST_SERVER_PORT}. "
          f"stdout: {stdout.decode()}, stderr: {stderr.decode()}"
        )

      # Run Playwright test in a subprocess to avoid event loop conflicts
      # with pytest-xdist
      test_script = f"""
import sys
sys.path.insert(0, '/workspaces/adk-agent-sim')

from playwright.sync_api import sync_playwright

MCP_TEST_BASE_URL = "{MCP_TEST_BASE_URL}"
ELEMENT_TIMEOUT = {ELEMENT_TIMEOUT}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_default_timeout(ELEMENT_TIMEOUT)

    # Navigate to the simulator
    page.goto(MCP_TEST_BASE_URL)
    page.wait_for_load_state("networkidle")

    # Verify we're on the agent selection page
    page.wait_for_selector("text=ADK Agent Simulator")
    page.wait_for_selector("text=MCPAgent")

    # Click the MCPAgent card to start (new card-based UI)
    page.click(".q-card:has-text('MCPAgent')")

    # Give the async operation time to complete or fail
    page.wait_for_timeout(8000)

    # Get page content for debugging
    page_content = page.content()

    # Check if simulation page loaded successfully
    simulation_header = page.query_selector("text=Simulating:")

    # Check for NiceGUI notification (Quasar component)
    notification = page.query_selector(".q-notification")

    result = "pass"
    error_msg = ""

    if notification:
        # Found a notification - test passes (error is shown)
        pass
    elif simulation_header:
        # Simulation page loaded - check for visible error in UI
        page.wait_for_timeout(2000)

        error_notification = page.query_selector(".q-notification")
        error_text = page.query_selector("text=error")
        failed_text = page.query_selector("text=failed")
        connection_text = page.query_selector("text=connection")

        has_visible_error = any([
            error_notification,
            error_text,
            failed_text,
            connection_text,
        ])

        if not has_visible_error:
            result = "fail"
            error_msg = (
                "Simulation page loaded but no error shown for unavailable "
                "MCP server. When MCP tools cannot connect, a user-friendly "
                "error message should be displayed."
            )
    else:
        # Simulation page didn't load - check for error indicators
        error_notification = page.query_selector(".q-notification")
        has_error_text = (
            "error" in page_content.lower()
            or "failed" in page_content.lower()
            or "connection" in page_content.lower()
        )

        if not error_notification and not has_error_text:
            result = "fail"
            error_msg = (
                "Application appears to have crashed or hung when MCP server "
                f"unavailable. Page content sample: {{page_content[:500]}}"
            )

    browser.close()

    if result == "fail":
        print(f"TEST_FAILED: {{error_msg}}")
        sys.exit(1)
    else:
        print("TEST_PASSED")
        sys.exit(0)
"""
      test_proc = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=60,
      )

      if test_proc.returncode != 0:
        error_output = test_proc.stdout + test_proc.stderr
        if "TEST_FAILED:" in error_output:
          # Extract the error message
          for line in error_output.split("\n"):
            if "TEST_FAILED:" in line:
              pytest.fail(line.replace("TEST_FAILED:", "").strip())
        else:
          pytest.fail(f"Playwright subprocess failed: {error_output}")

    finally:
      # Clean up server subprocess
      server_proc.terminate()
      try:
        server_proc.wait(timeout=5)
      except subprocess.TimeoutExpired:
        server_proc.kill()
        server_proc.wait()

# Quickstart: E2E Test Suite

**Feature**: 002-e2e-test-suite  
**Date**: 2024-12-23 (Updated: 2025-12-23)

## Prerequisites

The Dev Container automatically installs all dependencies via `postCreateCommand`. If you're running outside the container, ensure:
- Python 3.14+
- uv package manager
- Playwright browsers installed (`uv run playwright install --with-deps`)

## Running E2E Tests

### Full Suite

```bash
uv run pytest tests/e2e/ -v
```

### Specific Test Cases

```bash
# TC-01: Happy Path (complete simulation flow)
uv run pytest tests/e2e/test_simulation.py::TestHappyPath -v

# TC-02: Dynamic Forms (widget rendering)
uv run pytest tests/e2e/test_simulation.py::TestWidgetRendering -v

# TC-03: Error Handling
uv run pytest tests/e2e/test_simulation.py::TestErrorHandling -v

# TC-04: State Isolation
uv run pytest tests/e2e/test_simulation.py::TestStateIsolation -v

# TC-05: Screenshot Capture (visual documentation)
uv run pytest tests/e2e/test_simulation.py::TestScreenshotCapture -v
```

### With Headed Browser (Debugging)

```bash
uv run pytest tests/e2e/ -v --headed
```

> **Note**: Headed mode requires a display. In the Dev Container, this won't work unless you configure X11 forwarding.

### With Trace on Failure

```bash
uv run pytest tests/e2e/ -v --tracing=retain-on-failure
```

Traces are saved to `test-results/` and can be viewed with:

```bash
uv run playwright show-trace test-results/<test-name>/trace.zip
```

## Test Structure

```
tests/
├── e2e/
│   ├── __init__.py
│   ├── conftest.py          # E2E fixtures (server, browser, page)
│   └── test_simulation.py   # TC-01 through TC-04
└── fixtures/
    └── agents/
        └── test_agent/
            ├── __init__.py
            └── agent.py     # TestAgent with local FunctionTools
```

**Note**: The `test_agent` uses only local `FunctionTool` definitions—no MCP server is required. This simplifies test setup and reduces flakiness.

## Expected Output

```
tests/e2e/test_simulation.py::TestHappyPath::test_agent_selection[chromium] PASSED
tests/e2e/test_simulation.py::TestHappyPath::test_query_submission[chromium] PASSED
tests/e2e/test_simulation.py::TestHappyPath::test_tool_selection[chromium] PASSED
tests/e2e/test_simulation.py::TestHappyPath::test_tool_execution[chromium] PASSED
tests/e2e/test_simulation.py::TestHappyPath::test_final_response_and_session_completion[chromium] PASSED
tests/e2e/test_simulation.py::TestWidgetRendering::test_widget_number_input[chromium] PASSED
tests/e2e/test_simulation.py::TestWidgetRendering::test_widget_string_input[chromium] PASSED
tests/e2e/test_simulation.py::TestWidgetRendering::test_widget_checkbox[chromium] PASSED
tests/e2e/test_simulation.py::TestWidgetRendering::test_widget_dropdown[chromium] PASSED
tests/e2e/test_simulation.py::TestErrorHandling::test_error_display[chromium] PASSED
tests/e2e/test_simulation.py::TestErrorHandling::test_session_continues_after_error[chromium] PASSED
tests/e2e/test_simulation.py::TestErrorHandling::test_error_preserved_in_history[chromium] PASSED
tests/e2e/test_simulation.py::TestStateIsolation::test_state_clears_on_reload[chromium] PASSED
tests/e2e/test_simulation.py::TestStateIsolation::test_fresh_session_no_artifacts[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_agent_selection[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_query_input[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_tool_selection[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_tool_form[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_tool_result[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_error_display[chromium] PASSED
tests/e2e/test_simulation.py::TestScreenshotCapture::test_capture_session_complete[chromium] PASSED

========================= 21 passed in XX.XXs =========================
```

## Screenshot Verification

After running the screenshot tests, verify all 7 screenshots exist in `docs/screenshots/`:

```bash
ls -la docs/screenshots/
```

Expected output:

```
agent-selection.png
error-display.png
query-input.png
session-complete.png
tool-form.png
tool-result.png
tool-selection.png
```

These screenshots are:
- **Committed to version control** for PR reviews
- **1280x720 resolution** for consistent viewport
- **Used for AI-assisted UX analysis**

## Troubleshooting

### "Browser executable not found"

Run Playwright install:

```bash
uv run playwright install --with-deps
```

### Tests timeout waiting for elements

1. Check that port 8081 is available
2. Increase timeout if running on slow hardware:

```bash
uv run pytest tests/e2e/ -v --timeout=60
```

**Note**: The test agent uses only local `FunctionTool` definitions—no MCP server is required.

### "Address already in use" (port 8081)

Another process is using the test port. Find and kill it:

```bash
lsof -i :8081
kill <PID>
```

## CI/CD Integration

The tests are designed to run in CI without modification:

```yaml
# Example GitHub Actions step
- name: Run E2E Tests
  run: |
    uv sync
    uv run playwright install --with-deps
    uv run pytest tests/e2e/ -v
```

The `--with-deps` flag ensures system libraries are installed in CI containers.

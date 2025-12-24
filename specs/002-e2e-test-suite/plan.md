# Implementation Plan: E2E Test Suite

**Branch**: `002-e2e-test-suite` | **Date**: 2025-12-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-e2e-test-suite/spec.md`

## Summary

Implement an E2E test suite using Playwright via pytest to validate the "Simulator Run" feature. The test suite will:
- Launch the NiceGUI application in a background thread with server-mode configuration
- Use a dedicated `test_agent` with local `FunctionTool` definitions covering all required schema types
- Verify complete simulation flows, dynamic form rendering, error handling, and state isolation
- Capture screenshots of all major UX views for visual documentation and AI-assisted analysis
- Run headlessly within the Dev Container environment with zero manual intervention

## Technical Context

**Language/Version**: Python 3.14+  
**Primary Dependencies**: pytest, pytest-playwright, playwright, nicegui  
**Storage**: N/A (ephemeral session state only)  
**Testing**: pytest with pytest-playwright plugin  
**Target Platform**: Dev Container (Debian Linux headless)
**Project Type**: single (Python library with test suite)  
**Performance Goals**: Full test suite completes within 5 minutes  
**Constraints**: Must run headlessly, no desktop window spawning, single-threaded to avoid port conflicts  
**Scale/Scope**: 5 test cases (TC-01 through TC-05) covering P1-P3 user stories plus screenshot capture
**Screenshot Output**: `docs/screenshots/` directory with 7 PNG files at 1280x720 resolution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Library-First Architecture | ✅ PASS | Test suite is part of dev dependencies, not shipped with library |
| II. Wrapper Integration Pattern | ✅ PASS | `test_agent` follows same pattern as `demo_agent` |
| III. Wizard of Oz Interaction Model | ✅ PASS | Tests validate the human-in-the-loop UI behavior |
| IV. ADK Dependency & Abstractions | ✅ PASS | `test_agent` uses `FunctionTool` from ADK |
| V. Golden Trace Output | N/A | Not testing trace export in this suite |
| VI. Hermetic Development Environment | ✅ PASS | Playwright deps installed via devcontainer config |
| VII. Strict Development Standards | ✅ PASS | Using `uv`, `ruff`, `pyright`, `pytest` |
| VIII. Flexible UI Strategy | ✅ PASS | Testing existing NiceGUI implementation |

**Gate Result**: ✅ All gates pass. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/002-e2e-test-suite/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
.devcontainer/
├── devcontainer.json    # MODIFY: Add playwright install to postCreateCommand
└── setup-env.sh         # Existing setup script

docs/
└── screenshots/         # NEW: UX screenshot directory (committed to repo)
    ├── agent-selection.png
    ├── query-input.png
    ├── tool-selection.png
    ├── tool-form.png
    ├── tool-result.png
    ├── error-display.png
    └── session-complete.png

tests/
├── conftest.py          # (existing - no changes needed)
├── e2e/                 # NEW: E2E test directory
│   ├── __init__.py
│   ├── conftest.py      # E2E-specific fixtures (server, browser, page, screenshot helper)
│   └── test_simulation.py  # All 5 test cases including screenshot capture
└── fixtures/
    └── agents/          # NEW: Test agent directory
        └── test_agent/
            ├── __init__.py
            └── agent.py # test_agent with local FunctionTools
```

**Structure Decision**: Single project structure. E2E tests placed in `tests/e2e/` alongside existing `tests/unit/` and `tests/integration/`. Test agent isolated in `tests/fixtures/agents/` per clarification decisions. Screenshots stored in `docs/screenshots/` and committed to version control for AI-assisted visual analysis.

## Complexity Tracking

> No violations to justify. Implementation follows standard pytest conventions.

## Screenshot Capture Strategy

### Purpose

Screenshots serve three primary purposes:
1. **Visual Documentation**: Provide a visual record of the UI for documentation
2. **Change Detection**: Enable review of UI changes during PRs
3. **AI-Assisted Analysis**: Allow AI assistants (like GitHub Copilot) to analyze visual UX quality

### Implementation Approach

Screenshots will be captured during the E2E test execution using Playwright's built-in screenshot API:

```python
# Example fixture for screenshot capture
@pytest.fixture
def capture_screenshot(page: Page) -> Callable[[str], None]:
    def _capture(name: str) -> None:
        screenshot_dir = Path("docs/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=screenshot_dir / f"{name}.png")
    return _capture
```

### Screenshot Manifest

| View | Filename | Captured During | Description |
|------|----------|-----------------|-------------|
| Agent Selection | `agent-selection.png` | TC-01 Step 1 | Initial page showing agent dropdown and start button |
| Query Input | `query-input.png` | TC-01 Step 2 | Simulation page with query input form |
| Tool Selection | `tool-selection.png` | TC-01 Step 3 | Action panel showing available tools |
| Tool Form | `tool-form.png` | TC-01 Step 4 | Dynamic form for selected tool parameters |
| Tool Result | `tool-result.png` | TC-01 Step 5 | History panel showing tool execution result |
| Error Display | `error-display.png` | TC-03 | Error card styling for failed tool execution |
| Session Complete | `session-complete.png` | TC-01 Step 6 | Final response and completed session state |

### Viewport Configuration

All screenshots captured at 1280x720 pixels:
- Width: 1280px (standard laptop/desktop width)
- Height: 720px (ensures full page visibility without scroll)
- Format: PNG (lossless quality for text readability)

### Git Integration

Screenshots are committed to version control:
- Directory: `docs/screenshots/`
- NOT added to `.gitignore`
- Updated automatically on successful test runs
- Changes visible in PR diffs for visual review

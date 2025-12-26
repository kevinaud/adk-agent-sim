# adk-agent-sim Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-23

## Active Technologies
- Python 3.14+ + pytest, pytest-playwright, playwright (002-e2e-test-suite)
- N/A (ephemeral test sessions) (002-e2e-test-suite)
- Python 3.14+ + pytest, pytest-playwright, playwright, nicegui (002-e2e-test-suite)
- N/A (ephemeral session state only) (002-e2e-test-suite)
- Python 3.14+ + NiceGUI 2.0+ (includes Quasar/Vue, Tailwind CSS) (003-ux-modernization)
- N/A (in-memory session only) (003-ux-modernization)
- Python 3.14+ + `nicegui` (UI), Tailwind CSS (styling) (003-ux-modernization)
- N/A (ephemeral in-memory sessions only) (003-ux-modernization)
- Python 3.14+ + NiceGUI (web UI framework) (004-devtools-event-renderer)
- N/A (session-only in-memory state) (004-devtools-event-renderer)

- Python 3.14+ + `nicegui` (UI), `google-adk` (Agent framework), `pydantic` (data models) (001-simulator-run-spec)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.14+: Follow standard conventions

## Recent Changes
- 004-devtools-event-renderer: Added Python 3.14+ + NiceGUI (web UI framework)
- 004-devtools-event-renderer: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 003-ux-modernization-fixes: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.0.0 → 1.1.0 (Dev Container Emphasis)

Added Sections:
- Principle VI: Hermetic Development Environment

Modified Sections:
- Principle VII (Renumbered from VI): Removed environment bullet
- Principle VIII (Renumbered from VII): Updated reference to Principles I–VII

Templates Requiring Updates:
- .specify/templates/plan-template.md: ✅ Compatible
- .specify/templates/spec-template.md: ✅ Compatible
- .specify/templates/tasks-template.md: ✅ Compatible

Follow-up TODOs: None
================================================================================
-->

# adk_agent_sim Constitution

## Core Principles

### I. Library-First Architecture

This project is a Python **library/developer tool**, NOT a standalone SaaS or application.

- All code MUST be installable via `pip` or `uv` into an existing Python project.
- The library MUST be importable as a standard Python package (`import adk_agent_sim`).
- No implicit global state or singleton patterns that prevent multiple instantiations.
- Distribution as a PyPI-compatible package is the primary delivery mechanism.

**Rationale**: Developers integrate this tool into their own ADK-based projects; forcing a standalone app model would prevent the intended usage pattern.

### II. Wrapper Integration Pattern

The tool is designed to **wrap existing Google ADK Agent objects** provided by the user.

- The primary entry point MUST be an `AgentSimulator` class (or equivalent) that accepts a dictionary of initialized `Agent` instances.
- Example invocation pattern: `AgentSimulator(agents={"MyAgent": agent_instance}).run()`.
- The library MUST NOT require users to define agents in a proprietary format; it wraps their existing ADK agents.
- Configuration beyond the agent dictionary (e.g., port, output paths) SHOULD be optional kwargs with sensible defaults.

**Rationale**: The integration pattern minimizes friction for existing ADK users—they provide their agents, we provide the simulation interface.

### III. Wizard of Oz Interaction Model

The core functionality provides a GUI allowing a human developer to "roleplay" as the Agent.

- The human MUST see the full context available to the agent (conversation history, system prompt, available tools).
- The human MUST be able to inspect each tool's schema (name, description, parameters).
- The interface MUST allow the human to either:
  - (a) **Invoke a tool**: Select a tool, provide exact input parameters, and execute it.
  - (b) **Send a final response**: Compose and return text as the agent's output.
- Tool invocations MUST execute against the real tool implementations provided by the agent.
- The system MUST NOT auto-select tools or auto-fill parameters—human decision-making is the point.

**Rationale**: The "Wizard of Oz" methodology enables capturing expert human reasoning for agent tasks, producing high-quality training/evaluation data.

### IV. ADK Dependency & Abstractions

The system MUST rely on Google Agent Development Kit (ADK) internal abstractions for tool discovery and execution.

- Tool schemas MUST be derived from ADK's `canonical_tools()` and `FunctionDeclaration` APIs.
- Tool execution MUST use ADK's `run_async()` or equivalent execution pathways.
- The library MUST NOT reinvent schema parsing, parameter validation, or tool invocation logic that ADK already provides.
- ADK version compatibility MUST be documented; breaking ADK updates require a MINOR or MAJOR version bump.

**Rationale**: Leveraging ADK internals ensures compatibility with the broader ADK ecosystem and reduces maintenance burden.

### V. Golden Trace Output

The primary artifact produced by a simulation session is a **Golden Trace** (JSON).

- Each session MUST produce a structured JSON file representing the human's successful resolution of a task.
- The trace format MUST be compatible with ADK evaluation tools (schema to be defined during specification).
- Traces MUST capture: conversation history, tool invocations (with inputs/outputs), final response, and timing metadata.
- Incomplete or errored sessions MAY produce partial traces marked as invalid.

**Rationale**: Golden Traces enable training data generation and evaluation benchmarking, which is the tool's primary value proposition.

### VI. Hermetic Development Environment

The development environment MUST be fully defined and reproducible via Dev Containers.

- **Single Source of Truth**: The `.devcontainer/` configuration is the sole definition of the development environment.
- **No Manual Setup**: Any tool, library, or system dependency required to develop, build, test, or run the project MUST be installed automatically by the dev container.
- **Documentation Ban**: It is FORBIDDEN to document manual setup steps (e.g., "brew install x", "apt-get install y") in READMEs. If it's needed, it goes in the Dockerfile or `devcontainer.json`.
- **Universal Execution**: All development tasks (tests, linting, running the app) MUST be executable within the container without accessing host resources.

**Rationale**: Ensures that every developer works in an identical environment, eliminating "works on my machine" issues and simplifying onboarding.

### VII. Strict Development Standards

All code MUST adhere to the following non-negotiable standards:

- **Language**: Python 3.14+ (use modern syntax and type features).
- **Package Manager**: `uv` MUST be used for all dependency management. No `pip`, `poetry`, or `conda`.
- **Formatting**: `ruff` MUST be used for linting and formatting.
  - **2-space indentation** is REQUIRED (non-standard Python; enforced via ruff config).
  - Code that fails `ruff check` or `ruff format --check` MUST NOT be committed.
- **Type Safety**: `pyright` in **strict mode** is REQUIRED.
  - All code MUST pass `pyright` checks with zero errors.
  - Surgical suppression (`# pyright: ignore[...]`) is permitted ONLY for external dependencies lacking type stubs, with a comment explaining why.

**Rationale**: Strict tooling catches bugs early and ensures consistent code style across contributors.

### VIII. Flexible UI Strategy

The interface must allow users to control Python agent instances provided via the entry script.

- The UI architecture is intentionally NOT locked to a specific framework in this constitution.
- Acceptable architectures include (but are not limited to):
  - Python-generated web UI (e.g., Gradio, Streamlit, FastAPI + templates).
  - Standalone SPA communicating with a Python backend (e.g., React + FastAPI).
  - Native desktop application (e.g., Electron, Tauri, PyQt).
- The best approach MUST be determined during the **Specification** and **Planning** phases based on UX requirements.
- Any chosen architecture MUST NOT violate Principles I–VII.

**Rationale**: Premature commitment to a UI framework limits exploration; the optimal choice depends on detailed UX research.

## Technology Stack

| Category | Requirement |
|----------|-------------|
| Language | Python 3.14+ |
| Package Manager | `uv` (mandatory) |
| Linting/Formatting | `ruff` (2-space indent) |
| Type Checking | `pyright` strict mode |
| Testing | `pytest` |
| Dev Environment | Dev Containers |
| Core Dependency | Google ADK |

## Quality Gates

All code changes MUST pass these gates before merge:

1. **Formatting**: `ruff format --check` passes.
2. **Linting**: `ruff check` passes with zero errors.
3. **Type Checking**: `pyright` in strict mode passes with zero errors.
4. **Tests**: `pytest` passes with no failures.
5. **Dev Container**: Changes must not break the dev container build.

## Governance

This Constitution is the supreme authority for project decisions. All specifications, plans, and code MUST comply.

- **Amendment P1ocess**: Any principle change requires:
  1. Written proposal with rationale.
  2. Impact assessment on existing code.
  3. Version bump following semantic versioning:
     - MAJOR: Principle removal or backward-incompatible redefinition.
     - MINOR: New principle added or material expansion.
     - PATCH: Clarifications, typo fixes, non-semantic changes.
- **Compliance Review**: All PRs MUST verify adherence to Constitution principles.
- **Complexity Justification**: Any deviation from "simplest solution" MUST be documented with rationale.

**Version**: 1.0.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-23

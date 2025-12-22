# ADK Agent Simulator Constitution

## Core Principles

### I. Library-First Design
The ADK Agent Simulator is a **library**, not a standalone application. It follows the **Wrapper Pattern** where:
- Users provide the environment (their ADK agents, API keys, database connections)
- The library provides the UI and simulation capabilities
- All features must be importable and usable programmatically before any CLI/UI exposure

### II. ADK Native Integration
All agent introspection and tool execution MUST use Google ADK's internal abstractions:
- **Discovery**: Use `agent.canonical_tools()` for tool retrieval
- **Schema**: Use `tool._get_declaration()` for Gemini Function Declarations
- **Execution**: Use `tool.run_async()` for all tool execution (abstracts FunctionTool vs McpTool)
- **No custom reflection**: Never parse Python code directly when ADK provides the abstraction

### III. Streamlit UI Standards
The UI layer uses Streamlit exclusively:
- Dynamic form generation from JSON Schema (FunctionDeclaration)
- Consistent widget mapping: STRING→text_input, INTEGER/NUMBER→number_input, BOOLEAN→checkbox, ENUM→selectbox, Complex→text_area(JSON)
- Session state for conversation history and trace recording
- Clear separation between UI components and business logic

### IV. Test-First Development (NON-NEGOTIABLE)
- TDD mandatory: Tests written → Tests fail → Implement → Tests pass
- Unit tests for schema-to-widget mapping logic
- Integration tests for ADK tool execution
- Mock ADK agents/tools for isolated testing
- All async code must have proper test coverage

### V. Golden Trace Compliance
All session recordings must produce ADK-evaluation-compatible JSON:
- Metadata: agent_name, timestamp, user_query
- Trace array: step_index, type (tool_call|final_answer), tool_name, arguments, output
- Schema must remain stable for downstream evaluation tools

## Technology Constraints

### Required Stack
- **Python 3.14+**: Primary language
- **Streamlit**: UI framework (no alternatives)
- **Google ADK**: Agent framework (direct dependency)
- **uv**: Package management
- **pytest**: Testing framework
- **ruff**: Linting and formatting

### Async Handling
- Streamlit runs synchronously; all async ADK calls must use proper event loop bridging
- Implement \`_run_async()\` helper for \`tool.run_async()\` invocations
- Proper ToolContext and InvocationContext mocking required

## Quality Gates

### Code Quality
- All code must pass \`ruff check\` and \`ruff format\`
- Type hints required on all public interfaces
- Docstrings required on all public classes and functions
- 80%+ test coverage target

### PR Requirements
- All tests must pass
- No new linting errors
- Documentation updated for user-facing changes
- Golden Trace schema changes require migration plan

## Governance

This constitution supersedes all other development practices. Amendments require:
1. Documentation of the change rationale
2. Impact assessment on existing features
3. Migration plan if breaking changes

**Version**: 1.0.0 | **Ratified**: 2025-12-22 | **Last Amended**: 2025-12-22

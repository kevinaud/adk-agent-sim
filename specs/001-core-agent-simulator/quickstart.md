# Quickstart: Core Agent Simulator

**Feature**: 001-core-agent-simulator  
**Date**: 2025-12-22

## Overview

This quickstart validates the key scenarios for the ADK Agent Simulator. Use these scenarios to verify the implementation is working correctly.

## Prerequisites

1. Python 3.14+ installed
2. Project dependencies installed: `uv sync`
3. A working ADK agent with at least one tool

## Scenario 1: Basic Agent Loading

**Goal**: Verify the simulator can load an agent and display its information.

### Setup
```python
# test_agent.py
from google.adk import Agent
from google.adk.tools import FunctionTool

def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

agent = Agent(
    name="GreeterAgent",
    description="A simple agent that greets people",
    instruction="You are a friendly greeter. Use the greet tool to say hello.",
    tools=[FunctionTool(greet)]
)
```

### Run
```python
from adk_agent_sim import AgentSimulator

AgentSimulator(agents={"Greeter": agent}).run()
```

### Expected Results
- [ ] UI loads in browser at http://localhost:8501
- [ ] Agent name "Greeter" displayed
- [ ] System instruction visible: "You are a friendly greeter..."
- [ ] Tool "greet" appears in tool list with description

---

## Scenario 2: Tool Execution

**Goal**: Verify tools can be executed with correct parameter handling.

### Steps
1. Load the GreeterAgent from Scenario 1
2. Select the "greet" tool from the sidebar
3. Enter "World" in the `name` parameter field
4. Click "Run Tool"

### Expected Results
- [ ] Text input field rendered for `name` parameter
- [ ] Tool executes successfully
- [ ] Output "Hello, World!" displayed in results area
- [ ] Execution appears in history log

---

## Scenario 3: Session Recording

**Goal**: Verify a complete session can be recorded and exported.

### Setup
```python
# calculator_agent.py
from google.adk import Agent
from google.adk.tools import FunctionTool

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

agent = Agent(
    name="CalculatorAgent",
    description="A calculator agent",
    instruction="You perform mathematical calculations.",
    tools=[FunctionTool(add), FunctionTool(multiply)]
)
```

### Steps
1. Load CalculatorAgent
2. Enter user query: "What is 5 * 5 + 10?"
3. Execute `multiply` with a=5, b=5 → expect 25
4. Execute `add` with a=25, b=10 → expect 35
5. Click "End Turn" and enter: "The result is 35."
6. Click "Download Trace"

### Expected Results
- [ ] User query recorded in session
- [ ] Both tool calls appear in history
- [ ] Final response captured
- [ ] JSON file downloads with correct structure:
```json
{
  "metadata": {
    "agent_name": "CalculatorAgent",
    "timestamp": "...",
    "user_query": "What is 5 * 5 + 10?"
  },
  "trace": [
    {"step_index": 0, "type": "tool_call", "tool_name": "multiply", "arguments": {"a": 5, "b": 5}, "output": 25},
    {"step_index": 1, "type": "tool_call", "tool_name": "add", "arguments": {"a": 25, "b": 10}, "output": 35},
    {"step_index": 2, "type": "final_answer", "content": "The result is 35."}
  ]
}
```

---

## Scenario 4: Multiple Agent Selection

**Goal**: Verify switching between agents works correctly.

### Setup
```python
from adk_agent_sim import AgentSimulator

AgentSimulator(agents={
    "Greeter": greeter_agent,
    "Calculator": calculator_agent
}).run()
```

### Steps
1. Launch simulator with both agents
2. Verify dropdown/sidebar shows both agent names
3. Select "Calculator"
4. Verify Calculator tools displayed
5. Switch to "Greeter"
6. Verify Greeter tools displayed

### Expected Results
- [ ] Both agents appear in selector
- [ ] Switching updates displayed tools
- [ ] Switching updates displayed instructions
- [ ] Previous session state cleared on switch

---

## Scenario 5: Error Handling

**Goal**: Verify tool errors are handled gracefully.

### Setup
```python
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    return a / b  # Will raise ZeroDivisionError
```

### Steps
1. Execute `divide` with a=10, b=0

### Expected Results
- [ ] Error caught and displayed as "Tool Error"
- [ ] Error message includes exception details
- [ ] UI remains functional after error
- [ ] Error recorded in trace (if session active)

---

## Validation Checklist

After completing all scenarios:

- [ ] All 5 scenarios pass
- [ ] No unhandled exceptions
- [ ] UI is responsive throughout
- [ ] Exported traces validate against JSON schema
- [ ] Session state persists across tool executions

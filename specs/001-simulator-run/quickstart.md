# Quickstart: ADK Agent Simulator

**Date**: 2025-12-23  
**Plan**: [plan.md](plan.md)

## Installation

The simulator is part of the `adk_agent_sim` package. Add it to your project:

```bash
uv add adk-agent-sim
```

Or if developing locally:

```bash
uv add --editable /path/to/adk-agent-sim
```

## Basic Usage

### 1. Create your ADK Agent (your existing code)

```python
# my_project/agents.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def add(a: int, b: int) -> int:
  """Add two numbers together."""
  return a + b

def multiply(a: int, b: int) -> int:
  """Multiply two numbers together."""
  return a * b

math_agent = Agent(
  model="gemini-2.0-flash",
  name="MathAgent",
  description="A helpful math assistant",
  instruction="You are an expert mathematician. Use the available tools to solve math problems.",
  tools=[FunctionTool(add), FunctionTool(multiply)],
)
```

### 2. Launch the Simulator

```python
# simulate.py
from adk_agent_sim import AgentSimulator, SimulatedAgentConfig
from my_project.agents import math_agent

if __name__ == "__main__":
  simulator = AgentSimulator(
    agents=[
      SimulatedAgentConfig(
        name="Math Agent",
        agent=math_agent,
        eval_set_path="evals/math_agent_evals.json",
      )
    ]
  )
  simulator.run()  # Opens browser at http://localhost:8080
```

Run it:

```bash
uv run python simulate.py
```

### 3. Simulate a Session

1. **Select Agent**: Choose "Math Agent" from the agent cards
2. **Enter Query**: Type "What is 5 * 5 + 10?"
3. **Call Tools**:
   - Select `multiply` from the tool catalog
   - Fill in: `a=5`, `b=5` → Click "Execute"
   - See result: `25`
   - Select `add` from the tool catalog
   - Fill in: `a=25`, `b=10` → Click "Execute"
   - See result: `35`
4. **Final Response**: Click "Final Response" → Type "The answer is 35"
5. **Export**: Click "Export" → EvalCase is appended to `evals/math_agent_evals.json`

## Configuration Options

```python
simulator = AgentSimulator(
  agents=[
    SimulatedAgentConfig(
      name="Agent 1",
      agent=agent1,
      eval_set_path="evals/agent1.json",
    ),
    SimulatedAgentConfig(
      name="Agent 2",
      agent=agent2,
      eval_set_path="evals/agent2.json",
    ),
  ],
  port=8080,           # Default: 8080
  host="0.0.0.0",      # Default: "127.0.0.1"
  title="My Simulator", # Browser tab title
  dark_mode=True,      # Default: False
)
```

### Path Resolution

The `eval_set_path` supports both relative and absolute paths:

```python
# Relative path (resolved from current working directory)
SimulatedAgentConfig(
  name="Agent",
  agent=my_agent,
  eval_set_path="evals/my_evals.json",  # -> {cwd}/evals/my_evals.json
)

# Absolute path
SimulatedAgentConfig(
  name="Agent",
  agent=my_agent,
  eval_set_path="/data/golden_traces/my_evals.json",
)
```

## Working with Multiple Agents

Pass a list of agent configs. The user selects one at startup:

```python
simulator = AgentSimulator(
  agents=[
    SimulatedAgentConfig(
      name="Math Bot",
      agent=math_agent,
      eval_set_path="evals/math_bot.json",
    ),
    SimulatedAgentConfig(
      name="Writer Bot",
      agent=writer_agent,
      eval_set_path="evals/writer_bot.json",
    ),
    SimulatedAgentConfig(
      name="Search Bot",
      agent=search_agent,
      eval_set_path="evals/search_bot.json",
    ),
  ]
)
)
```

## Working with Structured Schemas

If your agent has `input_schema` or `output_schema`, the simulator renders forms automatically:

```python
from pydantic import BaseModel, Field

class QueryInput(BaseModel):
  query: str = Field(description="The user's question")
  max_results: int = Field(default=10, description="Maximum results to return")

class StructuredOutput(BaseModel):
  answer: str = Field(description="The final answer")
  confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")

agent = Agent(
  model="gemini-2.0-flash",
  name="StructuredAgent",
  input_schema=QueryInput,
  output_schema=StructuredOutput,
  # ...
)
```

## EvalSet File Format

The exported file is an ADK `EvalSet` containing one or more `EvalCase` entries:

```json
{
  "eval_set_id": "math_agent_evals",
  "name": "Math Agent Evaluation Set",
  "description": "Golden traces captured via ADK Agent Simulator for Math Agent",
  "eval_cases": [
    {
      "eval_id": "math_agent_2025-12-23T14:30:00",
      "conversation": [
        {
          "invocation_id": "session_abc123_inv_0",
          "user_content": {
            "parts": [{"text": "What is 5 * 5 + 10?"}]
          },
          "final_response": {
            "parts": [{"text": "The answer is 35"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {"id": "call_1", "name": "multiply", "args": {"a": 5, "b": 5}},
              {"id": "call_2", "name": "add", "args": {"a": 25, "b": 10}}
            ],
            "tool_responses": [
              {"id": "call_1", "name": "multiply", "response": {"result": 25}},
              {"id": "call_2", "name": "add", "response": {"result": 35}}
            ]
          },
          "creation_timestamp": 1703340600.0
        }
      ],
      "creation_timestamp": 1703340600.0
    }
  ],
  "creation_timestamp": 1703340000.0
}
```

### Export Behavior

- **First export**: Creates a new EvalSet file with one EvalCase
- **Subsequent exports**: Loads existing file, appends new EvalCase, writes back
- **File creation**: Parent directories are created automatically if they don't exist

## Using EvalSet Files for Evaluation

### With ADK CLI

```bash
# Run all eval cases in the set
uv run adk eval my_project/agents evals/math_agent_evals.json

# Run specific eval cases
uv run adk eval my_project/agents evals/math_agent_evals.json:math_agent_2025-12-23T14:30:00
```

### Programmatically

```python
from google.adk.evaluation.eval_set import EvalSet
import json

with open("evals/math_agent_evals.json") as f:
  data = json.load(f)

eval_set = EvalSet.model_validate(data)
print(f"Loaded {len(eval_set.eval_cases)} eval cases")

# Access individual cases
for case in eval_set.eval_cases:
  print(f"- {case.eval_id}")
```

## Troubleshooting

### Port Already in Use

```python
simulator.run(port=8081)  # Try a different port
```

### Tool Execution Hangs

The simulator shows a timer and "Cancel" button. Click Cancel to abort long-running tools.

### Session Lost After Browser Refresh

Sessions are ephemeral (in-memory only). Export your Golden Trace before closing the browser.

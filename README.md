# adk-agent-sim

A simulator that allows a human to perform the task of an ADK agent

## Setup

1. Install `uv` if you haven't already.
2. Run `uv sync` to install dependencies.
3. Copy `.env.example` to `.env` and fill in the values.

## Usage

```bash
uv run adk-agent-sim --help
```

## Development

### Quality Checks

Run the quality check script:
```bash
./scripts/check_quality.sh
```

### Testing

Run tests:
```bash
uv run pytest
```

Run integration tests:
```bash
uv run pytest --run-integration
```

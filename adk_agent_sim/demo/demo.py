"""ADK Agent Sim demo app."""

from __future__ import annotations

import structlog
import typer
from rich.console import Console
from structlog.typing import FilteringBoundLogger

from adk_agent_sim.logging_config import configure_logging

console = Console()


def get_logger() -> FilteringBoundLogger:
  """Configure logging and return a logger instance."""
  configure_logging()
  return structlog.get_logger()


app = typer.Typer(
  help="A simulator that allows a human to perform the task of an ADK agent",
  no_args_is_help=True,
)


@app.command()
def run(port: int = 8888):
  """Run demo."""
  log = get_logger()
  log.info("Running demo", port=port)
  console.print(f"Starting demo app on port [bold blue]{port}[/bold blue]...")


if __name__ == "__main__":
  app()

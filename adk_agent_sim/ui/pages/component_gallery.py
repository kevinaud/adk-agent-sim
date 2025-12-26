"""Component gallery for testing."""

import textwrap
from datetime import datetime

from starlette.datastructures import QueryParams

from adk_agent_sim.models.history import ToolOutput
from adk_agent_sim.ui.components.event_block import create_event_block
from adk_agent_sim.ui.components.gallery_engine import ComponentRegistry, GalleryEngine


def event_block_complex_tool_output():
  """Factory for a complex tool output event block."""
  result_data = {
    "status": "success",
    "total_duration": 1240,
    "execution_trace": [
      {
        "step_id": "init_01",
        "console_log": "> Connecting to subsystem...\n> Connection established.",
        "remote_config": '{"model": "gemini-1.5-pro", "temperature": 0.7}',
        "chain_of_thought": textwrap.dedent("""
          ### Reasoning
          
          * The system successfully initialized the core components.
          * Configuration parameters were correctly loaded from the remote source.
          * The initial connection established a stable baseline for subsequent operations.
        """).strip(),
      }
    ],
  }

  entry = ToolOutput(
    call_id="call_123",
    result=result_data,
    duration_ms=1240,
    timestamp=datetime.now(),
  )

  return create_event_block(entry)


REGISTRY: ComponentRegistry = {
  "EventBlock_ComplexToolOutput": event_block_complex_tool_output
}


def render_gallery_index():
  GalleryEngine(REGISTRY).render_index()


def render_gallery_component(name: str, query_params: QueryParams):
  GalleryEngine(REGISTRY).render_component(name, query_params)

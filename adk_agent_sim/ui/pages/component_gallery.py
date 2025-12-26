"""Component gallery for testing."""

import textwrap
from datetime import datetime
from typing import Any, List

from google.adk.tools import BaseTool
from google.genai.types import FunctionDeclaration, Schema, Type
from nicegui import ui
from starlette.datastructures import QueryParams

from adk_agent_sim.models.history import (
  FinalResponse,
  ToolCall,
  ToolError,
  ToolOutput,
  UserQuery,
)
from adk_agent_sim.ui.components.action_panel import ActionPanel
from adk_agent_sim.ui.components.agent_card import AgentCard
from adk_agent_sim.ui.components.devtools_tree import DevToolsTree
from adk_agent_sim.ui.components.event_block import LoadingBlock, create_event_block
from adk_agent_sim.ui.components.gallery_engine import ComponentRegistry, GalleryEngine
from adk_agent_sim.ui.components.json_tree import JsonTree
from adk_agent_sim.ui.components.text_presenter import TextPresenter
from adk_agent_sim.ui.components.tool_catalog import ToolCatalog
from adk_agent_sim.ui.components.tree_expansion_state import TreeExpansionState


class GalleryTool(BaseTool):
  """Simple tool wrapper for gallery demonstrations using real ADK types."""

  def __init__(self, name: str, declaration: FunctionDeclaration):
    self.name = name
    self._declaration = declaration

  def _get_declaration(self) -> FunctionDeclaration:
    return self._declaration


def get_gallery_tools() -> List[BaseTool]:
  """Generate a list of tools for gallery demonstrations."""
  return [
    GalleryTool(
      name="search_knowledge_base",
      declaration=FunctionDeclaration(
        name="search_knowledge_base",
        description=(
          "Searches the internal knowledge base for documents matching the query."
        ),
        parameters=Schema(
          type=Type.OBJECT,
          properties={
            "query": Schema(type=Type.STRING, description="The search query string."),
            "limit": Schema(type=Type.INTEGER, description="Max number of results."),
          },
          required=["query"],
        ),
      ),
    ),
    GalleryTool(
      name="calculator",
      declaration=FunctionDeclaration(
        name="calculator",
        description="Performs basic arithmetic operations.",
        parameters=Schema(
          type=Type.OBJECT,
          properties={
            "expression": Schema(
              type=Type.STRING,
              description="The mathematical expression to evaluate.",
            )
          },
          required=["expression"],
        ),
      ),
    ),
    GalleryTool(
      name="complex_tool",
      declaration=FunctionDeclaration(
        name="complex_tool",
        description="A tool with complex nested parameters.",
        parameters=Schema(
          type=Type.OBJECT,
          properties={
            "config": Schema(
              type=Type.OBJECT,
              description="Configuration object.",
              properties={
                "mode": Schema(
                  type=Type.STRING,
                  description="Operation mode.",
                  enum=["fast", "accurate"],
                ),
                "options": Schema(
                  type=Type.ARRAY,
                  description="List of options.",
                  items=Schema(type=Type.STRING),
                ),
              },
            )
          },
        ),
      ),
    ),
  ]


# --- Factory Functions (for components with complex parameters) ---


def event_block_user_query() -> Any:
  """Render a User Query event block."""
  entry = UserQuery(
    content="How do I reset my password?",
    timestamp=datetime.now(),
  )
  return create_event_block(entry)


def event_block_tool_call() -> Any:
  """Render a Tool Call event block."""
  entry = ToolCall(
    call_id="call_001",
    tool_name="search_knowledge_base",
    arguments={"query": "password reset", "limit": 5},
    timestamp=datetime.now(),
  )
  return create_event_block(entry)


def event_block_tool_output_string() -> Any:
  """Render a Tool Output event block with simple string result."""
  entry = ToolOutput(
    call_id="call_001",
    result="Found 2 articles related to 'password reset'.",
    duration_ms=450,
    timestamp=datetime.now(),
  )
  return create_event_block(entry)


def event_block_complex_tool_output() -> Any:
  """Render a complex tool output event block with reasoning trace."""
  result_data = {
    "status": "success",
    "total_duration": 1240,
    "execution_trace": [
      {
        "step_id": "init_01",
        "console_log": ("> Connecting to subsystem...\n> Connection established."),
        "remote_config": '{"model": "gemini-1.5-pro", "temperature": 0.7}',
        "chain_of_thought": textwrap.dedent("""
          ### Reasoning
          
          * The system successfully initialized the core components.
          * Configuration parameters were correctly loaded.
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


def event_block_tool_error() -> Any:
  """Render a Tool Error event block."""
  entry = ToolError(
    call_id="call_999",
    error_type="ValueError",
    error_message="Invalid argument: 'limit' must be positive.",
    traceback=(
      'Traceback (most recent call last):\n  File "tool.py", line 10, in run\n'
      '    raise ValueError("Invalid argument...")'
    ),
    duration_ms=120,
    timestamp=datetime.now(),
  )
  return create_event_block(entry)


def event_block_final_response() -> Any:
  """Render a Final Response event block with Markdown."""
  content = textwrap.dedent("""
    Here is the **summary** of your request:
    
    1. Check account status
    2. Review recent transactions
    
    Everything looks *normal*.
  """).strip()

  entry = FinalResponse(
    content=content,
    timestamp=datetime.now(),
  )
  return create_event_block(entry)


def event_block_loading() -> LoadingBlock:
  """Render a Loading block."""
  return LoadingBlock(tool_name="long_running_process", elapsed_ms=1500)


def tool_catalog_default() -> ToolCatalog:
  """Render ToolCatalog with gallery tools."""
  return ToolCatalog(tools=get_gallery_tools(), expanded=True)


def devtools_tree_nested() -> DevToolsTree:
  """Render DevToolsTree with nested JSON data."""
  data = {
    "execution_trace": {
      "step_id": "init_01",
      "status": "success",
      "config": {
        "model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 1024,
      },
      "results": [
        {"id": 1, "score": 0.95, "label": "positive"},
        {"id": 2, "score": 0.72, "label": "neutral"},
      ],
    },
    "metadata": {
      "timestamp": "2025-12-26T10:30:00Z",
      "version": "1.0.0",
    },
  }
  return DevToolsTree(data=data, tree_id="nested-demo")


def devtools_tree_collapsed() -> DevToolsTree:
  """Render DevToolsTree with collapsed state."""
  data = {"outer": {"inner": {"deep": {"value": 123, "items": [1, 2, 3]}}}}
  state = TreeExpansionState(default_expanded=False)
  return DevToolsTree(data=data, tree_id="collapsed-demo", expansion_state=state)


def devtools_tree_primitives() -> DevToolsTree:
  """Render DevToolsTree showcasing all primitive types."""
  data = {
    "string_value": "Hello, World!",
    "number_int": 42,
    "number_float": 3.14159,
    "bool_true": True,
    "bool_false": False,
    "null_value": None,
    "empty_object": {},
    "empty_array": [],
  }
  return DevToolsTree(data=data, tree_id="primitives-demo")


def action_panel_default() -> ActionPanel:
  """Render ActionPanel with gallery tools."""

  async def on_response(text: str):
    ui.notify(f"Response submitted: {text[:20]}...")

  return ActionPanel(
    tools=get_gallery_tools(),
    on_tool_select=lambda name: ui.notify(f"Selected: {name}"),
    on_final_response=on_response,
  )


# --- Registry Definition ---
# Classes are registered directly - query params drive initialization
# Factory functions are used for components with complex parameters (callbacks, tools)

REGISTRY: ComponentRegistry = {
  # Simple Components (class-based, query param driven)
  "AgentCard": AgentCard,
  "JsonTree": JsonTree,
  "DevToolsTree": DevToolsTree,
  "TextPresenter": TextPresenter,
  "LoadingBlock": LoadingBlock,
  # Event Blocks (factory-based, need HistoryEntry objects)
  "EventBlock_UserQuery": event_block_user_query,
  "EventBlock_ToolCall": event_block_tool_call,
  "EventBlock_ToolOutput_String": event_block_tool_output_string,
  "EventBlock_ToolOutput_Complex": event_block_complex_tool_output,
  "EventBlock_ToolError": event_block_tool_error,
  "EventBlock_FinalResponse": event_block_final_response,
  "EventBlock_Loading": event_block_loading,
  # DevToolsTree variations (factory-based for complex state)
  "DevToolsTree_Nested": devtools_tree_nested,
  "DevToolsTree_Collapsed": devtools_tree_collapsed,
  "DevToolsTree_Primitives": devtools_tree_primitives,
  # Complex Panels (factory-based, need tools/callbacks)
  "ToolCatalog_Default": tool_catalog_default,
  "ActionPanel_Default": action_panel_default,
}


def render_gallery_index() -> None:
  """Render the gallery index page."""
  GalleryEngine(REGISTRY).render_index()


def render_gallery_component(name: str, query_params: QueryParams) -> None:
  """Render a specific gallery component."""
  GalleryEngine(REGISTRY).render_component(name, query_params)

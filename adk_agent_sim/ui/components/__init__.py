"""Reusable UI components for the agent simulator."""

from adk_agent_sim.ui.components.agent_card import (
  AgentCard,
  AgentCardGrid,
  render_agent_card,
  render_agent_card_grid,
)
from adk_agent_sim.ui.components.devtools_tree import (
  BlobTogglePills,
  BlobType,
  BlobViewState,
  DevToolsTree,
  SmartBlobDetector,
  SmartBlobRenderer,
  TreeExpansionState,
  ValueType,
  render_smart_blob,
)
from adk_agent_sim.ui.components.event_block import (
  AgentResponseBlock,
  EventBlock,
  LoadingBlock,
  ToolCallBlock,
  ToolErrorBlock,
  ToolExecutionBlock,
  ToolOutputBlock,
  UserInputBlock,
  create_event_block,
  render_event_block,
)
from adk_agent_sim.ui.components.event_stream import (
  EventStream,
  RefreshableEventStream,
  render_event_stream,
)
from adk_agent_sim.ui.components.text_presenter import (
  PresentationMode,
  PresentationModeManager,
  TextPresenter,
  get_mode_manager,
  render_text_presenter,
)
from adk_agent_sim.ui.components.tool_catalog import (
  SelectableToolCatalog,
  ToolCatalog,
  ToolInfo,
  extract_tool_info,
  render_selectable_tool_catalog,
  render_tool_catalog,
)

__all__ = [
  # Agent Card
  "AgentCard",
  "AgentCardGrid",
  "render_agent_card",
  "render_agent_card_grid",
  # DevTools Tree (replaces JsonTree)
  "BlobTogglePills",
  "BlobType",
  "BlobViewState",
  "DevToolsTree",
  "SmartBlobDetector",
  "SmartBlobRenderer",
  "TreeExpansionState",
  "ValueType",
  "render_smart_blob",
  # Event Blocks
  "AgentResponseBlock",
  "EventBlock",
  "LoadingBlock",
  "ToolCallBlock",
  "ToolErrorBlock",
  "ToolExecutionBlock",
  "ToolOutputBlock",
  "UserInputBlock",
  "create_event_block",
  "render_event_block",
  # Event Stream
  "EventStream",
  "RefreshableEventStream",
  "render_event_stream",
  # Text Presenter
  "PresentationMode",
  "PresentationModeManager",
  "TextPresenter",
  "get_mode_manager",
  "render_text_presenter",
  # Tool Catalog
  "SelectableToolCatalog",
  "ToolCatalog",
  "ToolInfo",
  "extract_tool_info",
  "render_selectable_tool_catalog",
  "render_tool_catalog",
]

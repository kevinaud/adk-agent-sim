"""Tool catalog component for displaying all tools with full metadata."""

from typing import TYPE_CHECKING, Any, TypedDict

from nicegui import ui

if TYPE_CHECKING:
  from google.adk.tools import BaseTool


class ToolInfo(TypedDict):
  """Tool information for display in catalog."""

  name: str
  description: str | None
  parameters: dict[str, Any]  # JSON Schema for parameters


def extract_tool_info(tool: BaseTool) -> ToolInfo:
  """Extract tool information from a BaseTool instance.

  Args:
    tool: The ADK tool to extract info from

  Returns:
    ToolInfo dict with name, description, and parameter schema
  """
  # Get the tool's declaration (function schema)
  declaration = tool._get_declaration()

  # Extract parameter schema from declaration
  parameters: dict[str, Any] = {}
  if declaration and declaration.parameters:
    # FunctionDeclaration.parameters is a Schema object
    params = declaration.parameters
    if hasattr(params, "properties") and params.properties:
      for prop_name, prop_schema in params.properties.items():
        prop_dict: dict[str, Any] = {"type": getattr(prop_schema, "type", "any")}
        if hasattr(prop_schema, "description") and prop_schema.description:
          prop_dict["description"] = prop_schema.description
        parameters[prop_name] = prop_dict

    if hasattr(params, "required") and params.required:
      parameters["_required"] = list(params.required)

  return ToolInfo(
    name=tool.name,
    description=declaration.description if declaration else None,
    parameters=parameters,
  )


class ToolCatalog:
  """Read-only view of all tools available to the selected agent.

  Displays tool name, description, and collapsible input/output schemas.
  Supports click-to-select for tool execution.
  """

  def __init__(
    self,
    tools: list[BaseTool],
    on_select: Any | None = None,
    expanded: bool = False,
  ) -> None:
    """
    Initialize the tool catalog.

    Args:
      tools: List of ADK tools to display
      on_select: Optional callback when a tool is selected (receives tool name)
      expanded: Initial expansion state of the catalog (default: False)
    """
    self.tools = tools
    self.on_select = on_select
    self.expanded = expanded
    self._tool_infos = [extract_tool_info(t) for t in tools]

  def _render_tool_card(self, tool_info: ToolInfo) -> None:
    """Render a single tool card with name, description, and schema."""
    card_classes = "w-full mb-2 hover:shadow-md transition-shadow"
    if self.on_select:
      card_classes += " cursor-pointer"

    with ui.card().classes(card_classes) as card:
      # Click handler on card for tool selection
      if self.on_select:
        on_select_callback = self.on_select  # Capture for lambda
        card.on("click", lambda t=tool_info["name"]: on_select_callback(t))

      # Tool header with name
      with ui.row().classes("w-full items-center justify-between"):
        with ui.row().classes("items-center gap-2"):
          ui.icon("build", size="sm").classes("text-blue-600")
          ui.label(tool_info["name"]).classes("font-medium text-blue-800")

        if self.on_select:
          ui.icon("chevron_right", size="sm").classes("text-gray-400")

      # Description
      if tool_info["description"]:
        ui.label(tool_info["description"]).classes(
          "text-sm text-gray-600 mt-1 line-clamp-2"
        )
      else:
        ui.label("No description available").classes(
          "text-sm text-gray-400 italic mt-1"
        )

      # Parameter schema (always visible)
      if tool_info["parameters"]:
        # Filter out _required marker for display
        display_params = {
          k: v for k, v in tool_info["parameters"].items() if not k.startswith("_")
        }
        required = tool_info["parameters"].get("_required", [])

        if display_params:
          with ui.column().classes("w-full mt-2 pt-2 border-t border-gray-200"):
            with ui.row().classes("items-center gap-1 mb-2"):
              ui.icon("data_object", size="xs").classes("text-gray-500")
              ui.label("Parameters").classes("text-xs font-medium text-gray-600")

            # Show parameter list
            for param_name, param_info in display_params.items():
              is_required = param_name in required
              req_badge = "*" if is_required else ""

              with ui.row().classes("items-start gap-2 mb-1"):
                ui.label(f"{param_name}{req_badge}:").classes(
                  "font-mono text-xs text-blue-700 min-w-24"
                )
                param_type = param_info.get("type", "any")
                ui.badge(param_type, color="gray-4").props("dense")

              if param_info.get("description"):
                ui.label(param_info["description"]).classes(
                  "text-xs text-gray-500 ml-6 mb-2"
                )

            if required:
              ui.label("* required").classes("text-xs text-gray-400 italic mt-2")

  def render(self) -> None:
    """Render the tool catalog component."""
    if not self.tools:
      ui.label("No tools available").classes("text-gray-500 italic")
      return

    with ui.expansion(
      f"Tools ({len(self.tools)})",
      icon="construction",
      value=self.expanded,
    ).classes("w-full"):
      with ui.column().classes("w-full gap-2 p-2"):
        for tool_info in self._tool_infos:
          self._render_tool_card(tool_info)


class SelectableToolCatalog:
  """Tool catalog with selection capability for action panel integration."""

  def __init__(
    self,
    tools: list[BaseTool],
    on_tool_select: Any,
    selected_tool: str | None = None,
  ) -> None:
    """
    Initialize the selectable tool catalog.

    Args:
      tools: List of ADK tools to display
      on_tool_select: Callback when a tool is selected (receives tool name)
      selected_tool: Currently selected tool name (if any)
    """
    self.tools = tools
    self.on_tool_select = on_tool_select
    self.selected_tool = selected_tool
    self._tool_infos = [extract_tool_info(t) for t in tools]

  def _render_tool_card(self, tool_info: ToolInfo) -> None:
    """Render a single selectable tool card."""
    is_selected = tool_info["name"] == self.selected_tool

    # Highlight selected tool
    border_class = (
      "border-2 border-blue-500" if is_selected else "border border-gray-200"
    )
    bg_class = "bg-blue-50" if is_selected else "bg-white"

    card_cls = (
      f"w-full mb-2 cursor-pointer hover:shadow-md transition-all "
      f"{border_class} {bg_class}"
    )
    with ui.card().classes(card_cls) as card:
      # Click handler on card for tool selection
      card.on("click", lambda t=tool_info["name"]: self.on_tool_select(t))

      # Tool header
      with ui.row().classes("w-full items-center justify-between"):
        with ui.row().classes("items-center gap-2"):
          icon_color = "text-blue-600" if is_selected else "text-gray-500"
          ui.icon("build", size="sm").classes(icon_color)
          label_class = "font-medium text-blue-800" if is_selected else "font-medium"
          ui.label(tool_info["name"]).classes(label_class)

        if is_selected:
          ui.icon("check_circle", size="sm").classes("text-blue-600")
        else:
          ui.icon("radio_button_unchecked", size="sm").classes("text-gray-300")

      # Description
      if tool_info["description"]:
        ui.label(tool_info["description"]).classes(
          "text-sm text-gray-600 mt-1 line-clamp-2"
        )
      else:
        ui.label("No description available").classes(
          "text-sm text-gray-400 italic mt-1"
        )

      # Parameter schema (always visible)
      if tool_info["parameters"]:
        display_params = {
          k: v for k, v in tool_info["parameters"].items() if not k.startswith("_")
        }
        required = tool_info["parameters"].get("_required", [])

        if display_params:
          with ui.column().classes("w-full mt-2 pt-2 border-t border-gray-200"):
            with ui.row().classes("items-center gap-1 mb-2"):
              ui.icon("data_object", size="xs").classes("text-gray-500")
              ui.label("Parameters").classes("text-xs font-medium text-gray-600")

            for param_name, param_info in display_params.items():
              is_required = param_name in required
              req_badge = "*" if is_required else ""

              with ui.row().classes("items-start gap-2 mb-1"):
                ui.label(f"{param_name}{req_badge}:").classes(
                  "font-mono text-xs text-blue-700 min-w-24"
                )
                param_type = param_info.get("type", "any")
                ui.badge(param_type, color="gray-4").props("dense")

              if param_info.get("description"):
                ui.label(param_info["description"]).classes(
                  "text-xs text-gray-500 ml-6 mb-2"
                )

            if required:
              ui.label("* required").classes("text-xs text-gray-400 italic mt-2")

  def render(self) -> None:
    """Render the selectable tool catalog."""
    if not self.tools:
      ui.label("No tools available").classes("text-gray-500 italic")
      return

    ui.label("Select a tool:").classes("text-sm text-gray-600 mb-2")

    with ui.column().classes("w-full gap-2"):
      for tool_info in self._tool_infos:
        self._render_tool_card(tool_info)


def render_tool_catalog(
  tools: list[BaseTool],
  on_select: Any | None = None,
  expanded: bool = False,
) -> ToolCatalog:
  """
  Render a tool catalog component.

  Args:
    tools: List of ADK tools to display
    on_select: Optional callback when a tool is selected
    expanded: Initial expansion state

  Returns:
    ToolCatalog instance
  """
  catalog = ToolCatalog(tools, on_select, expanded)
  catalog.render()
  return catalog


def render_selectable_tool_catalog(
  tools: list[BaseTool],
  on_tool_select: Any,
  selected_tool: str | None = None,
) -> SelectableToolCatalog:
  """
  Render a selectable tool catalog component.

  Args:
    tools: List of ADK tools to display
    on_tool_select: Callback when a tool is selected
    selected_tool: Currently selected tool name

  Returns:
    SelectableToolCatalog instance
  """
  catalog = SelectableToolCatalog(tools, on_tool_select, selected_tool)
  catalog.render()
  return catalog

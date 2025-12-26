"""Shared CSS constants and styles for the UI."""

# Color palette
COLORS = {
  "primary": "#1976D2",
  "secondary": "#424242",
  "accent": "#82B1FF",
  "error": "#FF5252",
  "warning": "#FFC107",
  "success": "#4CAF50",
  "info": "#2196F3",
  "background": "#FAFAFA",
  "surface": "#FFFFFF",
  "text_primary": "#212121",
  "text_secondary": "#757575",
}

# History entry colors
HISTORY_COLORS = {
  "user_query": "#E3F2FD",  # Light blue
  "tool_call": "#FFF3E0",  # Light orange
  "tool_output": "#E8F5E9",  # Light green
  "tool_error": "#FFEBEE",  # Light red
  "final_response": "#F3E5F5",  # Light purple
}

# History entry border colors
HISTORY_BORDER_COLORS = {
  "user_query": "#1976D2",  # Blue
  "tool_call": "#F57C00",  # Orange
  "tool_output": "#388E3C",  # Green
  "tool_error": "#D32F2F",  # Red
  "final_response": "#7B1FA2",  # Purple
}

# Card styles
CARD_STYLE = """
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 12px;
"""

# History entry base style
HISTORY_ENTRY_STYLE = """
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-left: 4px solid;
"""

# Panel styles
PANEL_HEADER_STYLE = """
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #212121;
"""

# Form field styles
FIELD_STYLE = """
  margin-bottom: 8px;
"""

# Button styles
PRIMARY_BUTTON_STYLE = """
  background-color: #1976D2;
  color: white;
"""

DANGER_BUTTON_STYLE = """
  background-color: #D32F2F;
  color: white;
"""

SUCCESS_BUTTON_STYLE = """
  background-color: #388E3C;
  color: white;
"""

# Timer styles
TIMER_STYLE = """
  font-family: monospace;
  font-size: 1.2rem;
  color: #757575;
"""

# Layout constants
SIDEBAR_WIDTH = 300
MAIN_CONTENT_MIN_WIDTH = 600
HISTORY_PANEL_HEIGHT = "calc(100vh - 300px)"

# UX Modernization: Layout constants for 2/3 + 1/3 split
LAYOUT = {
  "main_content_width": "w-2/3",
  "sidebar_width": "w-1/3",
  "event_stream_height": "calc(100vh - 200px)",
  "sidebar_height": "calc(100vh - 200px)",
  "header_height": "64px",
}

# Agent card styles
AGENT_CARD_STYLE = """
  width: 280px;
  border-radius: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
"""

AGENT_CARD_HOVER_CLASSES = "hover:shadow-xl hover:scale-105"

# Event stream block styles
EVENT_BLOCK_STYLE = """
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid;
  width: 100%;
"""

# Icons for each event type
EVENT_ICONS = {
  "user_query": "person",
  "tool_call": "build",
  "tool_output": "check_circle",
  "tool_error": "error",
  "final_response": "smart_toy",
}

# JSON tree styles
JSON_TREE_KEY_STYLE = "font-weight: 500; color: #1976D2;"
JSON_TREE_VALUE_STYLE = "color: #424242; font-family: monospace;"
JSON_TREE_PRIMITIVE_COLORS = {
  "string": "#388E3C",
  "number": "#F57C00",
  "boolean": "#7B1FA2",
  "null": "#757575",
}

# Loading state styles
LOADING_BLOCK_STYLE = """
  background-color: #F5F5F5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
"""

# Control panel sidebar styles
CONTROL_PANEL_CLASSES = "h-full border-l bg-gray-50 p-4"

# Expandable header styles
EXPANDABLE_HEADER_CLASSES = "w-full bg-blue-50 mb-4"

# DevTools tree styling - clean-room implementation (no code reuse from json_tree)
DEVTOOLS_TREE_STYLES = {
  "font_family": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
  "font_size": "13px",
  "line_height": "1.4",
  "indent_size": "12px",
  "thread_line_color": "#E0E0E0",
  "key_color": "#881391",  # Purple for keys
  "string_color": "#C41A16",  # Red for strings
  "number_color": "#1C00CF",  # Blue for numbers
  "boolean_color": "#0D47A1",  # Dark blue for booleans
  "null_color": "#808080",  # Gray for null
  "bracket_color": "#000000",  # Black for brackets
}

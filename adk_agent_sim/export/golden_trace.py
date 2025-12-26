"""Golden Trace builder for exporting sessions as ADK EvalCase format."""

import json
import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from google.adk.evaluation.eval_case import EvalCase
  from google.genai.types import Content, FunctionCall, FunctionResponse

  from adk_agent_sim.models.session import SimulationSession


class GoldenTraceBuilder:
  """Builds ADK-compatible EvalCase from a completed simulation session."""

  def __init__(self, session: SimulationSession) -> None:
    """
    Initialize the builder with a completed session.

    Args:
      session: A completed SimulationSession
    """
    self.session = session

  def build(self) -> EvalCase:
    """
    Build an EvalCase from the session.

    Returns:
      EvalCase ready for serialization
    """
    from google.adk.evaluation.eval_case import EvalCase, Invocation

    eval_id = self._generate_eval_id()
    user_query = self._extract_user_query()
    final_response = self._extract_final_response()
    tool_uses, tool_responses = self._extract_tool_data()

    # Build intermediate_data dict for Invocation
    intermediate_data: dict[str, Any] = {}
    if tool_uses:
      intermediate_data["tool_uses"] = tool_uses
    if tool_responses:
      intermediate_data["tool_responses"] = tool_responses

    invocation = Invocation(
      invocation_id=self.session.session_id,
      user_content=user_query,
      final_response=final_response,
      intermediate_data=intermediate_data if intermediate_data else None,  # type: ignore
    )

    return EvalCase(
      eval_id=eval_id,
      conversation=[invocation],
      creation_timestamp=datetime.now(timezone.utc).timestamp(),
    )

  def _generate_eval_id(self) -> str:
    """Generate eval_id in format: {snake_case_agent_name}_{iso_timestamp}."""
    agent_name = self.session.agent_name or "unknown"
    # Convert to snake_case
    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", agent_name).lower()
    snake_name = re.sub(r"[^a-z0-9_]", "_", snake_name)
    snake_name = re.sub(r"_+", "_", snake_name).strip("_")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{snake_name}_{timestamp}"

  def _extract_user_query(self) -> Content:
    """Extract user query as Content with Part."""
    from google.genai.types import Content, Part

    from adk_agent_sim.models.history import UserQuery

    for entry in self.session.history:
      if isinstance(entry, UserQuery):
        return Content(
          role="user",
          parts=[Part(text=entry.content)],
        )

    # Fallback if no user query found
    return Content(role="user", parts=[Part(text="")])

  def _extract_final_response(self) -> Content:
    """Extract final response as Content with Part."""
    from google.genai.types import Content, Part

    from adk_agent_sim.models.history import FinalResponse

    for entry in reversed(self.session.history):
      if isinstance(entry, FinalResponse):
        return Content(
          role="model",
          parts=[Part(text=entry.content)],
        )

    # Fallback if no final response found
    return Content(role="model", parts=[Part(text="")])

  def _extract_tool_data(
    self,
  ) -> tuple[list[FunctionCall], list[FunctionResponse]]:
    """
    Extract tool calls and responses from history.

    Returns:
      Tuple of (FunctionCall list, FunctionResponse list)
    """
    from google.genai.types import FunctionCall, FunctionResponse

    from adk_agent_sim.models.history import ToolCall, ToolError, ToolOutput

    tool_uses: list[FunctionCall] = []
    tool_responses: list[FunctionResponse] = []

    # Map call_ids to their tool names for response matching
    call_id_to_name: dict[str, str] = {}

    for entry in self.session.history:
      if isinstance(entry, ToolCall):
        call_id_to_name[entry.call_id] = entry.tool_name
        tool_uses.append(
          FunctionCall(
            id=entry.call_id,
            name=entry.tool_name,
            args=entry.arguments,
          )
        )
      elif isinstance(entry, ToolOutput):
        tool_name = call_id_to_name.get(entry.call_id, "unknown")
        # Convert result to dict/JSON-serializable format
        response_data = self._serialize_result(entry.result)
        tool_responses.append(
          FunctionResponse(
            id=entry.call_id,
            name=tool_name,
            response=response_data,
          )
        )
      elif isinstance(entry, ToolError):
        tool_name = call_id_to_name.get(entry.call_id, "unknown")
        # Convert error to response format
        error_response = {
          "error": True,
          "error_type": entry.error_type,
          "error_message": entry.error_message,
        }
        if entry.traceback:
          error_response["traceback"] = entry.traceback
        tool_responses.append(
          FunctionResponse(
            id=entry.call_id,
            name=tool_name,
            response=error_response,
          )
        )

    return tool_uses, tool_responses

  def _serialize_result(self, result: Any) -> dict[str, Any]:
    """Serialize a tool result to a JSON-compatible dict."""
    if result is None:
      return {"result": None}

    if isinstance(result, dict):
      return result

    if isinstance(result, (str, int, float, bool)):
      return {"result": result}

    if isinstance(result, (list, tuple)):
      return {"result": list(result)}

    # Try to use model_dump for Pydantic models
    if hasattr(result, "model_dump"):
      try:
        return result.model_dump()
      except Exception:
        pass

    # Fallback to string representation
    return {"result": str(result)}

  def export_json(self, eval_case: EvalCase | None = None) -> str:
    """
    Export EvalCase to JSON string.

    Args:
      eval_case: Optional pre-built EvalCase (builds if not provided)

    Returns:
      JSON string of the EvalCase
    """
    if eval_case is None:
      eval_case = self.build()

    # Use model_dump_json if available (Pydantic v2)
    if hasattr(eval_case, "model_dump_json"):
      return eval_case.model_dump_json(indent=2)

    # Fallback for Pydantic v1 or non-Pydantic objects
    if hasattr(eval_case, "json"):
      return eval_case.json(indent=2)  # type: ignore

    # Last resort - manual serialization
    return json.dumps(self._to_dict(eval_case), indent=2)

  def _to_dict(self, obj: Any) -> Any:
    """Recursively convert object to dict."""
    if obj is None:
      return None

    if isinstance(obj, (str, int, float, bool)):
      return obj

    if isinstance(obj, (list, tuple)):
      return [self._to_dict(item) for item in obj]

    if isinstance(obj, dict):
      return {k: self._to_dict(v) for k, v in obj.items()}

    if hasattr(obj, "model_dump"):
      return obj.model_dump()

    if hasattr(obj, "__dict__"):
      return {k: self._to_dict(v) for k, v in obj.__dict__.items()}

    return str(obj)

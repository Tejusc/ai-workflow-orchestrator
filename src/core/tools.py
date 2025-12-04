from typing import Any, Dict, Callable

from src.core.logging import get_logger

logger = get_logger(__name__)

ToolPayload = Dict[str, Any]
ToolResult = Dict[str, Any]
ToolFunc = Callable[[ToolPayload], ToolResult]


def echo_tool(payload: ToolPayload) -> ToolResult:
    """
    Simple tool that just echoes the payload back.
    Useful as a smoke test for the orchestration layer.
    """
    return {"echo": payload}


def uppercase_tool(payload: ToolPayload) -> ToolResult:
    """
    Expects a 'text' field in payload and returns it uppercased.
    """
    text = str(payload.get("text", ""))
    return {"original": text, "uppercased": text.upper()}


TOOL_REGISTRY: Dict[str, ToolFunc] = {
    "echo": echo_tool,
    "uppercase": uppercase_tool,
}


def execute_tool(tool_name: str, payload: ToolPayload) -> ToolResult:
    """
    Look up a tool by name and execute it with the given payload.
    Raises ValueError if tool is unknown.
    """
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        logger.error("Unknown tool", extra={"tool_name": tool_name})
        raise ValueError(f"Unknown tool: {tool_name}")

    logger.info(
        "Executing tool",
        extra={
            "tool_name": tool_name,
            "has_payload": bool(payload),
        },
    )
    result = tool(payload)
    logger.info(
        "Tool execution completed",
        extra={
            "tool_name": tool_name,
        },
    )
    return result

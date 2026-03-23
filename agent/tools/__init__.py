"""
Agent tools registry. Registers available tools and executes them by name.
"""

from __future__ import annotations

import json

from .read_file import read_file, READ_FILE_DEFINITION

# All tool definitions for Ollama (OpenAI-compatible format)
TOOL_DEFINITIONS = [READ_FILE_DEFINITION]

# Map tool name -> callable
TOOL_EXECUTORS = {
    "read_file": read_file,
}


def get_tool_definitions() -> list[dict]:
    """Return tool definitions for the Ollama API."""
    return TOOL_DEFINITIONS.copy()


def execute_tool(name: str, arguments: str | dict) -> str:
    """Execute a tool by name. Arguments can be JSON string or dict."""
    if name not in TOOL_EXECUTORS:
        return f"Error: Unknown tool '{name}'"
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON arguments for {name}"
    if not isinstance(arguments, dict):
        arguments = {}
    try:
        result = TOOL_EXECUTORS[name](**arguments)
        return str(result) if result is not None else ""
    except Exception as e:
        return f"Error executing {name}: {e}"

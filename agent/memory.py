"""
Memory module - Isolated conversation state.

Manages message history for the agent. Keeps LLM and orchestration logic
separate from how we store and recall past turns.
"""

from __future__ import annotations

import json
from typing import Any


class ConversationMemory:
    """
    Holds the conversation history for the agent.
    Messages are stored in OpenAI/Ollama format. System prompt is injected separately by the LLM layer.
    """

    def __init__(self) -> None:
        self._messages: list[dict[str, Any]] = []

    def append_user(self, content: str) -> None:
        """Append a user message."""
        self._messages.append({"role": "user", "content": content})

    def append_assistant(self, msg: dict[str, Any]) -> None:
        """Append an assistant message (may include content and/or tool_calls)."""
        self._messages.append(msg)

    def append_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        """Append a tool result message."""
        self._messages.append({
            "role": "tool",
            "name": name,
            "content": content,
            "tool_call_id": tool_call_id,
        })

    def get_messages(self) -> list[dict[str, Any]]:
        """Return the full message list for the LLM."""
        return self._messages.copy()

    def format_for_display(self) -> str:
        """Return a JSON snapshot of stored messages for inspection (does not mutate state)."""
        if not self._messages:
            return "(memory empty)"
        return json.dumps(self._messages, ensure_ascii=False, indent=2)

    def rollback_last_user(self) -> None:
        """Remove the last user message (e.g. after an error)."""
        for i in range(len(self._messages) - 1, -1, -1):
            if self._messages[i].get("role") == "user":
                self._messages.pop(i)
                return

    def commit_assistant(self, _content: str) -> None:
        """No-op: assistant message already appended in run_turn."""
        pass

    def clear(self) -> None:
        """Clear conversation history."""
        self._messages.clear()

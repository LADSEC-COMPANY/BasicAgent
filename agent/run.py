"""
Agent run loop: orchestrates LLM, memory, and tools.
"""

from __future__ import annotations

import sys
from typing import Any

from agent.identity import SYSTEM_PROMPT
from agent.llm import LLMClient
from agent.memory import ConversationMemory
from agent.tools import execute_tool, get_tool_definitions


def run_turn(
    client: LLMClient,
    memory: ConversationMemory,
) -> str:
    """
    Run one agent turn: get LLM response, execute any tool calls, repeat until done.
    Returns the final assistant message content.
    """
    max_tool_rounds = 5
    tool_round = 0

    while tool_round < max_tool_rounds:
        response = client.chat(
            messages=memory.get_messages(),
            system=SYSTEM_PROMPT,
            tools=get_tool_definitions(),
        )

        msg = response.get("message", {})
        content = msg.get("content", "").strip()
        tool_calls = msg.get("tool_calls", [])

        # Add assistant message to memory (including any tool calls)
        memory.append_assistant(msg)

        # No tool calls -> we have the final response
        if not tool_calls:
            return content

        # Execute each tool call and add results
        for tc in tool_calls:
            name = tc.get("function", {}).get("name", "")
            args_str = tc.get("function", {}).get("arguments", "{}")
            call_id = tc.get("id", "")

            result = execute_tool(name, args_str)
            memory.append_tool_result(call_id, name, result)

        tool_round += 1

    return content or "(Reached max tool rounds without final response)"


def main_loop(model: str = "llama3.2:latest") -> int:
    """CLI agent loop."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    client = LLMClient(model=model)
    memory = ConversationMemory()

    print("Local AI Agent")
    print("A helpful assistant running entirely on your computer.")
    print("Type your request and press Enter. Type 'exit' or 'quit' to stop.")
    print("Type '/memory' to print the current conversation buffer (no LLM call).")
    print("Available tools: read_file (reads a file and explains its content)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAgent ended.")
            return 0

        if user_input.lower() in {"exit", "quit"}:
            print("Agent ended.")
            return 0
        if not user_input:
            continue
        if user_input.lower() == "/memory":
            print(memory.format_for_display(), end="\n\n")
            continue

        memory.append_user(user_input)

        try:
            answer = run_turn(client, memory)
        except Exception as err:
            print(f"\nError: {err}\n")
            memory.rollback_last_user()
            continue

        memory.commit_assistant(answer)
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:latest"
    raise SystemExit(main_loop(model))

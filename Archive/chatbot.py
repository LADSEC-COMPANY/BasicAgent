#!/usr/bin/env python3
"""
Local CLI chatbot using Ollama.

Runs fully on your desktop and talks to the Ollama local API at:
http://localhost:11434
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2:latest"


def call_ollama(model: str, messages: list[dict[str, str]]) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as err:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from err

    parsed = json.loads(body)
    if "message" not in parsed or "content" not in parsed["message"]:
        raise RuntimeError(f"Unexpected Ollama response: {parsed}")

    return parsed["message"]["content"]


def main() -> int:
    # Prevent Windows code-page crashes when model returns emoji/non-ASCII text.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    print(f"Local chatbot started with model: {model}")
    print("Type your prompt and press Enter.")
    print("Type 'exit' or 'quit' to stop.\n")

    messages: list[dict[str, str]] = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Chat ended.")
            return 0
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            answer = call_ollama(model, messages)
        except RuntimeError as err:
            print(f"\nError: {err}\n")
            continue

        messages.append({"role": "assistant", "content": answer})
        print(f"Bot: {answer}\n")


if __name__ == "__main__":
    raise SystemExit(main())

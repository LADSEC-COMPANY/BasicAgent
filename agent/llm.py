"""
LLM module - Isolated Ollama API integration.

Handles all communication with the local Ollama server.
No memory, no tools: pure request/response.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2:latest"
DEFAULT_TIMEOUT = 120


def chat(
    model: str,
    messages: list[dict],
    *,
    tools: list[dict] | None = None,
    stream: bool = False,
) -> dict:
    """  Send a chat request to Ollama and return the parsed response.
    """
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if tools:
        payload["tools"] = tools

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as err:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from err

    parsed = json.loads(body)
    if "message" not in parsed:
        raise RuntimeError(f"Unexpected Ollama response: {parsed}")
    return parsed


class LLMClient:
    """
    Client for Ollama chat API. Wraps chat() with model and injects system prompt.
    """

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model

    def chat(
        self,
        messages: list[dict],
        *,
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> dict:
        """Send chat request, prepending system prompt if given."""
        msgs = list(messages)
        if system:
            msgs = [{"role": "system", "content": system}] + msgs
        return chat(
            model=self.model,
            messages=msgs,
            tools=tools,
            stream=False,
        )

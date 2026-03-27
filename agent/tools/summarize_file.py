"""
summarize_file tool: Reads a file and asks the local LLM to summarize it.
"""

from __future__ import annotations

from pathlib import Path

from agent.llm import DEFAULT_MODEL, chat

SUMMARIZE_SYSTEM = (
    "You summarize file contents for the user. Be concise: state the main purpose, "
    "key points, and structure where relevant. Match the file's language. "
    "Do not invent content that is not supported by the text."
)

DEFAULT_MAX_INPUT_CHARS = 32000


def _coerce_max_input_chars(value: object) -> int:
    """LLM/tool JSON may pass max_input_chars as str or float; normalize to int."""
    if value is None:
        return DEFAULT_MAX_INPUT_CHARS
    if isinstance(value, bool):
        return DEFAULT_MAX_INPUT_CHARS
    try:
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return DEFAULT_MAX_INPUT_CHARS
            n = int(float(s))
        else:
            n = int(value)
    except (TypeError, ValueError, OverflowError):
        return DEFAULT_MAX_INPUT_CHARS
    return n if n >= 1 else DEFAULT_MAX_INPUT_CHARS


SUMMARIZE_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "summarize_file",
        "description": (
            "Read a text file and return a concise summary of its contents. "
            "Use when the user asks for a summary, overview, or TL;DR of a file "
            "(not when they need the full raw text — use read_file for that)."
        ),
        "parameters": {
            "type": "object",
            "required": ["file_path"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to summarize (relative or absolute).",
                },
                "max_input_chars": {
                    "type": "integer",
                    "description": (
                        "Maximum characters of file content to send to the summarizer "
                        f"(default {DEFAULT_MAX_INPUT_CHARS}). Longer files are truncated."
                    ),
                },
                "model": {
                    "type": "string",
                    "description": (
                        "Ollama model name for summarization. "
                        "If omitted, the app's default model is used."
                    ),
                },
            },
        },
    },
}


def summarize_file(
    file_path: str,
    max_input_chars: int = DEFAULT_MAX_INPUT_CHARS,
    model: str | None = None,
) -> str:
    """
    Read a file and return an LLM-generated summary.

    Args:
        file_path: Path to the file.
        max_input_chars: Truncate content after this many characters.
        model: Ollama model id; defaults to DEFAULT_MODEL.

    Returns:
        Summary text, or an error message.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    if path.is_dir():
        return f"Error: Path is a directory, not a file: {file_path}"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        return f"Error: Permission denied reading: {file_path}"
    except OSError as e:
        return f"Error reading {file_path}: {e}"

    if not text.strip():
        return f"(Empty file) {path.resolve()}"

    max_input_chars = _coerce_max_input_chars(max_input_chars)

    truncated = False
    if len(text) > max_input_chars:
        text = text[:max_input_chars]
        truncated = True

    if isinstance(model, str) and not model.strip():
        model = None
    m = model or DEFAULT_MODEL
    user_content = (
        f"Filename: {path.name}\n\n{text}"
        + ("\n\n[Content truncated for length.]" if truncated else "")
    )

    try:
        resp = chat(
            m,
            [
                {"role": "system", "content": SUMMARIZE_SYSTEM},
                {"role": "user", "content": user_content},
            ],
            tools=None,
        )
    except RuntimeError as e:
        return f"Error: {e}"

    msg = resp.get("message", {})
    out = (msg.get("content") or "").strip()
    if not out:
        return "Error: Summarizer returned no text."
    return out

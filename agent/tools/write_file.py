"""
write_file tool: Writes text to a file on disk.
The agent uses this when the user asks to create or overwrite a file.
"""

from __future__ import annotations

from pathlib import Path

WRITE_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write text to a file on the filesystem. Creates parent directories if they do not exist. Overwrites the file if it already exists. Use when the user asks to create, save, or update a file.",
        "parameters": {
            "type": "object",
            "required": ["file_path", "content"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write (relative or absolute).",
                },
                "content": {
                    "type": "string",
                    "description": "Full text content to write to the file.",
                },
            },
        },
    },
}


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file (relative to workspace or absolute).
        content: Text to write.

    Returns:
        A short success message, or an error message if the write fails.
    """
    path = Path(file_path)
    if path.exists() and path.is_dir():
        return f"Error: Path is a directory, not a file: {file_path}"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    except PermissionError:
        return f"Error: Permission denied writing: {file_path}"
    except OSError as e:
        return f"Error writing {file_path}: {e}"
    return f"Successfully wrote {path.resolve()}"

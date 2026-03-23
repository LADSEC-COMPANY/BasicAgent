"""
read_file tool: Reads a file from disk and returns its contents.
The agent uses this to read files and then explains the content to the user.
"""

from __future__ import annotations

from pathlib import Path

READ_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file from the filesystem. Use this when the user asks to read, open, or explain a file. Returns the raw file content.",
        "parameters": {
            "type": "object",
            "required": ["file_path"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (relative or absolute).",
                }
            },
        },
    },
}


def read_file(file_path: str) -> str:
    """
    Read a file and return its contents.

    Args:
        file_path: Path to the file (relative to workspace or absolute).

    Returns:
        File contents as a string, or an error message if the file cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    if path.is_dir():
        return f"Error: Path is a directory, not a file: {file_path}"
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        return f"Error: Permission denied reading: {file_path}"
    except OSError as e:
        return f"Error reading {file_path}: {e}"

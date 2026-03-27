"""
list_files tool: Lists files and subdirectories in a directory.
"""

from __future__ import annotations

from pathlib import Path

LIST_FILES_DEFINITION = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List files and subdirectories in a directory on the filesystem. Use when the user asks what files exist, to browse a folder, or before reading specific files. Returns names sorted alphabetically; directories are shown with a trailing slash.",
        "parameters": {
            "type": "object",
            "required": [],
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list (relative or absolute). Defaults to the current directory if omitted.",
                },
            },
        },
    },
}


def list_files(directory_path: str = ".") -> str:
    """
    List entries in a directory.

    Args:
        directory_path: Path to the directory (relative or absolute).

    Returns:
        Sorted list of names (dirs end with /), or an error message.
    """
    path = Path(directory_path)
    if not path.exists():
        return f"Error: Path not found: {directory_path}"
    if not path.is_dir():
        return f"Error: Not a directory: {directory_path}"
    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return f"Error: Permission denied listing: {directory_path}"
    except OSError as e:
        return f"Error listing {directory_path}: {e}"

    if not entries:
        return f"(empty directory) {path.resolve()}"

    lines = []
    for p in entries:
        name = p.name
        if p.is_dir():
            lines.append(f"{name}/")
        else:
            lines.append(name)
    return "\n".join(lines)

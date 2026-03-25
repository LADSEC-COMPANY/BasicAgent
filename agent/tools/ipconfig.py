"""
ipconfig tool: Runs Windows cmd with ipconfig and returns the text output.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Any

LIST_IPCONFIG_DEFINITION = {
    "type": "function",
    "function": {
        "name": "list_ipconfig",
        "description": "Run Windows cmd.exe with the ipconfig command and return the network adapter listing (IPv4, IPv6, subnet, default gateway). Use when the user asks for IP configuration, network interfaces, or ipconfig output.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


def list_ipconfig(**_kwargs: Any) -> str:
    """
    Launch cmd and run ipconfig; return stdout/stderr as text.

    Returns:
        Command output, or an error message.
    """
    if sys.platform != "win32":
        return "Error: list_ipconfig is only available on Windows (cmd + ipconfig)."

    try:
        result = subprocess.run(
            ["cmd", "/c", "ipconfig"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "Error: ipconfig timed out."
    except OSError as e:
        return f"Error running ipconfig: {e}"

    parts: list[str] = []
    if result.stdout:
        parts.append(result.stdout.rstrip("\n"))
    if result.stderr:
        parts.append(result.stderr.rstrip("\n"))
    text = "\n".join(parts) if parts else "(no output)"

    if result.returncode != 0:
        return f"Error: ipconfig exited with code {result.returncode}.\n{text}"
    return text

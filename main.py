#!/usr/bin/env python3
"""
Local AI Agent - Entry point.

A helpful AI assistant that runs entirely on your computer, using Ollama.
Can use tools like read_file to read and explain file contents.
"""

from __future__ import annotations

import sys

from agent.run import main_loop


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:latest"
    return main_loop(model)


if __name__ == "__main__":
    raise SystemExit(main())

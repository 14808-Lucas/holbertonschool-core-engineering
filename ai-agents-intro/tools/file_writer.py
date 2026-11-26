#!/usr/bin/env python3
"""Deterministic tool that saves Markdown content to a file.

This module does not depend on the agent framework, so it can be
tested on its own and reused anywhere.
"""
from pathlib import Path


def save_markdown_file(file_path: str, content: str) -> str:
    """Save Markdown content to a file.

    Args:
        file_path: Where to save the file, for example
            "output/study_guide.md". Missing folders are created.
        content: The Markdown text to write.

    Returns:
        A message starting with "Success:" and the saved path, or
        starting with "Error:" and the reason the file was not saved.
    """
    if not isinstance(content, str) or not content.strip():
        return "Error: content is empty, nothing was saved."

    path = Path(file_path)
    if path.suffix != ".md":
        return "Error: file_path must end with .md, got {}".format(
            file_path)

    if not content.endswith("\n"):
        content += "\n"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return "Error: could not save {}: {}".format(file_path, error)

    return "Success: saved Markdown file to {}".format(path)

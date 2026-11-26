#!/usr/bin/env python3
"""Programming Learning MCP Server built with FastMCP."""
import json
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "topics.json"
MAX_RESULTS = 5

mcp = FastMCP("Programming Learning Server")


def load_topics():
    """Load and return the list of topics from data/topics.json."""
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


@mcp.tool(annotations={"readOnlyHint": True})
def search_topics(query: str) -> list[dict]:
    """Search programming topics by title or key concept.

    Args:
        query: A keyword or phrase, for example "decorators" or "closures".

    Returns:
        Up to 5 matching topics, each with its id, title, and summary.
    """
    term = query.strip().lower()
    if not term:
        raise ToolError("The search query is empty. Provide a keyword "
                        "such as 'decorators' or 'classes'.")

    matches = []
    for topic in load_topics():
        searchable = [topic["title"]] + topic["key_concepts"]
        if any(term in text.lower() for text in searchable):
            matches.append({
                "id": topic["id"],
                "title": topic["title"],
                "summary": topic["summary"],
            })

    if not matches:
        raise ToolError("No topics matched '{}'. Try a broader keyword "
                        "such as 'functions' or 'classes'.".format(query))
    return matches[:MAX_RESULTS]


if __name__ == "__main__":
    mcp.run()

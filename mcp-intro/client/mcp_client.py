#!/usr/bin/env python3
"""FastMCP client that tests the Programming Learning MCP Server."""
import asyncio
import json
from pathlib import Path

from fastmcp import Client
from fastmcp.exceptions import ToolError

SERVER_SCRIPT = (Path(__file__).resolve().parent.parent
                 / "server" / "learning_server.py")


async def check_tool_error(client, tool_name, arguments):
    """Call a tool with bad input and print the error message it returns."""
    try:
        await client.call_tool(tool_name, arguments)
        print("  UNEXPECTED: {} accepted {}".format(tool_name, arguments))
    except ToolError as error:
        print("  {}({}) -> error: {}".format(tool_name, arguments, error))


async def main():
    """Run each server check one at a time and print the results."""
    client = Client(str(SERVER_SCRIPT))
    async with client:
        print("1. Server started and connected: {}".format(
            client.is_connected()))

        tools = await client.list_tools()
        print("2. Tools listed: {}".format([tool.name for tool in tools]))

        result = await client.call_tool("search_topics",
                                        {"query": "decorators"})
        print("3. search_topics('decorators'):")
        print(json.dumps(result.data, indent=2))

        result = await client.call_tool("get_topic_details",
                                        {"topic_id": "python-decorators"})
        print("4. get_topic_details('python-decorators'):")
        print(json.dumps(result.data, indent=2))

        contents = await client.read_resource("topics://catalog")
        print("5. Resource topics://catalog ({}):".format(
            contents[0].mime_type))
        print(contents[0].text)

        print("6. Invalid inputs:")
        await check_tool_error(client, "search_topics", {"query": "rust"})
        await check_tool_error(client, "search_topics", {"query": "  "})
        await check_tool_error(client, "get_topic_details",
                               {"topic_id": "does-not-exist"})
        await check_tool_error(client, "get_topic_details",
                               {"topic_id": 42})


if __name__ == "__main__":
    asyncio.run(main())

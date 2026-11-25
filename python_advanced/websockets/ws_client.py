#!/usr/bin/env python3
"""WebSocket client: sends one message and prints the server's reply."""
import asyncio

from websockets.asyncio.client import connect


async def connect_and_send(uri: str, text: str) -> str:
    """Connect to uri, send text once, and return the single reply."""
    async with connect(uri) as websocket:
        await websocket.send(text)
        response = await websocket.recv()
    return response


async def main():
    """Send "Hello WebSocket" to the echo server and print the reply."""
    response = await connect_and_send("ws://localhost:8765", "Hello WebSocket")
    print(response, end="")


if __name__ == "__main__":
    asyncio.run(main())

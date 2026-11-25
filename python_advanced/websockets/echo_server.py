#!/usr/bin/env python3
"""WebSocket echo server: sends every message back to its sender."""
import asyncio

from websockets.asyncio.server import serve


async def connection_handler(websocket):
    """Echo each message received on this connection back to the client."""
    async for message in websocket:
        await websocket.send(message)


async def main():
    """Start the server on 127.0.0.1:8765 and run it forever."""
    server = await serve(connection_handler, "127.0.0.1", 8765)
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

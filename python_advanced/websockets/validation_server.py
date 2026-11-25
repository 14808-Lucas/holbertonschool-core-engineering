#!/usr/bin/env python3
"""WebSocket server that validates messages before replying."""
import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed


async def connection_handler(websocket):
    """Reply ERR:EMPTY to blank messages and OK:<message> to the rest."""
    try:
        async for message in websocket:
            if len(message.strip()) == 0:
                await websocket.send("ERR:EMPTY")
            else:
                await websocket.send("OK:" + message)
    except ConnectionClosed:
        pass


async def main():
    """Start the server on 127.0.0.1:8765 and run it forever."""
    server = await serve(connection_handler, "127.0.0.1", 8765)
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""WebSocket server that replies only to the client that sent a message."""
import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

connected_clients = set()


async def connection_handler(websocket):
    """Track the client and reply U:<message> to the sender only."""
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            await websocket.send("U:" + message)
    except ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)


async def main():
    """Start the server on 127.0.0.1:8765 and run it forever."""
    server = await serve(connection_handler, "127.0.0.1", 8765)
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

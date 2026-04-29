"""
{{EXERCISE_TITLE}}

Pattern C: networked with asyncio. Use this for protocol-level exercises
(heartbeats, gossip, simple consensus, request routing).

Run server:    python server.py --port 9001
Run client:    python client.py --target localhost:9001
Run all:       python run_all.py
"""

import asyncio
import json
import sys


async def handle_message(reader, writer, on_message):
    """Read newline-delimited JSON messages and call on_message for each."""
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            msg = json.loads(line.decode())
        except json.JSONDecodeError:
            continue
        response = await on_message(msg)
        if response is not None:
            writer.write((json.dumps(response) + "\n").encode())
            await writer.drain()
    writer.close()
    await writer.wait_closed()


async def send_message(host, port, msg):
    """Send a single JSON message and read one JSON response."""
    reader, writer = await asyncio.open_connection(host, port)
    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()
    line = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return json.loads(line.decode()) if line else None


# TODO: implement on_message logic for the exercise


async def main(port):
    async def on_msg(msg):
        # TODO: protocol logic here
        return {"echo": msg}

    server = await asyncio.start_server(
        lambda r, w: handle_message(r, w, on_msg),
        host="127.0.0.1",
        port=port,
    )
    print(f"listening on 127.0.0.1:{port}", flush=True)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 9001
    asyncio.run(main(port))

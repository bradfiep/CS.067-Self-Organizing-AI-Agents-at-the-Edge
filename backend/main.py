import asyncio
import json
import websockets
import NodeClass

connected_clients = set()
event_loop = None   # ✅ store the main asyncio loop safely


# -------------------------
# WebSocket handler (Frontend → Python)
# -------------------------
async def handler(websocket):
    connected_clients.add(websocket)
    print("New client connected")

    try:
        async for message in websocket:
            print(f"Received message from client: {message}")

            data = json.loads(message)
            maze = data.get("maze")
            start = data.get("start")
            end = data.get("end")

            # Send maze to Node via UDP
            NodeClass.Node.send_data(
                node.sock,
                "127.0.0.1",
                9001,
                json.dumps({
                    "type": "maze",
                    "maze": maze,
                    "start": start,
                    "end": end
                })
            )

            # Optional ACK back to frontend
            await websocket.send(json.dumps({
                "type": "ack",
                "status": "Maze sent to Node"
            }))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)


# -------------------------
# UDP Node listener (Node → Python)
# -------------------------
node = NodeClass.Node(9000, "Node1")

def on_udp_message(msg, addr):
    print(f"Node received message: {msg} from {addr}")

    # Forward Node message to all WebSocket clients
    asyncio.run_coroutine_threadsafe(
        broadcast(msg),
        event_loop
    )

# 🔴 THIS LINE IS CRITICAL
node.on_message = on_udp_message


# -------------------------
# Broadcast to all connected WebSocket clients
# -------------------------
async def broadcast(message):
    if not connected_clients:
        return

    # If message is already JSON, forward as-is
    try:
        payload = json.loads(message)
    except Exception:
        payload = {
            "type": "node_message",
            "payload": message
        }

    msg_str = json.dumps(payload)

    await asyncio.gather(
        *(ws.send(msg_str) for ws in connected_clients)
    )


# -------------------------
# Main entry point
# -------------------------
async def main():
    global event_loop
    event_loop = asyncio.get_running_loop()  # ✅ safe loop reference

    ws_server = await websockets.serve(handler, "0.0.0.0", 8080)
    udp_listener = asyncio.create_task(node.web_listen())

    print("🚀 WebSocket server running on ws://localhost:8080")

    await asyncio.gather(
        ws_server.wait_closed(),
        udp_listener
    )


if __name__ == "__main__":
    asyncio.run(main())

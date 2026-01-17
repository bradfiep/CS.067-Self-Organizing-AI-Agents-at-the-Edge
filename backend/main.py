import NodeClass
import socket

import asyncio
import json
import websockets

connected_clients = set()


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

            # Example: Send maze to Node
            NodeClass.Node.send_data(node.sock, "127.0.0.1", 9001, f"Start:{start}, End:{end}, Maze:{maze}")

            await websocket.send(json.dumps({"status": "Maze sent to Node"}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)



node = NodeClass.Node(9000, "Node1")
def on_udp_message(msg, addr):
    print(f"Node received message: {msg} from {addr}")
   
    asyncio.run_coroutine_threadsafe(
        broadcast(msg), asyncio.get_event_loop()
    )

node.on_message = on_udp_message

async def broadcast(message):
    if connected_clients:
        msg_str = json.dumps(message)
        await asyncio.gather(*(ws.send(msg_str) for ws in connected_clients))


async def main():
    ws_server = await websockets.serve(handler, "0.0.0.0", 8080)
    udp_listener = asyncio.create_task(node.web_listen())
    print("WebSocket server running on ws://localhost:8080")
    await asyncio.gather(ws_server.wait_closed(), udp_listener)

if __name__ == "__main__":
    asyncio.run(main())
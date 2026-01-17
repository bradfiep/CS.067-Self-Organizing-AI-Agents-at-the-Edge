import json
import asyncio
from NodeClass import Node

node = Node(9002, "Node2")

def handle_message(msg, addr):
    print(f"[{node.name}] Received from {addr}: {msg}")

    # Save as before
    node.save_message(msg, "node2_messages.txt")

    # 🔁 SEND MAZE BACK TO PYTHON
    response = {
        "type": "maze_update",
        "source": node.name,
        "payload": msg
    }

    node.sock.sendto(
        json.dumps(response).encode("utf-8"),
        ("127.0.0.1", 9000)  # Python Node port
    )

node.on_message = handle_message

asyncio.run(node.web_listen())

import asyncio
from NodeClass import Node

# Create Node1 that listens on port 9001
node = Node(9001, "Node1")

# This node will receive messages and forward them to Node2
def handle_message(msg, addr):
    print(f"[{node.name}] Received from {addr}: {msg}")

    # Forward to Node2 on port 9002
    target_ip = "127.0.0.1"
    target_port = 9002
    Node.send_data(node.sock, target_ip, target_port, msg)
    print(f"[{node.name}] Forwarded message to {target_ip}:{target_port}")

node.on_message = handle_message

# Run the listener forever
asyncio.run(node.web_listen())

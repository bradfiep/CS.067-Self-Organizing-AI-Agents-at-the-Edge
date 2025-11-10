import asyncio
from NodeClass import Node

# Create Node2 that listens on port 9002
node = Node(9002, "Node2")

def handle_message(msg, addr):
    print(f"[{node.name}] Received from {addr}: {msg}")

    # Save the received message to file using class function
    node.save_message(msg, "node2_messages.txt")
    print(f"[{node.name}] Saved message to node2_messages.txt")

node.on_message = handle_message

# Run the listener forever
asyncio.run(node.web_listen())
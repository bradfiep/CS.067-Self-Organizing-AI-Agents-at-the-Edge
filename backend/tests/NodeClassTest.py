import socket
import pytest
import tempfile

import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from NodeClass import Node

# Configuration constants
MULTICAST_GROUP = "224.0.0.1"

def test_node_init_prints_listening(capsys):
    """
    Creating a Node should bind the socket and print a listening message.
    """
    # New Signature: port, name, multicast_group, node_id
    node = Node(0, "TestNode", MULTICAST_GROUP, 1)
    
    # Capture stdout
    captured = capsys.readouterr()
    
    # Check for the print statement from __init__
    # Based on your diff: print(f"{self.name} listening on port {udp_port}")
    assert "TestNode listening on port" in captured.out

    # Cleanup
    node.stop()


@pytest.mark.asyncio
async def test_udp_communication_flow():
    """
    Tests that two nodes can spin up listeners and exchange a UDP message.
    """
    # 1. Initialize Nodes
    node1 = Node(0, "NodeA", MULTICAST_GROUP, 1)
    node2 = Node(0, "NodeB", MULTICAST_GROUP, 2)
    
    # Capture received messages in a list so we can assert on them
    received_msgs = []
    
    # Mock handlers to capture data
    node2.on_udp_message = lambda msg, addr: received_msgs.append(msg)

    # 2. Start Listeners
    # We use create_task because udp_listen is an infinite loop
    task1 = asyncio.create_task(node1.udp_listen())
    task2 = asyncio.create_task(node2.udp_listen())

    # Give the event loop a moment to start the servers
    await asyncio.sleep(0.1)

    # 3. Send Message (Node1 -> Node2)
    # We must retrieve the actual port Node2 was assigned (since we passed 0)
    target_port = node2.udp_port
    
    test_payload = {"type": "test", "payload": "Integration Test Message"}
    
    # Use the new send_udp method
    node1.send_udp("127.0.0.1", target_port, test_payload)

    # Wait for processing
    await asyncio.sleep(0.2)

    # 4. Assertions
    # Check if the message JSON string is in the received list
    # (The Node class decodes the JSON, so we look for the payload string)
    found = any("Integration Test Message" in msg for msg in received_msgs)
    assert found, f"NodeB did not receive the message. Received: {received_msgs}"

    # 5. Cleanup
    # Stop the nodes (sets _listening = False and closes sockets)
    node1.stop()
    node2.stop()
    
    # Cancel the asyncio tasks
    task1.cancel()
    task2.cancel()
    
    # Wait for tasks to cancel cleanly
    await asyncio.gather(task1, task2, return_exceptions=True)

def test_save_message_creates_file(tmp_path):
    """
    Test that save_message writes a message to the specified file.
    """
    file_path = tmp_path / "test_messages.txt"
    node = Node(0, "Saver", MULTICAST_GROUP, 2)

    node.save_message("Hello world", filename=str(file_path))

    with open(file_path, "r") as f:
        content = f.read()
    
    assert "Hello world" in content
    node.stop()

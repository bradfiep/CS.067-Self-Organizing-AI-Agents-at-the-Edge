import pytest
import asyncio
import sys
import os

# Ensure we can import NodeClass from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from NodeClass import Node

# Constants for testing
MULTICAST_GROUP = "224.0.0.1"

def test_node_init_prints_listening(capsys):
    """
    Creating a Node should print a listening message to stdout.
    """
    # New signature: udp_port, name, multicast_group, node_id
    # We use port 0 to let OS assign an ephemeral port
    node = Node(0, "TestNode", MULTICAST_GROUP, 1)
    
    # Capture what was printed during __init__
    captured = capsys.readouterr()
    
    # Your new code prints: "TestNode listening on port {udp_port}"
    assert "TestNode listening on port" in captured.out

    # Cleanup
    node.stop()

def test_save_message_creates_file_and_writes_content(tmp_path):
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

@pytest.mark.asyncio
async def test_udp_send_and_receive(capsys):
    """
    Verifies that a Node can send a UDP message and another Node can receive it.
    This replaces the old 'test_receive_data_success' and 'test_send_message'.
    """
    # 1. Setup two nodes
    receiver = Node(0, "Receiver", MULTICAST_GROUP, 3)
    sender = Node(0, "Sender", MULTICAST_GROUP, 4)

    # 2. Capture received messages
    received_messages = []
    receiver.on_udp_message = lambda msg, addr: received_messages.append(msg)

    # 3. Start the receiver listening loop
    # We use a task so it runs in the background
    listen_task = asyncio.create_task(receiver.udp_listen())
    
    # Allow the loop to start
    await asyncio.sleep(0.1)

    # 4. Send a message from Sender to Receiver
    # We need the actual port the receiver was assigned
    target_port = receiver.udp_port
    payload = {"type": "ping", "data": "test_payload"}
    
    # Use the class's send_udp method
    sender.send_udp("127.0.0.1", target_port, payload)

    # 5. Wait for message processing
    await asyncio.sleep(0.2)

    # 6. Verify
    # Check if we captured the message
    # Note: The Node class likely converts the dict to a string or keeps it as dict depending on your implementation.
    # We check if the payload string exists in the captured logs/messages.
    assert len(received_messages) > 0
    # Convert the first received message to string to search in it (in case it's a dict)
    assert "test_payload" in str(received_messages[0])

    # 7. Cleanup
    receiver.stop()
    sender.stop()
    listen_task.cancel()
    
    try:
        await listen_task
    except asyncio.CancelledError:
        pass

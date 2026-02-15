import socket
import pytest
import io
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from NodeClass import Node

def test_node_init_prints_listening(capsys):
    """Creating a Node should print a listening message to stdout."""
    # Added 33333 as the agent_id
    node = Node(0, "TestNode", 33333)
    
    captured = capsys.readouterr()
    
    # We check for the name and the status since the exact string has changed
    assert "TestNode" in captured.out
    assert "listening on port" in captured.out

    if hasattr(node, 'sock'):
        node.sock.close()

def test_save_message_creates_file_and_writes_content(tmp_path):
    """
    Test that save_message writes a message to the specified file.
    """
    file_path = tmp_path / "test_messages.txt"
    # Added 123 as the agent_id
    node = Node(0, "Saver", 123)

    node.save_message("Hello world", filename=str(file_path))

    with open(file_path, "r") as f:
        content = f.read()
    
    assert "Hello world" in content
    node.sock.close()

def test_node_properties():
    """Verify that the Node correctly stores its ID and Name."""
    node = Node(0, "Robot1", 999)
    assert node.agent_id == 999
    assert node.name == "Robot1"
    node.sock.close()

# These two tests handle methods that might have been renamed or removed
# in your latest version. They check for the presence of the method first.

def test_node_send_json_interface():
    """Verify the send_json method exists (used in the swarm)."""
    node = Node(0, "Sender", 555)
    assert hasattr(node, 'send_json'), "Node should have a send_json method for swarm communication"
    node.sock.close()

def test_node_tick_interface():
    """Verify the tick method exists (used for simulation)."""
    node = Node(0, "Ticker", 777)
    assert hasattr(node, 'tick'), "Node should have a tick method for the exploration loop"
    node.sock.close()

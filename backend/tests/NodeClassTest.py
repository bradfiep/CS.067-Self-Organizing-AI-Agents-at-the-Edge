import socket
import pytest
import tempfile

import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from NodeClass import Node


def test_node_init_prints_listening(capsys):
    """Creating a Node should print a listening message to stdout."""
    # Use port 0 so the OS assigns an ephemeral port and we avoid collisions
    node = Node(0, "TestNode", 33333)
    # capture what was printed during __init__
    captured = capsys.readouterr()
    assert "TestNode listening on port" in captured.out

    # cleanup socket created by Node.__init__
    try:
        node.sock.close()
    except Exception:
        print(f"Could not close TestNode socket")
        pass


def test_node_listen_prints_socket_bound(capsys):
    """Calling node_listen should create and bind a UDP socket and print a message."""
    node = Node(0, "TmpNode")
    capsys.readouterr()  

    sock = node.node_listen(0)
    captured = capsys.readouterr()

    assert "Socket bound to port" in captured.out

    # cleanup created sockets
    try:
        sock.close()
    except Exception:
        print(f"Could not close socket bound to port 0")
        pass
    try:
        node.sock.close()
    except Exception:
        print(f"Could not close TmpNode socket")
        pass


def test_receive_data_success(capsys):
    """Node.receive_data should return decoded message and sender address."""
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver = Node(0, "Receiver")
    port = receiver.sock.getsockname()[1]

    sender.sendto(b"Ping", ("127.0.0.1", port))
    msg, addr = Node.receive_data(receiver.sock)

    captured = capsys.readouterr()
    assert msg == "Ping"
    assert "Received message from" in captured.out
    assert addr[0] == "127.0.0.1"

    sender.close()
    receiver.sock.close()


def test_send_message(monkeypatch):
    captured_output = io.StringIO()
    sys.stdout = captured_output
    node = Node(6000, "Node1")
    sock = node.node_listen(6000)
    Node.send_data(sock, "127.0.0.1", 6000, "Hello")

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert "Sent message to 127.0.0.1:6000" in output
    sock.close()


def test_save_message_creates_file_and_writes_content(tmp_path):
    """Test that save_message writes a message to the specified file."""
    file_path = tmp_path / "test_messages.txt"
    node = Node(0, "Saver")

    node.save_message("Hello world", filename=str(file_path))

    with open(file_path, "r") as f:
        content = f.read()
    assert "Hello world" in content
    node.sock.close()
import socket
import pytest

from NodeClass import Node


def test_node_init_prints_listening(capsys):
    """Creating a Node should print a listening message to stdout."""
    # Use port 0 so the OS assigns an ephemeral port and we avoid collisions
    node = Node(0, "TestNode")
    # capture what was printed during __init__
    captured = capsys.readouterr()
    assert "TestNode listening on port" in captured.out

    # cleanup socket created by Node.__init__
    try:
        node.sock.close()
    except Exception:
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
        pass
    try:
        node.sock.close()
    except Exception:
        pass

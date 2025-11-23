import socket
from NodeClass import Node

# In progress doesn't work to recive brodcasts to more then one node 



listener_node = Node(9005, "ListenerNode")


# Create and configure the socket to receive multicast/broadcast
sock = listener_node.node_listen(5008, multicast_group='224.1.1.1', listen_broadcast=True)
print(f"[{listener_node.name}] Listening for broadcasts on multicast group 224.1.1.1:5008")

try:
    while True:
        data, addr = sock.recvfrom(4096)
        try:
            msg = data.decode('utf-8')
        except Exception:
            msg = repr(data)
        print(f"[{listener_node.name}] Received: {msg} from {addr}")
except KeyboardInterrupt:
    print("Stopping listener...")
finally:
    try:
        sock.close()
    except Exception:
        pass
    try:
        listener_node.sock.close()
    except Exception:
        pass

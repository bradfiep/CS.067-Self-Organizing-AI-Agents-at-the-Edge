#Node class: creates a node that can 
#both listen and send messages

import socket

class Node:
    def __init__(self, port, name):
        self.port = port
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))
        print(f"{self.name} listening on port {port}")
        self.on_message = lambda msg, addr: None

    def node_listen(portnumber):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", portnumber))
            print(f"Socket bound to port {portnumber}")
        except socket.error as err:
            print(f"Socket creation failed with error {err}")
        return sock

    def send_data(sock, ip, portnumber, message):
        try:
            sock.sendto(message.encode('utf-8'), (ip, portnumber))
            print(f"Sent message to {ip}:{portnumber}")
        except socket.error as err:
            print(f"Failed to send data: {err}")
            
    def receive_data(sock):
        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received message from {addr}")
            return data.decode('utf-8'), addr
        except socket.error as err:
            print(f"Failed to receive data: {err}")
            return None, None


def main():
    node1_sock = Node.node_listen(5000)
    node2_sock = Node.node_listen(5001)

    print("\n[Mock] Webpage -> Node1")
    Node.send_data(node1_sock, "127.0.0.1", 5000, "Meow")

    msg1, addr1 = Node.receive_data(node1_sock)
    if msg1:
        print(f"Node1 processed message: {msg1}")
        print("Node1 Forwarding to Node2...")
        Node.send_data(node1_sock, "127.0.0.1", 5001, msg1)

    msg2, addr2 = Node.receive_data(node2_sock)
    if msg2:
        print(f"Node2 final received message: {msg2}")

if __name__ == "__main__":
    main()
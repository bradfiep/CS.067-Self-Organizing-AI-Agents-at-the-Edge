# Node class: creates a node that can both listen and send messages
import socket
import asyncio
import struct

class Node:
    def __init__(self, port, name, multicast_group='224.1.1.1', multicast_port=5007):
        self.port = port
        self.name = name
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        
        # Regular unicast socket for direct communication
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))
        print(f"{self.name} listening on port {port}")
        
        # Multicast socket for broadcast listening
        self.multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.multicast_sock.bind(('', multicast_port))
        
        # Join multicast group
        group = socket.inet_aton(multicast_group)
        mreq = group + socket.inet_aton('0.0.0.0')
        self.multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        print(f"{self.name} also listening to multicast group {multicast_group}:{multicast_port}")
        
        self.on_message = lambda msg, addr: None

    async def web_listen(self):
        """Listen for unicast messages"""
        loop = asyncio.get_event_loop()
        while True:
            data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 1024)
            msg = data.decode('utf-8')
            print(f"[{self.name}] Received unicast: {msg} from {addr}")
            self.on_message(msg, addr)

    async def multicast_listen(self):
        """Listen for multicast/broadcast messages"""
        loop = asyncio.get_event_loop()
        while True:
            data, addr = await loop.run_in_executor(None, self.multicast_sock.recvfrom, 1024)
            msg = data.decode('utf-8')
            print(f"[{self.name}] Received broadcast: {msg} from {addr}")
            self.on_message(msg, addr)

    def send_data(self, ip, portnumber, message):
        """Send data to specified IP and port"""
        try:
            self.sock.sendto(message.encode('utf-8'), (ip, portnumber))
            print(f"Sent message to {ip}:{portnumber}")
        except socket.error as err:
            print(f"Failed to send data: {err}")
            
    def broadcast_event(self, event_message):
        """Broadcast to all nodes in the multicast group"""
        print(f"Broadcasting event: {event_message}")
        try:
            # Create a temporary socket for sending multicast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            
            # Send to the multicast group and port that all nodes are listening on
            sock.sendto(event_message.encode('utf-8'), (self.multicast_group, self.multicast_port))
            print(f"Event broadcasted to {self.multicast_group}:{self.multicast_port}")
        except socket.error as err:
            print(f"Failed to broadcast event: {err}")
        finally:
            sock.close()

    def save_message(self, msg, filename="received_messages.txt"):
        with open(filename, "a") as f:
            f.write(f"{msg}\n")
            
if __name__ == "__main__":
    main()
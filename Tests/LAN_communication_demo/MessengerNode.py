import socket


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

if __name__ == "__main__":

    #while both nodes have the functionality to send and receive data,
    #this node currently only sends data.

    message = "One small step for man , one giant leap for mankind."
    portnumber = 12345
    sock = node_listen(portnumber)
    send_data(sock, "127.0.0.1", portnumber, message)

    

#Node class: creates a node that can 
#both listen and send messages
import socket
import asyncio
from collections import deque
import json

class Node:
    def __init__(self, udp_port, name, multicast_group, node_id):
        self.name = name
        self.udp_port = udp_port
        self.multicast_group = multicast_group
        self.node_id = node_id
        self._listening = False

        #saved list of visited rows, col
        self.visited = set()
        #dfs path uses path as a stack to search maze
        self.StackPath = []
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_sock.bind(("", udp_port))
        print(f"{self.name} listening on port {udp_port}")
        self.on_message = lambda msg, addr: None

        #get port if not specified
        if udp_port == 0:
            self.udp_port = self.udp_sock.getsockname()[1]
        
        #message handler setup
        self.on_udp_message = lambda msg, addr: None


        print(f"\n{self.name} (ID: {self.node_id})")
        print(f"  UDP listening on port {self.udp_port}")
        print(f"  Multicast group: {self.multicast_group}\n")


    #use simple stack for depth first search exploration

    def dfs (self, row, col, maze, endpoint):
        if(row < 0 or row >=  len(maze) or
            col < 0 or col >=  len(maze) or 
            maze[row][col] == 1 ):
            return False 
        #add current location to visited and StackPath
        if (row, col) in self.visited:
            return False
            
        self.visited.add((row, col))
        self.StackPath.append((row, col))
        
        #check if endpoint is reached
        if (row, col) == endpoint:
            return True

        for row_direction, col_direction in [(-1, 0), (1,0), (0,-1), (0,1)]:
            #recursive call to search diretions for endpoint
            if self.dfs(row + row_direction, col + col_direction, maze, endpoint):
                #if any of the directions are true return true
                return True 
        
        #if still in function reached dead end so
        self.StackPath.pop()
        return False
    
    def printdfs(self, row, col, maze, endpoint):
        if self.dfs(row, col, maze, endpoint):
            print('nodes visited: ', self.visited, 'path: ', self.StackPath)
        else:
            print('error')   

    
    def bfs (self, start, maze, endpoint):
        rows, cols = len(maze), len(maze[0])
        queue = deque()
        queue.append((start, [start]))
        self.visited = set()
        while queue:
            (row, col), path = queue.popleft()
            if (row, col) in self.visited:
                continue
            self.visited.add((row, col))
            #means goal reached
            if (row, col) == endpoint:
                self.StackPath = path
                return True
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = row + dr, col + dc
                if (
                    0 <= nr < rows and
                    0 <= nc < cols and
                    maze[nr][nc] == 0 and
                    (nr, nc) not in self.visited
                ):
                    queue.append(((nr, nc), path + [(nr, nc)]))
        return False

    #UDP comunication functions

    async def udp_listen(self):
        loop = asyncio.get_event_loop()
        self._listening = True

        # Set the timeout on the underlying socket
        self.udp_sock.settimeout(1.0)
        try:
            while self._listening:
                try:
                    data, addr = await loop.run_in_executor(None, self.udp_sock.recvfrom, 1024)
                except socket.timeout:
                    continue
                msg = data.decode('utf-8')
                self.on_udp_message(msg, addr)
               

        except (OSError, asyncio.CancelledError):
            # This catch allows the coroutine to return cleanly
            pass
        finally:
            self._listening = False


    #udp send function
    def send_udp(self, ip, port: int, data: dict):

        try:
            data["sender_ID"] = self.node_id
            data["sender_name"] = self.name
            # data{"timestamp"} = asyncio.get_event_loop().time()

            #could add encryption herewith .encode("utf-8")
            message = json.dumps(data).encode("utf-8")
            self.udp_sock.sendto(message, (ip, port))
        
        except Exception as e:
            print(f"Error sending UDP message: {e}")
            return False

    #UDP broadcast to group

    def broadcast_udp(self, port: int, data: dict):

        #if no port specified use node's udp port
        if port == 0:
            port = self.udp_port
        
        #prepare udp data packet
        data["sender_ID"] = self.node_id
        data["sender_name"] = self.name
        data["timestamp"] = asyncio.get_event_loop().time()

        try:
            #set TTL for multicast
            self.udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            
            message = json.dumps(data).encode("utf-8")
            self.udp_sock.sendto(message, (self.multicast_group, port))
            return True

        except Exception as e:
            print(f"Error broadcasting UDP message: {e}")
            return False

    async def start(self):
        udp_task = asyncio.create_task(self.udp_listen())
        
        await self.announce_presence()
        
        return udp_task
    
    async def announce_presence(self):
        """Announce node presence to network"""
        # Broadcast via UDP
        self.broadcast_udp({
            'type': 'node_join',
            'node_id': self.node_id,
            'name': self.name,
            'udp_port': self.udp_port})
    
    #stop function
    def stop(self):
        self._listening = False
        
        if self.udp_sock:
            self.udp_sock.close()
        
        print(f"node name: {self.name} broadcast/listening stopped.")
        




    def save_message(self, msg, filename="received_messages.txt"):
        with open(filename, "a") as f:
            f.write(f"{msg}\n")

    def send_json(self, ip, port, payload: dict):
        message = json.dumps(payload)
        self.udp_sock.sendto(message.encode("utf-8"), (ip, port))
 
def main():
    
    # Simple test: create two nodes, start listeners, send a UDP message,
    # and print received messages to the console.
    async def test_udp():
        node1 = Node(0, "NodeA", "224.0.0.1", "01")
        node2 = Node(0, "NodeB", "224.0.0.1", "02")

        # set message handlers to print received messages
        node1.on_udp_message = lambda msg, addr: print(f"[{node1.name}] Received: {msg} from {addr}")
        node2.on_udp_message = lambda msg, addr: print(f"[{node2.name}] Received: {msg} from {addr}")

        # start listeners
        task1 = asyncio.create_task(node1.udp_listen())
        task2 = asyncio.create_task(node2.udp_listen())

        # give listeners a moment to start
        await asyncio.sleep(0.1)

        # send a message from node1 to node2 (unicast to localhost)
        node1.send_udp("127.0.0.1", node2.udp_port, {"type": "test", "payload": "hello from node1"})

        # wait to ensure message is received and printed
        await asyncio.sleep(0.5)

        # cleanup: cancel listener tasks and close sockets
        # In your test_udp function:
        await asyncio.sleep(0.5)

        # 1. STOP the nodes first (this closes the sockets)
        node1.stop()
        node2.stop()

        # 2. NOW cancel the tasks
        task1.cancel()
        task2.cancel()

        # 3. Gather them to let the loop clean up
        await asyncio.gather(task1, task2, return_exceptions=True)

        return

         
    try:
        asyncio.run(test_udp())
    finally:
        print("UDP test completed.")


if __name__ == "__main__":
    main()
    print("NodeClass module test finished.")
#Node class: creates a node that can 
#both listen and send messages
import socket
import asyncio
from collections import deque

class Node:
    def __init__(self, port, name):
        self.port = port
        self.name = name
        #saved list of visited rows, col
        self.visited = set()
        #dfs path uses path as a stack to search maze
        self.StackPath = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))
        print(f"{self.name} listening on port {port}")
        self.on_message = lambda msg, addr: None



    #use simple stack for depth first search exploration

    def dfs (self, row, col, maze, endpoint):
        if(row < 0 or row >=  len(maze) or
            col < 0 or col >=  len(maze) or 
            maze[row][col] == 1):
            return False 
        #add current location to visited and StackPath

        self.visited.add (row, col)
        self.StackPath.append (row, col)

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

    #messaging functions

    async def web_listen(self):
        loop = asyncio.get_event_loop()
        while True:
            data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 1024)
            msg = data.decode('utf-8')
            print(f"[{self.name}] Received: {msg} from {addr}")
            self.on_message(msg, addr)

    def node_listen(self, portnumber):
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

    def save_message(self, msg, filename="received_messages.txt"):
        with open(filename, "a") as f:
            f.write(f"{msg}\n")
 
def main():
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]

    start = (0, 0)
    end = (4, 4)

    node = Node(port=0, name="TestNode")

    # print("\n--- DFS TEST ---")
    # node.visited.clear()
    # node.StackPath.clear()
    # if node.dfs(start[0], start[1], maze, end):
    #     print("DFS path found:")
    #     print(node.StackPath)
    # else:
    #     print("DFS failed")

    print("\n--- BFS TEST ---")
    node.visited.clear()
    node.StackPath.clear()
    if node.bfs(start, maze, end):
        print("BFS shortest path found:")
        print(node.StackPath)
    else:
        print("BFS failed")


if __name__ == "__main__":
    main()
"""
NodeClass.py: Agent implementation for Fixed-Size Swarm with Frontier-Based Exploration

Each agent:
1. Maintains a local_map of visited nodes and edges
2. Identifies frontiers (unexplored but reachable nodes)
3. Communicates via UDP to share map updates
4. Uses a tick() state machine to scan, broadcast, listen, decide, and move
5. Collaboratively explores the maze by claiming unique frontiers
"""

import socket
import asyncio
import json
from collections import deque
from typing import Set, Tuple, List, Dict, Optional
import math


class Node:
    """
    Agent node for swarm-based maze exploration.
    
    Data structures:
    - local_map: Dict mapping (x,y) to set of neighboring coordinates
    - frontiers: List of unexplored (x,y) coordinates adjacent to known nodes
    - target_frontier: Current (x,y) frontier this agent is moving toward
    - claimed_frontiers: Set of frontiers claimed by any agent
    """
    
    def __init__(self, port: int, name: str, agent_id: int):
        """
        Initialize a swarm agent.
        
        Args:
            port: UDP port for this agent
            name: Human-readable name
            agent_id: Unique numeric identifier
        """
        self.port = port
        self.name = name
        self.agent_id = agent_id
        
        # Core data structures
        self.local_map: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        self.frontiers: List[Tuple[int, int]] = []
        self.target_frontier: Optional[Tuple[int, int]] = None
        self.claimed_frontiers: Set[Tuple[int, int]] = set()
        
        # Current position
        self.current_position: Optional[Tuple[int, int]] = None
        
        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        print(f"{self.name} (Agent_{self.agent_id}) listening on port {port}")
        
        # Message handler callback
        self.on_message = lambda msg, addr: None
        
        # For tracking other agents' ports (populated externally)
        self.peer_ports: List[int] = []
        
        # Stuck detection
        self.stuck_counter: int = 0
    
    def set_initial_position(self, position: Tuple[int, int]):
        """Set the agent's starting position and initialize local_map."""
        self.current_position = position
        self.local_map[position] = set()
        print(f"{self.name} starting at {position}")
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _select_best_frontier(self) -> Optional[Tuple[int, int]]:
        """
        Select a frontier to explore using jiggle logic.
        
        Strategy:
        1. Find top 3 nearest unclaimed frontiers
        2. Randomly pick one (prevents deterministic clumping)
        3. If no unclaimed, pick a random claimed frontier (helps break deadlock)
        4. If no frontiers at all, return None
        
        Returns:
            (x,y) of a selected frontier, or None if no frontiers exist
        """
        import random
        
        if not self.frontiers:
            return None
        
        # Filter to unclaimed frontiers
        unclaimed = [f for f in self.frontiers if f not in self.claimed_frontiers]
        
        if unclaimed:
            # Find top 3 nearest unclaimed frontiers
            sorted_unclaimed = sorted(unclaimed, key=lambda f: self._manhattan_distance(self.current_position, f))
            top_3 = sorted_unclaimed[:min(3, len(sorted_unclaimed))]
            # Randomly pick one of the top 3
            return random.choice(top_3)
        else:
            # No unclaimed frontiers - pick random claimed one to help break deadlock
            if self.frontiers:
                return random.choice(self.frontiers)
            return None
    
    def _move_toward_target(self) -> Tuple[int, int]:
        """
        Calculate the next step toward target_frontier using Manhattan distance.
        Prefers moving horizontally first, then vertically.
        Detects when stuck and forces exploration of new frontiers.
        
        Returns:
            New (x,y) position (may be same as current if blocked)
        """
        import random
        
        if not self.target_frontier or not self.current_position:
            return self.current_position
        
        cx, cy = self.current_position
        tx, ty = self.target_frontier
        
        # Decide which direction to move
        if cx < tx:
            new_pos = (cx + 1, cy)
        elif cx > tx:
            new_pos = (cx - 1, cy)
        elif cy < ty:
            new_pos = (cx, cy + 1)
        elif cy > ty:
            new_pos = (cx, cy - 1)
        else:
            # Already at target
            return self.current_position
        
        # Check if we actually moved
        if new_pos == self.current_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        
        # If stuck too long, pick a random frontier to escape deadlock
        if self.stuck_counter > 5:
            if self.frontiers:
                self.target_frontier = random.choice(self.frontiers)
                self.stuck_counter = 0
        
        return new_pos
    
    def _is_wall(self, cell_value: int) -> bool:
        """Check if a cell value represents a wall (1 = wall)."""
        return cell_value == 1
    
    def _scan_neighbors(self, local_grid_view: List[List[int]]) -> List[Tuple[int, int]]:
        """
        Scan 4-neighbors in the local grid view and identify frontiers.
        Updates local_map and returns list of new frontiers found.
        
        Args:
            local_grid_view: 2D array where 0=open, 1=wall
        
        Returns:
            List of new frontier coordinates
        """
        if not self.current_position:
            return []
        
        new_frontiers = []
        cx, cy = self.current_position
        rows, cols = len(local_grid_view), len(local_grid_view[0])
        
        # Ensure current position is in local_map
        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()
        
        # Check 4 neighbors (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            
            # Bounds check
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            
            cell = local_grid_view[nx][ny]
            
            # Skip walls
            if self._is_wall(cell):
                continue
            
            # Check if this is a new frontier (neighbor not yet in local_map)
            if (nx, ny) not in self.local_map:
                # This is a frontier - reachable but unexplored
                if (nx, ny) not in self.frontiers:
                    self.frontiers.append((nx, ny))
                    new_frontiers.append((nx, ny))
            else:
                # Already explored, just update edges
                self.local_map[self.current_position].add((nx, ny))
                self.local_map[(nx, ny)].add(self.current_position)
        
        return new_frontiers
    
    def _broadcast_map_update(self, new_nodes: List[Tuple[int, int]], new_frontiers: List[Tuple[int, int]]):
        """
        Broadcast map update via UDP to all peer agents.
        
        Args:
            new_nodes: List of newly discovered nodes
            new_frontiers: List of newly discovered frontiers
        """
        if not new_nodes and not new_frontiers:
            return
        
        payload = {
            "type": "MERGE",
            "sender_id": self.agent_id,
            "sender_name": self.name,
            "nodes": new_nodes,
            "frontiers": new_frontiers
        }
        
        for peer_port in self.peer_ports:
            if peer_port != self.port:  # Don't send to self
                try:
                    self.send_json("127.0.0.1", peer_port, payload)
                except Exception as e:
                    print(f"{self.name} failed to send to port {peer_port}: {e}")
    
    def _broadcast_frontier_claim(self, frontier: Tuple[int, int]):
        """
        Broadcast frontier claim via UDP to all peer agents.
        
        Args:
            frontier: The (x,y) frontier being claimed
        """
        payload = {
            "type": "CLAIM",
            "sender_id": self.agent_id,
            "sender_name": self.name,
            "target_frontier": frontier
        }
        
        for peer_port in self.peer_ports:
            if peer_port != self.port:  # Don't send to self
                try:
                    self.send_json("127.0.0.1", peer_port, payload)
                except Exception as e:
                    print(f"{self.name} failed to send CLAIM to port {peer_port}: {e}")
    
    def _process_merge_packet(self, payload: Dict):
        """
        Process incoming MERGE packet and integrate remote agent's map.
        
        Args:
            payload: Dictionary with 'nodes' and 'frontiers'
        """
        sender = payload.get("sender_name", "Unknown")
        
        # Merge nodes into local_map
        for node in payload.get("nodes", []):
            node_tuple = tuple(node) if isinstance(node, list) else node
            if node_tuple not in self.local_map:
                self.local_map[node_tuple] = set()
        
        # Merge frontiers
        for frontier in payload.get("frontiers", []):
            frontier_tuple = tuple(frontier) if isinstance(frontier, list) else frontier
            if frontier_tuple not in self.frontiers:
                self.frontiers.append(frontier_tuple)
        
        print(f"{self.name} merged data from {sender}: {len(payload.get('nodes', []))} nodes, {len(payload.get('frontiers', []))} frontiers")
    
    def _process_claim_packet(self, payload: Dict):
        """
        Process incoming CLAIM packet and update claimed frontiers.
        
        Args:
            payload: Dictionary with 'target_frontier'
        """
        sender = payload.get("sender_name", "Unknown")
        frontier = payload.get("target_frontier")
        
        if frontier:
            frontier_tuple = tuple(frontier) if isinstance(frontier, list) else frontier
            self.claimed_frontiers.add(frontier_tuple)
            print(f"{self.name} recorded frontier claim from {sender}: {frontier_tuple}")
    
    def tick(self, local_grid_view: List[List[int]]):
        """
        State machine tick for the agent.
        
        Sequence:
        1. CLEANUP: Remove explored positions from frontier list
        2. SCAN: Look at neighbors and identify frontiers
        3. BROADCAST: Send new discoveries to peers
        4. LISTEN: Process incoming UDP messages (done asynchronously)
        5. DECIDE: Choose next frontier if needed
        6. MOVE: Take one step toward target frontier
        
        Args:
            local_grid_view: 2D array of the agent's surroundings (0=open, 1=wall)
        """
        # CLEANUP: Ensure current position is in local_map
        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()
        
        # CLEANUP: Remove explored positions from frontier list (zombie frontier fix)
        self.frontiers = [f for f in self.frontiers if f not in self.local_map]
        
        # Check if target_frontier has been reached
        if self.target_frontier == self.current_position:
            self.target_frontier = None
        
        # SCAN: Identify new frontiers
        new_frontiers = self._scan_neighbors(local_grid_view)
        new_nodes = list(self.local_map.keys())  # All discovered nodes
        
        # BROADCAST: Send updates
        self._broadcast_map_update(new_nodes, new_frontiers)
        
        # LISTEN: Process any pending messages
        # (This would be called from async handler in real implementation)
        
        # DECIDE: Select frontier if needed
        if self.target_frontier is None or self.target_frontier in self.claimed_frontiers:
            selected = self._select_best_frontier()
            if selected:
                self.target_frontier = selected
                self._broadcast_frontier_claim(selected)
                print(f"{self.name} selected frontier {selected}")
        
        # MOVE: Take one step toward target
        if self.target_frontier:
            new_pos = self._move_toward_target()
            if new_pos != self.current_position:
                self.current_position = new_pos
                print(f"{self.name} moved to {new_pos}")
            else:
                # Reached frontier or stuck
                if new_pos == self.target_frontier:
                    print(f"{self.name} reached target frontier {self.target_frontier}")
                    self.target_frontier = None
    
    def process_message(self, msg: str):
        """
        Process a received message.
        
        Args:
            msg: JSON string containing packet
        """
        try:
            payload = json.loads(msg)
            msg_type = payload.get("type")
            
            if msg_type == "MERGE":
                self._process_merge_packet(payload)
            elif msg_type == "CLAIM":
                self._process_claim_packet(payload)
            else:
                print(f"{self.name} received unknown message type: {msg_type}")
        
        except json.JSONDecodeError as e:
            print(f"{self.name} failed to parse message: {e}")
    
    # UDP communication methods
    
    async def web_listen(self):
        """Asynchronously listen for incoming UDP messages."""
        loop = asyncio.get_event_loop()
        while True:
            try:
                data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 1024)
                msg = data.decode('utf-8')
                print(f"[{self.name}] Received from {addr}: {msg}")
                self.process_message(msg)
                self.on_message(msg, addr)
            except Exception as e:
                print(f"{self.name} error in web_listen: {e}")
    
    def send_json(self, ip: str, port: int, payload: dict):
        """
        Send a JSON payload via UDP.
        
        Args:
            ip: Target IP address
            port: Target port
            payload: Dictionary to send as JSON
        """
        try:
            message = json.dumps(payload)
            self.sock.sendto(message.encode("utf-8"), (ip, port))
        except Exception as e:
            print(f"{self.name} failed to send JSON: {e}")
    
    def save_message(self, msg: str, filename: str = "received_messages.txt"):
        """Save a message to file for debugging."""
        try:
            with open(filename, "a") as f:
                f.write(f"{self.name}: {msg}\n")
        except Exception as e:
            print(f"{self.name} failed to save message: {e}")

def main():
    """Test the Node class with frontier-based exploration."""
    
    # Test maze
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]
    
    start = (0, 0)
    
    # Create a test agent
    agent = Node(port=9000, name="TestAgent", agent_id=1)
    agent.set_initial_position(start)
    
    # Simulate a tick with a local grid view
    print("\n--- FRONTIER-BASED EXPLORATION TEST ---")
    
    # Local view from starting position
    local_view = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0]
    ]
    
    print(f"\nTick 1:")
    agent.tick(local_view)
    print(f"Local map: {agent.local_map}")
    print(f"Frontiers: {agent.frontiers}")
    print(f"Target frontier: {agent.target_frontier}")
    
    print(f"\nTick 2 (simulating movement):")
    agent.current_position = (0, 1)
    local_view_2 = [
        [0, 0, 0],
        [1, 0, 1],
        [0, 0, 1]
    ]
    agent.tick(local_view_2)
    print(f"Local map: {agent.local_map}")
    print(f"Frontiers: {agent.frontiers}")


if __name__ == "__main__":
    main()
    print("NodeClass module test finished.")
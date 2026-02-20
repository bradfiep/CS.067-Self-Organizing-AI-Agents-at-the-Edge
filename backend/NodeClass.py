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
        # Map frontier coord -> agent_id that claimed it (lowest ID wins)
        self.claimed_frontiers: Dict[Tuple[int, int], int] = {}
        
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
    
    def _get_bfs_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate true path distance using BFS on the local_map.
        
        This solves the 'Commute Problem': frontiers that look close in Manhattan distance
        but require walking around walls are now properly evaluated at their true cost.
        
        Args:
            pos1: Starting position
            pos2: Target position (usually a frontier)
        
        Returns:
            Number of steps to reach pos2 from pos1 through known map.
            Returns 999999 if pos2 is unreachable.
        """
        if pos1 == pos2:
            return 0
        
        # BFS queue: stores (current_pos, distance)
        queue = deque([(pos1, 0)])
        visited = {pos1}
        
        # Directions: North, South, East, West
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current, distance = queue.popleft()
            
            # Check if we reached the target
            if current == pos2:
                return distance
            
            cx, cy = current
            
            # Explore 4-way grid neighbors
            for dx, dy in directions:
                neighbor = (cx + dx, cy + dy)
                
                if neighbor not in visited:
                    # Valid path rule: neighbor must be in local_map OR be the exact target
                    if neighbor in self.local_map or neighbor == pos2:
                        visited.add(neighbor)
                        queue.append((neighbor, distance + 1))
        
        # No path found to target - unreachable
        return 999999
    
    
    def _select_best_frontier(self) -> Optional[Tuple[int, int]]:
        """
        Select a frontier to explore using jiggle logic with BFS distance.
        
        Strategy:
        1. Find top 3 nearest unclaimed frontiers (using true path distance via BFS)
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
            # Find top 3 nearest unclaimed frontiers using TRUE path distance (BFS)
            sorted_unclaimed = sorted(unclaimed, key=lambda f: self._get_bfs_distance(self.current_position, f))
            top_3 = sorted_unclaimed[:min(3, len(sorted_unclaimed))]
            # Randomly pick one of the top 3 (jiggle logic prevents deterministic clumping)
            return random.choice(top_3)
        else:
            # No unclaimed frontiers - pick random claimed one to help break deadlock
            if self.frontiers:
                return random.choice(self.frontiers)
            return None
    
    def _find_next_step_bfs(self, target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Use BFS on local_map to find the next immediate step toward target.
        """
        if target == self.current_position:
            return None
        
        # BFS queue: stores (current_pos, path_to_reach_it)
        queue = deque([(self.current_position, [self.current_position])])
        visited = {self.current_position}
        
        # Directions: North, South, West, East
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current, path = queue.popleft()
            
            # Check if we reached the target
            if current == target:
                # Return the first step in the path (index 1)
                if len(path) > 1:
                    return path[1]
                return None
            
            cx, cy = current
            
            # Explore 4-way grid neighbors
            for dx, dy in directions:
                neighbor = (cx + dx, cy + dy)
                
                if neighbor not in visited:
                    # VALID PATH RULE:
                    # We can walk on it IF it is a fully explored node (in local_map)
                    # OR if it is the exact target frontier we are trying to step onto.
                    if neighbor in self.local_map or neighbor == target:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        
        # No path found to target
        return None
    
    def _move_toward_target(self) -> Tuple[int, int]:
        """
        Calculate the next step toward target_frontier using BFS on local_map.
        
        Algorithm:
        1. Use BFS to find shortest path from current position to target
        2. Only traverse nodes that exist in self.local_map (discovered nodes)
        3. Return the immediate next step (not the whole path)
        4. If no path exists, drop the target and increment stuck_counter
        
        Returns:
            New (x,y) position to move to
        """
        import random
        
        if not self.target_frontier or not self.current_position:
            return self.current_position
        
        # Ensure current position is in local_map
        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()
        
        # Try to find next step using BFS
        next_step = self._find_next_step_bfs(self.target_frontier)
        
        if next_step is None:
            # No path to target found - target is walled off or unreachable
            print(f"{self.name} cannot reach target {self.target_frontier}. Dropping target.")
            self.target_frontier = None
            self.stuck_counter += 1
            
            # If stuck too long, pick a random frontier
            if self.stuck_counter > 5 and self.frontiers:
                self.target_frontier = random.choice(self.frontiers)
                self.stuck_counter = 0
            
            return self.current_position
        
        # Successfully found a next step
        self.stuck_counter = 0
        return next_step
    
    
    def _is_wall(self, cell_value: int) -> bool:
        """Check if a cell value represents a wall (1 = wall)."""
        return cell_value == 1
    
    def _scan_neighbors(self, local_grid_view: List[List[int]]) -> List[Tuple[int, int]]:
        """
        Scan 4-neighbors in the local grid view and identify frontiers.
        """
        if not self.current_position:
            return []
        
        new_frontiers = []
        cx, cy = self.current_position
        rows, cols = len(local_grid_view), len(local_grid_view[0])
        
        # Ensure current position is registered
        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()
        
        # Check 4 neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            
            # Bounds check
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            
            cell = local_grid_view[nx][ny]
            
            # Skip walls
            if self._is_wall(cell):
                continue
            
            # Check if this open space is a new frontier
            if (nx, ny) not in self.local_map:
                if (nx, ny) not in self.frontiers:
                    self.frontiers.append((nx, ny))
                    new_frontiers.append((nx, ny))
        
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
        Uses agent ID hierarchy: lowest ID wins claim ownership.
        
        Args:
            payload: Dictionary with 'target_frontier' and 'sender_id'
        """
        sender = payload.get("sender_name", "Unknown")
        sender_id = payload.get("sender_id", 999)
        frontier = payload.get("target_frontier")
        
        if frontier:
            frontier_tuple = tuple(frontier) if isinstance(frontier, list) else frontier
            
            # Only update if frontier not claimed, or if new sender has lower ID (wins)
            if frontier_tuple not in self.claimed_frontiers:
                self.claimed_frontiers[frontier_tuple] = sender_id
                print(f"{self.name} recorded frontier claim from {sender} (ID {sender_id}): {frontier_tuple}")
            elif sender_id < self.claimed_frontiers[frontier_tuple]:
                old_owner = self.claimed_frontiers[frontier_tuple]
                self.claimed_frontiers[frontier_tuple] = sender_id
                print(f"{self.name} updated frontier owner {frontier_tuple} from Agent_{old_owner} to {sender} (ID {sender_id})")
    
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
        
        # ANTI-LIVELOCK: Check claim hierarchy for current target
        if self.target_frontier and self.target_frontier in self.claimed_frontiers:
            owner_id = self.claimed_frontiers[self.target_frontier]
            if owner_id < self.agent_id:
                # Lower ID agent owns this, must yield it
                print(f"{self.name} yielding frontier {self.target_frontier} to Agent_{owner_id} (lower ID)")
                self.target_frontier = None
        
        # SCAN: Identify new frontiers
        new_frontiers = self._scan_neighbors(local_grid_view)
        new_nodes = list(self.local_map.keys())  # All discovered nodes
        
        # BROADCAST: Send updates
        self._broadcast_map_update(new_nodes, new_frontiers)
        
        # LISTEN: Process any pending messages
        # (This would be called from async handler in real implementation)
        
        # DECIDE: Select frontier if needed
        if self.target_frontier is None:
            selected = self._select_best_frontier()
            if selected:
                # Claim locally FIRST to prevent race condition
                self.claimed_frontiers[selected] = self.agent_id
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
                data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 65535)
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


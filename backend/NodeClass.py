"""
NodeClass.py: Agent implementation for Fixed-Size Swarm with Frontier-Based Exploration
                + Ant Colony Optimization (ACO) for frontier selection

Each agent:
1. Maintains a local_map of visited nodes and edges
2. Maintains a pheromone_map of trail strengths per node
3. Identifies frontiers (unexplored but reachable nodes)
4. Communicates via UDP to share map updates AND pheromone trails
5. Uses a tick() state machine to scan, broadcast, listen, decide, and move
6. Uses ACO probability formula (τ^α · η^β) to select the best frontier
7. Collaboratively explores the maze by following shared pheromone trails
"""

import socket
import asyncio
import json
import random
from collections import deque
from typing import Set, Tuple, List, Dict, Optional
import math


class Node:
    """
    Agent node for swarm-based maze exploration with Ant Colony Optimization.

    ACO Overview
    ------------
    Each agent maintains a pheromone_map: Dict[Tuple[int,int], float] that records
    trail strength at every discovered node.  When an agent moves to a position it
    deposits PHEROMONE_DEPOSIT on that cell.  At the start of every tick, ALL
    pheromone values decay by factor (1 - PHEROMONE_DECAY), floored at PHEROMONE_INIT
    so trails never fully disappear.

    Frontier selection uses the standard ACO probability formula:

        score(f) = τ(f)^ALPHA  *  η(f)^BETA

    where τ(f) is the pheromone level at frontier f and η(f) = 1 / bfs_distance(f).
    A frontier is selected by weighted-random sampling over these scores, so high-
    pheromone / close frontiers are strongly preferred but rare frontiers can still
    be chosen (exploration vs. exploitation balance).

    Agents broadcast a PHEROMONE packet alongside the existing MERGE / CLAIM packets
    so that trail information is shared colony-wide.  Incoming trails are merged by
    taking the max of local and remote values, which preserves the strongest paths.

    Data structures:
    - local_map:     Dict[Tuple[int,int], Set[Tuple[int,int]]] — visited nodes → neighbours
    - pheromone_map: Dict[Tuple[int,int], float]               — trail strength per node
    - frontiers:     List[Tuple[int,int]]  — unexplored coords adjacent to known nodes
    - target_frontier: Optional[Tuple[int,int]] — current navigation target
    - claimed_frontiers: Dict[Tuple[int,int], int] — frontier → lowest-ID owner
    """

    # ------------------------------------------------------------------ #
    #  Initialisation                                                      #
    # ------------------------------------------------------------------ #

    def __init__(self, port: int, name: str, agent_id: int,
                 maze_width: int = 0, maze_height: int = 0):
        """
        Initialise a swarm agent.

        Args:
            port:        UDP port for this agent.
            name:        Human-readable name.
            agent_id:    Unique numeric identifier.
            maze_width:  Width of the maze (for boundary detection).
            maze_height: Height of the maze (for boundary detection).
        """
        self.port = port
        self.name = name
        self.agent_id = agent_id
        self.maze_width = maze_width
        self.maze_height = maze_height

        # ── ACO hyper-parameters ──────────────────────────────────────── #
        self.PHEROMONE_INIT    = 0.1   # Starting / minimum pheromone level
        self.PHEROMONE_DECAY   = 0.05  # Evaporation rate per tick (fraction lost)
        self.PHEREMONE_DEPOSIT = 1.0   # Amount deposited when a node is visited
        self.ALPHA             = 1.0   # Pheromone influence exponent in ACO formula
        self.BETA              = 2.0   # Distance (heuristic) influence exponent
        # How often (in ticks) to broadcast the full pheromone map to peers.
        # Broadcasting every tick is noisy; every N ticks reduces UDP traffic.
        self.PHEROMONE_BROADCAST_INTERVAL = 5

        # ── Core map data structures ──────────────────────────────────── #
        # local_map: node → set of known neighbours (edges discovered via scan)
        self.local_map:     Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        # pheromone_map: node → current pheromone level (ACO trail)
        self.pheromone_map: Dict[Tuple[int, int], float] = {}

        self.frontiers:       List[Tuple[int, int]]       = []
        self.target_frontier: Optional[Tuple[int, int]]   = None

        # Map frontier coord → agent_id that claimed it (lowest ID wins)
        self.claimed_frontiers: Dict[Tuple[int, int], int] = {}

        # ── Position ──────────────────────────────────────────────────── #
        self.current_position: Optional[Tuple[int, int]] = None

        # ── UDP socket ────────────────────────────────────────────────── #
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        print(f"{self.name} (Agent_{self.agent_id}) listening on port {port}")

        # Message handler callback (can be replaced externally)
        self.on_message = lambda msg, addr: None

        # Peer agent ports (populated externally before first tick)
        self.peer_ports: List[int] = []

        # ── Stuck / wall detection ────────────────────────────────────── #
        self.stuck_counter:    int              = 0
        self.recent_wall_hits: Set[Tuple[int, int]] = set()

        # ── Path & step tracking ──────────────────────────────────────── #
        self.agent_path: List[Tuple[int, int]] = []
        self.num_steps:  int = 0

        # ── Stats for completion display ──────────────────────────────── #
        self.total_wall_hits:         int            = 0
        self.tiles_discovered_directly: int          = 0
        self.ticks_elapsed:           int            = 0
        self.maps_merged:             int            = 0
        self.maze_complete:           bool           = False
        self.reached_goal:            bool           = False
        self.goal_tick:               Optional[int]  = None

    # ------------------------------------------------------------------ #
    #  Setup helpers                                                       #
    # ------------------------------------------------------------------ #

    def set_initial_position(self, position: Tuple[int, int]):
        """Set the agent's starting position and initialise local_map."""
        self.current_position = position
        self.local_map[position] = set()
        self.agent_path = [position]
        self.tiles_discovered_directly = 1   # starting tile counts as discovered
        # Give the start tile a strong initial trail so agents don't wander away
        self.pheromone_map[position] = self.PHEREMONE_DEPOSIT
        print(f"{self.name} starting at {position}")

    # ------------------------------------------------------------------ #
    #  ACO pheromone methods                                               #
    # ------------------------------------------------------------------ #

    def _get_pheromone(self, pos: Tuple[int, int]) -> float:
        """
        Return the current pheromone level at *pos*.

        Falls back to PHEROMONE_INIT for nodes not yet in the map, so that
        unvisited frontiers still have a non-zero (explorable) score.
        """
        return self.pheromone_map.get(pos, self.PHEROMONE_INIT)

    def _deposit_pheromone(self, pos: Tuple[int, int],
                           amount: Optional[float] = None):
        """
        Deposit pheromone at *pos* (additive).

        Args:
            pos:    Grid coordinate to reinforce.
            amount: Pheromone to add; defaults to PHEREMONE_DEPOSIT.
        """
        if amount is None:
            amount = self.PHEREMONE_DEPOSIT
        self.pheromone_map[pos] = self._get_pheromone(pos) + amount

    def _evaporate_pheromones(self):
        """
        Apply evaporation to every entry in pheromone_map.

        Each value is multiplied by (1 - PHEROMONE_DECAY) and floored at
        PHEROMONE_INIT so that old trails fade but never fully vanish.
        This is called once per tick BEFORE movement.
        """
        for pos in list(self.pheromone_map.keys()):
            evaporated = self.pheromone_map[pos] * (1.0 - self.PHEROMONE_DECAY)
            self.pheromone_map[pos] = max(self.PHEROMONE_INIT, evaporated)

    def _select_best_frontier_aco(self) -> Optional[Tuple[int, int]]:
        """
        Select the next frontier using the ACO probability formula.

        For each candidate frontier f:

            score(f) = τ(f)^ALPHA  *  η(f)^BETA

        where τ(f) = pheromone level at f  (from pheromone_map)
              η(f) = 1 / max(bfs_distance(current, f), 1)  (heuristic desirability)

        Candidates are then sampled by weighted probability, giving strong
        preference to high-pheromone or nearby frontiers while still allowing
        exploration of distant / low-pheromone options.

        Priority:
            1. Unclaimed frontiers (preferred — avoids overlapping with peers).
            2. Claimed frontiers   (fallback — helps break deadlock).
            3. None if no frontiers exist.

        Returns:
            (row, col) of the selected frontier, or None.
        """
        if not self.frontiers:
            return None

        # Prefer unclaimed frontiers; fall back to all frontiers if needed
        candidates = [f for f in self.frontiers if f not in self.claimed_frontiers]
        if not candidates:
            candidates = list(self.frontiers)
        if not candidates:
            return None

        scores: List[float] = []
        for frontier in candidates:
            dist = self._get_bfs_distance(self.current_position, frontier)
            # Guard against zero distance (shouldn't occur for frontiers, but safe)
            eta   = 1.0 / max(dist, 1)
            tau   = self._get_pheromone(frontier)
            score = (tau ** self.ALPHA) * (eta ** self.BETA)
            scores.append(score)

        total = sum(scores)
        if total == 0:
            # All scores zero (edge case) — fall back to uniform random
            return random.choice(candidates)

        # Weighted random selection
        probs = [s / total for s in scores]
        return random.choices(candidates, weights=probs, k=1)[0]

    # ------------------------------------------------------------------ #
    #  Pheromone networking                                               #
    # ------------------------------------------------------------------ #

    def _broadcast_pheromone_update(self):
        """
        Broadcast the current pheromone_map to all peer agents.

        This allows the swarm to share trail information so that paths
        found by one ant reinforce navigation choices for others.

        To reduce UDP traffic this should be called every
        PHEROMONE_BROADCAST_INTERVAL ticks rather than every tick.
        The serialised payload converts tuple keys to "r,c" strings because
        JSON requires string keys.
        """
        if not self.pheromone_map:
            return

        # Serialise: {"{r},{c}": float_value, ...}
        serialised = {
            f"{pos[0]},{pos[1]}": val
            for pos, val in self.pheromone_map.items()
        }

        payload = {
            "type":        "PHEROMONE",
            "sender_id":   self.agent_id,
            "sender_name": self.name,
            "trails":      serialised,
        }

        for peer_port in self.peer_ports:
            if peer_port != self.port:
                try:
                    self.send_json("127.0.0.1", peer_port, payload)
                except Exception as e:
                    print(f"{self.name} failed to send PHEROMONE to port {peer_port}: {e}")

    def _process_pheromone_packet(self, payload: Dict):
        """
        Merge an incoming PHEROMONE packet into the local pheromone_map.

        Merge rule: take the **maximum** of local and remote values.
        This preserves the strongest trail seen colony-wide without
        artificially doubling counts (additive merge would over-inflate).

        Args:
            payload: Dict with 'trails': {"r,c": float, ...}
        """
        sender = payload.get("sender_name", "Unknown")
        trails: Dict[str, float] = payload.get("trails", {})
        merged_count = 0

        for key, remote_val in trails.items():
            try:
                r, c = key.split(",")
                pos = (int(r), int(c))
            except ValueError:
                continue  # Malformed key — skip silently

            local_val = self._get_pheromone(pos)
            # Take the stronger of the two trail values
            if remote_val > local_val:
                self.pheromone_map[pos] = remote_val
                merged_count += 1

        if merged_count:
            print(f"{self.name} merged {merged_count} pheromone trail(s) from {sender}")

    # ------------------------------------------------------------------ #
    #  Distance / pathfinding helpers (unchanged from original)           #
    # ------------------------------------------------------------------ #

    def _manhattan_distance(self, pos1: Tuple[int, int],
                            pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _get_bfs_distance(self, pos1: Tuple[int, int],
                          pos2: Tuple[int, int]) -> int:
        """
        Calculate true path distance using BFS on the local_map.

        Frontiers that look close in Manhattan distance but require walking
        around walls are correctly evaluated at their true traversal cost.

        Returns 999999 if pos2 is unreachable from pos1 through known map.
        """
        if pos1 == pos2:
            return 0

        queue   = deque([(pos1, 0)])
        visited = {pos1}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current, distance = queue.popleft()
            if current == pos2:
                return distance
            cx, cy = current
            for dx, dy in directions:
                neighbor = (cx + dx, cy + dy)
                if neighbor not in visited:
                    if neighbor in self.local_map or neighbor == pos2:
                        visited.add(neighbor)
                        queue.append((neighbor, distance + 1))

        return 999999

    def _find_next_step_bfs(self,
                            target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Use BFS on local_map to find the immediate next step toward target."""
        if target == self.current_position:
            return None

        queue   = deque([(self.current_position, [self.current_position])])
        visited = {self.current_position}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path[1] if len(path) > 1 else None
            cx, cy = current
            for dx, dy in directions:
                neighbor = (cx + dx, cy + dy)
                if neighbor not in visited:
                    if neighbor in self.local_map or neighbor == target:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        return None

    def _move_toward_target(self) -> Tuple[int, int]:
        """
        Calculate the next step toward target_frontier using BFS on local_map.

        Returns the new (row, col) position to move to, or current_position
        if no path exists (stuck).
        """
        if not self.target_frontier or not self.current_position:
            return self.current_position

        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()

        next_step = self._find_next_step_bfs(self.target_frontier)

        if next_step is None:
            print(f"{self.name} cannot reach target {self.target_frontier}. Dropping target.")
            self.target_frontier = None
            self.stuck_counter += 1
            if self.stuck_counter > 5 and self.frontiers:
                self.target_frontier = random.choice(self.frontiers)
                self.stuck_counter = 0
            return self.current_position

        self.stuck_counter = 0
        return next_step

    # ------------------------------------------------------------------ #
    #  Scanning                                                            #
    # ------------------------------------------------------------------ #

    def _is_wall(self, cell_value: int) -> bool:
        """Return True if cell_value represents a wall (1 = wall)."""
        return cell_value == 1

    def _scan_neighbors(self,
                        local_grid_view: List[List[int]]) -> List[Tuple[int, int]]:
        """
        Scan 4-neighbours in the local grid view and identify new frontiers.
        Also detects and reports wall hits.
        """
        if not self.current_position:
            return []

        new_frontiers: List[Tuple[int, int]] = []
        cx, cy = self.current_position
        rows, cols = len(local_grid_view), len(local_grid_view[0])

        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy

            if not (0 <= nx < rows and 0 <= ny < cols):
                continue

            cell = local_grid_view[nx][ny]

            if self._is_wall(cell):
                if (nx, ny) not in self.recent_wall_hits:
                    self.report_wall_hit((nx, ny))
                    self.recent_wall_hits.add((nx, ny))
                    self.total_wall_hits += 1
                    if len(self.recent_wall_hits) > 10:
                        self.recent_wall_hits.clear()
                continue

            if (nx, ny) not in self.local_map:
                if (nx, ny) not in self.frontiers:
                    self.frontiers.append((nx, ny))
                    new_frontiers.append((nx, ny))

        return new_frontiers

    # ------------------------------------------------------------------ #
    #  Main tick (state machine)                                           #
    # ------------------------------------------------------------------ #

    def tick(self, local_grid_view: List[List[int]]):
        """
        State machine tick for the agent.

        Sequence
        --------
        0. PHEROMONE EVAPORATION  — decay all trail values
        1. CLEANUP                — remove explored positions from frontier list
        2. SCAN                   — identify new frontiers from surroundings
        3. BROADCAST              — send map updates + periodic pheromone broadcast
        4. LISTEN                 — process incoming UDP messages (async handler)
        5. DECIDE (ACO)           — choose next frontier via τ^α · η^β formula
        6. MOVE                   — take one BFS step toward target; deposit pheromone

        Args:
            local_grid_view: 2D array of surroundings (0 = open, 1 = wall).
        """
        self.ticks_elapsed += 1

        # ── 0. PHEROMONE EVAPORATION ──────────────────────────────────── #
        self._evaporate_pheromones()

        # ── 1. CLEANUP ────────────────────────────────────────────────── #
        if self.current_position not in self.local_map:
            self.local_map[self.current_position] = set()

        # Remove frontiers that have already been visited (zombie frontier fix)
        self.frontiers = [f for f in self.frontiers if f not in self.local_map]

        # Clear reached target
        if self.target_frontier == self.current_position:
            self.target_frontier = None

        # ANTI-LIVELOCK: yield target if a lower-ID agent has claimed it
        if self.target_frontier and self.target_frontier in self.claimed_frontiers:
            owner_id = self.claimed_frontiers[self.target_frontier]
            if owner_id < self.agent_id:
                print(f"{self.name} yielding frontier {self.target_frontier} "
                      f"to Agent_{owner_id} (lower ID)")
                self.target_frontier = None

        # ── 2. SCAN ───────────────────────────────────────────────────── #
        new_frontiers = self._scan_neighbors(local_grid_view)
        new_nodes     = list(self.local_map.keys())

        # ── 3. BROADCAST ─────────────────────────────────────────────── #
        self._broadcast_map_update(new_nodes, new_frontiers)

        # Broadcast pheromone trails every N ticks to avoid flooding peers
        if self.ticks_elapsed % self.PHEROMONE_BROADCAST_INTERVAL == 0:
            self._broadcast_pheromone_update()

        # ── 4. LISTEN ────────────────────────────────────────────────── #
        # (Handled asynchronously via web_listen / process_message)

        # ── 5. DECIDE (ACO) ───────────────────────────────────────────── #
        if self.target_frontier is None:
            selected = self._select_best_frontier_aco()
            if selected:
                self.claimed_frontiers[selected] = self.agent_id
                self.target_frontier = selected
                self._broadcast_frontier_claim(selected)
                print(f"{self.name} (ACO) selected frontier {selected}")
                self.send_activity_log("agent_frontier", {"frontier": list(selected)})

        # ── 6. MOVE + PHEROMONE DEPOSIT ──────────────────────────────── #
        if self.target_frontier:
            new_pos = self._move_toward_target()
            if new_pos != self.current_position:
                prev_pos              = self.current_position
                self.current_position = new_pos
                self.num_steps       += 1
                self.agent_path.append(new_pos)

                # Register newly visited tile in local_map
                if self.current_position not in self.local_map:
                    self.local_map[self.current_position] = set()
                    self.tiles_discovered_directly += 1

                # ── ACO: Deposit pheromone on the new tile ─────────────── #
                self._deposit_pheromone(self.current_position)

                self.send_activity_log("agent_move", {
                    "from_position": list(prev_pos),
                    "to_position":   list(new_pos),
                })
                print(f"{self.name} moved to {new_pos}")
            else:
                if new_pos == self.target_frontier:
                    print(f"{self.name} reached target frontier {self.target_frontier}")
                    if self.target_frontier not in self.local_map:
                        self.local_map[self.target_frontier] = set()
                    self.target_frontier = None

    # ------------------------------------------------------------------ #
    #  Map networking (MERGE / CLAIM)                                      #
    # ------------------------------------------------------------------ #

    def _broadcast_map_update(self, new_nodes:    List[Tuple[int, int]],
                               new_frontiers: List[Tuple[int, int]]):
        """Broadcast a MERGE packet with newly discovered nodes/frontiers."""
        if not new_nodes and not new_frontiers:
            return

        payload = {
            "type":         "MERGE",
            "sender_id":    self.agent_id,
            "sender_name":  self.name,
            "nodes":        new_nodes,
            "frontiers":    new_frontiers,
        }

        for peer_port in self.peer_ports:
            if peer_port != self.port:
                try:
                    self.send_json("127.0.0.1", peer_port, payload)
                except Exception as e:
                    print(f"{self.name} failed to send to port {peer_port}: {e}")

    def _broadcast_frontier_claim(self, frontier: Tuple[int, int]):
        """Broadcast a CLAIM packet so peers know this frontier is taken."""
        payload = {
            "type":             "CLAIM",
            "sender_id":        self.agent_id,
            "sender_name":      self.name,
            "target_frontier":  frontier,
        }

        for peer_port in self.peer_ports:
            if peer_port != self.port:
                try:
                    self.send_json("127.0.0.1", peer_port, payload)
                except Exception as e:
                    print(f"{self.name} failed to send CLAIM to port {peer_port}: {e}")

    def _process_merge_packet(self, payload: Dict):
        """Integrate a remote agent's MERGE packet into the local map."""
        sender = payload.get("sender_name", "Unknown")

        for node in payload.get("nodes", []):
            node_tuple = tuple(node) if isinstance(node, list) else node
            if node_tuple not in self.local_map:
                self.local_map[node_tuple] = set()

        for frontier in payload.get("frontiers", []):
            frontier_tuple = tuple(frontier) if isinstance(frontier, list) else frontier
            if frontier_tuple not in self.frontiers:
                self.frontiers.append(frontier_tuple)

        self.maps_merged += 1
        print(f"{self.name} merged data from {sender}: "
              f"{len(payload.get('nodes', []))} nodes, "
              f"{len(payload.get('frontiers', []))} frontiers")

    def _process_claim_packet(self, payload: Dict):
        """
        Process a CLAIM packet.  Lowest agent_id wins ownership.
        """
        sender    = payload.get("sender_name", "Unknown")
        sender_id = payload.get("sender_id",   999)
        frontier  = payload.get("target_frontier")

        if frontier:
            frontier_tuple = tuple(frontier) if isinstance(frontier, list) else frontier

            if frontier_tuple not in self.claimed_frontiers:
                self.claimed_frontiers[frontier_tuple] = sender_id
                print(f"{self.name} recorded claim from {sender} "
                      f"(ID {sender_id}): {frontier_tuple}")
            elif sender_id < self.claimed_frontiers[frontier_tuple]:
                old_owner = self.claimed_frontiers[frontier_tuple]
                self.claimed_frontiers[frontier_tuple] = sender_id
                print(f"{self.name} updated owner of {frontier_tuple} "
                      f"from Agent_{old_owner} to {sender} (ID {sender_id})")

    # ------------------------------------------------------------------ #
    #  Message dispatch                                                    #
    # ------------------------------------------------------------------ #

    def process_message(self, msg: str):
        """
        Dispatch a received JSON message to the correct handler.

        Packet types:
            MERGE     — remote map update
            CLAIM     — frontier ownership
            PHEROMONE — trail data  ← NEW (ACO)
        """
        try:
            payload  = json.loads(msg)
            msg_type = payload.get("type")

            # Types intended only for the frontend bridge — ignore silently
            BRIDGE_ONLY = {"agent_registered", "agent_move", "info", "agent_frontier"}
            if msg_type in BRIDGE_ONLY:
                return

            if   msg_type == "MERGE":
                self._process_merge_packet(payload)
            elif msg_type == "CLAIM":
                self._process_claim_packet(payload)
            elif msg_type == "PHEROMONE":                        # ← NEW
                self._process_pheromone_packet(payload)
            else:
                print(f"{self.name} received unknown message type: {msg_type}")

        except json.JSONDecodeError as e:
            print(f"{self.name} failed to parse message: {e}")

    # ------------------------------------------------------------------ #
    #  Activity logging / frontend bridge                                  #
    # ------------------------------------------------------------------ #

    def send_activity_log(self, log_type: str,
                          extra_data: Optional[Dict] = None):
        """Send an activity log entry to the frontend via the main.py bridge."""
        payload = {
            "type":       log_type,
            "agent_name": self.name,
            "agent_id":   self.agent_id,
        }
        if extra_data:
            payload.update(extra_data)
        try:
            self.send_json("127.0.0.1", 9000, payload)
        except Exception:
            pass

    def report_wall_hit(self, wall_position: Tuple[int, int]):
        """Report when an agent encounters a wall/blocked tile."""
        row, col = wall_position
        is_boundary = (
            row == 0
            or row == self.maze_height - 1
            or col == 0
            or col == self.maze_width - 1
        )
        obstacle_type = "boundary" if is_boundary else "wall"
        self.send_activity_log("agent_wall_hit", {
            "position":      list(self.current_position) if self.current_position else [0, 0],
            "wall_position": list(wall_position),
            "obstacle_type": obstacle_type,
        })

    # ------------------------------------------------------------------ #
    #  UDP transport                                                       #
    # ------------------------------------------------------------------ #

    async def web_listen(self):
        """Asynchronously listen for incoming UDP messages."""
        loop = asyncio.get_event_loop()
        while True:
            try:
                data, addr = await loop.run_in_executor(
                    None, self.sock.recvfrom, 65535
                )
                msg = data.decode("utf-8")
                print(f"[{self.name}] Received from {addr}: {msg}")
                self.process_message(msg)
                self.on_message(msg, addr)
            except Exception as e:
                print(f"{self.name} error in web_listen: {e}")

    def send_json(self, ip: str, port: int, payload: dict):
        """Send a JSON payload via UDP."""
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

    # ------------------------------------------------------------------ #
    #  Stats & path helpers                                                #
    # ------------------------------------------------------------------ #

    def _calculate_optimal_path_distance(self, goal: Tuple[int, int],
                                         maze: List[List[int]]) -> int:
        """
        Calculate the true shortest path from start to goal via BFS on the full maze.
        """
        if not self.agent_path:
            return 0

        start_pos  = self.agent_path[0]
        rows       = len(maze)
        cols       = len(maze[0]) if rows > 0 else 0
        queue      = deque([(start_pos, 0)])
        visited    = {start_pos}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current, distance = queue.popleft()
            if current == goal:
                return distance
            cx, cy = current
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and 0 <= nx < rows and 0 <= ny < cols \
                        and maze[nx][ny] == 0:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), distance + 1))

        return 0

    def get_agent_stats(self, goal: Tuple[int, int],
                        maze: List[List[int]],
                        all_explored: set) -> Dict:
        """
        Gather all agent statistics for display at maze completion.

        Now includes ACO-specific fields:
            - pheromone_nodes_tracked: number of entries in pheromone_map
            - peak_pheromone:          highest single pheromone value recorded
            - avg_pheromone:           mean trail strength across all tracked nodes
        """
        total_explored = len(self.local_map)
        remaining_frontiers = sum(
            1 for r in range(len(maze)) for c in range(len(maze[0]))
            if maze[r][c] == 0 and (r, c) not in all_explored
        )
        self_claimed_frontiers = len(
            [f for f in self.claimed_frontiers
             if self.claimed_frontiers[f] == self.agent_id]
        )
        unique_tiles_walked = len(set(self.agent_path))
        redundant_steps     = max(0, self.num_steps - (unique_tiles_walked - 1))
        exploration_rate    = (
            round(self.tiles_discovered_directly / self.num_steps, 3)
            if self.num_steps > 0 else 0
        )

        # ── ACO-specific stats ──────────────────────────────────────── #
        pheromone_values      = list(self.pheromone_map.values())
        pheromone_nodes       = len(pheromone_values)
        peak_pheromone        = round(max(pheromone_values), 4) if pheromone_values else 0.0
        avg_pheromone         = (
            round(sum(pheromone_values) / pheromone_nodes, 4)
            if pheromone_nodes > 0 else 0.0
        )

        return {
            "agent_name":                self.name,
            "agent_id":                  self.agent_id,
            "tiles_explored":            total_explored,
            "tiles_discovered_directly": self.tiles_discovered_directly,
            "tiles_learned_from_peers":  total_explored - self.tiles_discovered_directly,
            "steps_taken":               self.num_steps,
            "unique_tiles_walked":       unique_tiles_walked,
            "redundant_steps":           redundant_steps,
            "efficiency_percentage":     round(
                ((unique_tiles_walked - 1) / self.num_steps * 100)
                if self.num_steps > 0 else 0, 1
            ),
            "exploration_rate":          exploration_rate,
            "remaining_frontiers":       remaining_frontiers,
            "frontiers_claimed_by_agent": self_claimed_frontiers,
            "walls_boundaries_hit":      self.total_wall_hits,
            "maps_merged_from_peers":    self.maps_merged,
            "ticks_elapsed":             self.ticks_elapsed,
            "reached_goal":              self.reached_goal,
            "goal_tick":                 self.goal_tick,
            # ACO stats
            "pheromone_nodes_tracked":   pheromone_nodes,
            "peak_pheromone":            peak_pheromone,
            "avg_pheromone":             avg_pheromone,
        }

    # ------------------------------------------------------------------ #
    #  Getters                                                             #
    # ------------------------------------------------------------------ #

    def get_agent_path(self):
        return self.agent_path

    def get_agent_steps(self):
        return self.num_steps
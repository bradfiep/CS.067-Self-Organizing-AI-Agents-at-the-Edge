# Fixed-Size Swarm with Frontier-Based Exploration Architecture

## Overview

This document describes the complete architecture for the maze exploration system using a **fixed-size swarm** of agents that collaborate via **frontier-based exploration** and **UDP-based communication**.

---

## System Architecture

### Initialization Phase

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Maze Input                                               │
│    - 2D grid: 0=open, 1=wall                                │
│    - Start and goal coordinates                             │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Calculate Optimal Swarm Size (spawner.py)               │
│    - optimal_count = (width × height) / 50                 │
│    - Adjust by wall_density: 1.0x - 1.5x                   │
│    - Cap at max (width × height) / 10                       │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Spawn Fixed-Size Swarm (spawner.py)                     │
│    - Create N agents at start position                      │
│    - Assign unique UDP ports (9000-9999)                   │
│    - Configure peer_ports for each agent                    │
│    - Initialize local_map, frontiers, claimed_frontiers    │
│    ★ NO MORE AGENTS SPAWN AFTER THIS POINT ★              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
       Simulation Ready
```

### Simulation Phase - Agent State Machine (tick)

Each agent executes this sequence every simulation step:

```
┌──────────────────────────────────────────────────────────────┐
│ TICK(local_grid_view): Agent State Machine                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ 1. SCAN                                                      │
│    ├─ Check 4 neighbors in local_grid_view                  │
│    ├─ 0 (open) → check if discovered                        │
│    │  └─ Already in local_map? Update edges                 │
│    │  └─ Not in local_map? Add to frontiers                 │
│    ├─ 1 (wall) → ignore                                     │
│    └─ Return new_frontiers, new_nodes found                 │
│                                                               │
│ 2. BROADCAST (MAP UPDATE)                                   │
│    ├─ Create MERGE packet: {new_nodes, new_frontiers}      │
│    └─ Send UDP to all peers                                 │
│                                                               │
│ 3. LISTEN (ASYNC)                                           │
│    ├─ Receive MERGE packets from peers                      │
│    │  └─ Merge nodes into local_map                         │
│    │  └─ Add frontiers to frontier list                     │
│    ├─ Receive CLAIM packets from peers                      │
│    │  └─ Add frontier to claimed_frontiers                  │
│    └─ (Happens in background; processed each tick)          │
│                                                               │
│ 4. DECIDE (SELECT FRONTIER)                                 │
│    ├─ If target_frontier is None or claimed:               │
│    │  ├─ Get unclaimed frontiers                            │
│    │  ├─ Select nearest by Manhattan distance               │
│    │  ├─ Set as target_frontier                             │
│    │  └─ Broadcast CLAIM packet                             │
│    └─ If target_frontier is set, keep it                    │
│                                                               │
│ 5. MOVE                                                      │
│    ├─ Calculate next step toward target_frontier            │
│    │  └─ Prefer: horizontal movement first, then vertical   │
│    │  └─ Manhattan distance heuristic                       │
│    ├─ Update current_position                               │
│    └─ If reached target_frontier: clear target              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Data Structures

### Agent State (NodeClass.Node)

```python
class Node:
    # Identity
    port: int                    # UDP port
    name: str                   # "Agent_N"
    agent_id: int              # Unique ID

    # Position
    current_position: (x, y)   # Current location in maze

    # Map Knowledge
    local_map: Dict[(x,y) → Set[(x,y)]]
        # Discovered nodes and their neighbors
        # Built from: initial position + scans + MERGE packets

    frontiers: List[(x, y)]
        # Reachable but unexplored coordinates
        # Source: neighbors not yet in local_map

    # Exploration State
    target_frontier: (x, y) | None
        # Currently pursuing this frontier
        # Selected by _select_best_frontier()

    claimed_frontiers: Set[(x, y)]
        # Frontiers claimed by any agent
        # Prevents duplicate exploration

    # Communication
    peer_ports: List[int]      # All agent UDP ports
    sock: socket               # UDP socket
```

### Message Formats

#### MERGE - Map Sharing

```json
{
  "type": "MERGE",
  "sender_id": 0,
  "sender_name": "Agent_0",
  "nodes": [
    [1, 1],
    [1, 2]
  ],
  "frontiers": [
    [2, 3],
    [3, 2]
  ]
}
```

#### CLAIM - Frontier Reservation

```json
{
  "type": "CLAIM",
  "sender_id": 0,
  "sender_name": "Agent_0",
  "target_frontier": [2, 3]
}
```

---

## Frontier Selection Strategy

The `_select_best_frontier()` algorithm ensures efficient division of labor:

```
1. Input: self.frontiers (all known unexplored nodes)
2. Filter: unclaimed = [f for f in frontiers if f not in claimed_frontiers]
3. Select: best = min(unclaimed, key=manhattan_distance(current_pos, f))
4. Claim: broadcast CLAIM packet
5. Output: target_frontier = best
```

Benefits:

- **No centralized coordination**: Each agent decides independently
- **Work division**: Agents avoid duplicate exploration via CLAIM
- **Greedy efficiency**: Nearest frontier minimizes wasted steps
- **Adaptive**: Agents learn from peers' discoveries via MERGE

---

## Communication Protocol

### Packet Types

| Type  | Trigger           | Content           | Effect               |
| ----- | ----------------- | ----------------- | -------------------- |
| MERGE | New discovery     | Nodes + Frontiers | Merge into peer maps |
| CLAIM | Frontier selected | Target frontier   | Update claimed set   |

### Network Topology

- **Network**: Local loopback (127.0.0.1)
- **Ports**: Dynamic range 9000-9999
- **Protocol**: UDP (unreliable but fast)
- **Broadcast**: Each agent sends to all peers

### Resilience

- No guaranteed delivery → swarm adapts via continuous MERGE broadcasts
- Temporary failures don't break exploration
- Lost packets recovered by re-broadcasting in future ticks

---

## Removed Components

### Old Architecture (Deprecated)

The following have been completely removed:

#### DFS/BFS Search Algorithms

- **File**: NodeClass.py (removed methods)
- **Why**: No longer needed with frontier-based approach
- **Replacement**: Collaborative frontier exploration

#### Recursive Agent Spawning

- **File**: maze_exploration.py (explore_forward function removed)
- **Why**: Fixed-size swarms eliminate runtime complexity
- **Replacement**: spawn_agents() creates all agents upfront

#### Goal-Directed Agent Calculation

- **File**: agent_count.py (still exists but unused)
- **Why**: Replaced by dynamic size calculation
- **Replacement**: calculate_optimal_agent_count() in spawner.py

---

## Simulation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ maze_exploration.main()                                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ spawn_agents(maze, start) → List[Node]                      │
│ ★ Single upfront initialization                             │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
     ┌─────────────────────────────────┐
     │ Simulation Loop: tick 1..N      │
     │ ★ No new agents created ★       │
     ├─────────────────────────────────┤
     │                                 │
     │ For each agent:                 │
     │  1. Get local grid view         │
     │  2. agent.tick(local_view)      │
     │  3. Check if goal reached       │
     │                                 │
     │ Print swarm status              │
     │                                 │
     │ Repeat until goal or max_ticks  │
     │                                 │
     └─────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│ Print Summary:                                               │
│ - Ticks executed                                             │
│ - Goal reached status                                        │
│ - Per-agent statistics                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Improvements Over Old System

| Aspect          | Old (Recursive)       | New (Frontier-Based)    |
| --------------- | --------------------- | ----------------------- |
| Agent Count     | Dynamic, unbounded    | Fixed, calculated once  |
| Spawning        | Runtime (recursive)   | Initialization only     |
| Exploration     | DFS paths             | Frontier-driven         |
| Coordination    | None (tree structure) | UDP communication       |
| Scalability     | Limited               | Predictable             |
| Memory          | Growing               | Fixed                   |
| Synchronization | Tree node tracking    | Set-based deduplication |

---

## Configuration Parameters

### Swarm Size Calculation

```python
optimal_count = (width * height) / 50
wall_adjustment = 1.0 + (0.5 * wall_density)
final_count = min(max(int(optimal_count * wall_adjustment), 1), (width * height) / 10)
```

### Agent Movement

```python
move_strategy = "manhattan"  # Horizontal first, then vertical
frontier_selection = "nearest"  # Greedy nearest unclaimed
```

### Communication

```python
network = "loopback (127.0.0.1)"
protocol = "UDP"
packet_max_size = 1024 bytes
```

---

## Files Modified/Created

### Modified

- **NodeClass.py**: Complete rewrite (400+ lines)
- **spawner.py**: Dynamic calculation + initialization
- **maze_exploration.py**: New simulation framework

### Created

- **PROTOCOL.md**: Communication format specification
- **ARCHITECTURE.md**: This document

### Deprecated (still exist but unused)

- **agent_count.py**: Old agent calculation (goal-directed)
- **maze_exploration.py old code**: explore_forward() function

---

## Future Enhancements

Potential improvements to the architecture:

1. **Persistence**: Save/load swarm state to resume exploration
2. **Async I/O**: Full asyncio integration for real parallel execution
3. **Visualization**: Real-time web dashboard of swarm progress
4. **Advanced Routing**: A\* pathfinding instead of Manhattan distance
5. **Goal Signaling**: Dedicated GOAL_FOUND packet type
6. **Metrics**: Collect statistics on frontier efficiency
7. **Adaptive Swarm**: Dynamic agent population adjustments

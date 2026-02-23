"""
test_backend_simulation.py: Comprehensive test of the Fixed-Size Frontier Swarm

This script:
1. Creates a 20x20 maze with walls and open paths
2. Spawns a dynamic swarm of agents
3. Visualizes the exploration in real-time with ASCII art
4. Simulates UDP message delivery locally
5. Displays metrics (frontier count, exploration progress, agent status)
6. Runs for up to 200 ticks or until goal reached
"""


import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Tuple, Set, Dict
from spawner import spawn_agents
from NodeClass import Node
import contextlib
import io

# ============================================================================
# TASK 1: Maze Definition & Setup
# ============================================================================

def create_test_maze() -> List[List[int]]:
    """
    Create a complex 20x20 maze with walls (1), open paths (0), and rooms.
    
    Returns:
        20x20 2D array
    """
    # Manually designed maze with multiple paths, dead ends, and rooms
    maze = [
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    return maze


def count_open_cells(maze: List[List[int]]) -> int:
    """Count total open (non-wall) cells in maze."""
    return sum(row.count(0) for row in maze)


# ============================================================================
# TASK 2: ASCII Visualization
# ============================================================================

def get_local_grid_view(maze: List[List[int]], position: Tuple[int, int], radius: int = 2) -> List[List[int]]:
    """
    Extract a local grid view centered on the agent's position.
    
    Args:
        maze: Full maze grid
        position: (x, y) agent position
        radius: How many cells in each direction to include
    
    Returns:
        2D array representing the local view
    """
    if not position:
        return [[]]
    
    x, y = position
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    
    # Extract view
    view = []
    for i in range(x - radius, x + radius + 1):
        row = []
        for j in range(y - radius, y + radius + 1):
            if 0 <= i < rows and 0 <= j < cols:
                row.append(maze[i][j])
            else:
                row.append(1)  # Treat out-of-bounds as walls
        view.append(row)
    
    return view


def render_ascii_map(maze: List[List[int]], agents: List[Node], tick: int, start: Tuple[int, int], goal: Tuple[int, int]):
    """
    Render the maze with agent positions and exploration status.
    
    Symbols:
    - '#' = Wall
    - '.' = Unexplored open path
    - '░' = Explored path (in any agent's local_map)
    - '0'-'9' = Agent position (agent ID)
    - 'S' = Start (if not occupied by agent)
    - 'E' = End/Goal (if not occupied by agent)
    
    Args:
        maze: Full maze grid
        agents: List of agent objects
        tick: Current tick number
        start: Starting position
        goal: Goal position
    """
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    rows = len(maze)
    cols = len(maze[0])
    
    # Build explored set (union of all agent local_maps)
    explored_set: Set[Tuple[int, int]] = set()
    for agent in agents:
        explored_set.update(agent.local_map.keys())
    
    # Build agent position map
    agent_pos_map: Dict[Tuple[int, int], Node] = {}
    for agent in agents:
        if agent.current_position:
            agent_pos_map[agent.current_position] = agent
    
    # Render maze
    print("\n" + "="*80)
    print(f"FIXED-SIZE FRONTIER SWARM EXPLORATION - TICK {tick}")
    print("="*80)
    print()
    
    for i in range(rows):
        for j in range(cols):
            pos = (i, j)
            
            # Priority: Agent > Goal > Start > Explored > Wall > Unexplored
            if pos in agent_pos_map:
                agent = agent_pos_map[pos]
                print(str(agent.agent_id % 10), end=" ")
            elif pos == goal:
                print("E", end=" ")
            elif pos == start:
                print("S", end=" ")
            elif maze[i][j] == 1:
                print("#", end=" ")
            elif pos in explored_set:
                print("░", end=" ")
            else:
                print(".", end=" ")
        print()
    
    print("\n" + "="*80)
    print("Legend: # = Wall | . = Unexplored | ░ = Explored | S = Start | E = End | 0-9 = Agent ID")
    print("="*80)


def print_metrics(agents: List[Node], maze: List[List[int]], tick: int, goal_reached: bool, total_open_cells: int):
    """
    Print simulation metrics at the bottom of the display.
    
    Args:
        agents: List of agent objects
        maze: Maze grid
        tick: Current tick number
        goal_reached: Whether any agent reached goal
        total_open_cells: Total explorable cells in maze
    """
    # Calculate total unique explored cells
    explored_set: Set[Tuple[int, int]] = set()
    for agent in agents:
        explored_set.update(agent.local_map.keys())
    
    # Calculate total unique frontiers
    all_frontiers: Set[Tuple[int, int]] = set()
    for agent in agents:
        all_frontiers.update(agent.frontiers)
    
    # Exploration percentage
    explored_pct = (len(explored_set) / total_open_cells * 100) if total_open_cells > 0 else 0
    
    print(f"\nMETRICS:")
    print(f"  Tick: {tick}")
    print(f"  Goal Reached: {'✓ YES' if goal_reached else 'No'}")
    print(f"  Total Cells Explored: {len(explored_set)} / {total_open_cells} ({explored_pct:.1f}%)")
    print(f"  Unique Frontiers Discovered: {len(all_frontiers)}")
    print()
    
    print(f"AGENT STATUS:")
    for agent in agents:
        status_parts = []
        
        if agent.target_frontier:
            dist = abs(agent.current_position[0] - agent.target_frontier[0]) + \
                   abs(agent.current_position[1] - agent.target_frontier[1])
            status_parts.append(f"Moving to {agent.target_frontier} (dist={dist})")
        else:
            status_parts.append("Idle (selecting frontier)")
        
        status_parts.append(f"Pos={agent.current_position}")
        status_parts.append(f"Known={len(agent.local_map)} cells")
        
        status = " | ".join(status_parts)
        print(f"  {agent.name}: {status}")
    
    print()


def render_ascii_map_to_file(maze: List[List[int]], agents: List[Node], tick: int, start: Tuple[int, int], goal: Tuple[int, int], output_file):
    """
    Render the maze with agent positions and write to file.
    
    Symbols:
    - '#' = Wall
    - '.' = Unexplored open path
    - '░' = Explored path (in any agent's local_map)
    - '0'-'9' = Agent position (agent ID)
    - 'S' = Start (if not occupied by agent)
    - 'E' = End/Goal (if not occupied by agent)
    
    Args:
        maze: Full maze grid
        agents: List of agent objects
        tick: Current tick number
        start: Starting position
        goal: Goal position
        output_file: File object to write to
    """
    rows = len(maze)
    cols = len(maze[0])
    
    # Build explored set (union of all agent local_maps)
    explored_set: Set[Tuple[int, int]] = set()
    for agent in agents:
        explored_set.update(agent.local_map.keys())
    
    # Build agent position map
    agent_pos_map: Dict[Tuple[int, int], Node] = {}
    for agent in agents:
        if agent.current_position:
            agent_pos_map[agent.current_position] = agent
    
    # Write to file
    output_file.write("\n" + "="*80 + "\n")
    output_file.write(f"FIXED-SIZE FRONTIER SWARM EXPLORATION - TICK {tick}\n")
    output_file.write("="*80 + "\n\n")
    
    for i in range(rows):
        for j in range(cols):
            pos = (i, j)
            
            # Priority: Agent > Goal > Start > Explored > Wall > Unexplored
            if pos in agent_pos_map:
                agent = agent_pos_map[pos]
                output_file.write(str(agent.agent_id % 10) + " ")
            elif pos == goal:
                output_file.write("E ")
            elif pos == start:
                output_file.write("S ")
            elif maze[i][j] == 1:
                output_file.write("# ")
            elif pos in explored_set:
                output_file.write("░ ")
            else:
                output_file.write(". ")
        output_file.write("\n")
    
    output_file.write("\n" + "="*80 + "\n")
    output_file.write("Legend: # = Wall | . = Unexplored | ░ = Explored | S = Start | E = End | 0-9 = Agent ID\n")
    output_file.write("="*80 + "\n")
    output_file.flush()


def print_metrics_to_file(agents: List[Node], maze: List[List[int]], tick: int, goal_reached: bool, total_open_cells: int, output_file):
    """
    Print simulation metrics to file.
    
    Args:
        agents: List of agent objects
        maze: Maze grid
        tick: Current tick number
        goal_reached: Whether any agent reached goal
        total_open_cells: Total explorable cells in maze
        output_file: File object to write to
    """
    # Calculate total unique explored cells
    explored_set: Set[Tuple[int, int]] = set()
    for agent in agents:
        explored_set.update(agent.local_map.keys())
    
    # Calculate total unique frontiers
    all_frontiers: Set[Tuple[int, int]] = set()
    for agent in agents:
        all_frontiers.update(agent.frontiers)
    
    # Exploration percentage
    explored_pct = (len(explored_set) / total_open_cells * 100) if total_open_cells > 0 else 0
    
    output_file.write(f"\nMETRICS:\n")
    output_file.write(f"  Tick: {tick}\n")
    output_file.write(f"  Goal Reached: {'✓ YES' if goal_reached else 'No'}\n")
    output_file.write(f"  Total Cells Explored: {len(explored_set)} / {total_open_cells} ({explored_pct:.1f}%)\n")
    output_file.write(f"  Unique Frontiers Discovered: {len(all_frontiers)}\n")
    output_file.write("\n")
    
    output_file.write(f"AGENT STATUS:\n")
    for agent in agents:
        status_parts = []
        
        if agent.target_frontier:
            dist = abs(agent.current_position[0] - agent.target_frontier[0]) + \
                   abs(agent.current_position[1] - agent.target_frontier[1])
            status_parts.append(f"Moving to {agent.target_frontier} (dist={dist})")
        else:
            status_parts.append("Idle (selecting frontier)")
        
        status_parts.append(f"Pos={agent.current_position}")
        status_parts.append(f"Known={len(agent.local_map)} cells")
        
        status = " | ".join(status_parts)
        output_file.write(f"  {agent.name}: {status}\n")
    
    output_file.write("\n")
    output_file.flush()


# ============================================================================
# TASK 3: Simulation Loop with Message Delivery
# ============================================================================

def collect_outgoing_messages(agents: List[Node]) -> Dict[int, List[str]]:
    """
    Collect all messages that agents would send this tick.
    
    In the real system, these would be sent via UDP. For testing, we'll
    collect them and deliver them immediately to other agents.
    
    Args:
        agents: List of agents
    
    Returns:
        Dictionary mapping agent index to list of (recipient_port, json_payload) tuples
    """
    # This is a simplified version - in the real implementation, agents
    # send UDP packets. For testing, we'll capture them by temporarily
    # intercepting the send_json method.
    
    messages_sent = {}
    for i, agent in enumerate(agents):
        messages_sent[i] = []
    
    # Store original send_json
    original_send_json = {}
    for i, agent in enumerate(agents):
        original_send_json[i] = agent.send_json
    
    # Intercept send_json to capture messages
    def make_capture_sender(agent_idx, agent):
        captured_messages = messages_sent[agent_idx]
        def capture_send(ip: str, port: int, payload: dict):
            captured_messages.append((port, payload))
        return capture_send
    
    for i, agent in enumerate(agents):
        agent.send_json = make_capture_sender(i, agent)
    
    # Run tick for each agent (this will capture their outgoing messages)
    # We'll actually call tick in the main loop and collect messages there
    
    # Restore original send_json
    for i, agent in enumerate(agents):
        agent.send_json = original_send_json[i]
    
    return messages_sent


def simulate_tick(agents: List[Node], maze: List[List[int]], verbose: bool = False) -> List[Tuple[int, dict]]:
    """
    Simulate one tick: have agents act and collect messages.
    
    Args:
        agents: List of agents to tick
        maze: Full maze grid
        verbose: Whether to print debug messages
    
    Returns:
        List of (sender_agent_id, message_dict) tuples
    """
    messages = []
    
    # Temporarily suppress print output from agents during tick
    import io
    import contextlib
    
    # Intercept send_json to capture messages
    original_send_methods = {}
    
    def make_message_capturer(agent_idx):
        def capture_and_send(ip: str, port: int, payload: dict):
            messages.append((agent_idx, payload))
        return capture_and_send
    
    # Replace send_json with message capturer
    for i, agent in enumerate(agents):
        original_send_methods[i] = agent.send_json
        agent.send_json = make_message_capturer(i)
    
    # Execute tick for each agent
    # Pass the FULL maze, not a local view - the agent's _scan_neighbors handles bounds correctly
    if verbose:
        for agent in agents:
            if agent.current_position:
                agent.tick(maze)
    else:
        # Suppress debug output
        with contextlib.redirect_stdout(io.StringIO()):
            for agent in agents:
                if agent.current_position:
                    agent.tick(maze)
    
    # Restore original send_json
    for i, agent in enumerate(agents):
        agent.send_json = original_send_methods[i]
    
    return messages


def deliver_messages(agents: List[Node], messages: List[Tuple[int, dict]]):
    """
    Deliver captured messages to their recipients.
    
    Args:
        agents: List of agents
        messages: List of (sender_agent_id, payload) tuples
    """
    for sender_id, payload in messages:
        # Deliver to all other agents
        for recipient in agents:
            if recipient.agent_id != sender_id:
                # Convert payload to JSON string and process
                import json
                msg_str = json.dumps(payload)
                recipient.process_message(msg_str)


# ============================================================================
# TASK 4: Main Simulation
# ============================================================================

def main():
    """Main simulation entry point."""
    
    # Create output file for logging
    output_file = open("simulation_output.txt", "w")
    
    def log(message):
        """Write to file only."""
        output_file.write(message + "\n")
        output_file.flush()
    
    
    with contextlib.redirect_stdout(io.StringIO()):
        log("\n" + "="*80)
        log("FIXED-SIZE FRONTIER SWARM - BACKEND SIMULATION TEST")
        log("="*80)
        
        # TASK 1: Setup
        log("\n[1/4] Creating 20x20 maze...")
        maze = create_test_maze()
        start = (0, 0)
        goal = (19, 19)
        total_open_cells = count_open_cells(maze)
        
        log(f"  Maze size: 20x20 = 400 cells")
        log(f"  Open (explorable) cells: {total_open_cells}")
        log(f"  Start: {start}, Goal: {goal}")
        
        log("\n[2/4] Spawning dynamic swarm...")
        
        agents = spawn_agents(maze, start)
        
        log(f"  Spawned {len(agents)} agents")
        
        if not agents:
            log("ERROR: No agents spawned! Exiting.")
            output_file.close()
            return
        
        # TASK 2: Initialize visualization
        log("\n[3/4] Starting simulation loop (200 ticks max)...")
        log("\nInitial state:")
        
        render_ascii_map_to_file(maze, agents, 0, start, goal, output_file)
        print_metrics_to_file(agents, maze, 0, False, total_open_cells, output_file)
        
        # TASK 3: Main simulation loop
        goal_reached = False
        max_ticks = 1000
        
        for tick in range(1, max_ticks + 1):
            # Simulate one tick
            messages = simulate_tick(agents, maze, verbose=False)
            
            # Deliver messages to agents
            deliver_messages(agents, messages)
            
            # Check if any agent reached goal
            for agent in agents:
                if agent.current_position == goal:
                    goal_reached = True
                    log(f"\n*** GOAL REACHED by {agent.name} at tick {tick}! ***\n")
                    break
            
            # Log visualization every tick
            render_ascii_map_to_file(maze, agents, tick, start, goal, output_file)
            print_metrics_to_file(agents, maze, tick, goal_reached, total_open_cells, output_file)
            
            if goal_reached:
                break
        
        # Final summary
        log("\n" + "="*80)
        log("SIMULATION COMPLETE")
        log("="*80)
        
        explored_set: Set[Tuple[int, int]] = set()
        for agent in agents:
            explored_set.update(agent.local_map.keys())
        
        explored_pct = (len(explored_set) / total_open_cells * 100) if total_open_cells > 0 else 0
        
        log(f"\nFinal Statistics:")
        log(f"  Ticks executed: {tick}")
        log(f"  Goal reached: {'YES ✓' if goal_reached else 'NO'}")
        log(f"  Total cells explored: {len(explored_set)} / {total_open_cells} ({explored_pct:.1f}%)")
        log(f"  Agents in swarm: {len(agents)}")
        log("")
        
        log("Per-Agent Summary:")
        for agent in agents:
            log(f"  {agent.name}:")
            log(f"    Final position: {agent.current_position}")
            log(f"    Cells discovered: {len(agent.local_map)}")
            log(f"    Frontiers identified: {len(agent.frontiers)}")
            if agent.target_frontier:
                dist = abs(agent.current_position[0] - agent.target_frontier[0]) + \
                       abs(agent.current_position[1] - agent.target_frontier[1])
                log(f"    Pursuing frontier: {agent.target_frontier} (distance: {dist})")
            else:
                log(f"    Status: Idle (no target frontier)")
        
        log("\n" + "="*80)
        log("Test completed.")
        log("="*80 + "\n")
        
        output_file.close()
    
    print("✓ Simulation complete! Output saved to simulation_output.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
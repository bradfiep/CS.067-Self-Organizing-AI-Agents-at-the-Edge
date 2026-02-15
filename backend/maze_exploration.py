"""
maze_exploration.py: Main orchestration for Fixed-Size Swarm with Frontier-Based Exploration

Architecture:
1. Calculate optimal swarm size based on maze dimensions and wall density
2. Spawn ALL agents at the starting position (fixed-size swarm)
3. Run simulation ticks where each agent:
   - Scans local neighbors and identifies frontiers
   - Broadcasts map updates via UDP
   - Listens for updates from other agents
   - Selects and claims unclaimed frontiers
   - Moves toward their claimed frontier
4. No new agents spawn during runtime

This replaces the old recursive spawning approach with a collaborative, frontier-based model.
"""

from spawner import spawn_agents, calculate_optimal_agent_count
import asyncio
from typing import List, Tuple


def simulate_swarm_exploration(maze: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int], max_ticks: int = 1000):
    """
    Run the swarm exploration simulation.
    
    Args:
        maze: 2D array where 0=open, 1=wall
        start: (x, y) starting position
        goal: (x, y) goal position
        max_ticks: Maximum number of simulation ticks to run
    """
    # SPAWN PHASE: Create all agents upfront (no runtime spawning)
    agents = spawn_agents(maze, start)
    
    if not agents:
        print("ERROR: No agents were spawned!")
        return
    
    print(f"\n=== STARTING SWARM EXPLORATION ===")
    print(f"Swarm size: {len(agents)} agents")
    print(f"Start: {start}, Goal: {goal}")
    print(f"Max ticks: {max_ticks}\n")
    
    # SIMULATION PHASE: Run ticks
    tick_count = 0
    goal_reached = False
    
    while tick_count < max_ticks and not goal_reached:
        tick_count += 1
        
        print(f"--- TICK {tick_count} ---")
        
        # Each agent performs one tick
        for agent in agents:
            # Get local grid view (simplified - in real implementation, would extract from full maze)
            # For now, simulate a 3x3 local view around agent position
            local_view = get_local_grid_view(maze, agent.current_position)
            
            # Agent state machine: scan, broadcast, listen, decide, move
            agent.tick(local_view)
            
            # Check if goal reached
            if agent.current_position == goal:
                print(f"\n*** GOAL REACHED by {agent.name} at {goal} ***")
                goal_reached = True
                break
        
        # Print swarm status
        total_nodes_discovered = sum(len(agent.local_map) for agent in agents)
        total_unique_nodes = len(set(
            node for agent in agents for node in agent.local_map.keys()
        ))
        total_frontiers = len(set(
            frontier for agent in agents for frontier in agent.frontiers
        ))
        
        print(f"Swarm status: {total_unique_nodes} unique nodes, {total_frontiers} frontiers")
        print(f"Agent positions: {[agent.current_position for agent in agents]}\n")
        
        if tick_count % 100 == 0:
            print(f"[Progress] Completed {tick_count} ticks...")
    
    print(f"\n=== SIMULATION COMPLETE ===")
    print(f"Ticks executed: {tick_count}")
    print(f"Goal reached: {goal_reached}")
    
    # Final summary
    print(f"\n=== EXPLORATION SUMMARY ===")
    for i, agent in enumerate(agents):
        print(f"\n{agent.name}:")
        print(f"  Final position: {agent.current_position}")
        print(f"  Nodes discovered: {len(agent.local_map)}")
        print(f"  Frontiers identified: {len(agent.frontiers)}")
        print(f"  Target frontier: {agent.target_frontier}")


def get_local_grid_view(maze: List[List[int]], position: Tuple[int, int], radius: int = 1) -> List[List[int]]:
    """
    Extract a local grid view centered on the agent's position.
    
    Args:
        maze: Full maze grid
        position: (x, y) agent position
        radius: How many cells in each direction to include (default 1 = 3x3 view)
    
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


def main():
    """Run a test swarm exploration on a sample maze."""
    
    # Test maze with multiple paths
    maze = [
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    ]
    
    start = (0, 0)
    goal = (11, 9)
    
    # Run simulation
    simulate_swarm_exploration(maze, start, goal, max_ticks=500)


if __name__ == "__main__":
    main()
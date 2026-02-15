"""
spawner.py: Dynamic agent spawning for fixed-size swarms.

The spawner calculates the optimal number of agents based on maze size and wall density,
then instantiates all agents at the starting position. No agents are spawned during runtime.
"""

from NodeClass import Node
import socket
from typing import List, Tuple


def calculate_optimal_agent_count(maze: List[List[int]]) -> int:
    """
    Calculate the optimal number of agents based on maze dimensions and wall density.
    
    Logic:
    - Base: optimal_count = (width * height) / 50
    - Adjustment: More walls = slightly more agents (up to 1.5x base), to handle complexity
    - Cap: Never exceed (width * height) / 10 to avoid over-provisioning
    
    Args:
        maze: 2D array where 0=open, 1=wall
    
    Returns:
        Optimal number of agents to spawn
    """
    if not maze or not maze[0]:
        return 1
    
    height = len(maze)
    width = len(maze[0])
    total_cells = width * height
    
    # Base calculation: 1 agent per 50 cells
    base_count = max(1, total_cells // 50)
    
    # Calculate wall density
    wall_count = sum(row.count(1) for row in maze)
    wall_density = wall_count / total_cells if total_cells > 0 else 0
    
    # Adjust based on wall density: more walls = slightly more agents
    # Linear interpolation: at 0% walls, 1.0x; at 100% walls, 1.5x
    wall_adjustment = 1.0 + (0.5 * wall_density)
    
    optimal_count = int(base_count * wall_adjustment)
    
    # Cap: never exceed 1 agent per 10 cells
    max_count = max(1, total_cells // 10)
    optimal_count = min(optimal_count, max_count)
    
    # Ensure at least 1 agent
    optimal_count = max(1, optimal_count)
    
    return optimal_count


def find_available_port(start_port: int = 9000, max_attempts: int = 1000) -> int:
    """
    Find an available UDP port starting from start_port.
    
    Args:
        start_port: Starting port number to check
        max_attempts: Maximum number of ports to try before giving up
    
    Returns:
        An available port number
    
    Raises:
        RuntimeError: If no available port found after max_attempts
    """
    port = start_port
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            port += 1
    
    raise RuntimeError(f"No available ports found after {max_attempts} attempts")


def spawn_agents(maze: List[List[int]], start_position: Tuple[int, int]) -> List[Node]:
    """
    Spawn a fixed-size swarm of agents at the maze start position.
    
    This function:
    1. Calculates optimal_agent_count based on maze size and wall density
    2. Instantiates all agents at the start_position
    3. Configures inter-agent communication ports
    
    NO AGENTS ARE SPAWNED DURING RUNTIME - all agents are created here.
    
    Args:
        maze: 2D array representing the maze (0=open, 1=wall)
        start_position: (x, y) tuple for agent starting position
    
    Returns:
        List of instantiated Node agents
    """
    # Calculate optimal agent count
    optimal_count = calculate_optimal_agent_count(maze)
    print(f"\n=== SWARM SPAWNING ===")
    print(f"Maze size: {len(maze)} x {len(maze[0])} ({len(maze) * len(maze[0])} cells)")
    print(f"Calculated optimal agent count: {optimal_count}")
    
    agents = []
    base_port = 9000
    
    # Instantiate agents
    for i in range(optimal_count):
        try:
            port = find_available_port(base_port + i * 10)
            new_agent = Node(port=port, name=f"Agent_{i}", agent_id=i)
            new_agent.set_initial_position(start_position)
            agents.append(new_agent)
        except RuntimeError as e:
            print(f"Failed to create Agent_{i}: {e}")
            break
    
    print(f"Successfully spawned {len(agents)} agents")
    
    # Configure inter-agent communication: each agent knows all other agents' ports
    agent_ports = [agent.port for agent in agents]
    for agent in agents:
        agent.peer_ports = agent_ports
    
    print(f"Configured peer communication for all agents")
    return agents


def main():
    """Test the spawner with a sample maze."""
    
    # Test maze
    maze = [
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    
    start = (0, 0)
    
    # Spawn agents
    agents = spawn_agents(maze, start)
    
    print(f"\n=== AGENT STATUS ===")
    for agent in agents:
        print(f"{agent.name}: port={agent.port}, position={agent.current_position}")
    
    print(f"\n=== FRONTIER STATUS (Initial) ===")
    for agent in agents:
        print(f"{agent.name}: frontiers={agent.frontiers}, local_map={len(agent.local_map)} nodes")


if __name__ == "__main__":
    main()


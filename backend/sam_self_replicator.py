'''
Author: Samuel Garcia Lopez
Date: 1.27.2026

Description:
This module contains a function that details how an agent should self
replicate within the maze environment.

It uses the function inside of replicate.py to spawn new agents based on
the demand calculated from the maze structure.

Code aided by ChatGPT.
'''

def agent_demand(maze):
    """
    Estimate agent demand based on maze branching and frontier size.

    Args:
        maze (list[list[int]]): 0 = open, 1 = wall

    Returns:
        int: number of agents to spawn

    Description: 
        The agent demand is estimated by using the number of junctions. A junction is 
        defined as a cell with 3 or more open neighbors (where the maze branches in three different possible directions).
        We also use the size of the frontier (cells with less than 4 open neighbors) to estimate demand. The final demand 
        is the maximum between the number of junctions and a quarter of the frontier size.

        formula that calculates our efficency: time for one agent to explore / (time for multiple agents to explore * number of agents)


        
    """

    height = len(maze)
    width = len(maze[0])

    def neighbors(x, y):
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny

    open_cells = 0
    junctions = 0
    frontier = 0

    for y in range(height):
        for x in range(width):
            if maze[y][x] != 0:
                continue

            open_cells += 1
            open_neighbors = sum(
                1 for nx, ny in neighbors(x, y) if maze[ny][nx] == 0
            )

            # Junction: real parallelism opportunity
            if open_neighbors >= 3:
                junctions += 1

            # Frontier: edge of exploration
            if open_neighbors < 4:
                frontier += 1

    # --- Demand estimation ---
    # Branching dominates early, frontier dominates later
    demand = max(
        junctions,
        frontier // 4  # frontier is noisier; downscale it
    )

    # Soft cap: no point exceeding reasonable parallelism
    max_agents = max(4, open_cells // 8)

    return max(1, min(demand, max_agents))

#test
def main():
    maze = [
        [0,1,0,0,0,1,0,0,0,0],
        [0,1,0,1,0,1,0,1,1,0],
        [0,0,0,1,0,0,0,1,0,0],
        [1,1,0,1,1,1,0,1,0,1],
        [0,0,0,0,0,0,0,1,0,0],
        [0,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,0,1,0,1,0,0],
        [0,1,0,1,0,1,0,0,1,0],
        [0,1,0,1,0,1,0,1,1,0],
        [0,0,0,1,0,0,0,1,0,0],
        [1,1,0,1,1,1,0,1,0,1],
        [0,0,0,1,0,0,0,0,0,0]
    ]

    demand = agent_demand(maze)
    print(f"Calculated agent demand: {demand}")

if __name__ == "__main__":  
    main()
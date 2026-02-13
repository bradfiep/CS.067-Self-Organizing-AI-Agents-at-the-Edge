''' Class that performs the forward motion of the agents.
1)It calls compute agents function.
2)Spawns exactly the number of the agents calculated to solve the maze.
3)Then each agent:
    -checks neighbors
    -if 0 => reports dead end
    -if 1 => moves forward
    -if 2+ => spawn children in these directions, except for foward'''


from collections import deque
from agent_count import calculate_required_agents_to_goal
from spawner import spawn_agents
from collections import deque


def explore_forward(maze, start, goal, agents):
    rows, cols = len(maze), len(maze[0])
    visited = set()
    #active agent list to track them
    active_agents = [(0, start)]
    #directions to do
    DIRS = [(-1,0), (1,0), (0,-1), (0,1)]

    while active_agents:
        new_active = []

        for agent_id, (r, c) in active_agents:

            if (r, c) in visited:
                continue

            visited.add((r, c))
            print(f"{agents[agent_id].name} at ({r},{c})")

            if (r, c) == goal:
                print("Goal reached!")
                return

            neighbors = []

            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc

                if (0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited):
                    neighbors.append((nr, nc))

            if not neighbors:
                print(f"{agents[agent_id].name} reached DEAD END")
                #CALL SAM'S FUNCTION
                continue

            #first neighbor => parent continues
            new_active.append((agent_id, neighbors[0]))
            #remaining neighbors => assign next available agents
            next_agent_id = len(new_active)

            for nbr in neighbors[1:]:
                if next_agent_id >= len(agents):
                    print("No more agents available")
                    return

                new_active.append((next_agent_id, nbr))
                next_agent_id += 1

        active_agents = new_active
    print("Goal unreachable.")


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
    start = (0, 0)
    goal = (11, 9)

    total_agents, max_parallel = calculate_required_agents_to_goal(maze, start, goal)
    print("Total agents required:", total_agents)
    print("Max simultaneous agents:", max_parallel)

    agents = spawn_agents(total_agents)
    explore_forward(maze, start, goal, agents)


if __name__ == "__main__":
    main()
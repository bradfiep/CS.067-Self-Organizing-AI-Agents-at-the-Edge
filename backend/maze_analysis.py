from collections import deque

def calculate_required_agents_to_goal(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    visited = set()

    DIRS = [(-1,0), (1,0), (0,-1), (0,1)]
    stack = deque()
    stack.append((start[0], start[1], 1))

    total_agents = 1
    max_simultaneous_agents = 1

    while stack:
        r, c, active_agents = stack.pop()

        if (r, c) in visited:
            continue

        visited.add((r, c))
        max_simultaneous_agents = max(
            max_simultaneous_agents,
            active_agents
        )

        #check for goal and return if reached the goal, no more agents would be needed    
        if (r, c) == end:
            return total_agents, max_simultaneous_agents

        neighbors = []
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows and
                0 <= nc < cols and
                maze[nr][nc] == 0 and
                (nr, nc) not in visited
            ):
                neighbors.append((nr, nc))

        if not neighbors:
            continue

        stack.append((neighbors[0][0], neighbors[0][1], active_agents))

        for nbr in neighbors[1:]:
            total_agents += 1
            stack.append((nbr[0], nbr[1], active_agents + 1))

    #endpoint was unreachable
    return total_agents, max_simultaneous_agents

#stops when the goal is explored, so calculates needed agents only until they find the goal cell



#testing part
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
    end = (11, 9)

    total, max_parallel = calculate_required_agents_to_goal(
        maze, start, end
    )

    print("=== Goal-directed Agent Analysis ===")
    print("Total agents spawned:", total)
    print("Max simultaneous agents:", max_parallel)


if __name__ == "__main__":
    main()
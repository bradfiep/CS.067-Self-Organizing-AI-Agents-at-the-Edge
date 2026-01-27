from NodeClass import NodeClass

def spawn_agents(num_agents):
    agents = []

    for i in range(num_agents):
        agent = NodeClass(
            port=0,
            name=f"Agent-{i+1}"
        )
        agents.append(agent)

    print(f"Created {num_agents} agents")
    return agents

from NodeClass import Node
import socket

def spawn_agents(num_agents):
    #Make sure that we have an available port for our new agen
    def find_available_port(start_port):
        """Find an available port starting from start_port"""
        port = start_port
        while port < 65535:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                port += 1
        raise RuntimeError("No available ports found")
    
    agents = []
    
    #Make the new agent(s)
    for i in range(num_agents):
        try:
            available_port = find_available_port(0 + i)
            new_agent = Node(port=available_port, name=f"Agent_{i}")
            agents.append(new_agent)
        except RuntimeError as e:
            print(f"Failed to create Agent_{i}: {e}")
            break
    
    print(f"Created {len(agents)} agents")
    return agents


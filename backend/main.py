import asyncio
import json
import websockets
import NodeClass
from spawner import spawn_agents

connected_clients = set()
event_loop = None  


# -------------------------
# WebSocket handler (Frontend → Python)
# -------------------------
async def handler(websocket):
    connected_clients.add(websocket)
    print("New client connected")

    try:
        async for message in websocket:
            data = json.loads(message)
            maze = data.get("maze")
            start = data.get("start")
            end = data.get("end")

            # Acknowledge receipt to the frontend
            await websocket.send(json.dumps({
                "type": "ack",
                "status": "Maze received. Starting swarm simulation..."
            }))

            # Trigger the live simulation directly
            asyncio.create_task(run_live_simulation(maze, start, end, websocket))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

# -------------------------
# UDP Node listener (Node → Python)
# -------------------------
node = NodeClass.Node(9000, "Node1", 0)

def on_udp_message(msg, addr):
    print(f"Node received message: {msg} from {addr}")

    # Forward Node message to all WebSocket clients
    asyncio.run_coroutine_threadsafe(
        broadcast(msg),
        event_loop
    )


node.on_message = on_udp_message


# -------------------------
# Broadcast to all connected WebSocket clients
# -------------------------
async def broadcast(message):
    if not connected_clients:
        return

    # If message is already JSON, forward as-is
    try:
        payload = json.loads(message)
    except Exception:
        payload = {
            "type": "node_message",
            "payload": message
        }

    msg_str = json.dumps(payload)

    await asyncio.gather(
        *(ws.send(msg_str) for ws in connected_clients)
    )


# -------------------------
# Simulation logic (Node → Python → Frontend)
# -------------------------
async def run_live_simulation(maze, start, end, websocket):
    # 1. Spawn the swarm using your existing spawner logic
    agents = spawn_agents(maze, tuple(start))
    
    # Start UDP listeners for all agents so they can communicate with each other
    listener_tasks = [asyncio.create_task(agent.web_listen()) for agent in agents]
    
    # Register agents for frontend agent list
    for agent in agents:
        await websocket.send(json.dumps({
            "type": "agent_registered",
            "agent_name": agent.name,
            "agent_id": agent.agent_id,
            "position": list(agent.current_position),
            "status": "exploring"
        }))
    
    tick = 0
    goal_reached = False
    
    # 2. Run the simulation loop
    while not goal_reached and tick < 500: # Add a max_ticks failsafe
        tick += 1
        
        # Array to hold the state of all agents for the frontend
        agent_data = []
        
        for agent in agents:
            # Execute the agent's logic for this tick
            # Note: You may need to adapt this depending on how agent.tick() 
            # receives the global/local view in your exact implementation
            agent.tick(maze) 
            
            # Check if anyone found the end
            if agent.current_position == tuple(end):
                goal_reached = True
                # Send log to frontend activity page
                await websocket.send(json.dumps({
                    "type": "agent_goal_reached",
                    "agent_name": agent.name,
                    "agent_id": agent.agent_id,
                    "position": list(agent.current_position),
                    "tick": tick
                }))
            
            # Send frontier message 
            if agent.target_frontier:
                await websocket.send(json.dumps({
                    "type": "agent_frontier",
                    "agent_name": agent.name,
                    "agent_id": agent.agent_id,
                    "frontier": list(agent.target_frontier),
                    "tick": tick
                }))
            
            # Package the agent's current state
            agent_data.append({
                "id": agent.agent_id,
                "position": agent.current_position,
                "target_frontier": agent.target_frontier,
                "cells_discovered": len(agent.local_map)
            })

        # 3. Create the JSON payload for the frontend
        payload = {
            "type": "tick_update",
            "tick": tick,
            "goal_reached": goal_reached,
            "agents": agent_data
        }
        
        # 4. Send the data to the frontend
        await websocket.send(json.dumps(payload))
        
        # 5. Pause briefly to allow the frontend to render the frame smoothly
        await asyncio.sleep(0.1)
    
    # Compute coverage across all agents and send simulation summary
    explored = set()
    for agent in agents:
        explored.update(agent.local_map.keys())

    total_open = sum(1 for row in maze for cell in row if cell == 0)
    explored_pct = (len(explored) / total_open * 100) if total_open > 0 else 0

    await websocket.send(json.dumps({
        "type": "simulation_complete",
        "goal_reached": goal_reached,
        "tick": tick,
        "explored_cells": len(explored),
        "total_cells": total_open,
        "explored_pct": round(explored_pct, 1)
    }))

# -------------------------
# Main entry point
# -------------------------
async def main():
    global event_loop
    event_loop = asyncio.get_running_loop()  

    ws_server = await websockets.serve(handler, "0.0.0.0", 8080)
    udp_listener = asyncio.create_task(node.web_listen())

    print("🚀 WebSocket server running on ws://localhost:8080")

    await asyncio.gather(
        ws_server.wait_closed(),
        udp_listener
    )


if __name__ == "__main__":
    asyncio.run(main())

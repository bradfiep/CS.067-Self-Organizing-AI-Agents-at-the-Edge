import asyncio
from NodeClass import Node

# In progress doesn't work to recive brodcasts to more then one node 
broadcast_node = Node(9006, "BroadcastNode")

broadcast_node.broadcast_event(
	"One small step for man - one giant leap for mankind",
	multicast_group='224.1.1.1',
	ports=[5007, 5008]
)

print(f"[{broadcast_node.name}] Broadcasted message to multicast group 224.1.1.1 to ports [5007, 5008]")
// src/components/AgentActivity.tsx
import { useState, useEffect, useRef } from 'react';import Button from './Button';
import MazeGrid from './MazeGrid';

// Type definitions
interface Agent {
  id: string;
  name: string;
  position: [number, number];
  status: 'exploring' | 'inactive' | 'completed';
  color: string;
}

interface ActivityLog {
  id: string;
  timestamp: string;
  agentId: string;
  agentName: string;
  message: string;
  type: 'move' | 'info' | 'success' | 'error';
}

interface AgentActivityProps {
  onBack: () => void;
  messageQueue: string[];
  maze: number[][] | null;
  startPt: [number, number];
  endPt: [number, number];
}

interface BackendMessage {
  type: string;
  agent_name?: string;
  agent_id?: string;
  position?: [number, number];
  frontier?: [number, number];
  from_position?: [number, number];
  to_position?: [number, number];
  status?: string;
  goal_reached?: boolean;
  ticks?: number;
  explored_pct?: number;
}

// Agent list item component
function AgentListItem({ agent }: { agent: Agent }) {
  const position = agent.position || [0, 0];
  
  return (
    <div className="agent-card">
      <div className="agent-avatar" style={{ background: agent.color }}>
        {agent.name.charAt(agent.name.length - 1)}
      </div>
      <div className="agent-info">
        <div className="agent-name">{agent.name}</div>
        <div className="agent-details">
          <span>Status: {agent.status}</span>
          <span>Pos: ({position[0]},{position[1]})</span>
        </div>
      </div>
    </div>
  );
}

// Activity feed item component
function ActivityFeedItem({ log, agents }: { log: ActivityLog; agents: Agent[] }) {
  const agent = agents.find(a => a.name === log.agentName);
  const borderColor = agent ? agent.color : '#666'; 
  
  return (
    <div className="activity-log-item" style={{ borderLeftColor: borderColor }}>
      <div className="activity-log-time">{log.timestamp}</div>
      <div className="activity-log-agent" style={{ color: borderColor }}>
        [{log.agentName}]
      </div>
      <div className="activity-log-message">{log.message}</div>
    </div>
  );
}

export default function AgentActivity({
  onBack,
  messageQueue,
  maze,
  startPt,
  endPt
}: AgentActivityProps) {
  // Initialize agents with placeholder data
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const processedCount = useRef(0);

  const assignAgentColor = (agentName: string): string => {
    const colors = ['#297AEB', '#F28B1E', '#f8d32b', '#9718ad', '#e74337', '#1AB74E'];
    const agentNumber = agentName.match(/\d+/)?.[0] || agentName.charCodeAt(agentName.length - 1);
    const index = (typeof agentNumber === 'string' ? parseInt(agentNumber) : agentNumber) % colors.length;
    return colors[index];
  };

  const processMessage = (data: BackendMessage, timestamp: string) => {
    if (data.type === 'agent_registered') {
      if (!data.agent_name || !data.position) return;
      const newAgent: Agent = {
        id: data.agent_name.toLowerCase().replace(' ', '-'),
        name: data.agent_name,
        position: data.position,
        status: data.status as 'exploring' | 'inactive' | 'completed',
        color: assignAgentColor(data.agent_name)
      };
      setAgents(prev => {
        const exists = prev.some(a => a.id === newAgent.id);
        if (exists) return prev;
        return [...prev, newAgent];
      });
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: newAgent.id,
        agentName: data.agent_name,
        message: `Agent registered at position (${data.position[0]},${data.position[1]})`,
        type: 'info'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }

    else if (data.type === 'agent_move') {
      if (!data.agent_name || !data.from_position || !data.to_position) return;
      setAgents(prev => prev.map(agent =>
        agent.name === data.agent_name
          ? { ...agent, status: 'exploring', position: data.to_position! }
          : agent
      ));
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: data.agent_name.toLowerCase().replace(' ', '-'),
        agentName: data.agent_name,
        message: `Moving one step from (${data.from_position[0]},${data.from_position[1]}) to (${data.to_position[0]},${data.to_position[1]})`,
        type: 'move'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }

    else if (data.type === 'agent_frontier') {
      if (!data.agent_name || !data.frontier) return;
      setAgents(prev => prev.map(agent =>
        agent.name === data.agent_name && agent.status !== 'completed'
          ? { ...agent, status: 'exploring', position: data.frontier! }
          : agent
      ));
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: data.agent_name.toLowerCase().replace(' ', '-'),
        agentName: data.agent_name,
        message: `Exploring frontier (${data.frontier[0]},${data.frontier[1]})`,
        type: 'move'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }

    else if (data.type === 'agent_goal_reached') {
      if (!data.agent_name || !data.position) return;
      setAgents(prev => prev.map(agent =>
        agent.name === data.agent_name
          ? { ...agent, status: 'completed', position: data.position! }
          : agent
      ));
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: data.agent_name.toLowerCase().replace(' ', '-'),
        agentName: data.agent_name,
        message: `Reached goal (${data.position[0]},${data.position[1]}) ✓`,
        type: 'success'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }

    else if (data.type === 'simulation_complete') {
      const result = data.goal_reached ? 'Success' : 'Failed';
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: 'system',
        agentName: 'System',
        message: `${result} — ${data.ticks} ticks, ${data.explored_pct}% explored`,
        type: data.goal_reached ? 'success' : 'error'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }

    else if (data.type === 'ack') {
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        timestamp,
        agentId: 'system',
        agentName: 'System',
        message: data.status || 'Acknowledged',
        type: 'info'
      };
      setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
    }
  };

  useEffect(() => {
    const unprocessed = messageQueue.slice(processedCount.current);
    if (unprocessed.length === 0) return;

    unprocessed.forEach(msg => {
      try {
        const data = JSON.parse(msg);
        const timestamp = new Date().toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
        processMessage(data, timestamp);
      } catch (err) {
        console.error('Error parsing backend message:', err);
      }
    });

    processedCount.current = messageQueue.length;
  }, [messageQueue]);

  return (
    <div className="activity-section">
      <div className="activity-section-inner">
        <h1 className="activity-title">Agent Activity</h1>

        <div className="activity-content">
          <div className="activity-sidebar">
            {/* Agent List */}
            <div style={{ flex: 5, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
              <div className="agent-list-container">
                <div className="activity-section-header">
                    <h2 className="activity-section-title">Agent List</h2>
                </div>
                <div className='agent-list-scroll'>
                    {agents.map(agent => (
                  <AgentListItem key={agent.id} agent={agent} />
                ))}
                </div>
              </div>
            </div>

            {/* Maze Preview Section */}
            <div style={{ flex: 7, minHeight: 0 }}>
              <div className="activity-maze-preview">
                {maze ? (
                  <MazeGrid maze={maze} start={startPt} end={endPt} />
                ) : (
                  <div style={{ color: '#999', textAlign: 'center', padding: '2rem' }}>
                    Maze Preview
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="activity-feed-wrapper">
            <div className="activity-feed-container">
                <div className="activity-section-header">
                    <h2 className="activity-section-title">Activity Feed</h2>
                </div>
                <div className="activity-feed-scroll">
                    {activityLogs.length > 0 ? (
                        activityLogs.map(log => (
                            <ActivityFeedItem key={log.id} log={log} agents={agents} />
                        ))
                    ) : (
                        <div className="activity-feed-empty">
                            No activity yet. Agents will appear here once they start exploring the maze.
                        </div>
                    )}    
                </div>
            </div>
          </div>
        </div>

        {/* Back Button */}
        <Button 
          onClick={onBack}
          style={{ 
            position: 'absolute', 
            top: '1.5rem', 
            left: '2rem', 
            zIndex: 20,
            margin: 0
          }}
        >
          Back
        </Button>
      </div>
    </div>
  );
}
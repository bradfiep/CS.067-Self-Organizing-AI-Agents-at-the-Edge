// src/components/AgentActivity.tsx
import { useState, useEffect } from 'react';
import Button from './Button';
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
  type: 'move' | 'info';
}

interface AgentActivityProps {
  onBack: () => void;
  backendMessage?: string | null;
  maze: number[][] | null;
  startPt: [number, number];
  endPt: [number, number];
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
  backendMessage,
  maze,
  startPt,
  endPt
}: AgentActivityProps) {
  // Initialize agents with placeholder data
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);

  // Process backend messages
  useEffect(() => {
    if (!backendMessage) return;

    try {
      const data = JSON.parse(backendMessage);
      
      const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });

      // Handle agent_registered message
      if (data.type === 'agent_registered') {
        const newAgent: Agent = {
          id: data.agent_name.toLowerCase().replace(' ', '-'),
          name: data.agent_name,
          position: data.position,
          status: data.status as 'exploring' | 'inactive' | 'completed',
          color: assignAgentColor(data.agent_name)
        };

        // Add agent if not already in list
        setAgents(prev => {
          const exists = prev.some(a => a.id === newAgent.id);
          if (exists) return prev;
          return [...prev, newAgent];
        });

        // Add to activity log
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
      
      // Handle agent_move message
      else if (data.type === 'agent_move') {
        // Update agent position
        setAgents(prev => prev.map(agent => {
          if (agent.name === data.agent_name) {
            return { ...agent, position: data.to_position, status: 'exploring' };
          }
          return agent;
        }));

        // Add to activity log
        const newLog: ActivityLog = {
          id: `log-${Date.now()}-${Math.random()}`,
          timestamp,
          agentId: data.agent_name.toLowerCase().replace(' ', '-'),
          agentName: data.agent_name,
          message: `Moving one step from position (${data.from_position[0]},${data.from_position[1]}) to position (${data.to_position[0]},${data.to_position[1]})`,
          type: 'move'
        };
        setActivityLogs(prev => [newLog, ...prev].slice(0, 50));
      }
      // Handle ACK messages
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
    } catch (err) {
      console.error('Error parsing backend message:', err);
    }
  }, [backendMessage]);

  // Helper function to assign colors to agents
  const assignAgentColor = (agentName: string): string => {
    const colors = ['#297AEB', '#F28B1E', '#f8d32b', '#9718ad', '#e74337', '#1AB74E'];
    const agentNumber = agentName.match(/\d+/)?.[0] || agentName.charCodeAt(agentName.length - 1);
    const index = (typeof agentNumber === 'string' ? parseInt(agentNumber) : agentNumber) % colors.length;
    return colors[index];
  };

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
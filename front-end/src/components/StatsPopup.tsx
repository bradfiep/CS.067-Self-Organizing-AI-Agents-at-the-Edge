import React, { useState, useEffect } from 'react';
import '../styles/StatsPopup.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface AgentStats {
  agent_name: string;
  agent_id: number;
  tiles_explored: number;
  tiles_discovered_directly: number;
  tiles_learned_from_peers: number;
  steps_taken: number;
  unique_tiles_walked: number;
  redundant_steps: number;
  optimal_path_distance: number;
  path_optimality_ratio: number;
  efficiency_percentage: number;
  exploration_rate: number;
  remaining_frontiers: number;
  frontiers_claimed_by_agent: number;
  walls_boundaries_hit: number;
  maps_merged_from_peers: number;
  ticks_elapsed: number;
  reached_goal: boolean;
  goal_tick: number | null;
}

interface StatsPopupProps {
  isOpen: boolean;
  agents: AgentStats[];
  onClose: () => void;
}

const StatsPopup: React.FC<StatsPopupProps> = ({ isOpen, agents, onClose }) => {
  const [closing, setClosing] = useState(false);

  // Reset closing state when popup reopens
  useEffect(() => {
    if (isOpen) setClosing(false);
  }, [isOpen]);

  const handleClose = () => {
    setClosing(true);
    setTimeout(() => {
      onClose();
    }, 300); // matches animation duration
  };

  if (!isOpen) return null;

  const goalFinisher = agents.find(a => a.reached_goal) ?? null;
  const bestExplorer = agents.reduce((best, a) =>
    a.tiles_discovered_directly > best.tiles_discovered_directly ? a : best, agents[0]);
  const mostEfficient = agents.reduce((best, a) =>
    a.exploration_rate > best.exploration_rate ? a : best, agents[0]);
  const fewestRedundant = agents.reduce((best, a) =>
    a.redundant_steps < best.redundant_steps ? a : best, agents[0]);

  return (
    <div className={`stats-overlay${closing ? ' stats-overlay--closing' : ''}`}>
      <div className={`stats-modal${closing ? ' stats-modal--closing' : ''}`}>
        <div className="stats-header">
          <h1>Maze Exploration Complete!</h1>
        </div>

        <div className="stats-scroll-body">
        <div className="stats-container">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="agent-stats-card">
              <div className="agent-stats-header">
                <h2>{agent.agent_name}</h2>
                <span className="agent-id">Agent #{agent.agent_id}</span>
              </div>

              <div className="stats-grid">
                {/* Exploration Stats */}
                <div className="stat-group">
                  <h3>Exploration</h3>
                  <div className="stat-row">
                    <span className="stat-label">Tiles Explored:</span>
                    <span className="stat-value">{agent.tiles_explored}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Discovered Directly:</span>
                    <span className="stat-value">{agent.tiles_discovered_directly}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Learned From Peers:</span>
                    <span className="stat-value">{agent.tiles_learned_from_peers}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Remaining Frontiers:</span>
                    <span className="stat-value">{agent.remaining_frontiers}</span>
                  </div>
                </div>

                {/* Movement Stats */}
                <div className="stat-group">
                  <h3>Movement</h3>
                  <div className="stat-row">
                    <span className="stat-label">Steps Taken:</span>
                    <span className="stat-value">{agent.steps_taken}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Unique Tiles Walked:</span>
                    <span className="stat-value">{agent.unique_tiles_walked}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Redundant Steps:</span>
                    <span className="stat-value">{agent.redundant_steps}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Optimal Path (BFS):</span>
                    <span className="stat-value">{agent.optimal_path_distance}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Steps vs Optimal:</span>
                    <span className="stat-value optimality-ratio">
                      {agent.path_optimality_ratio}x
                    </span>
                  </div>
                </div>

                {/* Obstacles */}
                <div className="stat-group">
                  <h3>Obstacles</h3>
                  <div className="stat-row">
                    <span className="stat-label">Walls/Boundaries Hit:</span>
                    <span className="stat-value">{agent.walls_boundaries_hit}</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Frontiers Claimed:</span>
                    <span className="stat-value">{agent.frontiers_claimed_by_agent}</span>
                  </div>
                </div>

                {/* Collaboration */}
                <div className="stat-group">
                  <h3>Collaboration</h3>
                  <div className="stat-row">
                    <span className="stat-label">% Knowledge from Peers:</span>
                    <span className="stat-value">
                      {agent.tiles_explored > 0
                        ? Math.round((agent.tiles_learned_from_peers / agent.tiles_explored) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Scout vs Relay Ratio:</span>
                    <span className="stat-value">
                      {agent.tiles_learned_from_peers > 0
                        ? (agent.tiles_discovered_directly / agent.tiles_learned_from_peers).toFixed(2)
                        : '–'}
                    </span>
                  </div>
                </div>

                {/* Efficiency Metrics */}
                <div className="stat-group">
                  <h3>Efficiency</h3>
                  <div className="stat-row">
                    <span className="stat-label">Exploration Rate:</span>
                    <span className="stat-value">{agent.exploration_rate} tiles/step</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Movement Efficiency:</span>
                    <span className="stat-value efficiency">{agent.efficiency_percentage}%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="stats-summary">
          <h2 className="stats-summary-title">Summary</h2>
          <div className="stats-summary-grid">
            <div className="summary-card">
              <i className="bi bi-geo-alt summary-icon"></i>
              <span className="summary-label">Reached the Goal</span>
              <span className="summary-winner">
                {goalFinisher
                  ? `${goalFinisher.agent_name} (tick ${goalFinisher.goal_tick})`
                  : 'No agent reached goal'}
              </span>
            </div>
            <div className="summary-card">
              <i className="bi bi-map summary-icon"></i>
              <span className="summary-label">Most Tiles Discovered</span>
              <span className="summary-winner">
                {bestExplorer.agent_name} ({bestExplorer.tiles_discovered_directly} tiles)
              </span>
            </div>
            <div className="summary-card">
              <i className="bi bi-lightning summary-icon"></i>
              <span className="summary-label">Best Exploration Rate</span>
              <span className="summary-winner">
                {mostEfficient.agent_name} ({mostEfficient.exploration_rate} tiles/step)
              </span>
            </div>
            <div className="summary-card">
              <i className="bi bi-compass summary-icon"></i>
              <span className="summary-label">Least Backtracking</span>
              <span className="summary-winner">
                {fewestRedundant.agent_name} ({fewestRedundant.redundant_steps} redundant steps)
              </span>
            </div>
          </div>
        </div>
        </div>{/* end stats-scroll-body */}

        <div className="stats-footer">
          <button className="close-button" onClick={handleClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatsPopup;

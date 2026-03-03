import React from 'react';

interface Agent {
  id: string;
  name: string;
  position: [number, number];
  color: string;
  status: string;
  isHittingWall?: boolean;
}

interface MazeGridProps {
  maze: number[][];
  start: [number, number];
  end: [number, number];
  agents?: Agent[];
  discoveredCells?: Set<string>;
}

const MazeGrid: React.FC<MazeGridProps> = ({ maze, start, end, agents = [], discoveredCells = new Set() }) => {
  const getAgentAtPosition = (row: number, col: number): Agent | undefined => {
    return agents.find(agent => agent.position[0] === row && agent.position[1] === col);
  };

  const isDiscovered = (row: number, col: number): boolean => {
    return discoveredCells.has(`${row},${col}`);
  };

  return (
    <div className="maze-grid-container">
      <style>{`
        @keyframes wallFlash {
          0% {
            background-color: #e74337;
            box-shadow: 0 0 12px rgba(231, 67, 55, 0.8), inset 0 0 8px rgba(255, 255, 255, 0.3);
          }
          50% {
            background-color: #ff6b6b;
            box-shadow: 0 0 20px rgba(231, 67, 55, 1), inset 0 0 12px rgba(255, 255, 255, 0.5);
          }
          100% {
            background-color: #e74337;
            box-shadow: 0 0 12px rgba(231, 67, 55, 0.8), inset 0 0 8px rgba(255, 255, 255, 0.3);
          }
        }
        .agent-wall-hit {
          animation: wallFlash 0.6s ease-in-out;
        }
      `}</style>
      <table className="maze-table">
        <tbody>
          {maze.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => {
                const agent = getAgentAtPosition(rowIndex, colIndex);
                let bg = cell === 1 ? '#222' : '#eee';
                let content = '';
                let textColor = '#000';
                let animationClassName = '';

                if (agent) {
                  // Agent takes priority
                  if (agent.isHittingWall) {
                    bg = '#e74337';
                    animationClassName = 'agent-wall-hit';
                  } else {
                    bg = agent.color;
                  }
                  content = agent.name.charAt(agent.name.length - 1);
                  textColor = '#fff';
                } else if (start[0] === rowIndex && start[1] === colIndex) {
                  bg = '#4caf50';
                  content = 'A';
                  textColor = '#fff';
                } else if (end[0] === rowIndex && end[1] === colIndex) {
                  bg = '#e53935';
                  content = 'B';
                  textColor = '#fff';
                } else if (cell === 0 && isDiscovered(rowIndex, colIndex)) {
                  // Discovered open cell - light gray
                  bg = '#d0d0d0';
                }

                return (
                  <td
                    className={`maze-cell ${animationClassName}`}
                    style={{
                      background: bg,
                      color: textColor,
                      fontWeight: agent ? 'bold' : 'normal',
                      fontSize: agent ? '14px' : '12px'
                    }}
                    key={colIndex}
                    title={agent ? `${agent.name} at (${rowIndex}, ${colIndex})` : ''}
                  >
                    {content}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MazeGrid;

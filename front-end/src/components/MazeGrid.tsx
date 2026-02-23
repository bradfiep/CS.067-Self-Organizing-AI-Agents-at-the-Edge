import React from 'react';

interface Agent {
  id: string;
  name: string;
  position: [number, number];
  color: string;
  status: string;
}

interface MazeGridProps {
  maze: number[][];
  start: [number, number];
  end: [number, number];
  agents?: Agent[];
}

const MazeGrid: React.FC<MazeGridProps> = ({ maze, start, end, agents = [] }) => {
  const getAgentAtPosition = (row: number, col: number): Agent | undefined => {
    return agents.find(agent => agent.position[0] === row && agent.position[1] === col);
  };

  return (
    <div className="maze-grid-container">
      <table className="maze-table">
        <tbody>
          {maze.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => {
                const agent = getAgentAtPosition(rowIndex, colIndex);
                let bg = cell === 1 ? '#222' : '#eee';
                let content = '';
                let textColor = '#000';

                if (agent) {
                  // Agent takes priority
                  bg = agent.color;
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
                }

                return (
                  <td
                    className="maze-cell"
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

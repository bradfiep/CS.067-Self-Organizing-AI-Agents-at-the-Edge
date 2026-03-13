import React from 'react';

interface Agent {
  id: string;
  name: string;
  position: [number, number];
  color: string;
  status: string;
  isHittingWall?: boolean;
  isDiscoveringCell?: boolean;
}

interface MazeGridProps {
  maze: number[][];
  start: [number, number];
  end: [number, number];
  agents?: Agent[];
  discoveredCells?: Set<string>;
  flashingCells?: Set<string>;
}

const MazeGrid: React.FC<MazeGridProps> = ({
  maze,
  start,
  end,
  agents = [],
  discoveredCells = new Set(),
  flashingCells = new Set()
}) => {
  const [hoveredCell, setHoveredCell] = React.useState<[number, number] | null>(null);
  const [mousePos, setMousePos] = React.useState<{ x: number; y: number; tableWidth: number } | null>(null);

  const getAgentAtPosition = (row: number, col: number): Agent | undefined => {
    return agents.find(agent => agent.position[0] === row && agent.position[1] === col);
  };

  const isDiscovered = (row: number, col: number): boolean => {
    return discoveredCells.has(`${row},${col}`);
  };

  const isFlashing = (row: number, col: number): boolean => {
    return flashingCells.has(`${row},${col}`);
  };

  return (
    <div className="maze-grid-container" style={{ position: 'relative' }}>
      {hoveredCell && mousePos && (
        <div
          style={{
            position: 'absolute',
            left: `${mousePos.x > mousePos.tableWidth - 90 ? Math.max(0, mousePos.x - 64) : mousePos.x + 12}px`,
            top: `${mousePos.y + 12}px`,
            zIndex: 20,
            background: 'rgba(0, 0, 0, 0.82)',
            color: '#fff',
            borderRadius: '4px',
            padding: '4px 8px',
            fontSize: '12px',
            fontFamily: 'monospace',
            pointerEvents: 'none',
            whiteSpace: 'nowrap'
          }}
        >
          ({hoveredCell[1]},{hoveredCell[0]})
        </div>
      )}
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
          @keyframes discoverFlash {
            0% {
              background-color: #34eadd;
              box-shadow: 0 0 12px rgba(44, 239, 145, 0.8), inset 0 0 8px rgba(255,255,255,0.3);
            }
            50% {
              background-color: #81f2fa;
              box-shadow: 0 0 20px rgba(44, 239, 80, 0.8), inset 0 0 12px rgba(255,255,255,0.5);
            }
            100% {
              background-color: #4ff7f7;
              box-shadow: 0 0 12px rgba(44, 239, 145, 0.8), inset 0 0 8px rgba(255,255,255,0.3);
            }
          }
          .agent-discover-flash {
            animation: discoverFlash 0.5s ease-in-out;
          }
      `}</style>
      <table
        className="maze-table"
        onMouseLeave={() => {
          setHoveredCell(null);
          setMousePos(null);
        }}
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          setMousePos({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
            tableWidth: rect.width
          });
        }}
      >
        <tbody>
          {maze.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => {
                const agent = getAgentAtPosition(rowIndex, colIndex);
                let bg = cell === 1 ? '#222' : '#eee';
                let content = '';
                let textColor = '#000';
                let animationClassName = '';
                const flashing = isFlashing(rowIndex, colIndex);

                if (agent) {
                  // Agent takes priority
                    if (flashing || agent.isDiscoveringCell) {
                      bg = '#4fc3f7'; // blue flash for discovery
                      animationClassName = 'agent-discover-flash';
                    } else if (agent.isHittingWall) {
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
                } else if (flashing) {
                  bg = '#4fc3f7';
                  animationClassName = 'agent-discover-flash';
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
                    onMouseEnter={() => setHoveredCell([rowIndex, colIndex])}
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

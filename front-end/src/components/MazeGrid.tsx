import React from 'react';

interface MazeGridProps {
  maze: number[][];
  start: [number, number];
  end: [number, number];
}

const MazeGrid: React.FC<MazeGridProps> = ({ maze, start, end }) => {
  return (
    <div className="maze-grid-container">
      <table className="maze-table">
        <tbody>
          {maze.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => {
                let bg = cell === 1 ? '#222' : '#eee';
                let content = '';
                if (start[0] === rowIndex && start[1] === colIndex) {
                  bg = '#4caf50'; content = 'A';
                } else if (end[0] === rowIndex && end[1] === colIndex) {
                  bg = '#e53935'; content = 'B';
                }
                return (
                  <td className="maze-cell" style={{ background: bg }} key={colIndex}>
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

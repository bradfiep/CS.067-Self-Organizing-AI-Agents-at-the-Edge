import React from 'react';

// Component for displaying the maze key legend
const MazeKey: React.FC = () => (
  <div className="maze-key-popup">
    <div className="maze-key-row">
      <span className="maze-key-square maze-key-start">A</span>
      <span className="maze-key-label">Starting Point</span>
    </div>
    <div className="maze-key-row">
      <span className="maze-key-square maze-key-end">B</span>
      <span className="maze-key-label">Ending Point</span>
    </div>
    <div className="maze-key-row">
      <span className="maze-key-square maze-key-wall" />
      <span className="maze-key-label">Wall</span>
    </div>
    <div className="maze-key-row">
      <span className="maze-key-square maze-key-open" />
      <span className="maze-key-label">Open Path</span>
    </div>
  </div>
);

export default MazeKey;

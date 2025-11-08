
import { useState } from 'react';
import MazeKey from './components/MazeKey';

import oregonLogo from './assets/Oregon_State_text_logo.png';
import './App.css';
import Header from './components/Header';
import Button from './components/Button';
import mazeImg from './assets/maze.png';

// Utility functions for parsing maze data from CSV and JSON formats
function parseMazeCSV(csv: string): number[][] {
  return csv
    .trim()
    .split(/\r?\n/)
    .map(row => row.split(',').map(cell => parseInt(cell, 10)));
}

function parseMazeJSON(json: string): number[][] {
  try {
    const arr = JSON.parse(json);
    if (Array.isArray(arr) && arr.every(row => Array.isArray(row))) {
      return arr;
    }
    return [];
  } catch {
    return [];
  }
}

// Component to render the maze as a grid table
function MazeGrid({ maze, start, end }: { maze: number[][], start: [number, number], end: [number, number] }) {
  return (
    <div className="maze-grid-container">
      <table className="maze-table">
        <tbody>
          {maze.map((row, rIdx) => (
            <tr key={rIdx}>
              {row.map((cell, cIdx) => {
                let bg = cell === 1 ? '#222' : '#eee';
                let content = '';
                if (start[0] === rIdx && start[1] === cIdx) {
                  bg = '#4caf50'; content = 'A';
                } else if (end[0] === rIdx && end[1] === cIdx) {
                  bg = '#e53935'; content = 'B';
                }
                return (
                  <td className="maze-cell" style={{ background: bg }} key={cIdx}>
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
}

// Component for the hover trigger that shows the maze key popup
function MazeKeyHover() {
  const [show, setShow] = useState(false);
  return (
    <div
      className="maze-key-trigger"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
      tabIndex={0}
    >
      <div className="hamburger">
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
        <div className="hamburger-line"></div>
      </div>
      {show && <MazeKey />}
    </div>
  );
}

function App() {
  // State management for the application
  // States for builder view and maze configuration
  const [showBuilder, setShowBuilder] = useState(false);
  const [inputType, setInputType] = useState<'csv' | 'json'>('csv');
  const [csv, setCsv] = useState('');
  const [json, setJson] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [maze, setMaze] = useState<number[][] | null>(null);
  const [startPt, setStartPt] = useState<[number, number]>([0, 0]);
  const [endPt, setEndPt] = useState<[number, number]>([0, 0]);
  const [error, setError] = useState('');

  // Header actions component
  const header_actions = (
    <div>
      <Button variant='secondary' onClick={() => alert('About Button clicked!')}>About</Button>
      <Button variant='secondary' onClick={() => alert('Github Button clicked!')}>Github</Button>
      <Button onClick={() => { handleClear(); setShowBuilder(true); }}>Start Maze</Button>
    </div>
  );

  // Comprehensive handler to generate and validate maze from input data
  const handleGenerateMaze = () => {
    setError('');
    const input = inputType === 'csv' ? csv.trim() : json.trim();
    if (input === '') {
      setError(`Please enter maze data in ${inputType.toUpperCase()} format.`);
      return;
    }
    if (start.trim() === '') {
      setError('Please enter start point (e.g., 0,0).');
      return;
    }
    if (end.trim() === '') {
      setError('Please enter end point (e.g., 4,4).');
      return;
    }
    let m: number[][] = [];
    if (inputType === 'csv') {
      m = parseMazeCSV(csv);
    } else {
      m = parseMazeJSON(json);
    }
    if (m.length === 0) {
      setError('Invalid maze data. Please check the format.');
      return;
    }
    const s = start.split(',').map(Number);
    const e = end.split(',').map(Number);
    if (s.length !== 2 || e.length !== 2 || s.some(isNaN) || e.some(isNaN)) {
      setError('Invalid start or end points. Use format like 0,0');
      return;
    }
    const startPtTemp: [number, number] = [s[0], s[1]];
    const endPtTemp: [number, number] = [e[0], e[1]];
    const rows = m.length;
    const cols = m[0].length;
    if (startPtTemp[0] < 0 || startPtTemp[0] >= rows || startPtTemp[1] < 0 || startPtTemp[1] >= cols) {
      setError('Start point is out of bounds.');
      return;
    }
    if (endPtTemp[0] < 0 || endPtTemp[0] >= rows || endPtTemp[1] < 0 || endPtTemp[1] >= cols) {
      setError('End point is out of bounds.');
      return;
    }
    if (startPtTemp[0] === endPtTemp[0] && startPtTemp[1] === endPtTemp[1]) {
      setError('Start and end points cannot be the same.');
      return;
    }
    setMaze(m);
    setStartPt(startPtTemp);
    setEndPt(endPtTemp);
  };

  // Handler to clear all maze inputs and reset state
  const handleClear = () => {
    setCsv('');
    setJson('');
    setStart('');
    setEnd('');
    setMaze(null);
    setStartPt([0, 0]);
    setEndPt([0, 0]);
    setError('');
  };

  // Handler for importing maze data from a file
  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (inputType === 'csv') {
        setCsv(text);
      } else {
        setJson(text);
      }
    };
    reader.readAsText(file);
  };

  if (showBuilder) {
    // Render the Maze Builder interface
    return (
      <>
        <Header title="Multi-Agent Maze Solver" logoSrc={oregonLogo} actions={header_actions} />
        <div className="builder-section">
          <div className="builder-section-inner">
            <h1 className="builder-title">Maze Builder</h1>
            <div className="builder-content">
              {/* Left side: Maze setup and input */}
              <div className="maze-setup">
                <div className="maze-setup-card">
                  <div>
                    <div style={{ marginBottom: '0.5em', textAlign: 'left' }}><b>1. Import Maze</b></div>
                    <div className="data-tabs">
                      <button className={`tab${inputType === 'csv' ? ' active' : ''}`} onClick={() => setInputType('csv')}>CSV</button>
                      <button className={`tab${inputType === 'json' ? ' active' : ''}`} onClick={() => setInputType('json')}>JSON</button>
                    </div>
                    <div style={{ position: 'relative' }}>
                      <label className="import-label">
                        Import {inputType.toUpperCase()}
                        <input type="file" accept={inputType === 'csv' ? '.csv,.txt' : '.json,.txt'} style={{ display: 'none' }} onChange={handleImport} />
                      </label>
                      {inputType === 'csv' ? (
                        <textarea
                          className="maze-input"
                          rows={6}
                          placeholder="0,1,0,0,0,1,0,0,0,0\n..."
                          value={csv}
                          onChange={e => setCsv(e.target.value)}
                        />
                      ) : (
                        <textarea
                          className="maze-input"
                          rows={6}
                          placeholder="[[0,1,0,0,0],[1,0,1,1,0],...]"
                          value={json}
                          onChange={e => setJson(e.target.value)}
                        />
                      )}
                    </div>
                    <div className="input-info">
                      <span className="input-hint">
                        {inputType === 'csv' ? '0 = open path, 1 = wall' : 'JSON array of arrays, e.g. [[0,1,0],[1,0,1]]'}
                      </span>
                      <Button variant="secondary" onClick={handleClear} style={{ fontSize: '0.85em', padding: '0.3em 0.8em', marginLeft: '1em' }}>Clear</Button>
                    </div>
                    <div style={{ marginTop: '1.5em', textAlign: 'left' }}>
                      <b>2. Set Start &amp; End Points</b>
                      <div className="points-input">
                        <label className="start-label">Start (A)</label>
                        <input className="start-end-input" placeholder="0,0" value={start} onChange={e => setStart(e.target.value)} />
                        <label className="end-label">End (B)</label>
                        <input className="start-end-input" placeholder="9,9" value={end} onChange={e => setEnd(e.target.value)} />
                      </div>
                    </div>
                    <div className="generate-btn-container">
                      <Button variant="primary" onClick={handleGenerateMaze}>Generate Maze</Button>
                    </div>
                    {error && <div className="error-message">{error}</div>}
                  </div>
                </div>
              </div>
              {/* Right side: Maze preview */}
              <div className="maze-preview-container">
                <div className="maze-data">
                  <h3 className="maze-data-title">Maze Preview</h3>
                    {maze ? (
                      <>
                        <MazeGrid maze={maze} start={startPt} end={endPt} />
                        {/* Run Maze button appears only when maze is generated */}
                        <div style={{ width: '100%', display: 'flex', justifyContent: 'center', marginTop: '1.5em' }}>
                          <Button variant="primary">Run Maze</Button>
                        </div>
                      </>
                    ) : (
                      <div className="maze-placeholder">Enter maze data and points, then click Generate Maze.</div>
                    )}
                </div>
                {maze && (
                  <MazeKeyHover />
                )}
              </div>
            </div>
            {/* Move Back button to top left of builder-section */}
            <Button 
              onClick={() => setShowBuilder(false)}
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
      </>
    );
  }

  // Render the Home Page
  return (
    <>
      <Header title="Multi-Agent Maze Solver" logoSrc={oregonLogo} actions={header_actions} />
      <div className="maze-section">
        <div className="maze-text">
          <h2>
            A collaborative pathfinding simulation where AI agents explore mazes
            and communicate to find the fastest route from A to B
          </h2>
          <div className="maze-buttons">
            <Button onClick={() => { handleClear(); setShowBuilder(true); }}>Build Maze</Button>
            <Button variant="secondary" onClick={() => alert('Watch Demo clicked!')}>
              Watch Demo
            </Button>
          </div>
        </div>
        <div className="maze-image">
          <img src={mazeImg} alt="Maze Image" />
        </div>
      </div>
    </>
  );
}

export default App;

import { useState, useEffect, useRef } from "react";
import oregonLogo from './assets/Oregon_State_text_logo.png';
import './App.css';
import Header from './components/Header';
import Button from './components/Button';
import MazeBuilder from './components/MazeBuilder';
import AgentActivity from './components/AgentActivity';
import mazeImg from './assets/maze.png';

function App() {
  // State management for the application
  const [showBuilder, setShowBuilder] = useState(false);
  const [showActivity, setShowActivity] = useState(false);
  const [backendMessage, setBackendMessage] = useState<string | null>(null);


  const ws = useRef<WebSocket | null>(null);
  const wsUrl = import.meta.env.VITE_WEBSOCKET_URL;

  useEffect(() => {
    ws.current = new WebSocket(wsUrl)
    ws.current.onopen = () => console.log("WebSocket connected");
    ws.current.onclose = () => console.log("WebSocket disconnected");
    ws.current.onerror = (err) => console.error("WebSocket error", err);

    return () => {
      ws.current?.close();
    };
  }, [wsUrl]);

  useEffect(() => {
    ws.current = new WebSocket(wsUrl);
  
    ws.current.onopen = () => console.log("WebSocket connected");
    ws.current.onclose = () => console.log("WebSocket disconnected");
    ws.current.onerror = (err) => console.error("WebSocket error", err);
  
    ws.current.onmessage = (event) => {
      console.log("Received from backend:", event.data);
  
      try {
        const parsed = JSON.parse(event.data);
        setBackendMessage(JSON.stringify(parsed, null, 2));
      } catch {
        setBackendMessage(event.data);
      }
    };
  
    return () => {
      ws.current?.close();
    };
  }, [wsUrl]);
  

  // Function to send maze via WebSocket
  const handleSendMaze = (maze: number[][], start: [number, number], end: [number, number]) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error("WebSocket is not connected.");
      return;
    }

    const payload = {
        maze,
        start,
        end
    };

    ws.current.send(JSON.stringify(payload));
    console.log("Maze sent via WebSocket");

    setShowActivity(true);
    setShowBuilder(false);
  };

  // Header actions component
  const header_actions = (
    <div>
      <Button variant='secondary' onClick={() => alert('About Button clicked!')}>About</Button>
      <Button variant='secondary' onClick={() => alert('Github Button clicked!')}>Github</Button>
      <Button onClick={() => setShowBuilder(true)}>Start Maze</Button>
    </div>
  );

  // Show Agent Activity page
  if (showActivity) {
    return (
      <>
        <Header title="Multi-Agent Maze Solver" logoSrc={oregonLogo} actions={header_actions} />
        <AgentActivity
          onBack={() => {
            setShowActivity(false);
            setShowBuilder(true);
          }}
          wsConnected={ws.current?.readyState === WebSocket.OPEN}
          backendMessage={backendMessage}
        />
      </>
    );
  }
  
  if (showBuilder) {
    // Render the Maze Builder interface
    return (
      <>
        <Header title="Multi-Agent Maze Solver" logoSrc={oregonLogo} actions={header_actions} />
        <MazeBuilder 
          onBack={() => setShowBuilder(false)}
          onSendMaze={handleSendMaze}
          wsConnected={ws.current?.readyState === WebSocket.OPEN}
          backendMessage={backendMessage}
        />
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
            <Button onClick={() => setShowBuilder(true)}>Build Maze</Button>
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

import oregonLogo from './assets/Oregon_State_text_logo.png'
import './App.css'
import Header from './components/Header'
import Button from './components/Button'
import mazeImg from './assets/maze.png'

function App() {

  const header_actions = (
    <div>
      <Button variant='secondary' onClick={() => alert('About Button clicked!')}>About</Button>
      <Button variant='secondary' onClick={() => alert('Github Button clicked!')}>Github</Button>
      <Button onClick={() => alert('Start Maze Button clicked!')}>Start Maze</Button>
    </div>
  )



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
            <Button onClick={() => alert('Build Maze clicked!')}>Build Maze</Button>
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
  )
}

export default App

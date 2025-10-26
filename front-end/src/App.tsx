import { useState } from 'react'
import oregonLogo from './assets/Oregon_State_text_logo.png'
import './App.css'
import Header from './components/Header'
import Button from './components/Button'

function App() {
  const [count, setCount] = useState(0)

  const header_actions = (
    <div>
      <Button onClick={() => alert('Button clicked!')}>test button</Button>
    </div>
  )



  return (
    <>
      <Header title="Multi-Agent Maze Solver" logoSrc={oregonLogo} actions={header_actions} />

      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App

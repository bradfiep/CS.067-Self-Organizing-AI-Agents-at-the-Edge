# CS.067-Self-Organizing-AI-Agents-at-the-Edge
Check it out at https://cs-067-self-organizing-ai-agents-at.vercel.app/ 

A real-time multi-agent simulation platform for exploring decentralized coordination and emergent behavior.
Project Partner: Kyle Prouty, HP.

---

## Overview

A multi-agent system designed to demonstrate how decentralized decision-making leads to efficient and emergent maze-solving behavior.

This project was developed as part of a senior capstone at Oregon State University in collaboration with HP.

---

## Motivation

Many systems in the real world, like robots or edge devices, need to work together without a central controller. It is hard to design these systems because each agent only sees part of the environment, but still needs to make decisions that help the group. This project shows a simple version of that idea. The maze simulation acts like a small model of how agents could cooperate in real scenarios, helping students and developers understand how these systems might work in the future.

---

## Why This Matters

Rather than explicitly programming a solution, this system allows behavior to emerge from the interaction of multiple agents following simple rules. This project shows how simple, local decisions can lead to intelligent group behavior, demonstrating the potential of decentralized systems for real-world applications like robotics and edge computing.

---

## Features

- **Real-time simulation**  
  Real-time swarm simulation: watch a group of AI agents explore a maze live, with the frontend updating on progress each simulation step.

- **Decentralized decision-making**  
  Autonomous maze solving: the system sends agents into a maze and they cooperate to discover paths and reach the goal without manual direction.

- **Live Simulation**  
  Agent activity tracking: you can see individual agent status, positions, and exploration progress as the simulation runs.

- **Statistics**  
  Coverage and goal metrics: the app reports how much of the maze has been discovered, whether the goal was reached, and overall simulation completion stats.

- **Interactive Interface**  
  Interactive front-end control: submit a maze plus start/end points from the browser and receive continuous feedback through a websocket connection.

---

## Demo

<img width="1920" height="1032" alt="AntColonyDemo-1" src="https://github.com/user-attachments/assets/a0fc05d9-e104-4dca-9931-07def43ee3c1" />



---

## Project Structure

- `frontend/` — Web interface for visualization and user interaction  
- `backend/` — Simulation logic and agent coordination  

---

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)  
- npm  
- Python 3.10+  
- Git  

---

### Installation

```bash
git clone https://github.com/bradfiep/CS.067-Self-Organizing-AI-Agents-at-the-Edge
cd CS.067-Self-Organizing-AI-Agents-at-the-Edge
```

Run frontend:
```bash
cd front-end
npm install
npm run dev
```

Run backend:
```bash
cd backend
python main.py
```

### Team Information

**Team Roster**

| Name                 | Contact Information           |
|----------------------|-------------------------------|
| Payton Brafield      | bradfiep@oregonstate.edu      |
| Kush Patel           | patelkush@oregonstate.edu     |
| Lilian Le            | lelili@oregonstate.edu        |
| Natalia Zaitseva     | zaitsevn@oregonstate.edu      |
| Samuel Garcia-Lopez  | garcsamu@oregonstate.edu      |
| Sarah Satchell       | satchels@oregonstate.edu      |

**Questions & Feedback**

Discord: https://discord.gg/a6CdXFvq2P  

Questions can be asked in #questions channel, using the invite link above.  

For urgent issues, contact the team lead.


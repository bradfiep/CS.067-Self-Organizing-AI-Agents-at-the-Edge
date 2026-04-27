import 'bootstrap-icons/font/bootstrap-icons.css';
import Button from './Button';

interface AboutProps {
  onBack: () => void;
}

interface TeamMember {
  name: string;
  email: string;
}

const TEAM: TeamMember[] = [
  { name: 'Payton Brafield', email: 'bradfiep@oregonstate.edu' },
  { name: 'Kush Patel', email: 'patelkush@oregonstate.edu' },
  { name: 'Lilian Le', email: 'lelili@oregonstate.edu' },
  { name: 'Natalia Zaitseva', email: 'zaitsevn@oregonstate.edu' },
  { name: 'Samuel Garcia-Lopez', email: 'garcsamu@oregonstate.edu' },
  { name: 'Sarah Satchell', email: 'satchels@oregonstate.edu' },
];

export default function About({ onBack }: AboutProps) {
  return (
    <div className="about-section">
      <div className="about-section-inner">
        <h1 className="about-title">About the Project</h1>

        <section className="about-card about-overview">
          <h2 className="about-subtitle">
            <i className="bi bi-compass about-subtitle-icon" aria-hidden="true"></i>
            Project Overview
          </h2>
          <p className="about-paragraph">
            Multi-Agent Maze Solver is a collaborative pathfinding simulation
            where AI agents explore mazes and communicate to find the fastest
            route from a start point to an end point. Built as part of CS 467
            at Oregon State University, this project explores how
            self-organizing agents can coordinate at the edge to solve spatial
            problems more efficiently than any single agent could on its own.
          </p>
          <p className="about-paragraph">
            The system pairs a React + TypeScript frontend with a Python
            backend that streams agent activity over WebSockets. Users can
            build or import mazes, watch agents navigate them in real time, and
            inspect per-agent statistics as they go.
          </p>
        </section>

        <section className="about-card about-team">
          <h2 className="about-subtitle">
            <i className="bi bi-people-fill about-subtitle-icon" aria-hidden="true"></i>
            About the Team
          </h2>
          <div className="team-table-wrapper">
            <table className="team-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Contact Information</th>
                </tr>
              </thead>
              <tbody>
                {TEAM.map((member) => (
                  <tr key={member.email}>
                    <td className="team-name">{member.name}</td>
                    <td>
                      <a
                        className="team-email"
                        href={`mailto:${member.email}`}
                      >
                        {member.email}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <div className="about-actions">
          <Button onClick={onBack}>Back to Home</Button>
        </div>
      </div>
    </div>
  );
}

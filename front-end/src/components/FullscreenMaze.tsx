import MazeGrid from './MazeGrid';

interface Agent {
  id: string;
  name: string;
  position: [number, number];
  status: 'exploring' | 'inactive' | 'completed';
  color: string;
}

interface FullscreenMazeProps {
  maze: number[][] | null;
  startPt: [number, number];
  endPt: [number, number];
  agents: Agent[];
  onClose: () => void;
}

// Shrink Icon Component
function ShrinkIcon() {
  return <i className="bi bi-arrows-angle-contract" style={{ fontSize: '20px' }}></i>;
}

export default function FullscreenMaze({
  maze,
  startPt,
  endPt,
  agents,
  onClose
}: FullscreenMazeProps) {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(26, 26, 26, 0.98)',
        backdropFilter: 'blur(4px)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        padding: '2rem',
        animation: 'fadeInMaze 0.4s ease-out'
      }}
    >
      <style>{`
        @keyframes fadeInMaze {
          from {
            opacity: 0;
            backdrop-filter: blur(0px);
          }
          to {
            opacity: 1;
            backdrop-filter: blur(4px);
          }
        }
        @keyframes slideUp {
          from {
            transform: translateY(30px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', position: 'relative', zIndex: 10 }}>
        <h2 style={{ color: '#fff', margin: 0 }}>Maze Fullscreen View</h2>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '6rem',
            right: '2rem',
            background: '#e74337',
            color: 'white',
            border: 'none',
            padding: '12px 16px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '18px',
            fontWeight: 'bold',
            transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(231, 67, 55, 0.3)',
            animation: 'slideUp 0.4s ease-out 0.1s both'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#d32f2f';
            e.currentTarget.style.transform = 'scale(1.12)';
            e.currentTarget.style.boxShadow = '0 6px 20px rgba(211, 47, 47, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#e74337';
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(231, 67, 55, 0.3)';
          }}
          title="Shrink maze back to preview"
        >
          <ShrinkIcon />
        </button>
      </div>

      <div
        style={{
          flex: 1,
          overflow: 'auto',
          background: '#0a0a0a',
          borderRadius: '8px',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginTop: '1rem'
        }}
      >
        {maze && (
          <div style={{ maxWidth: '90vw', maxHeight: '85vh', overflow: 'auto' }}>
            <MazeGrid maze={maze} start={startPt} end={endPt} agents={agents} />
          </div>
        )}
      </div>
    </div>
  );
}

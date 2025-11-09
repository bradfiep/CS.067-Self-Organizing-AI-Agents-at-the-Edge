import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock the WebSocket to avoid connection errors in tests
Object.defineProperty(window, 'WebSocket', {
  writable: true,
  value: class MockWebSocket {
    constructor(_url: string) {
      setTimeout(() => {
        if (this.onopen) this.onopen({} as Event);
      }, 0);
    }
    onopen: ((event: Event) => void) | null = null;
    onclose: ((event: CloseEvent) => void) | null = null;
    onerror: ((event: Event) => void) | null = null;
    readyState = 1; // OPEN
    send() {}
    close() {}
  }
});

describe('App Component Test', () => {
  it('renders the application with correct title', () => {
    render(<App />);
    
    // Check that the main title is rendered
    expect(screen.getByText('Multi-Agent Maze Solver')).toBeInTheDocument();
  });

  it('renders the build maze button', () => {
    render(<App />);
    
    // Check that the build maze button is present
    expect(screen.getByRole('button', { name: /build maze/i })).toBeInTheDocument();
  });

  it('renders the start maze button', () => {
    render(<App />);
    
    // Check for the "Start Maze" button
    expect(screen.getByRole('button', { name: /start maze/i })).toBeInTheDocument();
  });

  it('renders about and github buttons', () => {
    render(<App />);
    
    // Check for action buttons
    expect(screen.getByRole('button', { name: /about/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /github/i })).toBeInTheDocument();
  });
});
import { render, screen } from '@testing-library/react';
import React from 'react';
import App from '../App';

// Mock the WebSocket to avoid connection errors in tests
Object.defineProperty(window, 'WebSocket', {
  writable: true,
  value: class MockWebSocket {
    constructor(url: string) {
      // Store url if needed for future use
      this.url = url;
      setTimeout(() => {
        if (this.onopen) this.onopen({} as Event);
      }, 0);
    }
    url: string;
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

  it('renders the maze builder section', () => {
    render(<App />);
    
    // Check that the maze builder heading is present
    expect(screen.getByRole('heading', { name: /maze builder/i })).toBeInTheDocument();
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
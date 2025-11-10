// This imports extended matchers (like toBeInTheDocument) from React Testing Library
import '@testing-library/jest-dom';

// Mock WebSocket globally to prevent any WebSocket-related errors in tests
class MockWebSocket {
  constructor() { 
    // Do nothing - just a stub
  }
  onopen: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;
  readyState = 1;
  send = () => {};
  close = () => {};
}

// Make available globally for tests
(globalThis as Record<string, unknown>).WebSocket = MockWebSocket; 
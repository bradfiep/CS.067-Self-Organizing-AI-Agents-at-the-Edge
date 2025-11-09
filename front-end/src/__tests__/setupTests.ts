// This imports extended matchers (like toBeInTheDocument) from React Testing Library
import '@testing-library/jest-dom';

// Mock WebSocket globally to prevent any WebSocket-related errors in tests
class MockWebSocket {
  constructor(_url?: string) { 
    // Do nothing - just a stub
  }
  onopen: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;
  readyState = 1;
  send = (..._args: any[]) => {};
  close = () => {};
}

// Make available globally for tests
(globalThis as any).WebSocket = MockWebSocket; 
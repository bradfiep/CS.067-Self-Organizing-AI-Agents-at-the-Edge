// This imports extended matchers (like toBeInTheDocument) from React Testing Library
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock environment variables
vi.stubEnv('VITE_WEBSOCKET_URL', 'ws://localhost:8080'); 
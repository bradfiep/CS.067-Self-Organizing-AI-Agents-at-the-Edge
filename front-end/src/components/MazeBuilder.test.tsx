import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import MazeBuilder from './MazeBuilder';

describe('MazeBuilder Component', () => {
  let mockOnBack: () => void;
  let mockOnSendMaze: (maze: number[][], start: [number, number], end: [number, number]) => void;

  beforeEach(() => {
    mockOnBack = vi.fn();
    mockOnSendMaze = vi.fn();
  });

  afterEach(() => {
    cleanup();
  });

  describe('Rendering', () => {
    it('should render the maze builder interface', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      expect(screen.getByText('Maze Builder')).toBeInTheDocument();
      expect(screen.getByText('1. Import Maze')).toBeInTheDocument();
      expect(screen.getByText('2. Set Start & End Points')).toBeInTheDocument();
      expect(screen.getByText('Generate Maze')).toBeInTheDocument();
    });

    it('should render CSV tab as active by default', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvTab = screen.getByRole('button', { name: 'CSV' });
      expect(csvTab).toHaveClass('active');
    });

    it('should render Back button', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      expect(screen.getByRole('button', { name: 'Back' })).toBeInTheDocument();
    });
  });

  describe('CSV Parsing', () => {
    it('should parse valid CSV maze data', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Maze Preview')).toBeInTheDocument();
      expect(screen.queryByText(/Invalid maze data/)).not.toBeInTheDocument();
    });

    it('should handle CSV with whitespace', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '  0,1,0\n1,0,1\n0,1,0  ' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.queryByText(/Invalid maze data/)).not.toBeInTheDocument();
    });
  });

  describe('JSON Parsing', () => {
    it('should parse valid JSON maze data', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const jsonTab = screen.getByRole('button', { name: 'JSON' });
      fireEvent.click(jsonTab);
      
      const jsonInput = screen.getByPlaceholderText(/\[\[0,1,0,0,0\],\[1,0,1,1,0\]/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(jsonInput, { target: { value: '[[0,1,0],[1,0,1],[0,1,0]]' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.queryByText(/Invalid maze data/)).not.toBeInTheDocument();
    });

    it('should show error for invalid JSON', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const jsonTab = screen.getByRole('button', { name: 'JSON' });
      fireEvent.click(jsonTab);
      
      const jsonInput = screen.getByPlaceholderText(/\[\[0,1,0,0,0\],\[1,0,1,1,0\]/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(jsonInput, { target: { value: 'not valid json' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Invalid maze data. Please check the format.')).toBeInTheDocument();
    });
  });

  describe('Validation - Input Size', () => {
    it('should reject maze input larger than 1MB', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      // Create a string larger than 1MB
      const largeInput = '0,1,0,1,0\n'.repeat(200000);
      
      fireEvent.change(csvInput, { target: { value: largeInput } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '1,1' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Input too large. Maximum 1MB of maze data allowed.')).toBeInTheDocument();
    });
  });

  describe('Validation - Empty Inputs', () => {
    it('should show error when maze data is empty', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Please enter maze data in CSV format.')).toBeInTheDocument();
    });

    it('should show error when start point is empty', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Please enter start point (e.g., 0,0).')).toBeInTheDocument();
    });

    it('should show error when end point is empty', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Please enter end point (e.g., 4,4).')).toBeInTheDocument();
    });
  });

  describe('Validation - Point Format', () => {
    it('should show error for invalid start point format', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: 'invalid' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Invalid start or end points. Use format like 0,0')).toBeInTheDocument();
    });

    it('should show error for invalid end point format', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: 'abc' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Invalid start or end points. Use format like 0,0')).toBeInTheDocument();
    });
  });

  describe('Validation - Point Bounds', () => {
    it('should show error when start point is out of bounds', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '10,10' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Start point is out of bounds.')).toBeInTheDocument();
    });

    it('should show error when end point is out of bounds', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '5,5' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('End point is out of bounds.')).toBeInTheDocument();
    });

    it('should show error when start point is negative', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '-1,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Start point is out of bounds.')).toBeInTheDocument();
    });
  });

  describe('Validation - Same Start and End', () => {
    it('should show error when start and end points are the same', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '1,1' } });
      fireEvent.change(endInput, { target: { value: '1,1' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Start and end points cannot be the same.')).toBeInTheDocument();
    });
  });

  describe('Validation - Points on Walls', () => {
    it('should show error when start point is on a wall', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,1' } }); // This is a wall (1)
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText("Start and end points can't be on walls (1).")).toBeInTheDocument();
    });

    it('should show error when end point is on a wall', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '1,0' } }); // This is a wall (1)
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText("Start and end points can't be on walls (1).")).toBeInTheDocument();
    });
  });

  describe('Clear Functionality', () => {
    it('should clear all inputs when Clear button is clicked', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/) as HTMLTextAreaElement;
      const startInput = screen.getByPlaceholderText('0,0') as HTMLInputElement;
      const endInput = screen.getByPlaceholderText('9,9') as HTMLInputElement;
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      expect(csvInput.value).toBe('0,1,0\n1,0,1\n0,1,0');
      expect(startInput.value).toBe('0,0');
      expect(endInput.value).toBe('2,2');
      
      const clearButton = screen.getByRole('button', { name: 'Clear' });
      fireEvent.click(clearButton);
      
      expect(csvInput.value).toBe('');
      expect(startInput.value).toBe('');
      expect(endInput.value).toBe('');
    });
  });

  describe('Tab Switching', () => {
    it('should switch between CSV and JSON tabs', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvTab = screen.getByRole('button', { name: 'CSV' });
      const jsonTab = screen.getByRole('button', { name: 'JSON' });
      
      expect(csvTab).toHaveClass('active');
      expect(jsonTab).not.toHaveClass('active');
      
      fireEvent.click(jsonTab);
      
      expect(csvTab).not.toHaveClass('active');
      expect(jsonTab).toHaveClass('active');
    });
  });

  describe('Maze Submission', () => {
    it('should call onSendMaze when Run Maze button is clicked', async () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      await waitFor(() => {
        const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
        expect(runMazeButton).toBeInTheDocument();
      });
      
      const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
      fireEvent.click(runMazeButton);
      
      expect(mockOnSendMaze).toHaveBeenCalledWith(
        [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
        [0, 0],
        [2, 2]
      );
    });

    it('should show error when WebSocket is not connected', async () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={false} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0\n1,0,1\n0,1,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      await waitFor(() => {
        const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
        expect(runMazeButton).toBeInTheDocument();
      });
      
      const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
      fireEvent.click(runMazeButton);
      
      expect(screen.getByText('WebSocket is not connected. Please check connection.')).toBeInTheDocument();
      expect(mockOnSendMaze).not.toHaveBeenCalled();
    });
  });

  describe('Back Button', () => {
    it('should call onBack when Back button is clicked', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const backButton = screen.getByRole('button', { name: 'Back' });
      fireEvent.click(backButton);
      
      expect(mockOnBack).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle single-cell maze', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '0,0' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText('Start and end points cannot be the same.')).toBeInTheDocument();
    });

    it('should handle large valid maze', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      // Create a 50x50 maze (under the 1MB limit)
      const largeMaze = Array(50).fill(Array(50).fill(0).join(',')).join('\n');
      
      fireEvent.change(csvInput, { target: { value: largeMaze } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '49,49' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it('should handle maze with only walls', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '1,1,1\n1,1,1\n1,1,1' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.getByText("Start and end points can't be on walls (1).")).toBeInTheDocument();
    });

    it('should handle maze with no walls', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,0,0\n0,0,0\n0,0,0' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '2,2' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it('should handle rectangular (non-square) maze', () => {
      render(<MazeBuilder onBack={mockOnBack} onSendMaze={mockOnSendMaze} wsConnected={true} />);
      
      const csvInput = screen.getByPlaceholderText(/0,1,0,0,0,1,0,0,0,0/);
      const startInput = screen.getByPlaceholderText('0,0');
      const endInput = screen.getByPlaceholderText('9,9');
      
      fireEvent.change(csvInput, { target: { value: '0,1,0,1,0\n1,0,1,0,1' } });
      fireEvent.change(startInput, { target: { value: '0,0' } });
      fireEvent.change(endInput, { target: { value: '1,4' } });
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });
  });
});

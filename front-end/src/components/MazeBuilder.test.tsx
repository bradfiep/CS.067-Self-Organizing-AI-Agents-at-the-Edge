import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import MazeBuilder from './MazeBuilder';

describe('MazeBuilder Component', () => {
  let mockOnBack: () => void;
  let mockOnSendMaze: (maze: number[][], start: [number, number], end: [number, number]) => void;
  let mockSetExportType: vi.Mock;
  let mockSetInputType: vi.Mock;
  let mockSetCsv: vi.Mock;
  let mockSetJson: vi.Mock;
  let mockSetStart: vi.Mock;
  let mockSetEnd: vi.Mock;
  let mockSetMaze: vi.Mock;
  let mockSetStartPt: vi.Mock;
  let mockSetEndPt: vi.Mock;
  let mockSetError: vi.Mock;

  // Default props for MazeBuilder component
  const getDefaultProps = () => ({
    onBack: mockOnBack,
    onSendMaze: mockOnSendMaze,
    wsConnected: true,
    backendMessage: null,
    exportType: 'csv' as 'csv' | 'json',
    setExportType: mockSetExportType,
    inputType: 'csv' as 'csv' | 'json',
    setInputType: mockSetInputType,
    csv: '',
    setCsv: mockSetCsv,
    json: '',
    setJson: mockSetJson,
    start: '',
    setStart: mockSetStart,
    end: '',
    setEnd: mockSetEnd,
    maze: null,
    setMaze: mockSetMaze,
    startPt: [0, 0] as [number, number],
    setStartPt: mockSetStartPt,
    endPt: [0, 0] as [number, number],
    setEndPt: mockSetEndPt,
    error: '',
    setError: mockSetError,
  });

  beforeEach(() => {
    mockOnBack = vi.fn();
    mockOnSendMaze = vi.fn();
    mockSetExportType = vi.fn();
    mockSetInputType = vi.fn();
    mockSetCsv = vi.fn();
    mockSetJson = vi.fn();
    mockSetStart = vi.fn();
    mockSetEnd = vi.fn();
    mockSetMaze = vi.fn();
    mockSetStartPt = vi.fn();
    mockSetEndPt = vi.fn();
    mockSetError = vi.fn();
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  describe('Rendering', () => {
    it('should render the maze builder interface', () => {
      render(<MazeBuilder {...getDefaultProps()} />);
      
      expect(screen.getByText('Maze Builder')).toBeInTheDocument();
      expect(screen.getByText('1. Import Maze')).toBeInTheDocument();
      expect(screen.getByText('2. Set Start & End Points')).toBeInTheDocument();
      expect(screen.getByText('Generate Maze')).toBeInTheDocument();
    });

    it('should render CSV tab as active by default', () => {
      render(<MazeBuilder {...getDefaultProps()} />);
      
      const csvTab = screen.getByRole('button', { name: 'CSV' });
      expect(csvTab).toHaveClass('active');
    });

    it('should render Back button', () => {
      render(<MazeBuilder {...getDefaultProps()} />);
      
      expect(screen.getByRole('button', { name: 'Back' })).toBeInTheDocument();
    });
  });

  describe('CSV Parsing', () => {
    it('should parse valid CSV maze data', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      // Should call setMaze with the parsed maze
      expect(mockSetMaze).toHaveBeenCalledWith([[0, 1, 0], [1, 0, 1], [0, 1, 0]]);
      expect(mockSetStartPt).toHaveBeenCalledWith([0, 0]);
      expect(mockSetEndPt).toHaveBeenCalledWith([2, 2]);
      expect(mockSetError).toHaveBeenCalledWith('');
    });

    it('should handle CSV with whitespace', () => {
      const props = getDefaultProps();
      props.csv = '  0,1,0\n1,0,1\n0,1,0  ';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      // Should successfully parse despite whitespace
      expect(mockSetMaze).toHaveBeenCalled();
      expect(mockSetError).toHaveBeenCalledWith('');
    });
  });

  describe('JSON Parsing', () => {
    it('should parse valid JSON maze data', () => {
      const props = getDefaultProps();
      props.inputType = 'json';
      props.json = '[[0,1,0],[1,0,1],[0,1,0]]';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetMaze).toHaveBeenCalledWith([[0, 1, 0], [1, 0, 1], [0, 1, 0]]);
      expect(mockSetError).toHaveBeenCalledWith('');
    });

    it('should show error for invalid JSON', () => {
      const props = getDefaultProps();
      props.inputType = 'json';
      props.json = 'not valid json';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Invalid maze data. Please check the format.');
    });
  });

  describe('Validation - Input Size', () => {
    it('should reject maze input larger than 1MB', () => {
      const props = getDefaultProps();
      // Create a string larger than 1MB
      props.csv = '0,1,0,1,0\n'.repeat(200000);
      props.start = '0,0';
      props.end = '1,1';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Input too large. Maximum 1MB of maze data allowed.');
    });
  });

  describe('Validation - Empty Inputs', () => {
    it('should show error when maze data is empty', () => {
      const props = getDefaultProps();
      props.csv = '';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Please enter maze data in CSV format.');
    });

    it('should show error when start point is empty', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Please enter start point (e.g., 0,0).');
    });

    it('should show error when end point is empty', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = '';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Please enter end point (e.g., 4,4).');
    });
  });

  describe('Validation - Point Format', () => {
    it('should show error for invalid start point format', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = 'invalid';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Invalid start or end points. Use format like 0,0');
    });

    it('should show error for invalid end point format', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = 'abc';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Invalid start or end points. Use format like 0,0');
    });
  });

  describe('Validation - Point Bounds', () => {
    it('should show error when start point is out of bounds', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '10,10';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Start point is out of bounds.');
    });

    it('should show error when end point is out of bounds', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = '5,5';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('End point is out of bounds.');
    });

    it('should show error when start point is negative', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '-1,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Start point is out of bounds.');
    });
  });

  describe('Validation - Same Start and End', () => {
    it('should show error when start and end points are the same', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '1,1';
      props.end = '1,1';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Start and end points cannot be the same.');
    });
  });

  describe('Validation - Points on Walls', () => {
    it('should show error when start point is on a wall', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,1'; // This is a wall (1)
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith("Start and end points can't be on walls (1).");
    });

    it('should show error when end point is on a wall', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = '1,0'; // This is a wall (1)
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith("Start and end points can't be on walls (1).");
    });
  });

  describe('Clear Functionality', () => {
    it('should clear all inputs when Clear button is clicked', () => {
      const props = getDefaultProps();
      props.csv = '0,1,0\n1,0,1\n0,1,0';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const clearButton = screen.getByRole('button', { name: 'Clear' });
      fireEvent.click(clearButton);
      
      // Should call all the state setters to clear values
      expect(mockSetCsv).toHaveBeenCalledWith('');
      expect(mockSetJson).toHaveBeenCalledWith('');
      expect(mockSetStart).toHaveBeenCalledWith('');
      expect(mockSetEnd).toHaveBeenCalledWith('');
      expect(mockSetMaze).toHaveBeenCalledWith(null);
      expect(mockSetStartPt).toHaveBeenCalledWith([0, 0]);
      expect(mockSetEndPt).toHaveBeenCalledWith([0, 0]);
      expect(mockSetError).toHaveBeenCalledWith('');
    });
  });

  describe('Tab Switching', () => {
    it('should switch between CSV and JSON tabs', () => {
      const props = getDefaultProps();
      render(<MazeBuilder {...props} />);
      
      const csvTab = screen.getByRole('button', { name: 'CSV' });
      const jsonTab = screen.getByRole('button', { name: 'JSON' });
      
      expect(csvTab).toHaveClass('active');
      expect(jsonTab).not.toHaveClass('active');
      
      fireEvent.click(jsonTab);
      
      expect(mockSetInputType).toHaveBeenCalledWith('json');
    });
  });

  describe('Maze Submission', () => {
    it('should call onSendMaze when Run Maze button is clicked', async () => {
      const props = { 
        ...getDefaultProps(), 
        maze: [[0, 1, 0], [1, 0, 1], [0, 1, 0]] as number[][] | null,
        startPt: [0, 0] as [number, number],
        endPt: [2, 2] as [number, number]
      };
      render(<MazeBuilder {...props} />);
      
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
      const props = { 
        ...getDefaultProps(), 
        wsConnected: false,
        maze: [[0, 1, 0], [1, 0, 1], [0, 1, 0]] as number[][] | null,
        startPt: [0, 0] as [number, number],
        endPt: [2, 2] as [number, number]
      };
      render(<MazeBuilder {...props} />);
      
      await waitFor(() => {
        const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
        expect(runMazeButton).toBeInTheDocument();
      });
      
      const runMazeButton = screen.getByRole('button', { name: 'Run Maze' });
      fireEvent.click(runMazeButton);
      
      expect(mockSetError).toHaveBeenCalledWith('WebSocket is not connected. Please check connection.');
      expect(mockOnSendMaze).not.toHaveBeenCalled();
    });
  });

  describe('Back Button', () => {
    it('should call onBack when Back button is clicked', () => {
      const props = getDefaultProps();
      render(<MazeBuilder {...props} />);
      
      const backButton = screen.getByRole('button', { name: 'Back' });
      fireEvent.click(backButton);
      
      expect(mockOnBack).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle single-cell maze', () => {
      const props = getDefaultProps();
      props.csv = '0';
      props.start = '0,0';
      props.end = '0,0';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith('Start and end points cannot be the same.');
    });

    it('should handle large valid maze', () => {
      const props = getDefaultProps();
      // Create a 50x50 maze (under the 1MB limit)
      props.csv = Array(50).fill(Array(50).fill(0).join(',')).join('\n');
      props.start = '0,0';
      props.end = '49,49';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      // Should not show an error
      expect(mockSetError).toHaveBeenCalledWith('');
      expect(mockSetMaze).toHaveBeenCalled();
    });

    it('should handle maze with only walls', () => {
      const props = getDefaultProps();
      props.csv = '1,1,1\n1,1,1\n1,1,1';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      expect(mockSetError).toHaveBeenCalledWith("Start and end points can't be on walls (1).");
    });

    it('should handle maze with no walls', () => {
      const props = getDefaultProps();
      props.csv = '0,0,0\n0,0,0\n0,0,0';
      props.start = '0,0';
      props.end = '2,2';
      
      render(<MazeBuilder {...props} />);
      
      const generateButton = screen.getByRole('button', { name: 'Generate Maze' });
      fireEvent.click(generateButton);
      
      // Should not show an error
      expect(mockSetError).toHaveBeenCalledWith('');
      expect(mockSetMaze).toHaveBeenCalled();
    });

   
  });
});

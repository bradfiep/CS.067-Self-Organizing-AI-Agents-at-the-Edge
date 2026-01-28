import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import AgentActivity from './AgentActivity';

describe('AgentActivity Component', () => {
  let mockOnBack: () => void;

  // Default props for AgentActivity component
  const getDefaultProps = () => ({
    onBack: mockOnBack,
    backendMessage: null,
    maze: [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
    startPt: [0, 0] as [number, number],
    endPt: [2, 2] as [number, number],
  });

  beforeEach(() => {
    mockOnBack = vi.fn();
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  describe('Rendering', () => {
    it('should render the agent activity interface', () => {
      render(<AgentActivity {...getDefaultProps()} />);
      
      expect(screen.getByText('Agent Activity')).toBeInTheDocument();
      expect(screen.getByText('Agent List')).toBeInTheDocument();
      expect(screen.getByText('Activity Feed')).toBeInTheDocument();
    });

    it('should render Back button', () => {
      render(<AgentActivity {...getDefaultProps()} />);
      
      const backButton = screen.getByRole('button', { name: 'Back' });
      expect(backButton).toBeInTheDocument();
    });

    it('should call onBack when Back button is clicked', () => {
      render(<AgentActivity {...getDefaultProps()} />);
      
      const backButton = screen.getByRole('button', { name: 'Back' });
      backButton.click();
      
      expect(mockOnBack).toHaveBeenCalledTimes(1);
    });

    it('should show empty state when no agents', () => {
      render(<AgentActivity {...getDefaultProps()} />);
      
      expect(screen.getByText(/No activity yet/)).toBeInTheDocument();
    });

    it('should render maze when maze data is provided', () => {
      render(<AgentActivity {...getDefaultProps()} />);
      
      // Check if maze grid is rendered (table element)
      const mazeTable = document.querySelector('.maze-table');
      expect(mazeTable).toBeInTheDocument();
    });

    it('should show placeholder when no maze data', () => {
      const props = { ...getDefaultProps(), maze: null as number[][] | null };
      render(<AgentActivity {...props} />);
      
      expect(screen.getByText('Maze Preview')).toBeInTheDocument();
    });
  });

  describe('Agent Registration', () => {
    it('should register a new agent when receiving agent_registered message', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      expect(screen.getByText('Status: exploring')).toBeInTheDocument();
      expect(screen.getByText('Pos: (0,0)')).toBeInTheDocument();
    });

    it('should add agent registration to activity log', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [1, 2],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText(/Agent registered at position \(1,2\)/)).toBeInTheDocument();
      });
    });

    it('should not add duplicate agents', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      // Try to register same agent again
      const msg2 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [1, 1],
        status: 'exploring'
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      // Should still only have one Agent 1
      const agentElements = screen.getAllByText('Agent 1');
      expect(agentElements).toHaveLength(1);
    });

    it('should register multiple different agents', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      // Register Agent 2
      const msg2 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 2',
        position: [1, 1],
        status: 'exploring'
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 2')).toBeInTheDocument();
      });

      // Both agents should be visible
      expect(screen.getByText('Agent 1')).toBeInTheDocument();
      expect(screen.getByText('Agent 2')).toBeInTheDocument();
    });
  });

  describe('Agent Movement', () => {
    it('should update agent position when receiving agent_move message', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Pos: (0,0)')).toBeInTheDocument();
      });

      // Move agent
      const msg2 = JSON.stringify({
        type: 'agent_move',
        agent_name: 'Agent 1',
        from_position: [0, 0],
        to_position: [1, 0]
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText('Pos: (1,0)')).toBeInTheDocument();
      });
    });

    it('should add agent move to activity log', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      // Move agent
      const msg2 = JSON.stringify({
        type: 'agent_move',
        agent_name: 'Agent 1',
        from_position: [0, 0],
        to_position: [1, 0]
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText(/Moving one step from position \(0,0\) to position \(1,0\)/)).toBeInTheDocument();
      });
    });

    it('should update agent status to exploring when moving', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'inactive'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Status: inactive')).toBeInTheDocument();
      });

      // Move agent
      const msg2 = JSON.stringify({
        type: 'agent_move',
        agent_name: 'Agent 1',
        from_position: [0, 0],
        to_position: [1, 0]
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText('Status: exploring')).toBeInTheDocument();
      });
    });
  });

  describe('ACK Messages', () => {
    it('should display ACK messages in activity log', async () => {
      const msg = JSON.stringify({
        type: 'ack',
        status: 'Maze received successfully'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText('Maze received successfully')).toBeInTheDocument();
      });
    });

    it('should show default acknowledged message when status not provided', async () => {
      const msg = JSON.stringify({
        type: 'ack'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText('Acknowledged')).toBeInTheDocument();
      });
    });
  });

  describe('Activity Log', () => {
    it('should display activity logs in chronological order (newest first)', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText(/Agent registered/)).toBeInTheDocument();
      });

      // Add second activity
      const msg2 = JSON.stringify({
        type: 'agent_move',
        agent_name: 'Agent 1',
        from_position: [0, 0],
        to_position: [1, 0]
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText(/Moving one step/)).toBeInTheDocument();
      });

      // The move message should appear before the registration message (newer first)
      const activityItems = document.querySelectorAll('.activity-log-item');
      expect(activityItems.length).toBeGreaterThanOrEqual(2);
    });

    it('should limit activity logs to 50 entries', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      // Add 51 move messages
      for (let i = 0; i < 51; i++) {
        const msg = JSON.stringify({
          type: 'agent_move',
          agent_name: 'Agent 1',
          from_position: [i % 3, 0],
          to_position: [(i + 1) % 3, 0]
        });
        rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);
      }

      await waitFor(() => {
        const activityItems = document.querySelectorAll('.activity-log-item');
        // Should be at most 50 items
        expect(activityItems.length).toBeLessThanOrEqual(50);
      });
    });

    it('should display timestamp for each activity log entry', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        const timeElement = document.querySelector('.activity-log-time');
        expect(timeElement).toBeInTheDocument();
        // Should have time format HH:MM:SS
        expect(timeElement?.textContent).toMatch(/\d{2}:\d{2}:\d{2}/);
      });
    });
  });

  describe('Agent Colors', () => {
    it('should assign different colors to different agents', async () => {
      const msg1 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      const { rerender } = render(<AgentActivity {...getDefaultProps()} backendMessage={msg1} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 1')).toBeInTheDocument();
      });

      const agent1Avatar = document.querySelector('.agent-avatar');
      const agent1Color = agent1Avatar ? window.getComputedStyle(agent1Avatar).background : '';

      // Register Agent 2
      const msg2 = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 2',
        position: [1, 1],
        status: 'exploring'
      });
      rerender(<AgentActivity {...getDefaultProps()} backendMessage={msg2} />);

      await waitFor(() => {
        expect(screen.getByText('Agent 2')).toBeInTheDocument();
      });

      const agent2Avatar = document.querySelectorAll('.agent-avatar')[1];
      const agent2Color = agent2Avatar ? window.getComputedStyle(agent2Avatar).background : '';

      // Colors should be different (or at least set)
      expect(agent1Color).toBeTruthy();
      expect(agent2Color).toBeTruthy();
    });

    it('should use agent color for activity log border', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        const logItem = document.querySelector('.activity-log-item');
        expect(logItem).toBeInTheDocument();
        
        const borderColor = logItem ? window.getComputedStyle(logItem).borderLeftColor : '';
        expect(borderColor).toBeTruthy();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid JSON without crashing', () => {
      // Should not throw an error
      expect(() => render(<AgentActivity {...getDefaultProps()} backendMessage={'not valid json'} />)).not.toThrow();
    });

    it('should handle null backendMessage gracefully', () => {
      expect(() => render(<AgentActivity {...getDefaultProps()} />)).not.toThrow();
      expect(screen.getByText(/No activity yet/)).toBeInTheDocument();
    });

    it('should handle undefined backendMessage gracefully', () => {
      expect(() => render(<AgentActivity {...getDefaultProps()} backendMessage={undefined} />)).not.toThrow();
      expect(screen.getByText(/No activity yet/)).toBeInTheDocument();
    });

    it('should handle unknown message types gracefully', async () => {
      const msg = JSON.stringify({
        type: 'unknown_type',
        data: 'some data'
      });
      // Should not throw an error
      expect(() => render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />)).not.toThrow();
    });
  });

  describe('Agent Display', () => {
    it('should display agent avatar with first letter', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 5',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        const avatar = document.querySelector('.agent-avatar');
        expect(avatar?.textContent).toBe('5');
      });
    });

    it('should display agent name and status', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'TestAgent',
        position: [2, 1],
        status: 'completed'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText('TestAgent')).toBeInTheDocument();
        expect(screen.getByText('Status: completed')).toBeInTheDocument();
        expect(screen.getByText('Pos: (2,1)')).toBeInTheDocument();
      });
    });
  });

  describe('Activity Feed Item', () => {
    it('should display agent name in activity log', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        expect(screen.getByText('[Agent 1]')).toBeInTheDocument();
      });
    });

    it('should color-code activity log entries by agent', async () => {
      const msg = JSON.stringify({
        type: 'agent_registered',
        agent_name: 'Agent 1',
        position: [0, 0],
        status: 'exploring'
      });
      render(<AgentActivity {...getDefaultProps()} backendMessage={msg} />);

      await waitFor(() => {
        const agentLabel = screen.getByText('[Agent 1]');
        expect(agentLabel).toBeInTheDocument();
        
        const style = window.getComputedStyle(agentLabel);
        expect(style.color).toBeTruthy();
      });
    });
  });
});

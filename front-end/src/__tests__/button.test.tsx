import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import Button from '../components/Button';

describe('Button Component', () => {
  it('renders with text content', () => {
    render(<Button>Test Button</Button>);
    
    expect(screen.getByRole('button', { name: /test button/i })).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    button.click();
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

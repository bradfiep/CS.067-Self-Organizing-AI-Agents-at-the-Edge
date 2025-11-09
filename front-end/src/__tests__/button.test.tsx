import { render, screen } from '@testing-library/react';
import Button from '../components/Button';

describe('Button Component', () => {
  it('renders with primary variant by default', () => {
    render(<Button>Test Button</Button>);
    
    expect(screen.getByRole('button', { name: /test button/i })).toBeInTheDocument();
  });

  it('renders with secondary variant when specified', () => {
    render(<Button variant="secondary">Secondary Button</Button>);
    
    const button = screen.getByRole('button', { name: /secondary button/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('button-secondary');
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    button.click();
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

import React from 'react';
import './Button.css';

// Reusable button component with primary and secondary variants
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
  style?: React.CSSProperties;
}


const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  variant = 'primary',
  className = '',
  style
}) => {
  return (
    <button
      style={{ margin: '5px 10px', ...style }}
      onClick={onClick}
      className={`button button-${variant} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;

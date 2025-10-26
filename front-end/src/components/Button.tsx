import React from 'react';
import './Button.css';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  variant = 'primary',
  className = '' 
}) => {
  return (
    <button 
      onClick={onClick}
      className={`button button-${variant} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;

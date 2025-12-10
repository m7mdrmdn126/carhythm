import React from 'react';
import './Card.css';

const Card = ({ 
  children, 
  variant = 'default',
  hover = false,
  className = '',
  onClick,
  ...props 
}) => {
  const classNames = [
    'card',
    `card-${variant}`,
    hover ? 'card-hover' : '',
    onClick ? 'card-clickable' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classNames} onClick={onClick} {...props}>
      {children}
    </div>
  );
};

export default Card;

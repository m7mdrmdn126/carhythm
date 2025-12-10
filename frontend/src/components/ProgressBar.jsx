import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ current, total, showText = true }) => {
  // Ensure we have valid numbers
  const currentNum = Number(current) || 0;
  const totalNum = Number(total) || 1;
  const percentage = Math.min(100, Math.max(0, (currentNum / totalNum) * 100));
  
  return (
    <div className="progress-bar-wrapper">
      {showText && (
        <div className="progress-info">
          <span className="progress-text">Question {currentNum} of {totalNum}</span>
          <span className="progress-percentage">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

export default ProgressBar;

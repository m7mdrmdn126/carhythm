import React, { useState } from 'react';
import './EssayQuestion.css';

const EssayQuestion = ({ question, onAnswer, initialValue = '' }) => {
  const [value, setValue] = useState(initialValue);
  const [charCount, setCharCount] = useState(initialValue.length);
  const maxLength = question.max_length || 500;
  const minLength = question.min_length || 0;

  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    setCharCount(newValue.length);
    onAnswer(newValue);
  };

  const isValid = charCount >= minLength && charCount <= maxLength;
  const progressPercentage = (charCount / maxLength) * 100;

  return (
    <div className="essay-question">
      <textarea
        className="essay-textarea"
        value={value}
        onChange={handleChange}
        placeholder={question.placeholder || "Share your thoughts here..."}
        maxLength={maxLength}
        rows={8}
      />
      <div className="essay-footer">
        <div className="essay-char-count">
          <span className={charCount > maxLength ? 'error' : ''}>
            {charCount}
          </span>
          <span className="char-count-separator">/</span>
          <span className="char-count-max">{maxLength}</span>
        </div>
        {minLength > 0 && (
          <div className="essay-min-length">
            {charCount < minLength ? (
              <span className="warning">
                Minimum {minLength} characters
              </span>
            ) : (
              <span className="success">✓ Minimum reached</span>
            )}
          </div>
        )}
      </div>
      <div className="essay-progress-track">
        <div 
          className={`essay-progress-fill ${progressPercentage > 90 ? 'warning' : ''}`}
          style={{ width: `${Math.min(progressPercentage, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default EssayQuestion;

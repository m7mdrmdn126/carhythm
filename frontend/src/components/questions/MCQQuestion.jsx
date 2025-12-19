import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './MCQQuestion.css';

const MCQQuestion = ({ question, onAnswer, initialValue = null, allowMultiple = false }) => {
  // Support both API v2 format (options.choices) and legacy format (options array)
  const options = question.options?.choices || question.options || [];
  const [selectedOptions, setSelectedOptions] = useState(
    initialValue ? (Array.isArray(initialValue) ? initialValue : [initialValue]) : []
  );
  const [showCheckmark, setShowCheckmark] = useState(null);

  const handleSelect = (optionValue) => {
    if (allowMultiple) {
      const newSelection = selectedOptions.includes(optionValue)
        ? selectedOptions.filter(v => v !== optionValue)
        : [...selectedOptions, optionValue];
      setSelectedOptions(newSelection);
      onAnswer(newSelection);
    } else {
      setSelectedOptions([optionValue]);
      setShowCheckmark(optionValue);
      
      // Hide checkmark after animation
      setTimeout(() => setShowCheckmark(null), 600);
      
      onAnswer(optionValue);
    }
  };

  const isSelected = (optionValue) => selectedOptions.includes(optionValue);

  return (
    <div className="mcq-question">
      {allowMultiple && (
        <p className="mcq-instruction">Select all that apply</p>
      )}
      <div className="mcq-options">
        {options.map((option, index) => {
          const optionValue = option.value || option.text || option;
          const optionLabel = option.label || option.text || option;
          const selected = isSelected(optionValue);
          
          return (
            <motion.div
              key={index}
              className={`mcq-option ${selected ? 'selected' : ''}`}
              onClick={() => handleSelect(optionValue)}
              whileTap={{ scale: 0.98 }}
              whileHover={{ scale: 1.02 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ 
                opacity: 1, 
                y: 0,
                scale: selected && showCheckmark === optionValue ? [1, 1.05, 1] : 1
              }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
            >
              <div className="mcq-option-number">{index + 1}.</div>
              <div className="mcq-option-check">
                {allowMultiple ? (
                  <div className={`checkbox ${selected ? 'checked' : ''}`}>
                    {selected && '✓'}
                  </div>
                ) : (
                  <div className={`radio ${selected ? 'checked' : ''}`}>
                    {selected && <div className="radio-dot"></div>}
                  </div>
                )}
              </div>
              <div className="mcq-option-label">{optionLabel}</div>
              {selected && !allowMultiple && showCheckmark === optionValue && (
                <motion.span
                  className="option-checkmark"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  ✓
                </motion.span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default MCQQuestion;

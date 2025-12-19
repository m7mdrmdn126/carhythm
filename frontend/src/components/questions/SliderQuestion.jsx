import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './SliderQuestion.css';

const SliderQuestion = ({ question, onAnswer, initialValue = null }) => {
  // Enhanced 5-point Likert scale with emoji support
  const scaleOptions = [
    { value: 1, label: "Strongly Disagree", emoji: "😵", color: "#ef4444" },
    { value: 2, label: "Disagree", emoji: "😐", color: "#f97316" },
    { value: 3, label: "Neutral", emoji: "😌", color: "#eab308" },
    { value: 4, label: "Agree", emoji: "😃", color: "#22c55e" },
    { value: 5, label: "Strongly Agree", emoji: "🤩", color: "#8b5cf6" }
  ];
  
  const [selectedValue, setSelectedValue] = useState(initialValue);
  const [hoveredValue, setHoveredValue] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleSelect = (value) => {
    setSelectedValue(value);
    setShowFeedback(true);
    
    // Hide feedback after a moment
    setTimeout(() => setShowFeedback(false), 600);
    
    onAnswer(value);
  };

  const displayValue = hoveredValue || selectedValue;
  const displayOption = scaleOptions.find(opt => opt.value === displayValue);

  return (
    <div className="likert-question-enhanced">
      {/* Interactive Scale */}
      <div className="likert-scale-container">
        <div className="likert-scale">
          {scaleOptions.map((option) => {
            const isSelected = selectedValue === option.value;
            const isHovered = hoveredValue === option.value;
            
            return (
              <motion.button
                key={option.value}
                onClick={() => handleSelect(option.value)}
                onMouseEnter={() => setHoveredValue(option.value)}
                onMouseLeave={() => setHoveredValue(null)}
                className={`likert-option ${isSelected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
                whileHover={{ scale: 1.15 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: option.value * 0.05 }}
              >
                <span className="likert-option-value">{option.value}</span>
                
                {isSelected && (
                  <motion.div
                    className="selection-ring"
                    layoutId="selection"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    style={{ borderColor: option.color }}
                  />
                )}
              </motion.button>
            );
          })}
        </div>
        
        {/* Scale Labels */}
        <div className="likert-labels">
          <span className="likert-label-start">Strongly Disagree</span>
          <span className="likert-label-end">Strongly Agree</span>
        </div>
      </div>

      {/* Live Feedback */}
      <AnimatePresence mode="wait">
        {displayOption && (
          <motion.div
            key={displayValue}
            className="likert-feedback-enhanced"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.3 }}
            style={{ 
              background: `linear-gradient(135deg, ${displayOption.color}15, ${displayOption.color}25)`,
              borderColor: `${displayOption.color}50`
            }}
          >
            <div className="feedback-text">
              <span className="feedback-label">{displayOption.label}</span>
              {selectedValue === displayValue && showFeedback && (
                <motion.span
                  className="feedback-checkmark"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 15 }}
                >
                  ✓
                </motion.span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SliderQuestion;

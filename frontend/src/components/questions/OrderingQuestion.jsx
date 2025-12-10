import React, { useState } from 'react';
import { motion, Reorder } from 'framer-motion';
import './OrderingQuestion.css';

const OrderingQuestion = ({ question, onAnswer, initialValue = null }) => {
  // Support both API v2 format (options.items) and legacy format (options array)
  const options = question.options?.items || question.options || [];
  const [items, setItems] = useState(
    initialValue || options.map((opt, idx) => ({ 
      id: idx, 
      value: opt.value || opt.text || opt,
      label: opt.label || opt.text || opt 
    }))
  );

  const handleReorder = (newOrder) => {
    setItems(newOrder);
    onAnswer(newOrder.map(item => item.value));
  };

  return (
    <div className="ordering-question">
      <p className="ordering-instruction">
        Drag to reorder from most to least important
      </p>
      <Reorder.Group 
        axis="y" 
        values={items} 
        onReorder={handleReorder}
        className="ordering-list"
      >
        {items.map((item, index) => (
          <Reorder.Item 
            key={item.id} 
            value={item}
            className="ordering-item"
            whileDrag={{ 
              scale: 1.05,
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
              cursor: 'grabbing'
            }}
          >
            <div className="ordering-rank">{index + 1}</div>
            <div className="ordering-content">
              <div className="ordering-label">{item.label}</div>
            </div>
            <div className="ordering-handle">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="6" cy="5" r="1.5" fill="currentColor"/>
                <circle cx="14" cy="5" r="1.5" fill="currentColor"/>
                <circle cx="6" cy="10" r="1.5" fill="currentColor"/>
                <circle cx="14" cy="10" r="1.5" fill="currentColor"/>
                <circle cx="6" cy="15" r="1.5" fill="currentColor"/>
                <circle cx="14" cy="15" r="1.5" fill="currentColor"/>
              </svg>
            </div>
          </Reorder.Item>
        ))}
      </Reorder.Group>
    </div>
  );
};

export default OrderingQuestion;

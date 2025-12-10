/**
 * XP Notification Component
 * Displays animated XP gain notification after answering questions
 * Fixed position top-right with slide-in animation
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './XPNotification.css';

const XPNotification = ({ show, xpAmount = 10, onComplete }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      
      // Auto-hide after 1.8s (0.3s slide-in + 1.0s stay + 0.5s fade-out)
      const timer = setTimeout(() => {
        setIsVisible(false);
        if (onComplete) {
          onComplete();
        }
      }, 1800);

      return () => clearTimeout(timer);
    }
  }, [show, onComplete]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="xp-notification"
          initial={{ x: 150, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{
            type: 'spring',
            stiffness: 200,
            damping: 20,
            duration: 0.3
          }}
        >
          <motion.div
            className="xp-content"
            animate={{
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 0.5,
              times: [0, 0.5, 1],
              repeat: 0
            }}
          >
            <span className="xp-icon">⚡</span>
            <span className="xp-text">+{xpAmount} XP</span>
          </motion.div>

          {/* Sparkle effects */}
          <motion.div
            className="sparkle sparkle-1"
            animate={{
              scale: [0, 1, 0],
              opacity: [0, 1, 0],
              x: [-10, -20],
              y: [-10, -20]
            }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            ✨
          </motion.div>
          <motion.div
            className="sparkle sparkle-2"
            animate={{
              scale: [0, 1, 0],
              opacity: [0, 1, 0],
              x: [10, 20],
              y: [-10, -20]
            }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            ✨
          </motion.div>
          <motion.div
            className="sparkle sparkle-3"
            animate={{
              scale: [0, 1, 0],
              opacity: [0, 1, 0],
              y: [10, 20]
            }}
            transition={{ duration: 0.6, delay: 0.25 }}
          >
            ✨
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default XPNotification;

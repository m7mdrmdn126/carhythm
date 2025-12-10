/**
 * Resume Modal Component
 * Displays when user returns and has saved progress
 * Allows user to continue or start fresh
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ResumeModal.css';

const ResumeModal = ({ 
  isOpen, 
  progressData, 
  onContinue, 
  onStartFresh, 
  onClose 
}) => {
  const [showConfirmation, setShowConfirmation] = useState(false);

  if (!isOpen) return null;

  const handleStartFresh = () => {
    setShowConfirmation(true);
  };

  const handleConfirmStartFresh = () => {
    setShowConfirmation(false);
    onStartFresh();
  };

  const handleCancelStartFresh = () => {
    setShowConfirmation(false);
  };

  // Format last activity date
  const formatLastActivity = (timestamp) => {
    if (!timestamp) return 'Recently';
    
    try {
      const date = new Date(timestamp);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Recently';
      }
      
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffMinutes = Math.floor(diffTime / (1000 * 60));
      const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

      if (diffMinutes < 1) {
        return 'Just now';
      } else if (diffMinutes < 60) {
        return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
      } else if (diffHours < 1) {
        return 'Less than an hour ago';
      } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
      } else {
        return `${diffDays} days ago`;
      }
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Recently';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="resume-modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal Container */}
          <motion.div
            className="resume-modal-container"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
          >
            {!showConfirmation ? (
              // Main Resume Screen
              <div className="resume-modal-content">
                <div className="resume-modal-header">
                  <motion.div
                    className="resume-icon"
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                  >
                    ⚡
                  </motion.div>
                  <h2>Welcome Back!</h2>
                  <p className="resume-subtitle">
                    You have an assessment in progress
                  </p>
                </div>

                <div className="progress-summary">
                  <div className="progress-stat">
                    <span className="stat-label">Progress</span>
                    <span className="stat-value">
                      {Math.round(progressData.percentage || 0)}%
                    </span>
                  </div>
                  <div className="progress-stat">
                    <span className="stat-label">Questions Answered</span>
                    <span className="stat-value">
                      {progressData.questions_answered || 0}
                    </span>
                  </div>
                  <div className="progress-stat">
                    <span className="stat-label">XP Earned</span>
                    <span className="stat-value">
                      ⚡ {progressData.total_xp || 0} XP
                    </span>
                  </div>
                  <div className="progress-stat">
                    <span className="stat-label">Last Activity</span>
                    <span className="stat-value stat-time">
                      {formatLastActivity(progressData.timestamp)}
                    </span>
                  </div>
                </div>

                <div className="progress-bar-container">
                  <div className="progress-bar-bg">
                    <motion.div
                      className="progress-bar-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${progressData.percentage || 0}%` }}
                      transition={{ duration: 0.8, delay: 0.3 }}
                    />
                  </div>
                </div>

                <div className="resume-modal-actions">
                  <motion.button
                    className="btn btn-primary btn-continue"
                    onClick={onContinue}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <span className="btn-icon">▶️</span>
                    Continue Where I Left Off
                  </motion.button>

                  <motion.button
                    className="btn btn-secondary btn-start-fresh"
                    onClick={handleStartFresh}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="btn-icon">🔄</span>
                    Start Fresh
                  </motion.button>
                </div>
              </div>
            ) : (
              // Confirmation Dialog
              <motion.div
                className="resume-modal-content confirmation-content"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="resume-modal-header">
                  <div className="resume-icon warning-icon">⚠️</div>
                  <h2>Start Fresh?</h2>
                  <p className="resume-subtitle warning-text">
                    This will discard your current progress
                  </p>
                </div>

                <div className="confirmation-message">
                  <p>
                    You've already completed <strong>{progressData.percentage || 0}%</strong> of 
                    the assessment and earned <strong>⚡ {progressData.total_xp || 0} XP</strong>.
                  </p>
                  <p>
                    Are you sure you want to start over? Your current progress will be lost.
                  </p>
                </div>

                <div className="resume-modal-actions">
                  <motion.button
                    className="btn btn-secondary"
                    onClick={handleCancelStartFresh}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Cancel
                  </motion.button>

                  <motion.button
                    className="btn btn-danger btn-confirm-fresh"
                    onClick={handleConfirmStartFresh}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Yes, Start Fresh
                  </motion.button>
                </div>
              </motion.div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default ResumeModal;

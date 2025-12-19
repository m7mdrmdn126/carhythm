import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../components/Button';
import './ModuleCompletion.css';

const ModuleCompletion = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showConfetti, setShowConfetti] = useState(true);
  
  // Get module data from navigation state
  const moduleData = location.state || {
    moduleName: 'Module',
    moduleEmoji: '✅',
    totalQuestions: 0,
    xpEarned: 0,
    nextPageId: null,
    colorPrimary: '#8b5cf6',
    colorSecondary: '#3b82f6',
  };

  useEffect(() => {
    // Hide confetti after animation
    const timer = setTimeout(() => setShowConfetti(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  const handleContinue = () => {
    if (moduleData.nextPageId) {
      navigate(`/module/${moduleData.nextPageId}`);
    } else {
      // All modules complete, go to feedback
      navigate('/feedback');
    }
  };

  return (
    <div 
      className="module-completion-container"
      style={{
        '--module-color-primary': moduleData.colorPrimary,
        '--module-color-secondary': moduleData.colorSecondary,
      }}
    >
      {/* Confetti Animation */}
      {showConfetti && (
        <div className="confetti-container">
          {[...Array(50)].map((_, i) => (
            <div 
              key={i} 
              className="confetti-piece"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${2 + Math.random() * 3}s`,
                backgroundColor: i % 2 === 0 ? moduleData.colorPrimary : moduleData.colorSecondary,
              }}
            />
          ))}
        </div>
      )}

      {/* Background Gradient */}
      <div className="completion-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      {/* Content */}
      <motion.div
        className="completion-content"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {/* Success Icon */}
        <motion.div
          className="success-icon"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ 
            type: "spring", 
            stiffness: 200, 
            damping: 12,
            delay: 0.2 
          }}
        >
          <div className="icon-circle">
            <span className="icon-emoji">{moduleData.moduleEmoji}</span>
            <motion.div
              className="checkmark"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              ✓
            </motion.div>
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          className="completion-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          ✨ Module Complete! ✨
        </motion.h1>

        {/* Module Name */}
        <motion.div
          className="completion-module-name"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {moduleData.moduleName} Assessment
        </motion.div>

        {/* Stats */}
        <motion.div
          className="completion-stats"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{moduleData.totalQuestions}/{moduleData.totalQuestions}</div>
            <div className="stat-label">Questions Answered</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎖️</div>
            <div className="stat-value">+{moduleData.xpEarned}</div>
            <div className="stat-label">XP Earned</div>
          </div>
        </motion.div>

        {/* Motivational Message */}
        <motion.p
          className="completion-message"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          {moduleData.nextPageId 
            ? "Fantastic work! Ready for the next chapter?"
            : "Amazing! You've completed all modules. Let's wrap up!"
          }
        </motion.p>

        {/* CTA Button */}
        <motion.div
          className="completion-cta"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8, type: "spring" }}
        >
          <Button
            variant="primary"
            size="large"
            onClick={handleContinue}
            className="continue-button"
          >
            {moduleData.nextPageId ? 'Continue to Next Chapter →' : 'Complete Assessment →'}
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default ModuleCompletion;

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import './ModuleIntro.css';

const ModuleIntro = () => {
  const { pageId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [moduleData, setModuleData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadModuleData();
  }, [pageId]);

  const loadModuleData = async () => {
    try {
      setLoading(true);
      const data = await api.getQuestions(pageId);
      
      setModuleData({
        id: data.page.id,
        title: data.page.title,
        module: data.page.module,
        description: data.page.module_description,
        emoji: data.page.module_emoji,
        chapterNumber: data.page.chapter_number,
        totalQuestions: data.questions.length,
        estimatedMinutes: data.page.estimated_minutes,
        colorPrimary: data.page.module_color_primary,
        colorSecondary: data.page.module_color_secondary,
      });
    } catch (err) {
      console.error('Failed to load module data:', err);
      setError('Could not load module information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBegin = () => {
    navigate(`/question/${pageId}`);
  };

  if (loading) {
    return (
      <div className="module-intro-loading">
        <LoadingSpinner size="large" message="Loading module..." />
      </div>
    );
  }

  if (error || !moduleData) {
    return (
      <div className="module-intro-error">
        <div className="error-icon">⚠️</div>
        <h2>Oops!</h2>
        <p>{error || 'Module not found'}</p>
        <Button onClick={() => navigate('/')}>Go Home</Button>
      </div>
    );
  }

  return (
    <div 
      className="module-intro-container"
      style={{
        '--module-color-primary': moduleData.colorPrimary,
        '--module-color-secondary': moduleData.colorSecondary,
      }}
    >
      {/* Animated Background */}
      <div className="module-intro-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      {/* Content */}
      <motion.div
        className="module-intro-content"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        {/* Module Icon */}
        <motion.div
          className="module-icon"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ 
            type: "spring", 
            stiffness: 200, 
            damping: 15,
            delay: 0.2 
          }}
        >
          <span className="module-emoji">{moduleData.emoji}</span>
        </motion.div>

        {/* Chapter Badge */}
        <motion.div
          className="chapter-badge"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          Chapter {moduleData.chapterNumber} of 3
        </motion.div>

        {/* Title */}
        <motion.h1
          className="module-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {moduleData.title}
        </motion.h1>

        {/* Module Name */}
        <motion.div
          className="module-name"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          {moduleData.module} Assessment
        </motion.div>

        {/* Description */}
        <motion.p
          className="module-description"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          {moduleData.description}
        </motion.p>

        {/* Stats */}
        <motion.div
          className="module-stats"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <div className="stat-item">
            <span className="stat-icon">📝</span>
            <span className="stat-value">{moduleData.totalQuestions}</span>
            <span className="stat-label">Questions</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-icon">⏱</span>
            <span className="stat-value">~{moduleData.estimatedMinutes}</span>
            <span className="stat-label">Minutes</span>
          </div>
        </motion.div>

        {/* CTA Button */}
        <motion.div
          className="module-cta"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ 
            delay: 0.9,
            type: "spring",
            stiffness: 300
          }}
        >
          <Button
            variant="primary"
            size="large"
            onClick={handleBegin}
            className="begin-button"
          >
            🚀 Let's Begin!
          </Button>
        </motion.div>

        {/* Progress Hint */}
        <motion.div
          className="progress-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          Your progress is automatically saved
        </motion.div>
      </motion.div>
    </div>
  );
};

export default ModuleIntro;

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';
import { getProgress, clearProgress, hasValidProgress, saveProgress } from '../services/storage';
import Button from '../components/Button';
import './Welcome.css';

const Welcome = () => {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showStartForm, setShowStartForm] = useState(false);
  const [savedProgress, setSavedProgress] = useState(null);

  useEffect(() => {
    loadModules();
    checkForSavedProgress();
  }, []);

  const checkForSavedProgress = async () => {
    if (hasValidProgress()) {
      const progress = getProgress();
      if (progress && progress.session_id) {
        try {
          const response = await api.validateSession(progress.session_id);
          if (response.valid) {
            setSavedProgress(response.progress);
          } else {
            clearProgress();
          }
        } catch (err) {
          console.error('Failed to validate session:', err);
          clearProgress();
        }
      }
    }
  };

  const loadModules = async () => {
    try {
      setLoading(true);
      const data = await api.getModules();
      setModules(data);
    } catch (err) {
      console.error('Failed to load modules:', err);
      setError('Could not load assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAssessment = async (startPageId = null) => {
    try {
      const session = await api.startSession();
      if (session.session_id && modules.length > 0) {
        // Navigate to specified page or first module
        const targetPageId = startPageId || modules[0]?.id;
        if (targetPageId) {
          // Initialize progress for new session
          saveProgress({
            session_id: session.session_id,
            current_page_id: targetPageId,
            current_question_index: 0,
            percentage: 0,
            total_xp: 0,
            questions_answered: 0
          });
          // Navigate to module intro first
          navigate(`/module/${targetPageId}`);
        } else {
          setError('No questions available. Please contact administrator.');
        }
      } else {
        setError('Could not start session. Please try again.');
      }
    } catch (err) {
      console.error('Failed to start session:', err);
      setError('Could not start assessment. Please try again.');
    }
  };

  const handleContinue = () => {
    const progress = getProgress();
    
    if (progress && progress.current_page_id) {
      navigate(`/question/${progress.current_page_id}`);
    } else if (savedProgress && savedProgress.current_page_id) {
      navigate(`/question/${savedProgress.current_page_id}`);
    } else {
      console.warn('No valid page ID found, starting fresh');
      handleStartFresh();
    }
  };

  const handleStartFresh = async () => {
    const progress = getProgress();
    if (progress && progress.session_id) {
      try {
        await api.abandonSession(progress.session_id);
      } catch (err) {
        console.error('Failed to abandon session:', err);
      }
    }
    
    clearProgress();
    setSavedProgress(null);
    handleStartAssessment();
  };
  
  const handleBeginJourney = () => {
    if (savedProgress) {
      // Show the start form with resume option
      setShowStartForm(true);
    } else {
      // No saved progress, start directly
      handleStartAssessment();
    }
  };

  if (loading) {
    return (
      <div className="welcome-loading">
        <div className="loading-spinner"></div>
        <p>Loading your journey...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="welcome-error">
        <div className="error-icon">⚠️</div>
        <h2>Oops!</h2>
        <p>{error}</p>
        <Button onClick={loadModules}>Try Again</Button>
      </div>
    );
  }

  const totalQuestions = modules.reduce((sum, mod) => sum + (mod.total_questions || 0), 0);
  const estimatedTime = modules.reduce((sum, mod) => sum + (mod.estimated_minutes || 0), 0);

  return (
    <div className="welcome-container">
      {!showStartForm ? (
        <>
          {/* Parallax Hero Section */}
          <motion.div 
            className="parallax-hero"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              className="hero-content"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
            >
              <motion.div 
                className="hero-logo-container"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <img src="/CaRhythm updated logo.png" alt="CaRhythm" className="hero-logo" />
                <h2 className="hero-brand-name">CaRhythm</h2>
              </motion.div>
              
              <motion.h1 
                className="hero-title-massive"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                Discover Your
                <span className="title-highlight"> Career DNA</span>
              </motion.h1>
              
              <motion.p 
                className="hero-subtitle-large"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                A scientifically-backed journey to uncover your unique strengths,
                personality traits, and ideal career pathways
              </motion.p>
              
              <motion.div
                className="hero-cta"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.8 }}
              >
                <Button 
                  variant="primary" 
                  size="large"
                  onClick={handleBeginJourney}
                  className="cta-button-massive"
                >
                  🚀 Start the Journey
                </Button>
                <p className="hero-time">
                  <span className="time-icon">⏱</span>
                  {estimatedTime} minutes · {totalQuestions} questions
                </p>
              </motion.div>
            </motion.div>
            
            {/* Scroll Indicator - Inside Hero */}
            <motion.div 
              className="scroll-indicator"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5, duration: 1 }}
            >
              <span className="scroll-text">Scroll to explore</span>
              <div className="scroll-arrow">↓</div>
            </motion.div>
          </motion.div>

          {/* Floating Background Elements */}
          <div className="floating-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>

          {/* Features Section with Parallax Cards */}
          <motion.section 
            className="features-section"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="section-title-big">What You'll Discover</h2>
            
            <div className="features-grid-modern">
              <motion.div 
                className="feature-card-large"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="feature-icon-large">🧠</div>
                <h3 className="feature-title-large">Find Your Flow</h3>
                <p className="feature-description">
                  Discover your natural career passions through the Holland Code framework
                </p>
                <div className="feature-badge">Career Interests</div>
              </motion.div>

              <motion.div 
                className="feature-card-large"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="feature-icon-large">👤</div>
                <h3 className="feature-title-large">Discover Your Design</h3>
                <p className="feature-description">
                  Understand your core personality traits and behavioral patterns
                </p>
                <div className="feature-badge">Personality Traits</div>
              </motion.div>

              <motion.div 
                className="feature-card-large"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.3 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                <div className="feature-icon-large">🎵</div>
                <h3 className="feature-title-large">Own Your Edge</h3>
                <p className="feature-description">
                  Learn how you naturally approach tasks and handle pressure
                </p>
                <div className="feature-badge">Work Rhythm</div>
              </motion.div>
            </div>
          </motion.section>

          {/* Stats Section */}
          <motion.section 
            className="stats-section-modern"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="stats-container-modern">
              <div className="stat-item-modern">
                <div className="stat-number">{modules.length}</div>
                <div className="stat-label">Assessment Modules</div>
              </div>
              <div className="stat-divider-modern"></div>
              <div className="stat-item-modern">
                <div className="stat-number">{totalQuestions}</div>
                <div className="stat-label">Total Questions</div>
              </div>
              <div className="stat-divider-modern"></div>
              <div className="stat-item-modern">
                <div className="stat-number">{estimatedTime}min</div>
                <div className="stat-label">Completion Time</div>
              </div>
            </div>
          </motion.section>

          {/* Trust Indicators */}
          <motion.section 
            className="trust-section"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="trust-badges-modern">
              <div className="trust-badge-modern">
                <span className="trust-icon-large">🔬</span>
                <span className="trust-label">Research-Based</span>
              </div>
              <div className="trust-badge-modern">
                <span className="trust-icon-large">✓</span>
                <span className="trust-label">Validated Methods</span>
              </div>
              <div className="trust-badge-modern">
                <span className="trust-icon-large">📊</span>
                <span className="trust-label">Data-Driven</span>
              </div>
            </div>
          </motion.section>

          {/* Final CTA */}
          <motion.section 
            className="final-cta-section"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="final-cta-title">Ready to Begin?</h2>
            <p className="final-cta-subtitle">
              Your personalized career insights are just minutes away
            </p>
            <Button 
              variant="primary" 
              size="large"
              onClick={handleBeginJourney}
              className="cta-button-final"
            >
              🚀 Start Your Assessment
            </Button>
          </motion.section>

          {/* Footer */}
          <footer className="welcome-footer-modern">
            <div className="footer-content">
              <img src="/CaRhythm updated logo.png" alt="CaRhythm" className="footer-logo" />
              <p className="footer-tagline">Career Compass with a Heartbeat</p>
            </div>
          </footer>
        </>
      ) : (
        // Start Form with Resume Option
        <motion.div 
          className="start-form-container"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="start-form-card">
            <button 
              className="back-button"
              onClick={() => setShowStartForm(false)}
            >
              ← Back
            </button>
            
            <h2 className="form-title">Welcome Back! 👋</h2>
            <p className="form-subtitle">
              You have an assessment in progress
            </p>

            <div className="progress-card">
              <div className="progress-header">
                <span className="progress-icon">⚡</span>
                <span className="progress-title">Your Progress</span>
              </div>
              
              <div className="progress-stats">
                <div className="progress-stat">
                  <div className="stat-label-small">Progress</div>
                  <div className="stat-value-large">{savedProgress?.percentage || 0}%</div>
                </div>
                <div className="progress-stat">
                  <div className="stat-label-small">Questions</div>
                  <div className="stat-value-large">{savedProgress?.questions_answered || 0}</div>
                </div>
                <div className="progress-stat">
                  <div className="stat-label-small">XP Earned</div>
                  <div className="stat-value-large">⚡ {savedProgress?.total_xp || 0}</div>
                </div>
              </div>

              <div className="progress-bar-container">
                <div 
                  className="progress-bar-fill"
                  style={{ width: `${savedProgress?.percentage || 0}%` }}
                ></div>
              </div>
              
              <p className="last-activity">
                Last activity: {formatLastActivity(savedProgress?.last_activity)}
              </p>
            </div>

            <div className="form-actions">
              <Button
                variant="primary"
                size="large"
                fullWidth
                onClick={handleContinue}
              >
                Continue Where You Left Off
              </Button>
              
              <Button
                variant="outline"
                size="large"
                fullWidth
                onClick={handleStartFresh}
              >
                Start Fresh
              </Button>
            </div>

            <p className="form-note">
              💡 Starting fresh will reset your progress
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};

// Helper function
const formatLastActivity = (timestamp) => {
  if (!timestamp) return 'Recently';
  
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) return 'Recently';
    
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return `${diffDays} days ago`;
  } catch (error) {
    return 'Recently';
  }
};

export default Welcome;

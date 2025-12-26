import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { api, getSessionId, getPreferredLanguage } from '../services/api';
import { saveProgress, updateProgress, getProgress } from '../services/storage';
import SliderQuestion from '../components/questions/SliderQuestion';
import MCQQuestion from '../components/questions/MCQQuestion';
import OrderingQuestion from '../components/questions/OrderingQuestion';
import EssayQuestion from '../components/questions/EssayQuestion';
import ProgressBar from '../components/ProgressBar';
import Button from '../components/Button';
import LoadingSpinner from '../components/LoadingSpinner';
import XPNotification from '../components/XPNotification';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './Question.css';

const Question = () => {
  const { pageId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [questionData, setQuestionData] = useState(null);
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [showXP, setShowXP] = useState(false);
  const [xpGained, setXpGained] = useState(10);
  const [totalXP, setTotalXP] = useState(0);
  const [showAnswerFeedback, setShowAnswerFeedback] = useState(false);
  const [autoAdvancing, setAutoAdvancing] = useState(false);
  const [moduleInfo, setModuleInfo] = useState(null);
  const [language, setLanguage] = useState(getPreferredLanguage());

  // Helper to get session ID from localStorage progress or sessionStorage
  const getCurrentSessionId = () => {
    const progress = getProgress();
    return progress?.session_id || getSessionId();
  };

  useEffect(() => {
    loadQuestion();
  }, [pageId, language]);

  const loadQuestion = async () => {
    try {
      setLoading(true);
      const data = await api.getQuestions(pageId, language);
      setQuestionData(data);
      
      // Store module info for header display
      setModuleInfo({
        name: data.page.module,
        emoji: data.page.module_emoji,
        chapterNumber: data.page.chapter_number,
        colorPrimary: data.page.module_color_primary,
        colorSecondary: data.page.module_color_secondary,
      });
      
      // Check if we should restore question index from saved progress
      const progress = getProgress();
      const sessionId = getCurrentSessionId();
      console.log('Loading page', pageId, 'with progress:', progress);
      console.log('SessionStorage sessionId:', getSessionId());
      console.log('Using sessionId:', sessionId);
      
      // If we have a valid session, find first unanswered question
      if (sessionId && data.questions.length > 0) {
        try {
          // Fetch which questions have been answered
          console.log('Fetching answered questions for session:', sessionId, 'page:', pageId);
          const answeredIds = await api.getAnsweredQuestions(sessionId, pageId);
          console.log('Answered question IDs:', answeredIds);
          const answeredSet = new Set(answeredIds);
          
          // Find first unanswered question
          let firstUnansweredIndex = -1;
          for (let i = 0; i < data.questions.length; i++) {
            if (!answeredSet.has(data.questions[i].id)) {
              firstUnansweredIndex = i;
              console.log('Found first unanswered question at index:', i, 'ID:', data.questions[i].id);
              break;
            }
          }
          
          // If all questions answered, go to last question or next page
          if (firstUnansweredIndex === -1) {
            console.log('All questions on this page answered');
            firstUnansweredIndex = data.questions.length - 1;
          }
          
          console.log('Setting question index to:', firstUnansweredIndex);
          setCurrentQuestionIndex(firstUnansweredIndex);
          
          // Update progress to reflect this position
          if (progress && progress.session_id) {
            updateProgress({
              current_page_id: parseInt(pageId),
              current_question_index: firstUnansweredIndex
            });
          }
        } catch (err) {
          console.error('Failed to fetch answered questions:', err);
          // Fallback to saved index if API fails
          if (progress && 
              progress.current_page_id === parseInt(pageId) && 
              progress.current_question_index !== undefined &&
              progress.current_question_index < data.questions.length) {
            console.log('Fallback: Restoring question index:', progress.current_question_index);
            setCurrentQuestionIndex(progress.current_question_index);
          } else {
            console.log('Fallback: Starting at question 0');
            setCurrentQuestionIndex(0);
          }
        }
      } else {
        console.log('No session or no questions, starting at question 0');
        setCurrentQuestionIndex(0);
        
        // Initialize progress if starting fresh
        if (progress && progress.session_id) {
          updateProgress({
            current_page_id: parseInt(pageId),
            current_question_index: 0
          });
        }
      }
      
      setCurrentAnswer(null);
    } catch (err) {
      console.error('Failed to load question:', err);
      setError('Could not load question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answer) => {
    setCurrentAnswer(answer);
    
    // Check if this question type should auto-advance
    const currentQuestion = questionData.questions[currentQuestionIndex];
    const questionType = currentQuestion.question_type || currentQuestion.type;
    
    if (shouldAutoAdvance(questionType)) {
      // Auto-submit for Slider and MCQ (single-select)
      handleAutoSubmit(answer);
    }
  };

  // Determine if question type should auto-advance
  const shouldAutoAdvance = (questionType) => {
    return questionType === 'slider' || questionType === 'mcq' || questionType === 'mcq-single';
  };

  // Handle auto-submission with coordinated timing
  const handleAutoSubmit = async (answer) => {
    if (autoAdvancing || submitting) return;
    
    const currentQuestion = questionData.questions[currentQuestionIndex];
    
    // For MCQ, check if it's multiple selection
    if ((currentQuestion.question_type === 'mcq' || currentQuestion.type === 'mcq') && 
        currentQuestion.options?.multiple === true) {
      // Don't auto-advance for multiple selection MCQ
      return;
    }
    
    setAutoAdvancing(true);
    
    // Show answer feedback (0.3s)
    setShowAnswerFeedback(true);
    await new Promise(resolve => setTimeout(resolve, 300));
    setShowAnswerFeedback(false);
    
    // Submit answer and show XP (0.5s XP animation)
    await submitAnswer(answer);
    
    // Total delay: 0.3s feedback + 0.5s XP = 0.8s
    // Then auto-advance
    await new Promise(resolve => setTimeout(resolve, 100)); // Small buffer
    
    setAutoAdvancing(false);
    advanceToNext();
  };

  const handleNext = async () => {
    if (!currentAnswer || submitting || autoAdvancing) return;
    
    setSubmitting(true);
    await submitAnswer(currentAnswer);
    setSubmitting(false);
    advanceToNext();
  };

  const submitAnswer = async (answer) => {
    const currentQuestion = questionData.questions[currentQuestionIndex];
    const sessionId = getCurrentSessionId();

    try {
      // Format answer based on question type
      const questionType = currentQuestion.question_type || currentQuestion.type;
      let answerPayload = {};
      
      if (questionType === 'slider') {
        answerPayload = {
          type: 'slider',
          value: answer
        };
      } else if (questionType === 'mcq' || questionType === 'mcq-single' || questionType === 'mcq-multiple') {
        answerPayload = {
          type: 'mcq',
          selected_options: Array.isArray(answer) ? answer : [answer]
        };
      } else if (questionType === 'ordering') {
        answerPayload = {
          type: 'ordering',
          ordered_items: answer
        };
      } else if (questionType === 'essay') {
        answerPayload = {
          type: 'essay',
          text: answer
        };
      }
      
      // Submit answer to backend
      const response = await api.submitAnswer({
        session_id: sessionId,
        question_id: currentQuestion.id,
        answer: answerPayload
      });

      // Handle XP and progress from response
      if (response) {
        const xp = response.xp_gained || 10;
        const total = response.total_xp || 0;
        const progress = response.progress || {};
        
        setXpGained(xp);
        setTotalXP(total);
        setShowXP(true);
        
        // Update only XP and stats, don't change current_page_id or current_question_index
        // Those will be updated by advanceToNext() after navigation
        updateProgress({
          percentage: progress.percentage || 0,
          total_xp: total,
          questions_answered: progress.questions_answered || 0
        });
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError('Could not submit answer. Please try again.');
      throw err;
    }
  };

  const advanceToNext = () => {
    // Move to next question or page
    if (currentQuestionIndex < questionData.questions.length - 1) {
      // Move to next question on same page
      const nextQuestionIndex = currentQuestionIndex + 1;
      console.log('Advancing to next question:', nextQuestionIndex, 'on page:', pageId);
      setCurrentQuestionIndex(nextQuestionIndex);
      setCurrentAnswer(null);
      
      // Update progress with current page (still on same page)
      const sessionId = getCurrentSessionId();
      updateProgress({
        session_id: sessionId,
        current_page_id: parseInt(pageId),
        current_question_index: nextQuestionIndex
      });
      console.log('Progress updated: page', pageId, 'question', nextQuestionIndex);
    } else {
      // Check if there's a next page
      if (questionData.navigation?.next_page_id) {
        const nextPageId = questionData.navigation.next_page_id;
        console.log('Module complete, showing completion screen before next module');
        
        // Calculate XP earned for this module
        const moduleXP = questionData.questions.length * 10;
        
        // Navigate to module completion screen with data
        navigate('/module-complete', {
          state: {
            moduleName: questionData.page.module,
            moduleEmoji: moduleInfo?.emoji || '✅',
            totalQuestions: questionData.questions.length,
            xpEarned: moduleXP,
            nextPageId: nextPageId,
            colorPrimary: moduleInfo?.colorPrimary,
            colorSecondary: moduleInfo?.colorSecondary,
          }
        });
      } else {
        // Assessment complete - navigate to feedback page
        console.log('Assessment complete, navigating to /feedback');
        navigate('/feedback');
      }
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setCurrentAnswer(null);
    } else if (questionData?.previous_page_id) {
      navigate(`/question/${questionData.previous_page_id}`);
    } else {
      navigate('/');
    }
  };

  if (loading) {
    return (
      <div className="question-loading">
        <LoadingSpinner size="large" message="Loading question..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="question-error">
        <div className="error-icon">⚠️</div>
        <h2>Oops!</h2>
        <p>{error}</p>
        <Button onClick={loadQuestion}>Try Again</Button>
      </div>
    );
  }

  if (!questionData || questionData.questions.length === 0) {
    return (
      <div className="question-error">
        <div className="error-icon">📝</div>
        <h2>No Questions</h2>
        <p>No questions found for this page.</p>
        <Button onClick={() => navigate('/')}>Go Home</Button>
      </div>
    );
  }

  const currentQuestion = questionData.questions[currentQuestionIndex];
  const totalQuestions = questionData.questions.length;
  const hasSceneNarrative = currentQuestion.scene_narrative || currentQuestion.scene_title;
  const questionType = currentQuestion.question_type || currentQuestion.type;
  const showNextButton = !shouldAutoAdvance(questionType) || 
                        (questionType === 'mcq' && currentQuestion.options?.multiple === true);

  const renderQuestion = () => {
    const props = {
      question: currentQuestion,
      onAnswer: handleAnswer,
      initialValue: currentAnswer,
      language: language
    };

    // Map backend question types to frontend components
    const questionType = currentQuestion.question_type || currentQuestion.type;
    
    switch (questionType) {
      case 'slider':
        return <SliderQuestion {...props} />;
      case 'mcq':
        // Check if multiple selection is allowed
        const isMultiple = currentQuestion.options?.multiple === true;
        return <MCQQuestion {...props} allowMultiple={isMultiple} />;
      case 'mcq-single':
        return <MCQQuestion {...props} allowMultiple={false} />;
      case 'mcq-multiple':
        return <MCQQuestion {...props} allowMultiple={true} />;
      case 'ordering':
        return <OrderingQuestion {...props} />;
      case 'essay':
        return <EssayQuestion {...props} />;
      default:
        return <div className="unknown-question-type">
          <p>Unknown question type: {questionType}</p>
          <p>Question: {currentQuestion.text}</p>
        </div>;
    }
  };

  return (
    <div 
      className={`question-container theme-${currentQuestion.scene_theme || 'default'}`}
      style={{
        '--module-color-primary': moduleInfo?.colorPrimary || '#8b5cf6',
        '--module-color-secondary': moduleInfo?.colorSecondary || '#3b82f6',
      }}
    >
      {/* XP Notification */}
      <XPNotification 
        show={showXP} 
        xpAmount={xpGained}
        onComplete={() => setShowXP(false)}
      />
      
      {/* CaRhythm Header with Module Badge */}
      <div className="question-header-brand">
        <div className="brand-mini">
          <img 
            src="/CaRhythm updated logo.png" 
            alt="CaRhythm" 
            className="brand-logo"
          />
          <span className="brand-name">CaRhythm</span>
        </div>
        <div className="header-right">
          <LanguageSwitcher onLanguageChange={setLanguage} />
          {moduleInfo && (
            <div className="module-badge">
              <span className="module-badge-emoji">{moduleInfo.emoji}</span>
              <span className="module-badge-text">
                Chapter {moduleInfo.chapterNumber}: {moduleInfo.name}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="question-progress">
        <ProgressBar 
          current={currentQuestionIndex + 1} 
          total={totalQuestions}
        />
      </div>

      {/* Scene Narrative (Story Mode) */}
      <AnimatePresence mode="wait">
        {hasSceneNarrative && (
          <motion.div
            key={`scene-${currentQuestionIndex}`}
            className="scene-narrative"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
          >
            {(currentQuestion.scene_image || currentQuestion.scene_image_url) && (
              <div className="scene-image">
                <img src={currentQuestion.scene_image || currentQuestion.scene_image_url} alt="Scene" />
              </div>
            )}
            {currentQuestion.scene_title && (
              <h2 className="scene-title">{currentQuestion.scene_title}</h2>
            )}
            {currentQuestion.scene_narrative && (
              <p className="scene-text">{currentQuestion.scene_narrative}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Question Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`question-${currentQuestionIndex}`}
          className="question-content"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <div className="question-header">
            <h3 className="question-text">{currentQuestion.text || currentQuestion.question_text}</h3>
            {currentQuestion.description && (
              <p className="question-description">{currentQuestion.description}</p>
            )}
          </div>

          <div className="question-body">
            {renderQuestion()}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="question-navigation">
        <Button
          variant="ghost"
          onClick={handleBack}
          icon="←"
        >
          Back
        </Button>
        {showNextButton && (
          <Button
            variant="primary"
            onClick={handleNext}
            disabled={!currentAnswer || submitting || autoAdvancing}
            loading={submitting}
            icon="→"
          >
            {currentQuestionIndex === totalQuestions - 1 && !questionData.navigation?.next_page_id
              ? 'Finish'
              : 'Next'}
          </Button>
        )}
      </div>
    </div>
  );
};

export default Question;

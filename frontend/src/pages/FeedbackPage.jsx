import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { getSessionId } from '../services/api';
import './FeedbackPage.css';

const FeedbackPage = () => {
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [experienceText, setExperienceText] = useState('');
  const [wouldRecommend, setWouldRecommend] = useState(null);
  const [suggestions, setSuggestions] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    const sessionId = getSessionId();
    
    if (!sessionId) {
      console.error('No session ID found');
      // Continue to email page even without session
      navigate('/email');
      return;
    }

    setIsSubmitting(true);

    try {
      const feedbackData = {
        session_id: sessionId,
        rating: rating || null,
        experience_text: experienceText.trim() || null,
        would_recommend: wouldRecommend,
        suggestions: suggestions.trim() || null
      };

      await api.post('/feedback/submit', feedbackData);
      
      // Navigate to email collection page
      navigate('/email');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      // Even if feedback fails, continue to email page
      navigate('/email');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = () => {
    // Skip feedback and go directly to email page
    navigate('/email');
  };

  const renderStars = () => {
    return [1, 2, 3, 4, 5].map((star) => (
      <button
        key={star}
        type="button"
        className={`star-button ${star <= (hoveredRating || rating) ? 'active' : ''}`}
        onMouseEnter={() => setHoveredRating(star)}
        onMouseLeave={() => setHoveredRating(0)}
        onClick={() => setRating(star)}
        aria-label={`Rate ${star} stars`}
      >
        <svg
          className="star-icon"
          viewBox="0 0 24 24"
          fill={star <= (hoveredRating || rating) ? 'currentColor' : 'none'}
          stroke="currentColor"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </button>
    ));
  };

  return (
    <div className="feedback-page">
      <div className="feedback-container">
        <div className="feedback-header">
          <div className="feedback-icon">💬</div>
          <h1>We'd Love Your Feedback!</h1>
          <p className="feedback-subtitle">
            Your feedback is <strong>optional</strong> but helps us improve the experience for everyone
          </p>
        </div>

        <div className="feedback-form">
          {/* Star Rating */}
          <div className="form-section">
            <label className="form-label">
              How would you rate your overall experience?
            </label>
            <div className="star-rating">
              {renderStars()}
            </div>
            {rating > 0 && (
              <p className="rating-text">
                {rating === 5 && "Excellent! ⭐"}
                {rating === 4 && "Great! 😊"}
                {rating === 3 && "Good 👍"}
                {rating === 2 && "Fair 😐"}
                {rating === 1 && "Poor 😔"}
              </p>
            )}
          </div>

          {/* Experience Text */}
          <div className="form-section">
            <label className="form-label" htmlFor="experience">
              How was your experience?
            </label>
            <textarea
              id="experience"
              className="form-textarea"
              placeholder="Share your thoughts about the assessment..."
              value={experienceText}
              onChange={(e) => setExperienceText(e.target.value)}
              rows={4}
              maxLength={2000}
            />
            <span className="char-count">
              {experienceText.length}/2000
            </span>
          </div>

          {/* Would Recommend */}
          <div className="form-section">
            <label className="form-label">
              Would you recommend this to others?
            </label>
            <div className="recommendation-buttons">
              <button
                type="button"
                className={`recommendation-btn ${wouldRecommend === true ? 'active yes' : ''}`}
                onClick={() => setWouldRecommend(true)}
              >
                <span className="recommendation-icon">👍</span>
                Yes
              </button>
              <button
                type="button"
                className={`recommendation-btn ${wouldRecommend === false ? 'active no' : ''}`}
                onClick={() => setWouldRecommend(false)}
              >
                <span className="recommendation-icon">👎</span>
                No
              </button>
            </div>
          </div>

          {/* Suggestions */}
          <div className="form-section">
            <label className="form-label" htmlFor="suggestions">
              Any suggestions for improvement?
            </label>
            <textarea
              id="suggestions"
              className="form-textarea"
              placeholder="Let us know how we can improve..."
              value={suggestions}
              onChange={(e) => setSuggestions(e.target.value)}
              rows={4}
              maxLength={2000}
            />
            <span className="char-count">
              {suggestions.length}/2000
            </span>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleSkip}
              disabled={isSubmitting}
            >
              Skip to Results
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback & Continue'}
            </button>
          </div>
        </div>

        <div className="feedback-footer">
          <p>✨ Thank you for taking the time to share your feedback!</p>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPage;

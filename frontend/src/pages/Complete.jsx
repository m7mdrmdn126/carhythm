import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';
import { getProgress } from '../services/storage';
import Button from '../components/Button';
import Card from '../components/Card';
import './Complete.css';

const Complete = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    age_group: '',
    country: '',
    origin_country: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [emailSent, setEmailSent] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isEditingEmail, setIsEditingEmail] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [resending, setResending] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.email) {
      setError('Full name and email are required');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      // Get session ID from localStorage progress object
      const progress = getProgress();
      const currentSessionId = progress?.session_id;
      
      console.log('Submitting with session ID:', currentSessionId);
      console.log('Progress data:', progress);
      
      if (!currentSessionId) {
        setError('Session not found. Please complete the assessment first.');
        setSubmitting(false);
        return;
      }
      
      const response = await api.submitStudentInfo({
        ...formData,
        session_id: currentSessionId
      });
      
      setSubmitted(true);
      setEmailSent(response.email_sent || false);
      setResponseMessage(response.message || 'Assessment completed!');
      setSessionId(response.session_id || currentSessionId);
      setNewEmail(formData.email);
      
    } catch (err) {
      console.error('Failed to submit info:', err);
      setError(err.response?.data?.detail || 'Could not submit your information. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!sessionId) {
      setError('Session not found. Please try again.');
      return;
    }

    try {
      setResending(true);
      setError(null);
      
      const emailToSend = isEditingEmail && newEmail ? newEmail : formData.email;
      
      const response = await api.resendResults({
        session_id: sessionId,
        new_email: isEditingEmail ? emailToSend : null
      });
      
      if (response.success) {
        setResponseMessage(response.message);
        setEmailSent(true);
        setIsEditingEmail(false);
        if (isEditingEmail) {
          setFormData({ ...formData, email: emailToSend });
        }
      } else {
        setError(response.message || 'Failed to resend email');
        setEmailSent(false);
      }
      
    } catch (err) {
      console.error('Failed to resend:', err);
      setError(err.response?.data?.detail || 'Failed to resend email. Please try again.');
    } finally {
      setResending(false);
    }
  };

  if (submitted) {
    return (
      <div className="complete-container">
        <motion.div
          className="complete-success"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="success-animation"
            initial={{ scale: 0 }}
            animate={{ scale: [0, 1.2, 1] }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="success-icon">
              {emailSent ? '📧' : '⚠️'}
            </div>
          </motion.div>
          
          <h1 className="success-title">
            {emailSent ? 'Check Your Email!' : 'Assessment Complete!'}
          </h1>
          
          <p className="success-message">
            {responseMessage}
          </p>
          
          <Card className="success-info">
            {emailSent ? (
              <>
                <h3>📬 Your Results Are On The Way!</h3>
                <p className="email-info">
                  We've sent a comprehensive PDF report to:<br/>
                  <strong className="email-address">{formData.email}</strong>
                </p>
                <ul className="email-checklist">
                  <li>✨ RIASEC Career Interests with Holland Code</li>
                  <li>🧠 Big Five Personality Profile</li>
                  <li>🚩 Behavioral Insights & Growth Areas</li>
                  <li>🎯 Ikigai Career Sweet Spot</li>
                  <li>💼 Personalized Career Recommendations</li>
                  <li>📝 Action Plan for Next Steps</li>
                </ul>
                <p className="email-note">
                  <strong>Didn't receive it?</strong> Check your spam folder, or use the button below to resend.
                </p>
              </>
            ) : (
              <>
                <h3>⚠️ Email Delivery Issue</h3>
                <p>
                  Your assessment was saved successfully, but we couldn't send the email.
                  Please try resending or contact support.
                </p>
              </>
            )}
          </Card>

          {/* Email Edit and Resend Section */}
          <Card className="resend-section">
            {isEditingEmail ? (
              <div className="email-edit-form">
                <h4>Update Email Address</h4>
                <div className="form-group">
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    placeholder="new.email@example.com"
                    className="email-input"
                  />
                </div>
                <div className="button-group">
                  <Button
                    onClick={handleResend}
                    variant="primary"
                    loading={resending}
                    disabled={resending || !newEmail}
                    icon="📧"
                  >
                    Send to New Email
                  </Button>
                  <Button
                    onClick={() => setIsEditingEmail(false)}
                    variant="secondary"
                    disabled={resending}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="resend-options">
                <Button
                  onClick={handleResend}
                  variant="secondary"
                  loading={resending}
                  disabled={resending}
                  icon="🔄"
                >
                  Resend Email
                </Button>
                <Button
                  onClick={() => {
                    setIsEditingEmail(true);
                    setNewEmail(formData.email);
                  }}
                  variant="outline"
                  disabled={resending}
                  icon="✏️"
                >
                  Change Email Address
                </Button>
              </div>
            )}
          </Card>

          {error && (
            <div className="form-error resend-error">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <div className="success-footer">
            <p className="footer-note">
              Your results are saved and ready! The PDF includes all visualizations, 
              career recommendations, and a personalized action plan.
            </p>
            <p className="footer-support">
              Need help? Contact us at <a href="mailto:support@carhythm.com">support@carhythm.com</a>
            </p>
          </div>

          <div className="success-social">
            <p>Share your journey with friends!</p>
            <div className="social-icons">
              <span>🔗</span>
              <span>📧</span>
              <span>💬</span>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="complete-container">
      <motion.div
        className="complete-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="complete-hero">
          <motion.div
            className="hero-emoji"
            initial={{ scale: 0 }}
            animate={{ scale: [0, 1.2, 1] }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            ✨
          </motion.div>
          <h1 className="complete-title">
            Assessment <span className="text-gradient">Complete!</span>
          </h1>
          <p className="complete-subtitle">
            Amazing work! You've completed all the questions.
          </p>
        </div>

        <motion.div
          className="complete-form-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2>Tell Us About Yourself</h2>
          <p className="form-description">
            We'll use this information to share your personalized career insights.
          </p>

          <form onSubmit={handleSubmit} className="student-form">
            <div className="form-group">
              <label htmlFor="full_name">Full Name *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="your.email@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="age_group">Age Group *</label>
              <select
                id="age_group"
                name="age_group"
                value={formData.age_group}
                onChange={handleChange}
                required
              >
                <option value="">Select your age group</option>
                <option value="Under 18">Under 18</option>
                <option value="18-24">18-24</option>
                <option value="25-34">25-34</option>
                <option value="35-44">35-44</option>
                <option value="45-54">45-54</option>
                <option value="55+">55+</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="country">Country of Residence *</label>
              <input
                type="text"
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
                required
                placeholder="e.g., United States, Egypt, Canada"
              />
            </div>

            <div className="form-group">
              <label htmlFor="origin_country">Country of Origin *</label>
              <input
                type="text"
                id="origin_country"
                name="origin_country"
                value={formData.origin_country}
                onChange={handleChange}
                required
                placeholder="e.g., United States, Egypt, Canada"
              />
            </div>

            {error && (
              <div className="form-error">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="large"
              fullWidth
              loading={submitting}
              disabled={submitting}
              icon="🚀"
            >
              Submit Information
            </Button>

            <p className="form-note">
              Your information is secure and will only be used to share your career assessment results.
            </p>
          </form>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Complete;

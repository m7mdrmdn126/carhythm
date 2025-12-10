import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Results.css';

const API_BASE = 'http://localhost:8000/api/v2';

const Results = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [sessionId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/scores/${sessionId}`);
      setProfile(response.data.profile);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError(err.response?.data?.detail || 'Failed to load results');
      setLoading(false);
    }
  };

  const getStrengthColor = (label) => {
    const colors = {
      'Very High': '#8b5cf6',
      'High': '#22c55e',
      'Medium': '#eab308',
      'Low': '#ef4444'
    };
    return colors[label] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="results-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Calculating your rhythm profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-container">
        <div className="error-message">
          <h2>Unable to Load Results</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/welcome')} className="btn-primary">
            Start New Assessment
          </button>
        </div>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="results-container">
      {/* Header */}
      <div className="results-header">
        <h1 className="results-title">Your CaRhythm Profile</h1>
        <p className="results-subtitle">
          Discover your unique professional rhythm
        </p>
      </div>

      {/* RIASEC Section */}
      <section className="results-section riasec-section">
        <div className="section-header">
          <h2>🎯 Career Interests (Holland Code)</h2>
          <div className="holland-code-badge">
            {profile.riasec.holland_code}
          </div>
        </div>
        
        <div className="strength-grid">
          {Object.entries(profile.riasec.strength_labels).map(([domain, label]) => {
            const domainNames = {
              R: 'Realistic',
              I: 'Investigative',
              A: 'Artistic',
              S: 'Social',
              E: 'Enterprising',
              C: 'Conventional'
            };
            
            return (
              <div key={domain} className="strength-card">
                <div className="strength-header">
                  <span className="domain-letter">{domain}</span>
                  <span className="domain-name">{domainNames[domain]}</span>
                </div>
                <div className="strength-bar-container">
                  <div 
                    className="strength-bar"
                    style={{
                      width: `${(profile.riasec.raw_scores[domain] / 15) * 100}%`,
                      backgroundColor: getStrengthColor(label)
                    }}
                  />
                </div>
                <div className="strength-info">
                  <span className="strength-score">{profile.riasec.raw_scores[domain]}/15</span>
                  <span 
                    className="strength-label"
                    style={{ color: getStrengthColor(label) }}
                  >
                    {label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Big Five Section */}
      <section className="results-section bigfive-section">
        <div className="section-header">
          <h2>🧠 Personality Traits</h2>
        </div>
        
        <div className="strength-grid">
          {Object.entries(profile.bigfive.strength_labels).map(([trait, label]) => {
            const traitNames = {
              O: 'Openness',
              C: 'Conscientiousness',
              E: 'Extraversion',
              A: 'Agreeableness',
              N: 'Emotional Stability'
            };
            
            return (
              <div key={trait} className="strength-card">
                <div className="strength-header">
                  <span className="domain-letter">{trait}</span>
                  <span className="domain-name">{traitNames[trait]}</span>
                </div>
                <div className="strength-bar-container">
                  <div 
                    className="strength-bar"
                    style={{
                      width: `${(profile.bigfive.raw_scores[trait] / 25) * 100}%`,
                      backgroundColor: getStrengthColor(label)
                    }}
                  />
                </div>
                <div className="strength-info">
                  <span className="strength-score">{profile.bigfive.raw_scores[trait]}/25</span>
                  <span 
                    className="strength-label"
                    style={{ color: getStrengthColor(label) }}
                  >
                    {label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Behavioral Flags Section */}
      <section className="results-section behavioral-section">
        <div className="section-header">
          <h2>🚀 Work Style Insights</h2>
        </div>
        
        <div className="flags-grid">
          {profile.behavioral.behavioral_flags.growth_mindset && (
            <div className="flag-card positive">
              <span className="flag-icon">✨</span>
              <h3>Growth Mindset</h3>
              <p>You believe abilities can be developed through practice</p>
            </div>
          )}
          
          {profile.behavioral.behavioral_flags.procrastination_risk && (
            <div className="flag-card warning">
              <span className="flag-icon">⏰</span>
              <h3>Task Initiation</h3>
              <p>Consider starting with small actions to build momentum</p>
            </div>
          )}
          
          {profile.behavioral.behavioral_flags.perfectionism_risk && (
            <div className="flag-card warning">
              <span className="flag-icon">🎯</span>
              <h3>Perfectionism Alert</h3>
              <p>Remember: progress over perfection</p>
            </div>
          )}
          
          {profile.behavioral.behavioral_flags.low_grit_risk && (
            <div className="flag-card warning">
              <span className="flag-icon">💪</span>
              <h3>Persistence Potential</h3>
              <p>Building grit can unlock long-term success</p>
            </div>
          )}
          
          {profile.behavioral.behavioral_flags.poor_regulation_risk && (
            <div className="flag-card warning">
              <span className="flag-icon">🧭</span>
              <h3>Self-Efficacy</h3>
              <p>Trust in your ability to figure things out</p>
            </div>
          )}
        </div>
      </section>

      {/* Ikigai Zones Section */}
      <section className="results-section ikigai-section">
        <div className="section-header">
          <h2>🌸 Your Ikigai Zones</h2>
          <p className="section-description">
            The intersection of what you love, what you're good at, what the world needs, and what you can be paid for
          </p>
        </div>
        
        <div className="ikigai-grid">
          <div className={`ikigai-zone zone-${profile.ikigai_zones.love.level.toLowerCase()}`}>
            <div className="zone-icon">❤️</div>
            <h3>Love</h3>
            <p className="zone-subtitle">What you love</p>
            <div className="zone-score">
              {profile.ikigai_zones.love.level}
            </div>
            <div className="zone-bar">
              <div 
                className="zone-fill"
                style={{ width: `${(profile.ikigai_zones.love.score / 4) * 100}%` }}
              />
            </div>
          </div>
          
          <div className={`ikigai-zone zone-${profile.ikigai_zones.mastery.level.toLowerCase()}`}>
            <div className="zone-icon">⚡</div>
            <h3>Mastery</h3>
            <p className="zone-subtitle">What you're good at</p>
            <div className="zone-score">
              {profile.ikigai_zones.mastery.level}
            </div>
            <div className="zone-bar">
              <div 
                className="zone-fill"
                style={{ width: `${(profile.ikigai_zones.mastery.score / 4) * 100}%` }}
              />
            </div>
          </div>
          
          <div className={`ikigai-zone zone-${profile.ikigai_zones.contribution.level.toLowerCase()}`}>
            <div className="zone-icon">🌍</div>
            <h3>Contribution</h3>
            <p className="zone-subtitle">What the world needs</p>
            <div className="zone-score">
              {profile.ikigai_zones.contribution.level}
            </div>
            <div className="zone-bar">
              <div 
                className="zone-fill"
                style={{ width: `${(profile.ikigai_zones.contribution.score / 4) * 100}%` }}
              />
            </div>
          </div>
          
          <div className={`ikigai-zone zone-${profile.ikigai_zones.sustainability.level.toLowerCase()}`}>
            <div className="zone-icon">💰</div>
            <h3>Sustainability</h3>
            <p className="zone-subtitle">What you can be paid for</p>
            <div className="zone-score">
              {profile.ikigai_zones.sustainability.level}
            </div>
            <div className="zone-bar">
              <div 
                className="zone-fill"
                style={{ width: `${(profile.ikigai_zones.sustainability.score / 4) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Actions */}
      <div className="results-actions">
        <button 
          onClick={() => window.print()} 
          className="btn-secondary"
        >
          📄 Download PDF
        </button>
        <button 
          onClick={() => navigate('/welcome')} 
          className="btn-primary"
        >
          Start New Assessment
        </button>
      </div>
    </div>
  );
};

export default Results;

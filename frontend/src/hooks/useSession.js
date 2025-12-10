import { useState, useEffect } from 'react';
import { api, getSessionId } from '../services/api';

/**
 * Custom hook for managing assessment session state
 */
export const useSession = () => {
  const [sessionId, setSessionId] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check for existing session
    const existingSession = getSessionId();
    if (existingSession) {
      setSessionId(existingSession);
      loadProgress(existingSession);
    }
  }, []);

  const startSession = async (studentData = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.startSession(studentData);
      setSessionId(response.session_id);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async (sessId = sessionId) => {
    if (!sessId) return;
    
    try {
      setLoading(true);
      const progressData = await api.getProgress(sessId);
      setProgress(progressData);
      return progressData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (answerData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.submitAnswer({
        ...answerData,
        session_id: sessionId
      });
      // Optionally reload progress after submitting
      if (response.success) {
        await loadProgress();
      }
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    sessionId,
    progress,
    loading,
    error,
    startSession,
    loadProgress,
    submitAnswer
  };
};

export default useSession;

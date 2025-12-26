import axios from 'axios';

// API Base Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v2`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add session token if available
    const sessionId = sessionStorage.getItem('session_id');
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API Service Methods
export const api = {
  // Health Check
  health: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Get all modules with metadata
  getModules: async () => {
    const response = await apiClient.get('/modules');
    return response.data;
  },

  // Get questions for a specific page
  getQuestions: async (pageId, language = 'en') => {
    const response = await apiClient.get('/questions', {
      params: { 
        page_id: pageId,
        language: language
      }
    });
    return response.data;
  },

  // Start a new assessment session
  startSession: async (studentData = {}) => {
    const response = await apiClient.post('/session/start', studentData);
    // Store session ID in sessionStorage
    if (response.data.session_id) {
      sessionStorage.setItem('session_id', response.data.session_id);
    }
    return response.data;
  },

  // Submit an answer
  submitAnswer: async (answerData) => {
    const response = await apiClient.post('/answers/submit', answerData);
    return response.data;
  },

  // Get session progress
  getProgress: async (sessionId) => {
    const response = await apiClient.get(`/session/${sessionId}/progress`);
    return response.data;
  },

  // Submit student information
  submitStudentInfo: async (studentInfo) => {
    const response = await apiClient.post('/student/info', studentInfo, {
      timeout: 60000 // 60 seconds for PDF generation
    });
    return response.data;
  },

  // Resend assessment results
  resendResults: async (resendData) => {
    const response = await apiClient.post('/resend-results', resendData);
    return response.data;
  },

  // Validate session for resume
  validateSession: async (sessionId) => {
    const response = await apiClient.get(`/session/${sessionId}/validate`);
    return response.data;
  },

  // Abandon session (when starting fresh)
  abandonSession: async (sessionId) => {
    const response = await apiClient.post(`/session/${sessionId}/abandon`);
    return response.data;
  },

  // Get answered questions for a session (optionally filtered by page)
  getAnsweredQuestions: async (sessionId, pageId = null) => {
    const params = pageId ? { page_id: pageId } : {};
    const response = await apiClient.get(`/session/${sessionId}/answered-questions`, { params });
    return response.data.answered_question_ids || [];
  },

  // Get theme settings
  getTheme: async (themeName = null) => {
    const params = themeName ? { theme: themeName } : {};
    const response = await apiClient.get('/settings/theme', { params });
    return response.data;
  },
};

// Helper function to clear session
export const clearSession = () => {
  sessionStorage.removeItem('session_id');
};

// Helper function to get current session ID
export const getSessionId = () => {
  return sessionStorage.getItem('session_id');
};

// Helper function to get preferred language
export const getPreferredLanguage = () => {
  return localStorage.getItem('preferredLanguage') || 'en';
};

// Helper function to set preferred language
export const setPreferredLanguage = (language) => {
  localStorage.setItem('preferredLanguage', language);
};

export default api;

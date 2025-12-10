/**
 * Progress Storage Service
 * Manages assessment progress persistence using localStorage with cookie fallback
 * Implements 30-day expiration for saved sessions
 */

const STORAGE_KEY = 'carhythm_progress';
const COOKIE_NAME = 'carhythm_progress';
const EXPIRY_DAYS = 30;

/**
 * Save progress to localStorage and cookie backup
 * @param {Object} progressData - Progress data to save
 * @param {string} progressData.session_id - Unique session identifier
 * @param {number} progressData.current_page_id - Current page ID
 * @param {number} progressData.percentage - Progress percentage (0-100)
 * @param {number} progressData.total_xp - Total XP earned
 * @param {number} progressData.questions_answered - Number of questions answered
 */
export const saveProgress = (progressData) => {
  try {
    const timestamp = new Date().toISOString();
    const dataToStore = {
      ...progressData,
      timestamp,
      version: '1.0' // For future compatibility
    };

    // Save to localStorage (primary storage)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToStore));
    } catch (localStorageError) {
      console.warn('localStorage not available:', localStorageError);
    }

    // Save to cookie (fallback)
    saveToCookie(dataToStore);

    return true;
  } catch (error) {
    console.error('Error saving progress:', error);
    return false;
  }
};

/**
 * Get saved progress from localStorage or cookie
 * @returns {Object|null} Progress data or null if not found/expired
 */
export const getProgress = () => {
  try {
    // Try localStorage first
    let progressData = null;
    
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        progressData = JSON.parse(stored);
      }
    } catch (localStorageError) {
      console.warn('localStorage not available, trying cookie:', localStorageError);
    }

    // Fallback to cookie if localStorage failed
    if (!progressData) {
      progressData = getFromCookie();
    }

    if (!progressData) {
      return null;
    }

    // Check if expired (30 days)
    if (isExpired(progressData.timestamp)) {
      clearProgress();
      return null;
    }

    return progressData;
  } catch (error) {
    console.error('Error getting progress:', error);
    return null;
  }
};

/**
 * Clear saved progress from both localStorage and cookie
 */
export const clearProgress = () => {
  try {
    // Clear localStorage
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (localStorageError) {
      console.warn('localStorage not available:', localStorageError);
    }

    // Clear cookie
    document.cookie = `${COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict`;
    
    return true;
  } catch (error) {
    console.error('Error clearing progress:', error);
    return false;
  }
};

/**
 * Check if a timestamp is expired (older than 30 days)
 * @param {string} timestamp - ISO timestamp string
 * @returns {boolean} True if expired
 */
export const isExpired = (timestamp) => {
  try {
    const savedDate = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - savedDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays > EXPIRY_DAYS;
  } catch (error) {
    console.error('Error checking expiry:', error);
    return true; // Treat as expired if error
  }
};

/**
 * Save data to cookie (fallback mechanism)
 * @param {Object} data - Data to save
 */
const saveToCookie = (data) => {
  try {
    const jsonString = JSON.stringify(data);
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + EXPIRY_DAYS);
    
    // Encode to handle special characters
    const encoded = encodeURIComponent(jsonString);
    
    document.cookie = `${COOKIE_NAME}=${encoded}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Strict`;
  } catch (error) {
    console.error('Error saving to cookie:', error);
  }
};

/**
 * Get data from cookie
 * @returns {Object|null} Parsed cookie data or null
 */
const getFromCookie = () => {
  try {
    const name = COOKIE_NAME + '=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
      let cookie = cookieArray[i].trim();
      if (cookie.indexOf(name) === 0) {
        const value = cookie.substring(name.length);
        return JSON.parse(decodeURIComponent(value));
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error reading from cookie:', error);
    return null;
  }
};

/**
 * Update specific progress fields without overwriting entire object
 * @param {Object} updates - Fields to update
 */
export const updateProgress = (updates) => {
  try {
    const currentProgress = getProgress();
    if (!currentProgress) {
      return false;
    }

    const updatedProgress = {
      ...currentProgress,
      ...updates,
      timestamp: new Date().toISOString() // Update timestamp
    };

    return saveProgress(updatedProgress);
  } catch (error) {
    console.error('Error updating progress:', error);
    return false;
  }
};

/**
 * Check if progress exists and is valid
 * @returns {boolean} True if valid progress exists
 */
export const hasValidProgress = () => {
  const progress = getProgress();
  return progress !== null && progress.session_id && !isExpired(progress.timestamp);
};

/**
 * Get progress summary for display
 * @returns {Object|null} Summary object or null
 */
export const getProgressSummary = () => {
  const progress = getProgress();
  if (!progress) {
    return null;
  }

  return {
    percentage: progress.percentage || 0,
    totalXP: progress.total_xp || 0,
    questionsAnswered: progress.questions_answered || 0,
    lastActivity: progress.timestamp,
    sessionId: progress.session_id
  };
};

export default {
  saveProgress,
  getProgress,
  clearProgress,
  isExpired,
  updateProgress,
  hasValidProgress,
  getProgressSummary
};

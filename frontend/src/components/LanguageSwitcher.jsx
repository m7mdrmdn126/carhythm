import React, { useState, useEffect } from 'react';
import './LanguageSwitcher.css';

const LanguageSwitcher = ({ onLanguageChange }) => {
  const [language, setLanguage] = useState('en');

  // Load saved language preference on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    setLanguage(savedLanguage);
    
    // Set initial direction
    document.documentElement.dir = savedLanguage === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = savedLanguage;
  }, []);

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    localStorage.setItem('preferredLanguage', newLanguage);
    
    // Update HTML dir and lang attributes for RTL support
    document.documentElement.dir = newLanguage === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLanguage;
    
    // Notify parent component
    if (onLanguageChange) {
      onLanguageChange(newLanguage);
    }
  };

  return (
    <div className="language-switcher">
      <button
        className={`language-btn ${language === 'en' ? 'active' : ''}`}
        onClick={() => handleLanguageChange('en')}
        aria-label="Switch to English"
      >
        EN
      </button>
      <button
        className={`language-btn ${language === 'ar' ? 'active' : ''}`}
        onClick={() => handleLanguageChange('ar')}
        aria-label="Switch to Arabic"
      >
        عربي
      </button>
    </div>
  );
};

export default LanguageSwitcher;

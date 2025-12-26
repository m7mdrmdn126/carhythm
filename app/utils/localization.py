"""
Localization utilities for bilingual support (English/Arabic)
"""
from typing import Any, Optional


def get_localized_text(obj: Any, field_name: str, language: str = "en") -> Optional[str]:
    """
    Get text in requested language with fallback to English.
    
    Args:
        obj: Database model object with text fields
        field_name: Base field name (e.g., 'question_text', 'title')
        language: Language code ('en' or 'ar')
    
    Returns:
        Localized text or None if field doesn't exist
        
    Examples:
        >>> get_localized_text(question, 'question_text', 'ar')
        # Returns question.question_text_ar if available, else question.question_text
    """
    if language == "ar":
        # Try to get Arabic version
        ar_field_name = f"{field_name}_ar"
        ar_value = getattr(obj, ar_field_name, None)
        
        # Return Arabic if available and not empty
        if ar_value and (isinstance(ar_value, str) and ar_value.strip()):
            return ar_value
    
    # Fallback to English (base field)
    en_value = getattr(obj, field_name, None)
    return en_value


def get_localized_json(obj: Any, field_name: str, language: str = "en") -> Optional[Any]:
    """
    Get JSON data (lists) in requested language with fallback.
    Used for MCQ options, ordering options, etc.
    
    Args:
        obj: Database model object
        field_name: Base field name (e.g., 'mcq_options')
        language: Language code ('en' or 'ar')
    
    Returns:
        JSON data (typically a list) or None
        
    Examples:
        >>> get_localized_json(question, 'mcq_options', 'ar')
        # Returns question.mcq_options_ar if available, else question.mcq_options
    """
    if language == "ar":
        # Try to get Arabic version
        ar_field_name = f"{field_name}_ar"
        ar_value = getattr(obj, ar_field_name, None)
        
        # Return Arabic if available and not empty
        if ar_value:
            return ar_value
    
    # Fallback to English (base field)
    en_value = getattr(obj, field_name, None)
    return en_value


def is_rtl_language(language: str) -> bool:
    """
    Check if a language is RTL (Right-to-Left).
    
    Args:
        language: Language code
        
    Returns:
        True if RTL language, False otherwise
    """
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    return language in rtl_languages


def get_supported_languages() -> list:
    """
    Get list of supported language codes.
    
    Returns:
        List of supported language codes
    """
    return ['en', 'ar']


def validate_language(language: str) -> str:
    """
    Validate and normalize language code.
    
    Args:
        language: Language code to validate
        
    Returns:
        Normalized language code ('en' or 'ar')
        Defaults to 'en' if invalid
    """
    language = language.lower().strip() if language else 'en'
    
    if language in get_supported_languages():
        return language
    
    # Default to English
    return 'en'

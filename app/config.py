"""
CaRhythm Configuration Management
Loads and validates environment variables for email, database, and app settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./career_dna.db"
    
    # Email Configuration (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "CaRhythm Team")
    
    # Admin Notifications
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    ADMIN_NAME: str = os.getenv("ADMIN_NAME", "CaRhythm Admin")
    
    # Application Settings
    APP_URL: str = os.getenv("APP_URL", "http://localhost:5173")
    ENABLE_EMAIL: bool = os.getenv("ENABLE_EMAIL", "true").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # PDF Settings
    MAX_PDF_SIZE_MB: int = 10
    PDF_GENERATION_TIMEOUT: int = 60  # seconds
    PDF_TEMPLATE_VERSION: str = os.getenv("PDF_TEMPLATE_VERSION", "v2")  # 'v1' or 'v2'
    PREMIUM_CHECKOUT_URL: str = os.getenv("PREMIUM_CHECKOUT_URL", "https://carhythm.com/premium")
    
    # Email Settings
    EMAIL_RETRY_ATTEMPTS: int = 3
    EMAIL_RETRY_DELAY: int = 5  # seconds
    MAX_RESEND_PER_SESSION: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_email_config() -> tuple[bool, str]:
    """
    Validate email configuration is complete
    Returns: (is_valid, error_message)
    """
    if not settings.ENABLE_EMAIL:
        return True, "Email disabled in configuration"
    
    if not settings.SMTP_USER:
        return False, "SMTP_USER not configured in .env"
    
    if not settings.SMTP_PASSWORD:
        return False, "SMTP_PASSWORD not configured in .env"
    
    if not settings.SMTP_FROM_EMAIL:
        return False, "SMTP_FROM_EMAIL not configured in .env"
    
    if not settings.ADMIN_EMAIL:
        return False, "ADMIN_EMAIL not configured in .env"
    
    return True, "Email configuration valid"


def get_settings() -> Settings:
    """Get settings instance"""
    return settings

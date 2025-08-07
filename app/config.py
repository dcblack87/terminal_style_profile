"""
Configuration settings for the hacker terminal personal brand page.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///terminal_brand.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 3600))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    
    # Pagination
    POSTS_PER_PAGE = 5
    
    # Site configuration
    SITE_NAME = os.environ.get('SITE_NAME', 'david.black')
    SITE_TAGLINE = os.environ.get('SITE_TAGLINE', 'Making apps for fun and profit')
    PROFILE_IMAGE_URL = os.environ.get('PROFILE_IMAGE_URL', '')
    
    # Social media links
    GITHUB_URL = os.environ.get('GITHUB_URL', '#')
    TWITTER_URL = os.environ.get('TWITTER_URL', '#')
    YOUTUBE_URL = os.environ.get('YOUTUBE_URL', '#')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Contact form settings
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'team@youremail.com')
    CONTACT_FORM_ENABLED = os.environ.get('CONTACT_FORM_ENABLED', 'false').lower() in ['true', 'on', '1']
    
    # reCAPTCHA configuration
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    
    # Terminal theme colors
    TERMINAL_COLORS = {
        'primary': '#00ff00',    # Matrix green
        'secondary': '#0080ff',  # Cyber blue
        'warning': '#ffff00',    # Terminal yellow
        'error': '#ff0040',      # Error red
        'background': '#000012', # Deep space black
        'surface': '#001122',    # Dark blue-black
        'text': '#e0e0e0',      # Light gray text
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Additional security headers for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
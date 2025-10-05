"""
Configuration settings for Kolam Generator application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kolam-generator-2025-secure-key')
    
    # Application settings
    MAX_GRID_SIZE = int(os.environ.get('MAX_GRID_SIZE', 20))
    MIN_GRID_SIZE = int(os.environ.get('MIN_GRID_SIZE', 4))
    DEFAULT_GRID_SIZE = int(os.environ.get('DEFAULT_GRID_SIZE', 8))
    
    # Image generation settings
    IMAGE_DPI = int(os.environ.get('IMAGE_DPI', 100))
    IMAGE_SIZE = (10, 10)  # Figure size in inches
    
    # Performance settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Cache settings
    CACHE_TIMEOUT = timedelta(hours=1)
    
    # Theme settings
    DEFAULT_THEME = 'light'
    SUPPORTED_THEMES = ['light', 'dark']
    
    # Color palette
    DEFAULT_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

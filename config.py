"""
Configuration settings for Streamlit Kolam Generator
"""
import streamlit as st

class Config:
    """Configuration class for the application"""
    
    # Grid settings
    MIN_GRID_SIZE = 4
    MAX_GRID_SIZE = 20
    DEFAULT_GRID_SIZE = 8
    
    # Image settings
    IMAGE_DPI = 100
    IMAGE_SIZE = (10, 10)
    
    # Default colors
    DEFAULT_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
    ]
    
    # Theme settings
    SUPPORTED_THEMES = ['light', 'dark']
    DEFAULT_THEME = 'light'

@st.cache_data
def get_app_config():
    """Get cached application configuration"""
    return {
        'version': '2.0.0',
        'author': 'Kolam Generator Team',
        'description': 'Advanced Traditional Kolam Pattern Generator'
    }


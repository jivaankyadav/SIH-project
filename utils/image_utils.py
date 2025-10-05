"""
Image utilities optimized for Streamlit deployment
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import streamlit as st
import logging
from config import Config

logger = logging.getLogger(__name__)

@st.cache_data
def get_theme_config(theme: str):
    """Cached theme configuration"""
    if theme.lower() == 'dark':
        return {
            'bg_color': '#0d1117',
            'default_color': '#58a6ff', 
            'accent_color': '#21262d',
            'grid_color': '#30363d'
        }
    else:
        return {
            'bg_color': '#ffffff',
            'default_color': '#1f77b4',
            'accent_color': '#f8f9fa',
            'grid_color': '#e1e4e8'
        }

def get_random_color():
    """Get random color from palette"""
    return np.random.choice(Config.DEFAULT_COLORS)

def create_kolam_image(ijngp, theme='light', kolam_color=None):
    """Create kolam image optimized for Streamlit"""
    try:
        if ijngp.size == 0:
            ijngp = np.array([[0, 0], [1, 1]])
        
        theme_config = get_theme_config(theme)
        color = kolam_color or theme_config['default_color']
        
        # Use Streamlit's matplotlib backend
        fig, ax = plt.subplots(
            figsize=Config.IMAGE_SIZE,
            facecolor=theme_config['bg_color'],
            dpi=Config.IMAGE_DPI
        )
        ax.set_facecolor(theme_config['bg_color'])
        
        if len(ijngp) > 1:
            # Transform coordinates
            ijngpx = (ijngp[:, 0] + ijngp[:, 1]) / 2
            ijngpy = (ijngp[:, 0] - ijngp[:, 1]) / 2
            
            # Main path
            ax.plot(ijngpx, ijngpy, 
                   color=color, linewidth=3, alpha=0.9,
                   linestyle='-', solid_capstyle='round', 
                   solid_joinstyle='round', zorder=10)
            
            # Shadow effect
            ax.plot(ijngpx, ijngpy, 
                   color=theme_config['accent_color'], linewidth=5, 
                   alpha=0.3, zorder=5)
            
            # Decorative dots
            if len(ijngpx) > 5:
                step = max(1, len(ijngpx) // 15)
                ax.scatter(ijngpx[::step], ijngpy[::step], 
                          color=color, s=25, alpha=0.7, zorder=20)
        
        # Configure appearance
        ND = int(np.max(np.abs(ijngp))) + 2 if len(ijngp) > 0 else 5
        padding = max(1, ND * 0.1)
        
        ax.set_xlim(-ND - padding, ND + padding)
        ax.set_ylim(-ND - padding, ND + padding)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Convert to base64
        plt.tight_layout(pad=0.1)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor=theme_config['bg_color'],
                   bbox_inches='tight', pad_inches=0.1, dpi=Config.IMAGE_DPI)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        logger.error(f"Image creation error: {e}")
        st.error(f"Image generation failed: {e}")
        return create_error_image(theme)

def create_error_image(theme='light'):
    """Create error image for failed generations"""
    theme_config = get_theme_config(theme)
    
    fig, ax = plt.subplots(figsize=(6, 6), facecolor=theme_config['bg_color'])
    ax.set_facecolor(theme_config['bg_color'])
    
    ax.text(0.5, 0.5, '⚠️\nGeneration Error\nPlease try again', 
           ha='center', va='center', transform=ax.transAxes,
           fontsize=14, color='red')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor=theme_config['bg_color'])
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"

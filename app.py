#!/usr/bin/env python3
"""
Advanced Kolam Generator - Streamlit Application
Traditional South Indian pattern generator with dual algorithms
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import logging

# Import custom modules
from utils.kolam_algorithms import KolamDrawV1, KolamDrawV2
from utils.image_utils import create_kolam_image, get_random_color
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Advanced Kolam Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/arnabc13/kolam-generator',
        'Report a bug': 'https://github.com/arnabc13/kolam-generator/issues',
        'About': "Generate beautiful traditional South Indian kolam patterns using computational algorithms."
    }
)

# Custom CSS
def load_custom_css():
    """Load custom CSS styling"""
    with open('assets/styles.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'last_generation_info' not in st.session_state:
        st.session_state.last_generation_info = None
    if 'generation_count' not in st.session_state:
        st.session_state.generation_count = 0

def create_algorithm_selector():
    """Create algorithm selection interface"""
    st.sidebar.markdown("### 🔬 Algorithm Selection")
    
    algorithm_options = {
        "v1": {
            "name": "One Stroke (Incomplete)",
            "description": "Single continuous path, artistic flowing style",
            "icon": "🎨"
        },
        "v2": {
            "name": "Complete Pattern", 
            "description": "Multiple strokes with full grid coverage",
            "icon": "🔗"
        }
    }
    
    selected_algorithm = st.sidebar.radio(
        "Choose Algorithm Type:",
        options=list(algorithm_options.keys()),
        format_func=lambda x: f"{algorithm_options[x]['icon']} {algorithm_options[x]['name']}",
        help="Select the type of kolam generation algorithm"
    )
    
    # Show algorithm description
    st.sidebar.info(algorithm_options[selected_algorithm]['description'])
    
    return selected_algorithm

def create_parameter_controls():
    """Create parameter control interface"""
    st.sidebar.markdown("### ⚙️ Pattern Parameters")
    
    # Grid size
    grid_size = st.sidebar.slider(
        "Grid Size",
        min_value=Config.MIN_GRID_SIZE,
        max_value=Config.MAX_GRID_SIZE,
        value=Config.DEFAULT_GRID_SIZE,
        help="Size of the dot grid (larger = more complex)"
    )
    
    # Complexity
    complexity = st.sidebar.slider(
        "Complexity",
        min_value=10,
        max_value=90,
        value=50,
        help="Pattern complexity (higher = more intricate paths)"
    ) / 100.0
    
    # Color selection
    st.sidebar.markdown("### 🎨 Color Settings")
    
    col1, col2 = st.sidebar.columns([2, 1])
    with col1:
        selected_color = st.color_picker(
            "Pattern Color",
            value="#1f77b4",
            help="Choose the color for your kolam pattern"
        )
    
    with col2:
        if st.button("🎲 Random", help="Pick a random color"):
            selected_color = get_random_color()
            st.rerun()
    
    # Theme selection
    theme = st.sidebar.selectbox(
        "Background Theme",
        options=["light", "dark"],
        index=0,
        help="Choose background theme for the pattern"
    )
    
    return {
        'algorithm': None,  # Will be set by caller
        'grid_size': grid_size,
        'complexity': complexity,
        'color': selected_color,
        'theme': theme
    }

def generate_kolam_pattern(params):
    """Generate kolam pattern with given parameters"""
    try:
        with st.spinner('🎨 Generating your beautiful kolam pattern...'):
            # Generate pattern based on algorithm
            if params['algorithm'] == 'v1':
                drawer = KolamDrawV1(params['grid_size'])
                path = drawer.generate_path(params['complexity'])
                algorithm_name = "One Stroke (Incomplete)"
            else:
                drawer = KolamDrawV2(params['grid_size'])
                path = drawer.generate_path(params['complexity'])
                algorithm_name = "Complete Pattern"
            
            # Create image
            image_data = create_kolam_image(path, params['theme'], params['color'])
            
            # Store in session state
            st.session_state.generated_image = image_data
            st.session_state.last_generation_info = {
                'algorithm': algorithm_name,
                'grid_size': params['grid_size'],
                'complexity': int(params['complexity'] * 100),
                'path_length': len(path),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'color': params['color'],
                'theme': params['theme']
            }
            st.session_state.generation_count += 1
            
            logger.info(f"Generated kolam: {algorithm_name}, size={params['grid_size']}, points={len(path)}")
            return True
            
    except Exception as e:
        logger.error(f"Error generating kolam: {e}")
        st.error(f"❌ Generation failed: {str(e)}")
        return False

def display_kolam_result():
    """Display the generated kolam and information"""
    if st.session_state.generated_image:
        # Create columns for layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🎨 Your Generated Kolam")
            # Display image
            image_bytes = base64.b64decode(st.session_state.generated_image.split(',')[1])
            st.image(image_bytes, use_column_width=True)
            
            # Download button
            st.download_button(
                label="📥 Download PNG",
                data=image_bytes,
                file_name=f"kolam_{st.session_state.generation_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                help="Download your kolam as a PNG image"
            )
        
        with col2:
            st.markdown("### 📊 Pattern Info")
            info = st.session_state.last_generation_info
            
            st.info(f"""
            **Algorithm:** {info['algorithm']}
            
            **Grid Size:** {info['grid_size']}×{info['grid_size']}
            
            **Complexity:** {info['complexity']}%
            
            **Path Points:** {info['path_length']:,}
            
            **Generated:** {info['timestamp']}
            
            **Theme:** {info['theme'].title()}
            """)
            
            # Generation statistics
            st.markdown("### 📈 Statistics")
            st.metric("Total Generated", st.session_state.generation_count)
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("🔄 Generate Similar", help="Generate with same settings"):
                # Keep current parameters but regenerate
                st.rerun()
                
            if st.button("🎲 Surprise Me!", help="Random parameters"):
                st.session_state.surprise_mode = True
                st.rerun()

def create_gallery():
    """Create a gallery of example patterns"""
    st.markdown("### 🖼️ Pattern Gallery")
    st.markdown("*Explore different kolam styles and get inspired!*")
    
    # Example configurations
    examples = [
        {"name": "Classic Flow", "algo": "v1", "size": 8, "complexity": 0.3},
        {"name": "Intricate Web", "algo": "v2", "size": 12, "complexity": 0.7},
        {"name": "Minimal Elegance", "algo": "v1", "size": 6, "complexity": 0.5},
        {"name": "Complex Mandala", "algo": "v2", "size": 16, "complexity": 0.8}
    ]
    
    cols = st.columns(len(examples))
    
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(f"🎨 {example['name']}", key=f"example_{i}"):
                # Set parameters and generate
                st.session_state.example_params = example
                st.rerun()

def create_info_section():
    """Create information and help section"""
    with st.expander("ℹ️ About Kolam Patterns"):
        st.markdown("""
        **Kolam** is a traditional art form from South India, particularly Tamil Nadu. These intricate patterns are:
        
        - 🎨 **Traditional Art**: Hand-drawn geometric and mathematical patterns
        - 🏠 **Cultural Heritage**: Created daily at home entrances for prosperity
        - 🔢 **Mathematical Beauty**: Based on grid systems and symmetrical designs
        - 🌅 **Spiritual Significance**: Represents harmony between human and nature
        
        Our algorithms recreate these beautiful patterns using computational methods while preserving their traditional essence.
        """)
    
    with st.expander("🔬 Algorithm Details"):
        st.markdown("""
        ### Algorithm V1: One Stroke (Incomplete)
        - **Single Path**: Creates one continuous flowing line
        - **Artistic Style**: Emphasizes aesthetic beauty over completeness
        - **Gate System**: Uses directional gates to control path flow
        - **Symmetry**: Maintains mathematical balance and harmony
        
        ### Algorithm V2: Complete Pattern
        - **Full Coverage**: Ensures comprehensive pattern completion
        - **Multiple Strokes**: May use several paths for complexity
        - **Grid Optimization**: Maximizes coverage of available grid points
        - **Geometric Precision**: Focuses on mathematical completeness
        """)

def handle_keyboard_shortcuts():
    """Handle keyboard shortcuts and quick actions"""
    # Add keyboard shortcut hints
    st.sidebar.markdown("### ⌨️ Quick Shortcuts")
    st.sidebar.markdown("""
    - **Ctrl+Enter**: Generate pattern
    - **Ctrl+R**: Random color  
    - **Ctrl+S**: Download image
    - **Space**: Surprise me mode
    """)

def main():
    """Main application function"""
    try:
        # Load custom styling
        load_custom_css()
        
        # Initialize session state
        initialize_session_state()
        
        # App header
        st.markdown("""
        # 🎨 Advanced Kolam Generator
        *Create beautiful traditional South Indian kolam patterns with computational algorithms*
        """)
        
        # Create sidebar controls
        algorithm = create_algorithm_selector()
        params = create_parameter_controls()
        params['algorithm'] = algorithm
        
        # Handle example parameters
        if 'example_params' in st.session_state:
            example = st.session_state.example_params
            params.update({
                'algorithm': example['algo'],
                'grid_size': example['size'], 
                'complexity': example['complexity']
            })
            del st.session_state.example_params
        
        # Handle surprise mode
        if 'surprise_mode' in st.session_state:
            params.update({
                'algorithm': np.random.choice(['v1', 'v2']),
                'grid_size': np.random.randint(6, 16),
                'complexity': np.random.uniform(0.2, 0.8),
                'color': get_random_color()
            })
            del st.session_state.surprise_mode
        
        # Generation button
        st.sidebar.markdown("### 🚀 Generate Pattern")
        if st.sidebar.button("🎨 Generate Kolam", type="primary", use_container_width=True):
            generate_kolam_pattern(params)
        
        # Add keyboard shortcuts info
        handle_keyboard_shortcuts()
        
        # Main content area
        if st.session_state.generated_image:
            display_kolam_result()
        else:
            # Welcome message
            st.markdown("""
            ## Welcome to Kolam Generator! 🙏
            
            **Get started by:**
            1. 🔬 Choose your preferred algorithm in the sidebar
            2. ⚙️ Adjust the pattern parameters 
            3. 🎨 Pick your favorite colors
            4. 🚀 Click "Generate Kolam" to create your masterpiece!
            
            ---
            """)
            
            # Create gallery
            create_gallery()
        
        # Information sections
        create_info_section()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            Made with ❤️ using Streamlit • Celebrating Traditional Art Through Technology<br>
            <small>© 2025 Advanced Kolam Generator</small>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("❌ Application error occurred. Please refresh and try again.")

if __name__ == "__main__":
    main()

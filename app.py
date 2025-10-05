#!/usr/bin/env python3
"""
Kolam Pattern Generator Web Application
Production-ready Flask backend with dual algorithm support
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import logging
import os

from utils.kolam_algorithms import KolamDrawV1, KolamDrawV2
from utils.image_utils import create_kolam_image
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_kolam():
    """Generate kolam pattern based on user parameters"""
    try:
        data = request.json
        
        # Extract and validate parameters
        algorithm = data.get('algorithm', 'v1')
        grid_size = int(data.get('gridSize', 8))
        complexity = float(data.get('complexity', 0.5))
        theme = data.get('theme', 'light')
        color = data.get('color', None)
        
        # Validate inputs
        grid_size = max(4, min(20, grid_size))
        complexity = max(0.1, min(0.9, complexity))
        
        logger.info(f"Generating kolam: algorithm={algorithm}, size={grid_size}, complexity={complexity}")
        
        # Generate kolam based on selected algorithm
        if algorithm == 'v1':
            drawer = KolamDrawV1(grid_size)
            path = drawer.generate_path(complexity)
        else:
            drawer = KolamDrawV2(grid_size)
            path = drawer.generate_path(complexity)
        
        # Create image
        image_data = create_kolam_image(path, theme, color)
        
        return jsonify({
            'success': True,
            'image': image_data,
            'algorithm_used': algorithm,
            'grid_size': grid_size,
            'path_length': len(path),
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Error generating kolam: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

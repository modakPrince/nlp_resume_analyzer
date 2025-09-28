"""
Flask Web Application Package
Contains the web interface for the resume analyzer.
"""

from flask import Flask

def create_app(config_name='default'):
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    
    # Configure app based on environment
    if config_name == 'development':
        app.config['DEBUG'] = True
        app.config['SECRET_KEY'] = 'dev-secret-key'
    
    return app

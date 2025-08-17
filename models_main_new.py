"""
Database Models for HIS (Hospital Information System)
MariaDB/MySQL Database Connection and SQLAlchemy ORM Models
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON
import os
from config import config

# Initialize SQLAlchemy
db = SQLAlchemy()

# Path to store document files - defined as global variable for easy migration
DOCUMENTS_PATH = '/static/documents'

def create_app(config_name=None):
    """Create and configure Flask application with database connection.
    Uses 'frontend' directory for Jinja templates (renamed from default 'templates').
    """
    app = Flask(__name__, template_folder='frontend', static_folder='static')
    
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize database with app
    db.init_app(app)
    
    # Register static versioning filter for cache management
    try:
        from utils.static_versioning import register_static_version_filter
        register_static_version_filter(app)
    except ImportError:
        # Fallback if utils not available
        @app.template_filter('static_version')
        def static_version_filter(filename):
            return app.config.get('STATIC_VERSION', '1.1')
    
    return app

# ===========================================
# Database helper functions
# ===========================================

def init_database(app):
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def test_connection():
    """Test database connection"""
    try:
        # Simple query to test connection
        result = db.session.execute(db.text("SELECT 1"))
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

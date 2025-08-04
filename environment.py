"""
Environment Variables Configuration and Helper Functions
Demonstrates how to use environment variables in Flask application
"""

from flask import Flask, jsonify, current_app
import os

def create_example_routes(app):
    """Add example routes that demonstrate environment variable usage"""
    
    @app.route('/config')
    def show_config():
        """Show current configuration (sanitized for security)"""
        config_info = {
            'environment': os.getenv('FLASK_ENV', 'development'),
            'database_host': 'localhost',  # Don't expose full connection string
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'session_lifetime_hours': os.getenv('SESSION_LIFETIME_HOURS', '8'),
            'items_per_page': os.getenv('ITEMS_PER_PAGE', '20'),
            'gunicorn_workers': os.getenv('GUNICORN_WORKERS', 'not set'),
            'gunicorn_bind': os.getenv('GUNICORN_BIND', 'not set'),
            'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
            'database_configured': bool(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
        }
        return jsonify(config_info)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint using environment configuration"""
        try:
            from models import test_connection
            db_healthy = test_connection()
        except Exception as e:
            db_healthy = False
            
        health_status = {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'version': '1.0.0'
        }
        
        status_code = 200 if db_healthy else 503
        return jsonify(health_status), status_code

# Example of using environment variables in business logic
def get_pagination_settings():
    """Get pagination settings from environment variables"""
    return {
        'items_per_page': int(os.getenv('ITEMS_PER_PAGE', 20)),
        'max_per_page': int(os.getenv('MAX_ITEMS_PER_PAGE', 100))
    }

def get_database_pool_settings():
    """Get database pool settings from environment variables"""
    return {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600))
    }

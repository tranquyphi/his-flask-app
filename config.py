"""
Configuration module for HIS Flask Application
Handles environment variables and application settings
"""

import os
import logging
from datetime import timedelta
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_CONNECTION_STRING')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DB_CONNECTION_STRING environment variable is required")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20))
    }
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv('SESSION_LIFETIME_HOURS', 8))
    )
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/his/his.log')
    
    # Application Settings
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 25 * 1024 * 1024))  # 25MB
    
    # Static File Versioning (configurable via environment variable)
    STATIC_VERSION = os.getenv('STATIC_VERSION', '1.5')
    
    # Security Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Ensure log directory exists
        log_path = Path(Config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate critical configuration
        Config._validate_config()
    
    @staticmethod
    def _validate_config():
        """Validate critical configuration values"""
        required_vars = ['DB_CONNECTION_STRING', 'SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate database connection string format
        db_uri = os.getenv('DB_CONNECTION_STRING')
        if db_uri and not (db_uri.startswith('mysql+pymysql://') or db_uri.startswith('postgresql://')):
            logging.warning("Database connection string format may not be supported")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Override for development - allow fallback to local database
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_CONNECTION_STRING', 'mysql+pymysql://localhost/examdb_dev')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log to file in production
        if not app.debug:
            file_handler = logging.handlers.RotatingFileHandler(
                Config.LOG_FILE, 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('HIS application startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DB_CONNECTION_STRING', 'mysql+pymysql://localhost/examdb_test')
    SECRET_KEY = os.getenv('TEST_SECRET_KEY', 'test-secret-key')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

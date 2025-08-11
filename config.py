"""
Configuration module for HIS Flask Application
Handles environment variables and application settings
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DB_CONNECTION_STRING',
        'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20))
    }
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv('SESSION_LIFETIME_HOURS', 8))
    )
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/his/his.log')
    
    # Application Settings
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Static File Versioning (increment when JS/CSS changes)
    STATIC_VERSION = os.getenv('STATIC_VERSION', '1.3')
    
    # Security Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log to file in production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
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
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DB_CONNECTION_STRING',
        'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb_test'
    )

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

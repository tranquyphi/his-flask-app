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
    
    # Import all models to register them with SQLAlchemy
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from models.DocumentType import DocumentType
        from models.BodyPart import BodyPart
        from models.BodySite import BodySite
        from models.BodySystem import BodySystem
        from models.Department import Department
        from models.DrugGroup import DrugGroup
        from models.Drug import Drug
        from models.ICD import ICD
        from models.Patient import Patient
        from models.Proc import Proc
        from models.PatientDepartment import PatientDepartment
        from models.Sign import Sign
        from models.Staff import Staff
        from models.Template import Template
        from models.Test import Test
        from models.Visit import Visit
        # Visit-related association models
        from models.VisitDiagnosis import VisitDiagnosis
        from models.VisitDocuments import VisitDocuments
        from models.VisitImage import VisitImage
        from models.VisitDrug import VisitDrug
        from models.VisitProc import VisitProc
        from models.VisitSign import VisitSign
        from models.VisitStaff import VisitStaff
        from models.VisitTest import VisitTest
        # Template-related association models
        from models.TestTemplate import TestTemplate
        from models.DrugTemplate import DrugTemplate
        from models.DrugTemplateDetail import DrugTemplateDetail
        from models.SignTemplate import SignTemplate
        from models.SignTemplateDetail import SignTemplateDetail
        # Document and service models
        from models.PatientDocuments import PatientDocuments
        from models.PatientsWithDepartment import PatientsWithDepartment
    
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

def get_db():
    """
    FastAPI dependency function to get database session
    Yields a database session for use in FastAPI route handlers
    """
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    
    # Create engine using the same database URL as Flask
    db_url = os.getenv('DB_CONNECTION_STRING', 'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb')
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

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

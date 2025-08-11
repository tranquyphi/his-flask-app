"""
Static file versioning utilities for cache management
"""
import os
from datetime import datetime

def get_static_version(app, filename=None):
    """
    Get version string for static files.
    Uses STATIC_VERSION config first, then file modification time as fallback.
    
    Args:
        app: Flask application instance
        filename: Optional specific filename to get version for
        
    Returns:
        str: Version string for cache busting
    """
    # Use configured static version (preferred for production)
    static_version = app.config.get('STATIC_VERSION')
    if static_version:
        return static_version
    
    # Fallback: Use file modification time if filename provided
    if filename:
        try:
            static_folder = app.static_folder or 'static'
            file_path = os.path.join(static_folder, filename)
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                return str(int(mtime))
        except (OSError, ValueError):
            pass
    
    # Ultimate fallback: Use current timestamp (development only)
    if app.config.get('DEBUG', False):
        return str(int(datetime.now().timestamp()))
    
    return '1.0'

def register_static_version_filter(app):
    """Register Jinja2 filter for static file versioning"""
    
    @app.template_filter('static_version')
    def static_version_filter(filename):
        return get_static_version(app, filename)
    
    return static_version_filter

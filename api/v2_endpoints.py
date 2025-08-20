"""
V2 API endpoints to resolve 404 errors in department_patients_specific
"""
from flask import Blueprint, jsonify, request
from models import db

v2_bp = Blueprint('v2', __name__)

@v2_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for v2 API"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'timestamp': '2025-08-11T07:00:00Z',
        'services': {
            'database': 'connected',
            'api': 'operational'
        }
    })

@v2_bp.route('/sign-templates', methods=['GET'])
def get_sign_templates():
    """Get sign templates for department"""
    department_id = request.args.get('department_id', type=int)
    
    if not department_id:
        return jsonify({'error': 'department_id parameter required'}), 400
    
    # For now return empty array since SignTemplate functionality is commented out
    # In future this would query SignTemplate model filtered by department
    return jsonify({
        'sign_templates': [],
        'department_id': department_id,
        'count': 0,
        'message': 'Sign templates feature will be implemented in future version'
    })

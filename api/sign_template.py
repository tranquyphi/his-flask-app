"""
SignTemplate API Blueprint
CRUD operations for Sign Templates
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models import db, SignTemplate, Department

sign_template_bp = Blueprint('sign_template', __name__)


def sign_template_to_dict(template, department_name=None):
    """Convert SignTemplate to dictionary with department name"""
    return {
        'SignTemplateId': template.SignTemplateId,
        'SignTemplateName': template.SignTemplateName,
        'DepartmentId': template.DepartmentId,
        'DepartmentName': department_name,
        'SignTemplateType': template.SignTemplateType
    }


@sign_template_bp.route('/sign-templates', methods=['GET'])
def list_sign_templates():
    """List sign templates with optional filters and search."""
    try:
        # Get templates with department names
        query = db.session.query(SignTemplate, Department.DepartmentName).join(
            Department, SignTemplate.DepartmentId == Department.DepartmentId, isouter=True
        )

        q = request.args.get('q', type=str)
        department_id = request.args.get('department_id', type=int)
        template_type = request.args.get('template_type', type=str)

        if q:
            query = query.filter(SignTemplate.SignTemplateName.ilike(f"%{q}%"))
        if department_id:
            query = query.filter(SignTemplate.DepartmentId == department_id)
        if template_type and template_type in ('BA', 'TD', 'PK', 'CC'):
            query = query.filter(SignTemplate.SignTemplateType == template_type)

        records = query.order_by(asc(SignTemplate.SignTemplateName)).all()
        data = [sign_template_to_dict(template, dept_name) for template, dept_name in records]
        return jsonify({'sign_templates': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sign_template_bp.route('/sign-templates/<int:template_id>', methods=['GET'])
def get_sign_template(template_id):
    """Get a specific sign template by ID"""
    try:
        template = SignTemplate.query.get_or_404(template_id)
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        return jsonify({
            'sign_template': sign_template_to_dict(
                template, 
                department.DepartmentName if department else None
            )
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sign_template_bp.route('/sign-templates', methods=['POST'])
def create_sign_template():
    """Create a new sign template"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['SignTemplateName', 'DepartmentId', 'SignTemplateType']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        if payload['SignTemplateType'] not in ('BA', 'TD', 'PK', 'CC'):
            return jsonify({'error': 'SignTemplateType must be one of: BA, TD, PK, CC'}), 400

        department = Department.query.get(payload['DepartmentId'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        template = SignTemplate(
            SignTemplateName=payload['SignTemplateName'].strip(),
            DepartmentId=int(payload['DepartmentId']),
            SignTemplateType=payload['SignTemplateType']
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'sign_template': sign_template_to_dict(template, department.DepartmentName)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sign_template_bp.route('/sign-templates/<int:template_id>', methods=['PUT'])
def update_sign_template(template_id):
    """Update an existing sign template"""
    try:
        template = SignTemplate.query.get_or_404(template_id)
        payload = request.get_json(force=True) or {}

        if 'SignTemplateName' in payload:
            template.SignTemplateName = payload['SignTemplateName'].strip()
        
        if 'DepartmentId' in payload:
            department = Department.query.get(payload['DepartmentId'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404
            template.DepartmentId = int(payload['DepartmentId'])
        
        if 'SignTemplateType' in payload:
            if payload['SignTemplateType'] not in ('BA', 'TD', 'PK', 'CC'):
                return jsonify({'error': 'SignTemplateType must be one of: BA, TD, PK, CC'}), 400
            template.SignTemplateType = payload['SignTemplateType']

        db.session.commit()
        
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        return jsonify({
            'sign_template': sign_template_to_dict(
                template, 
                department.DepartmentName if department else None
            )
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sign_template_bp.route('/sign-templates/<int:template_id>', methods=['DELETE'])
def delete_sign_template(template_id):
    """Delete a sign template"""
    try:
        template = SignTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted', 'SignTemplateId': template_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

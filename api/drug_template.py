"""
DrugTemplate API Blueprint
CRUD operations for Drug Templates
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models import db, DrugTemplate, Department

drug_template_bp = Blueprint('drug_template', __name__)


def drug_template_to_dict(template, department_name=None):
    """Convert DrugTemplate to dictionary with department name"""
    return {
        'DrugTemplateId': template.DrugTemplateId,
        'DrugTemplateName': template.DrugTemplateName,
        'DepartmentId': template.DepartmentId,
        'DepartmentName': department_name,
        'DrugTemplateType': template.DrugTemplateType
    }


@drug_template_bp.route('/drug-templates', methods=['GET'])
def list_drug_templates():
    """List drug templates with optional filters and search."""
    try:
        # Get templates with department names
        query = db.session.query(DrugTemplate, Department.DepartmentName).join(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId, isouter=True
        )

        q = request.args.get('q', type=str)
        department_id = request.args.get('department_id', type=int)
        template_type = request.args.get('template_type', type=str)

        if q:
            query = query.filter(DrugTemplate.DrugTemplateName.ilike(f"%{q}%"))
        if department_id:
            query = query.filter(DrugTemplate.DepartmentId == department_id)
        if template_type and template_type in ('BA', 'TD', 'PK', 'CC'):
            query = query.filter(DrugTemplate.DrugTemplateType == template_type)

        records = query.order_by(asc(DrugTemplate.DrugTemplateName)).all()
        data = [drug_template_to_dict(template, dept_name) for template, dept_name in records]
        return jsonify({'drug_templates': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_bp.route('/drug-templates/<int:template_id>', methods=['GET'])
def get_drug_template(template_id):
    """Get a specific drug template by ID"""
    try:
        template = DrugTemplate.query.get_or_404(template_id)
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        return jsonify({
            'drug_template': drug_template_to_dict(
                template, 
                department.DepartmentName if department else None
            )
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drug_template_bp.route('/drug-templates', methods=['POST'])
def create_drug_template():
    """Create a new drug template"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['DrugTemplateName', 'DepartmentId', 'DrugTemplateType']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        if payload['DrugTemplateType'] not in ('BA', 'TD', 'PK', 'CC'):
            return jsonify({'error': 'DrugTemplateType must be one of: BA, TD, PK, CC'}), 400

        department = Department.query.get(payload['DepartmentId'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        template = DrugTemplate(
            DrugTemplateName=payload['DrugTemplateName'].strip(),
            DepartmentId=int(payload['DepartmentId']),
            DrugTemplateType=payload['DrugTemplateType']
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'drug_template': drug_template_to_dict(template, department.DepartmentName)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_bp.route('/drug-templates/<int:template_id>', methods=['PUT'])
def update_drug_template(template_id):
    """Update an existing drug template"""
    try:
        template = DrugTemplate.query.get_or_404(template_id)
        payload = request.get_json(force=True) or {}

        if 'DrugTemplateName' in payload:
            template.DrugTemplateName = payload['DrugTemplateName'].strip()
        
        if 'DepartmentId' in payload:
            department = Department.query.get(payload['DepartmentId'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404
            template.DepartmentId = int(payload['DepartmentId'])
        
        if 'DrugTemplateType' in payload:
            if payload['DrugTemplateType'] not in ('BA', 'TD', 'PK', 'CC'):
                return jsonify({'error': 'DrugTemplateType must be one of: BA, TD, PK, CC'}), 400
            template.DrugTemplateType = payload['DrugTemplateType']

        db.session.commit()
        
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        return jsonify({
            'drug_template': drug_template_to_dict(
                template, 
                department.DepartmentName if department else None
            )
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_bp.route('/drug-templates/<int:template_id>', methods=['DELETE'])
def delete_drug_template(template_id):
    """Delete a drug template"""
    try:
        template = DrugTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted', 'DrugTemplateId': template_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

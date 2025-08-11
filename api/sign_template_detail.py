"""
SignTemplateDetail API Blueprint
Operations for managing signs within specific templates
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models import db, SignTemplate, SignTemplateDetail, Sign, BodySystem

sign_template_detail_bp = Blueprint('sign_template_detail', __name__)


def template_sign_to_dict(sign, system_name=None):
    """Convert Sign with system info to dictionary"""
    return {
        'SignId': sign.SignId,
        'SignDesc': sign.SignDesc,
        'SignType': 1 if sign.SignType else 0,
        'SystemId': sign.SystemId,
        'SystemName': system_name,
        'Speciality': sign.Speciality
    }


@sign_template_detail_bp.route('/sign-templates/<int:template_id>/signs', methods=['GET'])
def list_template_signs(template_id):
    """Get all signs for a specific template"""
    try:
        # Get the template to verify it exists
        template = SignTemplate.query.get_or_404(template_id)
        
        # Get signs for this template with body system info
        signs = db.session.query(
            Sign, BodySystem.SystemName
        ).select_from(
            SignTemplateDetail
        ).join(
            Sign, SignTemplateDetail.SignId == Sign.SignId
        ).outerjoin(
            BodySystem, Sign.SystemId == BodySystem.SystemId
        ).filter(
            SignTemplateDetail.SignTemplateId == template_id
        ).all()
        
        result = []
        for sign, system_name in signs:
            sign_dict = {
                'SignId': sign.SignId,
                'SignDesc': sign.SignDesc,
                'SignType': sign.SignType,
                'SystemId': sign.SystemId,
                'SystemName': system_name or 'N/A',
                'Speciality': sign.Speciality
            }
            result.append(sign_dict)
            
        return jsonify({'signs': result})
    except Exception as e:
        print(f"Error listing template signs: {e}")
        return jsonify({'error': str(e)}), 500


@sign_template_detail_bp.route('/sign-templates/<int:template_id>/signs', methods=['POST'])
def add_sign_to_template(template_id):
    """Add a sign to a template"""
    try:
        data = request.get_json()
        sign_id = data.get('SignId')
        
        if not sign_id:
            return jsonify({'error': 'SignId is required'}), 400
            
        # Check if template exists
        template = SignTemplate.query.get_or_404(template_id)
        
        # Check if sign exists
        sign = Sign.query.get_or_404(sign_id)
        
        # Check if already exists
        existing = SignTemplateDetail.query.filter_by(
            SignTemplateId=template_id,
            SignId=sign_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Sign already exists in this template'}), 409
            
        # Create new association
        detail = SignTemplateDetail(
            SignTemplateId=template_id,
            SignId=sign_id
        )
        
        db.session.add(detail)
        db.session.commit()
        
        return jsonify({'message': 'Sign added to template successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sign to template: {e}")
        return jsonify({'error': str(e)}), 500


@sign_template_detail_bp.route('/sign-templates/<int:template_id>/signs/<int:sign_id>', methods=['DELETE'])
def remove_sign_from_template(template_id, sign_id):
    """Remove a sign from a template"""
    try:
        # Find the association
        detail = SignTemplateDetail.query.filter_by(
            SignTemplateId=template_id,
            SignId=sign_id
        ).first_or_404()
        
        db.session.delete(detail)
        db.session.commit()
        
        return jsonify({
            'message': 'Sign removed from template',
            'SignTemplateId': template_id,
            'SignId': sign_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sign_template_detail_bp.route('/sign-templates/<int:template_id>/available-signs', methods=['GET'])
def get_available_signs_for_template(template_id):
    """Get signs that can be added to the template (not already in it)"""
    try:
        # Verify template exists
        SignTemplate.query.get_or_404(template_id)
        
        # Get all signs that are NOT in this template
        subquery = db.session.query(SignTemplateDetail.SignId).filter_by(
            SignTemplateId=template_id
        ).subquery()
        
        query = db.session.query(Sign, BodySystem.SystemName).join(
            BodySystem, Sign.SystemId == BodySystem.SystemId
        ).filter(
            ~Sign.SignId.in_(subquery)
        )

        # Optional filtering
        q = request.args.get('q', type=str)
        system_id = request.args.get('system_id', type=int)
        sign_type = request.args.get('type', type=str)

        if q:
            query = query.filter(Sign.SignDesc.ilike(f"%{q}%"))
        if system_id:
            query = query.filter(Sign.SystemId == system_id)
        if sign_type in ('0', '1'):
            query = query.filter(Sign.SignType == (sign_type == '1'))

        records = query.order_by(asc(Sign.SignDesc)).all()
        available_signs = [template_sign_to_dict(sign, sys_name) for sign, sys_name in records]
        
        return jsonify({
            'template_id': template_id,
            'available_signs': available_signs,
            'total_available': len(available_signs)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

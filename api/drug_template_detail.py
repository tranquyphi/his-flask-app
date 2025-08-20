"""
DrugTemplateDetail API Blueprint
Managing associations between drug templates and drugs
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models import db
from models import DrugTemplate, DrugTemplateDetail, Drug, DrugGroup, Department

drug_template_detail_bp = Blueprint('drug_template_detail', __name__)


def template_detail_to_dict(detail, drug=None, template_name=None, department_name=None, group_name=None):
    """Convert DrugTemplateDetail to dictionary with full drug information"""
    result = {
        'DrugTemplateId': detail.DrugTemplateId,
        'DrugId': detail.DrugId,
        'DrugTemplateName': template_name,
        'DepartmentName': department_name
    }
    
    # Add full drug information if available
    if drug:
        result.update({
            'DrugName': drug.DrugName,
            'DrugChemical': drug.DrugChemical,
            'DrugGenericName': drug.DrugChemical,  # Alias for frontend consistency
            'DrugContent': drug.DrugContent,
            'DrugFormulation': drug.DrugFormulation,
            'DrugGroupId': drug.DrugGroupId,
            'DrugGroup': group_name,  # Keep for backward compatibility
            'DrugGroupName': group_name,  # Add for frontend consistency
            'DrugTherapy': drug.DrugTherapy,
            'DrugRoute': drug.DrugRoute,
            'DrugAvailable': drug.DrugAvailable,
            'DrugPriceBHYT': drug.DrugPriceBHYT,
            'DrugPriceVP': drug.DrugPriceVP,
            'DrugNote': drug.DrugNote
        })
    else:
        # Set defaults if drug not found
        result.update({
            'DrugName': None,
            'DrugChemical': None,
            'DrugGenericName': None,
            'DrugContent': None,
            'DrugFormulation': None,
            'DrugGroupId': None,
            'DrugGroup': None,
            'DrugGroupName': None,
            'DrugTherapy': None,
            'DrugRoute': None,
            'DrugAvailable': False,
            'DrugPriceBHYT': 0,
            'DrugPriceVP': 0,
            'DrugNote': ''
        })
    
    return result


# NEW: REST API endpoints for drug templates
@drug_template_detail_bp.route('/drug-templates/<int:template_id>/drugs', methods=['GET'])
def get_template_drugs(template_id):
    """Get all drugs in a specific template with filtering"""
    try:
        # Base query with joins for full drug information
        query = db.session.query(
            DrugTemplateDetail,
            Drug,
            DrugGroup.DrugGroupName,
            DrugTemplate.DrugTemplateName,
            Department.DepartmentName
        ).join(
            Drug, DrugTemplateDetail.DrugId == Drug.DrugId
        ).join(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId, isouter=True
        ).join(
            DrugTemplate, DrugTemplateDetail.DrugTemplateId == DrugTemplate.DrugTemplateId
        ).join(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId, isouter=True
        ).filter(
            DrugTemplateDetail.DrugTemplateId == template_id
        )
        
        # Apply filters
        drug_name = request.args.get('drug_name', type=str)
        drug_group_id = request.args.get('drug_group_id', type=str)
        available = request.args.get('available', type=str)
        formulation = request.args.get('formulation', type=str)
        
        if drug_name:
            query = query.filter(
                (Drug.DrugName.ilike(f"%{drug_name}%")) |
                (Drug.DrugChemical.ilike(f"%{drug_name}%"))
            )
        if drug_group_id:
            query = query.filter(Drug.DrugGroupId == drug_group_id)
        if available in ('true', 'false'):
            is_available = available == 'true'
            query = query.filter(Drug.DrugAvailable == is_available)
        if formulation:
            query = query.filter(Drug.DrugFormulation.ilike(f"%{formulation}%"))
            
        records = query.order_by(asc(Drug.DrugName)).all()
        data = [
            template_detail_to_dict(detail, drug, template_name, dept_name, group_name)
            for detail, drug, group_name, template_name, dept_name in records
        ]
        return jsonify({'drugs': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-templates/<int:template_id>/drugs', methods=['POST'])
def add_drug_to_template(template_id):
    """Add a drug to a template"""
    try:
        payload = request.get_json(force=True) or {}
        drug_id = payload.get('DrugId')
        
        if not drug_id:
            return jsonify({'error': 'DrugId is required'}), 400
            
        # Check if template exists
        template = DrugTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
            
        # Check if drug exists
        drug = Drug.query.get(drug_id)
        if not drug:
            return jsonify({'error': 'Drug not found'}), 404
            
        # Check if association already exists
        existing = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id,
            DrugId=drug_id
        ).first()
        if existing:
            return jsonify({'error': 'Drug already in template'}), 409
            
        # Create new association
        detail = DrugTemplateDetail(
            DrugTemplateId=template_id,
            DrugId=drug_id
        )
        db.session.add(detail)
        db.session.commit()
        
        return jsonify({'message': 'Drug added to template successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-templates/<int:template_id>/drugs/<string:drug_id>', methods=['DELETE'])
def remove_drug_from_template(template_id, drug_id):
    """Remove a drug from a template"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id,
            DrugId=drug_id
        ).first()
        
        if not detail:
            return jsonify({'error': 'Association not found'}), 404
            
        db.session.delete(detail)
        db.session.commit()
        
        return jsonify({'message': 'Drug removed from template successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details', methods=['GET'])
def list_drug_template_details():
    """List drug template details with optional filters and search."""
    try:
        # Query with all related data
        query = db.session.query(
            DrugTemplateDetail, 
            Drug,
            DrugGroup.DrugGroupName,
            DrugTemplate.DrugTemplateName,
            Department.DepartmentName
        ).join(
            Drug, DrugTemplateDetail.DrugId == Drug.DrugId, isouter=True
        ).join(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId, isouter=True
        ).join(
            DrugTemplate, DrugTemplateDetail.DrugTemplateId == DrugTemplate.DrugTemplateId, isouter=True
        ).join(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId, isouter=True
        )

        template_id = request.args.get('template_id', type=int)
        drug_id = request.args.get('drug_id', type=int)
        q = request.args.get('q', type=str)

        if template_id:
            query = query.filter(DrugTemplateDetail.DrugTemplateId == template_id)
        if drug_id:
            query = query.filter(DrugTemplateDetail.DrugId == drug_id)
        if q:
            query = query.filter(Drug.DrugName.ilike(f"%{q}%"))

        records = query.order_by(asc(Drug.DrugName)).all()
        data = [
            template_detail_to_dict(detail, drug, template_name, dept_name, group_name) 
            for detail, drug, group_name, template_name, dept_name in records
        ]
        return jsonify({'drug_template_details': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details/<int:template_id>/<drug_id>', methods=['GET'])
def get_drug_template_detail(template_id, drug_id):
    """Get a specific drug template detail by composite key"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id, DrugId=drug_id
        ).first_or_404()
        
        drug = Drug.query.get(detail.DrugId) if detail.DrugId else None
        template = DrugTemplate.query.get(detail.DrugTemplateId) if detail.DrugTemplateId else None
        
        template_name = template.DrugTemplateName if template else None
        department_name = None
        if template and template.DepartmentId:
            department = Department.query.get(template.DepartmentId)
            department_name = department.DepartmentName if department else None
        
        group_name = None
        if drug and drug.DrugGroupId:
            drug_group = DrugGroup.query.get(drug.DrugGroupId)
            group_name = drug_group.DrugGroupName if drug_group else None
        
        data = template_detail_to_dict(detail, drug, template_name, department_name, group_name)
        return jsonify({'drug_template_detail': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details', methods=['POST'])
def create_drug_template_detail():
    """Create a new drug template detail association"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['DrugTemplateId', 'DrugId']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        template = DrugTemplate.query.get(payload['DrugTemplateId'])
        if not template:
            return jsonify({'error': 'DrugTemplate not found'}), 404

        drug = Drug.query.get(payload['DrugId'])
        if not drug:
            return jsonify({'error': 'Drug not found'}), 404

        # Check if association already exists
        existing = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=payload['DrugTemplateId'],
            DrugId=payload['DrugId']
        ).first()
        if existing:
            return jsonify({'error': 'Association already exists'}), 409

        detail = DrugTemplateDetail(**{k: v for k, v in payload.items() if k in ['DrugTemplateId', 'DrugId']})
        db.session.add(detail)
        db.session.commit()

        # Get full data for response
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        drug_group = DrugGroup.query.get(drug.DrugGroupId) if drug.DrugGroupId else None
        
        data = template_detail_to_dict(
            detail, drug, template.DrugTemplateName, 
            department.DepartmentName if department else None,
            drug_group.DrugGroupName if drug_group else None
        )
        return jsonify({'drug_template_detail': data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details/<int:template_id>/<drug_id>', methods=['PUT'])
def update_drug_template_detail(template_id, drug_id):
    """Update a drug template detail association"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id, DrugId=drug_id
        ).first_or_404()
        
        payload = request.get_json(force=True) or {}
        # Currently, there's no additional data to update for associations
        # This endpoint exists for API completeness
        
        return jsonify({'message': 'Drug template detail updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details/<int:template_id>/<drug_id>', methods=['DELETE'])
def delete_drug_template_detail(template_id, drug_id):
    """Delete a drug template detail association"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id, DrugId=drug_id
        ).first_or_404()
        
        db.session.delete(detail)
        db.session.commit()
        
        return jsonify({'message': 'Drug template detail deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

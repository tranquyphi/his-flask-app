"""
DrugTemplateDetail API Blueprint
Managing associations between drug templates and drugs
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models import db, DrugTemplate, DrugTemplateDetail, Drug, DrugGroup, Department

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
            'DrugContent': drug.DrugContent,
            'DrugFormulation': drug.DrugFormulation,
            'DrugGroupId': drug.DrugGroupId,
            'DrugGroup': group_name,  # Include the group name from the join
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
            'DrugContent': None,
            'DrugFormulation': None,
            'DrugGroupId': None,
            'DrugGroup': None,
            'DrugTherapy': None,
            'DrugRoute': None,
            'DrugAvailable': False,
            'DrugPriceBHYT': 0,
            'DrugPriceVP': 0,
            'DrugNote': ''
        })
    
    return result


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
            DrugTemplateId=template_id, 
            DrugId=drug_id
        ).first_or_404()
        
        drug = Drug.query.get(detail.DrugId) if detail.DrugId else None
        template = DrugTemplate.query.get(detail.DrugTemplateId) if detail.DrugTemplateId else None
        department = None
        group_name = None
        
        if template and template.DepartmentId:
            department = Department.query.get(template.DepartmentId)
        
        if drug and drug.DrugGroupId:
            drug_group = DrugGroup.query.get(drug.DrugGroupId)
            if drug_group:
                group_name = drug_group.DrugGroupName
        
        return jsonify({
            'drug_template_detail': template_detail_to_dict(
                detail, 
                drug,
                template.DrugTemplateName if template else None,
                department.DepartmentName if department else None,
                group_name
            )
        })
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

        # Verify template exists
        template = DrugTemplate.query.get(payload['DrugTemplateId'])
        if not template:
            return jsonify({'error': 'Drug template not found'}), 404

        # Verify drug exists
        drug = Drug.query.get(payload['DrugId'])
        if not drug:
            return jsonify({'error': 'Drug not found'}), 404

        # Check for duplicate association
        existing = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=payload['DrugTemplateId'],
            DrugId=payload['DrugId']
        ).first()
        if existing:
            return jsonify({'error': 'Association already exists'}), 409

        detail = DrugTemplateDetail(
            DrugTemplateId=int(payload['DrugTemplateId']),
            DrugId=int(payload['DrugId'])
        )
        
        db.session.add(detail)
        db.session.commit()
        
        department = Department.query.get(template.DepartmentId) if template.DepartmentId else None
        return jsonify({
            'drug_template_detail': template_detail_to_dict(
                detail, 
                drug.DrugName,
                template.DrugTemplateName,
                department.DepartmentName if department else None
            )
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details/<int:template_id>/<drug_id>', methods=['PUT'])
def update_drug_template_detail(template_id, drug_id):
    """Update an existing drug template detail association"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id, 
            DrugId=drug_id
        ).first_or_404()
        
        payload = request.get_json(force=True) or {}

        # For composite key tables, updating the key fields means creating a new record
        # and deleting the old one, which is complex. For now, we'll not allow key updates.
        # Only allow updating related data if needed in the future.
        
        return jsonify({'error': 'Updates not supported for composite key associations'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-template-details/<int:template_id>/<drug_id>', methods=['DELETE'])
def delete_drug_template_detail(template_id, drug_id):
    """Delete a drug template detail association"""
    try:
        detail = DrugTemplateDetail.query.filter_by(
            DrugTemplateId=template_id, 
            DrugId=drug_id
        ).first_or_404()
        
        db.session.delete(detail)
        db.session.commit()
        return jsonify({
            'message': 'Association deleted', 
            'DrugTemplateId': template_id,
            'DrugId': drug_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_template_detail_bp.route('/drug-templates/<int:template_id>/drugs', methods=['GET'])
def get_template_drugs(template_id):
    """Get all drugs associated with a specific template"""
    try:
        template = DrugTemplate.query.get_or_404(template_id)
        
        query = db.session.query(
            DrugTemplateDetail,
            Drug.DrugName,
            Drug.DrugChemical,
            DrugGroup.DrugGroupName,
            Drug.DrugAvailable,
            Drug.DrugFormulation
        ).join(
            Drug, DrugTemplateDetail.DrugId == Drug.DrugId
        ).join(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId, isouter=True
        ).filter(
            DrugTemplateDetail.DrugTemplateId == template_id
        ).order_by(asc(Drug.DrugName))

        records = query.all()
        drugs = []
        for detail, drug_name, chemical_name, group_name, availability, formulation in records:
            drugs.append({
                'DrugTemplateId': detail.DrugTemplateId,
                'DrugId': detail.DrugId,
                'DrugName': drug_name,
                'DrugChemical': chemical_name,
                'DrugGroup': group_name,
                'DrugAvailable': availability,
                'DrugFormulation': formulation
            })
        
        return jsonify({
            'template': {
                'DrugTemplateId': template.DrugTemplateId,
                'DrugTemplateName': template.DrugTemplateName,
                'DrugTemplateType': template.DrugTemplateType
            },
            'drugs': drugs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

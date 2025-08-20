"""
DrugGroup API Blueprint
CRUD operations for DrugGroup management
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import asc, func
from models_main import db
from models import DrugGroup, Drug

drug_groups_bp = Blueprint('drug_groups', __name__)


def drug_group_to_dict(group, drug_count=0):
    """Convert DrugGroup to dictionary with drug count"""
    return {
        'DrugGroupId': group.DrugGroupId,
        'DrugGroupName': group.DrugGroupName,
        'DrugGroupDescription': group.DrugGroupDescription,
        'drug_count': drug_count
    }


@drug_groups_bp.route('/drug-groups', methods=['GET'])
def list_drug_groups():
    """List all drug groups with optional search and drug counts"""
    try:
        # Query drug groups with drug counts
        query = db.session.query(
            DrugGroup,
            func.count(Drug.DrugId).label('drug_count')
        ).outerjoin(
            Drug, DrugGroup.DrugGroupId == Drug.DrugGroupId
        ).group_by(DrugGroup.DrugGroupId)
        
        # Search by name if provided
        search = request.args.get('q', type=str)
        if search:
            query = query.filter(DrugGroup.DrugGroupName.ilike(f"%{search}%"))
        
        results = query.order_by(asc(DrugGroup.DrugGroupName)).all()
        data = [drug_group_to_dict(group, drug_count) for group, drug_count in results]
        return jsonify({'drug_groups': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_groups_bp.route('/drug-groups/<int:group_id>', methods=['GET'])
def get_drug_group(group_id):
    """Get a specific drug group by ID"""
    try:
        group = DrugGroup.query.get_or_404(group_id)
        return jsonify({'drug_group': drug_group_to_dict(group)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drug_groups_bp.route('/drug-groups', methods=['POST'])
def create_drug_group():
    """Create a new drug group"""
    try:
        payload = request.get_json(force=True) or {}
        
        # Validate required fields
        required = ['DrugGroupName']
        missing = [f for f in required if f not in payload or not payload[f]]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Check if name already exists
        existing = DrugGroup.query.filter_by(DrugGroupName=payload['DrugGroupName']).first()
        if existing:
            return jsonify({'error': 'Tên nhóm thuốc đã tồn tại'}), 400
        
        # Create new drug group
        new_group = DrugGroup(
            DrugGroupName=payload['DrugGroupName'].strip(),
            DrugGroupDescription=payload.get('DrugGroupDescription', '').strip() or None
        )
        
        db.session.add(new_group)
        db.session.commit()
        
        return jsonify({
            'message': 'Drug group created successfully',
            'drug_group': drug_group_to_dict(new_group)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_groups_bp.route('/drug-groups/<int:group_id>', methods=['PUT'])
def update_drug_group(group_id):
    """Update an existing drug group"""
    try:
        group = DrugGroup.query.get_or_404(group_id)
        payload = request.get_json(force=True) or {}
        
        # Validate required fields
        if 'DrugGroupName' in payload and not payload['DrugGroupName']:
            return jsonify({'error': 'DrugGroupName is required'}), 400
        
        # Check if new name conflicts with existing (excluding current record)
        if 'DrugGroupName' in payload:
            existing = DrugGroup.query.filter(
                DrugGroup.DrugGroupName == payload['DrugGroupName'],
                DrugGroup.DrugGroupId != group_id
            ).first()
            if existing:
                return jsonify({'error': 'Tên nhóm thuốc đã tồn tại'}), 400
        
        # Update fields
        if 'DrugGroupName' in payload:
            group.DrugGroupName = payload['DrugGroupName'].strip()
        if 'DrugGroupDescription' in payload:
            group.DrugGroupDescription = payload['DrugGroupDescription'].strip() or None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Drug group updated successfully',
            'drug_group': drug_group_to_dict(group)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drug_groups_bp.route('/drug-groups/<int:group_id>', methods=['DELETE'])
def delete_drug_group(group_id):
    """Delete a drug group"""
    try:
        group = DrugGroup.query.get_or_404(group_id)
        
        # Check if any drugs are using this group
        if group.drugs:
            return jsonify({'error': f'Không thể xóa nhóm thuốc này vì đang có {len(group.drugs)} thuốc sử dụng'}), 400
        
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({'message': 'Drug group deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

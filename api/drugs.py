"""
Drug API Blueprint
CRUD operations for Drug management
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc, text
from models import db, Drug, DrugGroup

drugs_bp = Blueprint('drugs', __name__)


def drug_to_dict(drug, group_name=None):
    """Convert Drug to dictionary with optional group name"""
    return {
        'DrugId': drug.DrugId,
        'DrugName': drug.DrugName,
        'DrugChemical': drug.DrugChemical,
        'DrugContent': drug.DrugContent,
        'DrugFormulation': drug.DrugFormulation,
        'DrugRemains': drug.DrugRemains,
        'DrugGroupId': drug.DrugGroupId,
        'DrugGroup': group_name,  # Include the group name
        'DrugTherapy': drug.DrugTherapy,
        'DrugRoute': drug.DrugRoute,
        'DrugQuantity': drug.DrugQuantity,
        'CountStr': drug.CountStr,
        'DrugAvailable': drug.DrugAvailable,
        'DrugPriceBHYT': drug.DrugPriceBHYT,
        'DrugPriceVP': drug.DrugPriceVP,
        'DrugNote': drug.DrugNote,
        'Count': drug.Count
    }


@drugs_bp.route('/drugs', methods=['GET'])
def list_drugs():
    """List drugs with optional filters and search.
    Query params:
      q: substring in DrugName or DrugChemical (case-insensitive)
      group: substring in DrugGroupId
      available: 0/1 for DrugAvailable
      formulation: substring in DrugFormulation
    """
    try:
        # Query with left join to include group names
        query = db.session.query(Drug, DrugGroup.DrugGroupName).outerjoin(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId
        )

        q = request.args.get('q', type=str)
        drug_group = request.args.get('group', type=str)
        available = request.args.get('available', type=str)
        formulation = request.args.get('formulation', type=str)

        if q:
            query = query.filter(
                (Drug.DrugName.ilike(f"%{q}%")) | 
                (Drug.DrugChemical.ilike(f"%{q}%"))
            )
        if drug_group:
            query = query.filter(Drug.DrugGroupId == drug_group)
        if available in ('0', '1'):
            query = query.filter(Drug.DrugAvailable == (available == '1'))
        if formulation:
            query = query.filter(Drug.DrugFormulation.ilike(f"%{formulation}%"))

        records = query.order_by(asc(Drug.DrugName)).all()
        data = [drug_to_dict(drug, group_name) for drug, group_name in records]
        return jsonify({'drugs': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drugs_bp.route('/drugs/<string:drug_id>', methods=['GET'])
def get_drug(drug_id):
    """Get a specific drug by ID"""
    try:
        # Query with join to get group name
        result = db.session.query(Drug, DrugGroup.DrugGroupName).outerjoin(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId
        ).filter(Drug.DrugId == drug_id).first_or_404()
        
        drug, group_name = result
        return jsonify({'drug': drug_to_dict(drug, group_name)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drugs_bp.route('/drugs', methods=['POST'])
def create_drug():
    """Create a new drug"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['DrugName']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        # Auto-generate DrugId if not provided
        if 'DrugId' not in payload or not payload['DrugId']:
            # Get the maximum DrugId by trying to convert to int
            max_id = 6043  # Start from known max
            try:
                result = db.session.execute(text("SELECT MAX(CAST(DrugId AS UNSIGNED)) as max_id FROM Drug WHERE DrugId REGEXP '^[0-9]+$'")).fetchone()
                if result and result[0]:
                    max_id = result[0]
            except:
                pass
            payload['DrugId'] = str(max_id + 1)

        # Check if DrugId already exists
        existing = Drug.query.get(payload['DrugId'])
        if existing:
            return jsonify({'error': 'DrugId already exists'}), 409

        drug = Drug(
            DrugId=payload['DrugId'].strip(),
            DrugName=payload['DrugName'].strip(),
            DrugChemical=payload.get('DrugChemical', '').strip() or None,
            DrugContent=payload.get('DrugContent', '').strip() or None,
            DrugFormulation=payload.get('DrugFormulation', '').strip() or None,
            DrugRemains=payload.get('DrugRemains', 0) or 0,
            DrugGroupId=payload.get('DrugGroupId', None),
            DrugTherapy=payload.get('DrugTherapy', '').strip() or None,
            DrugRoute=payload.get('DrugRoute', '').strip() or None,
            DrugQuantity=payload.get('DrugQuantity', '').strip() or None,
            CountStr=payload.get('CountStr', '').strip() or None,
            DrugAvailable=bool(payload.get('DrugAvailable', True)),
            DrugPriceBHYT=int(payload.get('DrugPriceBHYT', 0) or 0),
            DrugPriceVP=int(payload.get('DrugPriceVP', 0) or 0),
            DrugNote=payload.get('DrugNote', '').strip() or '',
            Count=payload.get('Count', '').strip() or None
        )
        
        db.session.add(drug)
        db.session.commit()
        
        return jsonify({'drug': drug_to_dict(drug)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        return jsonify({'error': str(e)}), 500


@drugs_bp.route('/drugs/<string:drug_id>', methods=['PUT'])
def update_drug(drug_id):
    """Update an existing drug"""
    try:
        drug = Drug.query.get_or_404(drug_id)
        payload = request.get_json(force=True) or {}

        # Update fields if provided
        if 'DrugName' in payload:
            drug.DrugName = payload['DrugName'].strip()
        if 'DrugChemical' in payload:
            drug.DrugChemical = payload['DrugChemical'].strip() or None
        if 'DrugContent' in payload:
            drug.DrugContent = payload['DrugContent'].strip() or None
        if 'DrugFormulation' in payload:
            drug.DrugFormulation = payload['DrugFormulation'].strip() or None
        if 'DrugRemains' in payload:
            drug.DrugRemains = int(payload['DrugRemains'] or 0)
        if 'DrugGroupId' in payload:
            drug.DrugGroupId = payload['DrugGroupId']
        if 'DrugTherapy' in payload:
            drug.DrugTherapy = payload['DrugTherapy'].strip() or None
        if 'DrugRoute' in payload:
            drug.DrugRoute = payload['DrugRoute'].strip() or None
        if 'DrugQuantity' in payload:
            drug.DrugQuantity = payload['DrugQuantity'].strip() or None
        if 'CountStr' in payload:
            drug.CountStr = payload['CountStr'].strip() or None
        if 'DrugAvailable' in payload:
            drug.DrugAvailable = bool(payload['DrugAvailable'])
        if 'DrugPriceBHYT' in payload:
            drug.DrugPriceBHYT = int(payload['DrugPriceBHYT'] or 0)
        if 'DrugPriceVP' in payload:
            drug.DrugPriceVP = int(payload['DrugPriceVP'] or 0)
        if 'DrugNote' in payload:
            drug.DrugNote = payload['DrugNote'].strip() or ''
        if 'Count' in payload:
            drug.Count = payload['Count'].strip() or None

        db.session.commit()
        return jsonify({'drug': drug_to_dict(drug)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drugs_bp.route('/drugs/<string:drug_id>', methods=['DELETE'])
def delete_drug(drug_id):
    """Delete a drug"""
    try:
        drug = Drug.query.get_or_404(drug_id)
        db.session.delete(drug)
        db.session.commit()
        return jsonify({'message': 'Drug deleted', 'DrugId': drug_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

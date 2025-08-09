from flask import Blueprint, jsonify, request
from models import db, BodyPart

body_parts_bp = Blueprint('body_parts', __name__)

@body_parts_bp.route('/api/body_parts', methods=['GET'])
def get_all_body_parts():
    parts = BodyPart.query.all()
    return jsonify([
        {"BodyPartId": p.BodyPartId, "BodyPartName": p.BodyPartName}
        for p in parts
    ])

@body_parts_bp.route('/api/body_parts/<int:part_id>', methods=['GET'])
def get_body_part(part_id):
    part = BodyPart.query.get_or_404(part_id)
    return jsonify({"BodyPartId": part.BodyPartId, "BodyPartName": part.BodyPartName})

@body_parts_bp.route('/api/body_parts', methods=['POST'])
def create_body_part():
    data = request.json
    part = BodyPart(
        BodyPartId=data.get('BodyPartId'),
        BodyPartName=data.get('BodyPartName')
    )
    db.session.add(part)
    db.session.commit()
    return jsonify({"message": "Created", "BodyPartId": part.BodyPartId}), 201

@body_parts_bp.route('/api/body_parts/<int:part_id>', methods=['PUT'])
def update_body_part(part_id):
    data = request.json
    part = BodyPart.query.get_or_404(part_id)
    if 'BodyPartName' in data:
        part.BodyPartName = data['BodyPartName']
    db.session.commit()
    return jsonify({"message": "Updated"})

@body_parts_bp.route('/api/body_parts/<int:part_id>', methods=['DELETE'])
def delete_body_part(part_id):
    part = BodyPart.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Deleted"})

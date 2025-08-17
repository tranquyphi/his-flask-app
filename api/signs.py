from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models_main import db
from models import Sign, BodySystem

signs_bp = Blueprint('signs', __name__)


def sign_to_dict(sign, system_name=None):
	return {
		'SignId': sign.SignId,
		'SignDesc': sign.SignDesc,
		'SignType': 1 if sign.SignType else 0,
		'SystemId': sign.SystemId,
		'Speciality': sign.Speciality,
		'SystemName': system_name
	}


@signs_bp.route('/signs', methods=['GET'])
def list_signs():
	"""List signs with optional filters and search.
	Query params:
	  q: substring in SignDesc (case-insensitive)
	  type: 0/1 for SignType
	  system_id: int BodySystem.SystemId
	  speciality: substring in Speciality
	"""
	try:
		query = db.session.query(Sign, BodySystem.SystemName).join(BodySystem)

		q = request.args.get('q', type=str)
		sign_type = request.args.get('type', type=str)
		system_id = request.args.get('system_id', type=int)
		speciality = request.args.get('speciality', type=str)

		if q:
			query = query.filter(Sign.SignDesc.ilike(f"%{q}%"))
		if sign_type in ('0', '1'):
			query = query.filter(Sign.SignType == (sign_type == '1'))
		if system_id:
			query = query.filter(Sign.SystemId == system_id)
		if speciality:
			query = query.filter(Sign.Speciality.ilike(f"%{speciality}%"))

		records = query.order_by(asc(Sign.SignDesc)).all()
		data = [sign_to_dict(s, sys_name) for s, sys_name in records]
		return jsonify({'signs': data})
	except Exception as e:
		db.session.rollback()
		return jsonify({'error': str(e)}), 500


@signs_bp.route('/signs/<int:sign_id>', methods=['GET'])
def get_sign(sign_id):
	try:
		sign = Sign.query.get_or_404(sign_id)
		system = BodySystem.query.get(sign.SystemId)
		return jsonify({'sign': sign_to_dict(sign, system.SystemName if system else None)})
	except Exception as e:
		return jsonify({'error': str(e)}), 500


@signs_bp.route('/signs', methods=['POST'])
def create_sign():
	try:
		payload = request.get_json(force=True) or {}
		required = ['SignDesc', 'SignType', 'SystemId']
		missing = [f for f in required if f not in payload or payload[f] in (None, '')]
		if missing:
			return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

		sign = Sign(
			SignDesc=payload['SignDesc'].strip(),
			SignType=bool(int(payload['SignType'])),
			SystemId=int(payload['SystemId']),
			Speciality=payload.get('Speciality', '').strip() or None
		)
		db.session.add(sign)
		db.session.commit()
		system = BodySystem.query.get(sign.SystemId)
		return jsonify({'sign': sign_to_dict(sign, system.SystemName if system else None)}), 201
	except Exception as e:
		db.session.rollback()
		return jsonify({'error': str(e)}), 500


@signs_bp.route('/signs/<int:sign_id>', methods=['PUT'])
def update_sign(sign_id):
	try:
		sign = Sign.query.get_or_404(sign_id)
		payload = request.get_json(force=True) or {}

		if 'SignDesc' in payload:
			sign.SignDesc = payload['SignDesc'].strip()
		if 'SignType' in payload:
			sign.SignType = bool(int(payload['SignType']))
		if 'SystemId' in payload:
			sign.SystemId = int(payload['SystemId'])
		if 'Speciality' in payload:
			speciality_val = payload.get('Speciality')
			sign.Speciality = speciality_val.strip() if speciality_val else None

		db.session.commit()
		system = BodySystem.query.get(sign.SystemId)
		return jsonify({'sign': sign_to_dict(sign, system.SystemName if system else None)})
	except Exception as e:
		db.session.rollback()
		return jsonify({'error': str(e)}), 500


@signs_bp.route('/signs/<int:sign_id>', methods=['DELETE'])
def delete_sign(sign_id):
	try:
		sign = Sign.query.get_or_404(sign_id)
		db.session.delete(sign)
		db.session.commit()
		return jsonify({'message': 'Deleted', 'SignId': sign_id})
	except Exception as e:
		db.session.rollback()
		return jsonify({'error': str(e)}), 500

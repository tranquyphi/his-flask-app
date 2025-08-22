"""
Visits API Blueprint
Basic CRUD operations for Visit management
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc, text
from models_main import db
from models import Visit, Patient, Department, Staff, VisitStaff
from datetime import datetime

visits_bp = Blueprint('visits', __name__)


def visit_to_dict(visit, patient_name=None, staff_names=None):
    """Convert Visit to dictionary with optional related data"""
    result = visit.to_dict()
    
    # Add related information if available
    if patient_name:
        result['PatientName'] = patient_name
    if staff_names:
        result['StaffNames'] = staff_names
    
    return result


@visits_bp.route('/visits', methods=['GET'])
def list_visits():
    """List visits with optional filters and search.
    Query params:
      patient_id: filter by PatientId
      purpose: filter by VisitPurpose
      date_from: filter visits from date (YYYY-MM-DD)
      date_to: filter visits to date (YYYY-MM-DD)
      limit: limit number of results (default 100)
      offset: offset for pagination
    """
    try:
        # Base query with joins for related data
        query = db.session.query(
            Visit,
            Patient.PatientName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        )
        
        # Apply filters
        patient_id = request.args.get('patient_id', type=str)
        purpose = request.args.get('purpose', type=str)
        date_from = request.args.get('date_from', type=str)
        date_to = request.args.get('date_to', type=str)
        
        if patient_id:
            query = query.filter(Visit.PatientId == patient_id)
        if purpose:
            query = query.filter(Visit.VisitPurpose == purpose)
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Visit.VisitTime >= from_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format. Use YYYY-MM-DD'}), 400
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Visit.VisitTime <= to_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format. Use YYYY-MM-DD'}), 400
        
        # Pagination
        limit = min(request.args.get('limit', 100, type=int), 1000)  # Max 1000 records
        offset = request.args.get('offset', 0, type=int)
        
        # Order by most recent visits first
        query = query.order_by(desc(Visit.VisitTime), desc(Visit.VisitId))
        
        # Apply pagination
        records = query.offset(offset).limit(limit).all()
        
        # Convert to dictionaries and get staff information
        data = []
        for visit, patient_name in records:
            # Get staff names for this visit
            staff_names = [vs.staff.StaffName for vs in visit.visit_staff if vs.staff]
            visit_data = visit_to_dict(visit, patient_name, staff_names)
            data.append(visit_data)
        
        return jsonify({'visits': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/<int:visit_id>', methods=['GET'])
def get_visit(visit_id):
    """Get a specific visit by ID with full related information"""
    try:
        # Query with joins for related data
        result = db.session.query(
            Visit,
            Patient.PatientName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).filter(Visit.VisitId == visit_id).first()
        
        if not result:
            return jsonify({'error': 'Visit not found'}), 404
            
        visit, patient_name = result
        
        # Get staff names for this visit
        staff_names = [vs.staff.StaffName for vs in visit.visit_staff if vs.staff]
        
        return jsonify({'visit': visit_to_dict(visit, patient_name, staff_names)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits', methods=['POST'])
def create_visit():
    """Create a new visit"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['PatientId', 'StaffIds']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Validate PatientId exists
        patient = Patient.query.get(payload['PatientId'])
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Validate StaffIds exist
        staff_ids = payload['StaffIds']
        if not isinstance(staff_ids, list) or len(staff_ids) == 0:
            return jsonify({'error': 'StaffIds must be a non-empty list'}), 400
        
        staff_list = Staff.query.filter(Staff.StaffId.in_(staff_ids)).all()
        if len(staff_list) != len(staff_ids):
            return jsonify({'error': 'One or more StaffIds not found'}), 404
        
        # Parse VisitTime if provided
        visit_time = None
        if 'VisitTime' in payload and payload['VisitTime']:
            try:
                visit_time = datetime.fromisoformat(payload['VisitTime'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid VisitTime format. Use ISO format'}), 400
        else:
            visit_time = datetime.utcnow()  # Default to current time
        
        # Create visit
        visit = Visit(
            PatientId=payload['PatientId'],
            VisitPurpose=payload.get('VisitPurpose'),
            VisitTime=visit_time
        )
        
        db.session.add(visit)
        db.session.flush()  # Get the VisitId
        
        # Create VisitStaff associations
        for staff_id in staff_ids:
            visit_staff = VisitStaff(VisitId=visit.VisitId, StaffId=staff_id)
            db.session.add(visit_staff)
        
        db.session.commit()
        
        # Return the created visit with related data
        staff_names = [staff.StaffName for staff in staff_list]
        return jsonify({
            'visit': visit_to_dict(
                visit, 
                patient.PatientName,
                staff_names
            )
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/<int:visit_id>', methods=['PUT'])
def update_visit(visit_id):
    """Update a visit"""
    try:
        visit = Visit.query.get_or_404(visit_id)
        payload = request.get_json(force=True) or {}
        
        # Update fields if provided
        if 'VisitPurpose' in payload:
            visit.VisitPurpose = payload['VisitPurpose']
        if 'VisitTime' in payload and payload['VisitTime']:
            try:
                visit.VisitTime = datetime.fromisoformat(payload['VisitTime'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid VisitTime format. Use ISO format'}), 400
        
        # Update staff associations if provided
        if 'StaffIds' in payload:
            staff_ids = payload['StaffIds']
            if not isinstance(staff_ids, list):
                return jsonify({'error': 'StaffIds must be a list'}), 400
            
            # Validate StaffIds exist
            staff_list = Staff.query.filter(Staff.StaffId.in_(staff_ids)).all()
            if len(staff_list) != len(staff_ids):
                return jsonify({'error': 'One or more StaffIds not found'}), 404
            
            # Remove existing staff associations
            VisitStaff.query.filter_by(VisitId=visit_id).delete()
            
            # Create new staff associations
            for staff_id in staff_ids:
                visit_staff = VisitStaff(VisitId=visit_id, StaffId=staff_id)
                db.session.add(visit_staff)
        
        db.session.commit()
        
        # Return updated visit with related data
        result = db.session.query(
            Visit,
            Patient.PatientName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).filter(Visit.VisitId == visit_id).first()
        
        visit, patient_name = result
        
        # Get staff names for this visit
        staff_names = [vs.staff.StaffName for vs in visit.visit_staff if vs.staff]
        
        return jsonify({'visit': visit_to_dict(visit, patient_name, staff_names)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/<int:visit_id>', methods=['DELETE'])
def delete_visit(visit_id):
    """Delete a visit and all related records"""
    try:
        visit = Visit.query.get_or_404(visit_id)
        db.session.delete(visit)
        db.session.commit()
        
        return jsonify({'message': 'Visit deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/purposes', methods=['GET'])
def get_visit_purposes():
    """Get all available visit purposes"""
    purposes = [
        'Thường quy', 'Cấp cứu', 'Phòng khám', 'Nhận bệnh', 'Bệnh án',
        'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám', 'Khám chuyên khoa'
    ]
    return jsonify({'visit_purposes': purposes})


@visits_bp.route('/visits/<int:visit_id>/staff', methods=['GET'])
def get_visit_staff(visit_id):
    """Get all staff associated with a specific visit"""
    try:
        visit = Visit.query.get_or_404(visit_id)
        staff_data = []
        
        for vs in visit.visit_staff:
            if vs.staff:
                staff_data.append({
                    'StaffId': vs.StaffId,
                    'StaffName': vs.staff.StaffName,
                    'StaffRole': vs.staff.StaffRole
                })
        
        return jsonify({'staff': staff_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/<int:visit_id>/staff', methods=['POST'])
def add_staff_to_visit(visit_id):
    """Add staff to a visit"""
    try:
        visit = Visit.query.get_or_404(visit_id)
        payload = request.get_json(force=True) or {}
        
        if 'StaffId' not in payload:
            return jsonify({'error': 'StaffId is required'}), 400
        
        staff_id = payload['StaffId']
        
        # Check if staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
        
        # Check if association already exists
        existing = VisitStaff.query.filter_by(VisitId=visit_id, StaffId=staff_id).first()
        if existing:
            return jsonify({'error': 'Staff already associated with this visit'}), 400
        
        # Create new association
        visit_staff = VisitStaff(VisitId=visit_id, StaffId=staff_id)
        db.session.add(visit_staff)
        db.session.commit()
        
        return jsonify({'message': 'Staff added to visit successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits/<int:visit_id>/staff/<int:staff_id>', methods=['DELETE'])
def remove_staff_from_visit(visit_id, staff_id):
    """Remove staff from a visit"""
    try:
        visit_staff = VisitStaff.query.filter_by(VisitId=visit_id, StaffId=staff_id).first()
        if not visit_staff:
            return jsonify({'error': 'Staff not associated with this visit'}), 404
        
        db.session.delete(visit_staff)
        db.session.commit()
        
        return jsonify({'message': 'Staff removed from visit successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

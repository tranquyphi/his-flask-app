"""
Visits API Blueprint
Basic CRUD operations for Visit management
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc, text
from models import db, Visit, Patient, Department, Staff
from datetime import datetime

visits_bp = Blueprint('visits', __name__)


def visit_to_dict(visit, patient_name=None, department_name=None, staff_name=None):
    """Convert Visit to dictionary with optional related data"""
    result = visit.to_dict()
    
    # Add related information if available
    if patient_name:
        result['PatientName'] = patient_name
    if department_name:
        result['DepartmentName'] = department_name
    if staff_name:
        result['StaffName'] = staff_name
    
    return result


@visits_bp.route('/visits', methods=['GET'])
def list_visits():
    """List visits with optional filters and search.
    Query params:
      patient_id: filter by PatientId
      department_id: filter by DepartmentId
      staff_id: filter by StaffId
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
            Patient.PatientName,
            Department.DepartmentName,
            Staff.StaffName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).join(
            Department, Visit.DepartmentId == Department.DepartmentId, isouter=True
        ).join(
            Staff, Visit.StaffId == Staff.StaffId, isouter=True
        )
        
        # Apply filters
        patient_id = request.args.get('patient_id', type=str)
        department_id = request.args.get('department_id', type=int)
        staff_id = request.args.get('staff_id', type=int)
        purpose = request.args.get('purpose', type=str)
        date_from = request.args.get('date_from', type=str)
        date_to = request.args.get('date_to', type=str)
        
        if patient_id:
            query = query.filter(Visit.PatientId == patient_id)
        if department_id:
            query = query.filter(Visit.DepartmentId == department_id)
        if staff_id:
            query = query.filter(Visit.StaffId == staff_id)
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
        
        # Convert to dictionaries
        data = [
            visit_to_dict(visit, patient_name, dept_name, staff_name)
            for visit, patient_name, dept_name, staff_name in records
        ]
        
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
            Patient.PatientName,
            Department.DepartmentName,
            Staff.StaffName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).join(
            Department, Visit.DepartmentId == Department.DepartmentId, isouter=True
        ).join(
            Staff, Visit.StaffId == Staff.StaffId, isouter=True
        ).filter(Visit.VisitId == visit_id).first()
        
        if not result:
            return jsonify({'error': 'Visit not found'}), 404
            
        visit, patient_name, dept_name, staff_name = result
        
        return jsonify({'visit': visit_to_dict(visit, patient_name, dept_name, staff_name)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@visits_bp.route('/visits', methods=['POST'])
def create_visit():
    """Create a new visit"""
    try:
        payload = request.get_json(force=True) or {}
        required = ['PatientId', 'DepartmentId', 'StaffId']
        missing = [f for f in required if f not in payload or payload[f] in (None, '')]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Validate PatientId exists
        patient = Patient.query.get(payload['PatientId'])
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Validate DepartmentId exists
        department = Department.query.get(payload['DepartmentId'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Validate StaffId exists
        staff = Staff.query.get(payload['StaffId'])
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
        
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
            DepartmentId=payload['DepartmentId'],
            StaffId=payload['StaffId'],
            VisitPurpose=payload.get('VisitPurpose'),
            VisitTime=visit_time
        )
        
        db.session.add(visit)
        db.session.commit()
        
        # Return the created visit with related data
        return jsonify({
            'visit': visit_to_dict(
                visit, 
                patient.PatientName,
                department.DepartmentName,
                staff.StaffName
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
        
        # Validate and update DepartmentId if provided
        if 'DepartmentId' in payload:
            department = Department.query.get(payload['DepartmentId'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404
            visit.DepartmentId = payload['DepartmentId']
        
        # Validate and update StaffId if provided
        if 'StaffId' in payload:
            staff = Staff.query.get(payload['StaffId'])
            if not staff:
                return jsonify({'error': 'Staff not found'}), 404
            visit.StaffId = payload['StaffId']
        
        db.session.commit()
        
        # Return updated visit with related data
        result = db.session.query(
            Visit,
            Patient.PatientName,
            Department.DepartmentName,
            Staff.StaffName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).join(
            Department, Visit.DepartmentId == Department.DepartmentId, isouter=True
        ).join(
            Staff, Visit.StaffId == Staff.StaffId, isouter=True
        ).filter(Visit.VisitId == visit_id).first()
        
        visit, patient_name, dept_name, staff_name = result
        
        return jsonify({'visit': visit_to_dict(visit, patient_name, dept_name, staff_name)})
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

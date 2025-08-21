"""
Departments API Blueprint
CRUD operations for Department management
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import asc
from models_main import db
from models import Department
from models.StaffDepartment import StaffDepartment as StaffDepartmentModel
from models.PatientDepartment import PatientDepartment as PatientDepartmentModel

departments_bp = Blueprint('departments', __name__)


def department_to_dict(dept):
    """Convert Department to dictionary with additional stats"""
    return {
        'DepartmentId': dept.DepartmentId,
        'DepartmentName': dept.DepartmentName,
        'DepartmentType': dept.DepartmentType
    }


@departments_bp.route('/departments', methods=['GET'])
def list_departments():
    """List all departments with optional search and counts"""
    try:
        query = db.session.query(Department)
        
        # Search by name if provided
        search = request.args.get('q', type=str)
        if search:
            query = query.filter(Department.DepartmentName.ilike(f"%{search}%"))
        
        # Filter by type if provided
        dept_type = request.args.get('type', type=str)
        if dept_type:
            query = query.filter(Department.DepartmentType == dept_type)
        
        departments = query.order_by(asc(Department.DepartmentName)).all()
        
        # Get staff counts for filtered departments in one query
        dept_ids = [dept.DepartmentId for dept in departments]
        if dept_ids:
            staff_counts = db.session.query(
                StaffDepartmentModel.DepartmentId,
                db.func.count(StaffDepartmentModel.StaffId).label('staff_count')
            ).filter(
                StaffDepartmentModel.DepartmentId.in_(dept_ids),
                StaffDepartmentModel.Current == True
            ).group_by(StaffDepartmentModel.DepartmentId).all()
            
            patient_counts = db.session.query(
                PatientDepartmentModel.DepartmentId,
                db.func.count(PatientDepartmentModel.PatientId).label('patient_count')
            ).filter(
                PatientDepartmentModel.DepartmentId.in_(dept_ids),
                PatientDepartmentModel.Current == True
            ).group_by(PatientDepartmentModel.DepartmentId).all()
            
            # Convert to dictionaries for easy lookup
            staff_counts_dict = {dept_id: count for dept_id, count in staff_counts}
            patient_counts_dict = {dept_id: count for dept_id, count in patient_counts}
        else:
            staff_counts_dict = {}
            patient_counts_dict = {}
        
        # Build response with counts
        data = []
        for dept in departments:
            dept_data = department_to_dict(dept)
            dept_data.update({
                'current_staff_count': staff_counts_dict.get(dept.DepartmentId, 0),
                'current_patient_count': patient_counts_dict.get(dept.DepartmentId, 0),
                'total_visits': len(dept.visits)
            })
            data.append(dept_data)
        
        return jsonify({'departments': data})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    """Get a specific department by ID with stats"""
    try:
        dept = Department.query.get_or_404(dept_id)
        
        # Get current staff count
        current_staff = db.session.query(StaffDepartmentModel).filter_by(
            DepartmentId=dept_id, 
            Current=True
        ).count()
        
        # Get current patient count
        current_patients = db.session.query(PatientDepartmentModel).filter_by(
            DepartmentId=dept_id, 
            Current=True
        ).count()
        
        # Get total visits
        total_visits = len(dept.visits)
        
        result = department_to_dict(dept)
        result.update({
            'current_staff_count': current_staff,
            'current_patient_count': current_patients,
            'total_visits': total_visits
        })
        
        return jsonify({'department': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments', methods=['POST'])
def create_department():
    """Create a new department"""
    try:
        payload = request.get_json(force=True) or {}
        
        # Validate required fields
        required = ['DepartmentName', 'DepartmentType']
        missing = [f for f in required if f not in payload or not payload[f]]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Validate DepartmentType
        valid_types = ['Nội trú', 'Cấp cứu', 'Phòng khám', 'CLS']
        if payload['DepartmentType'] not in valid_types:
            return jsonify({'error': f'Invalid DepartmentType. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Check if name already exists
        existing = Department.query.filter_by(DepartmentName=payload['DepartmentName']).first()
        if existing:
            return jsonify({'error': 'Tên khoa đã tồn tại'}), 400
        
        # Create new department
        new_dept = Department(
            DepartmentName=payload['DepartmentName'].strip(),
            DepartmentType=payload['DepartmentType']
        )
        
        db.session.add(new_dept)
        db.session.commit()
        
        return jsonify({
            'message': 'Department created successfully',
            'department': department_to_dict(new_dept)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    """Update an existing department"""
    try:
        dept = Department.query.get_or_404(dept_id)
        payload = request.get_json(force=True) or {}
        
        # Validate required fields
        if 'DepartmentName' in payload and not payload['DepartmentName']:
            return jsonify({'error': 'DepartmentName is required'}), 400
        
        if 'DepartmentType' in payload and not payload['DepartmentType']:
            return jsonify({'error': 'DepartmentType is required'}), 400
        
        # Validate DepartmentType if provided
        if 'DepartmentType' in payload:
            valid_types = ['Nội trú', 'Cấp cứu', 'Phòng khám', 'CLS']
            if payload['DepartmentType'] not in valid_types:
                return jsonify({'error': f'Invalid DepartmentType. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Check if new name conflicts with existing (excluding current record)
        if 'DepartmentName' in payload:
            existing = Department.query.filter(
                Department.DepartmentName == payload['DepartmentName'],
                Department.DepartmentId != dept_id
            ).first()
            if existing:
                return jsonify({'error': 'Tên khoa đã tồn tại'}), 400
        
        # Update fields
        if 'DepartmentName' in payload:
            dept.DepartmentName = payload['DepartmentName'].strip()
        if 'DepartmentType' in payload:
            dept.DepartmentType = payload['DepartmentType']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Department updated successfully',
            'department': department_to_dict(dept)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    """Delete a department"""
    try:
        dept = Department.query.get_or_404(dept_id)
        
        # Check if any staff are currently assigned to this department
        current_staff = db.session.query(StaffDepartmentModel).filter_by(
            DepartmentId=dept_id, 
            Current=True
        ).count()
        
        if current_staff > 0:
            return jsonify({'error': f'Không thể xóa khoa này vì đang có {current_staff} nhân viên làm việc'}), 400
        
        # Check if any patients are currently in this department
        current_patients = PatientDepartment.query.filter_by(
            DepartmentId=dept_id, 
            Current=True
        ).count()
        
        if current_patients > 0:
            return jsonify({'error': f'Không thể xóa khoa này vì đang có {current_patients} bệnh nhân điều trị'}), 400
        
        # Check if department has any visits
        if dept.visits.count() > 0:
            return jsonify({'error': 'Không thể xóa khoa này vì đã có lịch sử khám bệnh'}), 400
        
        db.session.delete(dept)
        db.session.commit()
        
        return jsonify({'message': 'Department deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/<int:dept_id>/staff', methods=['GET'])
def get_department_staff(dept_id):
    """Get all staff currently assigned to a department"""
    try:
        dept = Department.query.get_or_404(dept_id)
        
        staff_assignments = db.session.query(StaffDepartmentModel).filter_by(
            DepartmentId=dept_id,
            Current=True
        ).all()
        
        staff_data = []
        for assignment in staff_assignments:
            staff = assignment.staff_member
            staff_data.append({
                'StaffId': staff.StaffId,
                'StaffName': staff.StaffName,
                'StaffRole': staff.StaffRole,
                'Position': assignment.Position,
                'AssignedAt': assignment.id  # Using id as timestamp proxy
            })
        
        return jsonify({
            'department': department_to_dict(dept),
            'staff': staff_data,
            'count': len(staff_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/stats', methods=['GET'])
def get_departments_stats():
    """Get statistics for all departments in one query"""
    try:
        # Get all departments
        departments = Department.query.order_by(Department.DepartmentName).all()
        
        # Get staff counts for all departments in one query
        staff_counts = db.session.query(
            StaffDepartmentModel.DepartmentId,
            db.func.count(StaffDepartmentModel.StaffId).label('staff_count')
        ).filter(
            StaffDepartmentModel.Current == True
        ).group_by(StaffDepartmentModel.DepartmentId).all()
        
        # Get patient counts for all departments in one query
        patient_counts = db.session.query(
            PatientDepartmentModel.DepartmentId,
            db.func.count(PatientDepartmentModel.PatientId).label('patient_count')
        ).filter(
            PatientDepartmentModel.Current == True
        ).group_by(PatientDepartmentModel.DepartmentId).all()
        
        # Convert to dictionaries for easy lookup
        staff_counts_dict = {dept_id: count for dept_id, count in staff_counts}
        patient_counts_dict = {dept_id: count for dept_id, count in patient_counts}
        
        # Build response with all statistics
        departments_stats = []
        for dept in departments:
            dept_data = department_to_dict(dept)
            dept_data.update({
                'current_staff_count': staff_counts_dict.get(dept.DepartmentId, 0),
                'current_patient_count': patient_counts_dict.get(dept.DepartmentId, 0),
                'total_visits': len(dept.visits)
            })
            departments_stats.append(dept_data)
        
        return jsonify({
            'departments': departments_stats,
            'total_departments': len(departments),
            'total_staff': sum(staff_counts_dict.values()),
            'total_patients': sum(patient_counts_dict.values()),
            'total_visits': sum(len(dept.visits) for dept in departments)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/departments/<int:dept_id>/patients', methods=['GET'])
def get_department_patients(dept_id):
    """Get all patients currently in a department"""
    try:
        dept = Department.query.get_or_404(dept_id)
        
        patient_assignments = db.session.query(PatientDepartmentModel).filter_by(
            DepartmentId=dept_id,
            Current=True
        ).all()
        
        patients_data = []
        for assignment in patient_assignments:
            patient = assignment.patient
            patients_data.append({
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientAge': patient.PatientAge,
                'PatientGender': patient.PatientGender,
                'AdmittedAt': assignment.At.isoformat() if assignment.At else None,
                'Reason': assignment.Reason
            })
        
        return jsonify({
            'department': department_to_dict(dept),
            'patients': patients_data,
            'count': len(patients_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500




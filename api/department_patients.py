from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db
from models import PatientDepartment, Patient, Department

# Create Blueprint for department patients API routes
dept_patients_bp = Blueprint('department_patients', __name__)

@dept_patients_bp.route('/department_patients/<int:department_id>', methods=['GET'])
def get_department_patients(department_id):
    """Get all current patients in a specific department"""
    try:
        # Get department info first
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Get patients for specific department
        patients_data = db.session.query(
            PatientDepartment.id,
            PatientDepartment.PatientId,
            PatientDepartment.DepartmentId,
            PatientDepartment.Current,
            PatientDepartment.At,
            Patient.PatientName,
            Patient.PatientGender,
            Patient.PatientAge,
            Department.DepartmentName
        ).join(Patient, Patient.PatientId == PatientDepartment.PatientId)\
         .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)\
         .filter(
            PatientDepartment.DepartmentId == department_id,
            PatientDepartment.Current == True
         )\
         .order_by(PatientDepartment.At.desc())\
         .all()
        
        # Convert results to dictionaries with proper formatting
        data = []
        for r in patients_data:
            row_dict = dict(r._mapping)
            # Ensure datetime is serializable
            if row_dict.get('At'):
                row_dict['At'] = row_dict['At'].isoformat()
            data.append(row_dict)
        
        return jsonify({
            'department': {
                'DepartmentId': department.DepartmentId,
                'DepartmentName': department.DepartmentName,
                'DepartmentType': department.DepartmentType
            },
            'patients': data,
            'count': len(data)
        })
        
    except Exception as e:
        print(f"Error in get_department_patients: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@dept_patients_bp.route('/department_stats/<int:department_id>', methods=['GET'])
def get_department_stats(department_id):
    """Get statistics for a specific department"""
    try:
        # Current patients count
        current_count = (
            db.session.query(PatientDepartment)
            .filter(
                PatientDepartment.DepartmentId == department_id,
                PatientDepartment.Current == True
            )
            .count()
        )
        
        # Total patients ever assigned to this department
        total_count = (
            db.session.query(PatientDepartment)
            .filter(PatientDepartment.DepartmentId == department_id)
            .count()
        )
        
        # Recent admissions (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_count = (
            db.session.query(PatientDepartment)
            .filter(
                PatientDepartment.DepartmentId == department_id,
                PatientDepartment.At >= week_ago,
                PatientDepartment.Current == True
            )
            .count()
        )
        
        return jsonify({
            'current_patients': current_count,
            'total_patients': total_count,
            'recent_admissions': recent_count
        })
        
    except Exception as e:
        print(f"Error in get_department_stats: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@dept_patients_bp.route('/department_access/<int:department_id>', methods=['GET'])
def check_department_access(department_id):
    """Check if current user has access to a specific department - for future authorization"""
    try:
        # Get department info
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
            
        # For now, allow access to all departments
        # In future, this will check user permissions/staff assignments
        # Example: check if current_user.department_id == department_id
        
        return jsonify({
            'access_granted': True,
            'department': {
                'DepartmentId': department.DepartmentId,
                'DepartmentName': department.DepartmentName,
                'DepartmentType': department.DepartmentType
            },
            'permissions': {
                'view_patients': True,
                'edit_patients': True,
                'discharge_patients': True,
                'view_statistics': True
            },
            'message': 'Access granted to department'
        })
        
    except Exception as e:
        print(f"Error in check_department_access: {e}")
        return jsonify({'error': f'Authorization error: {str(e)}'}), 500

@dept_patients_bp.route('/staff_department', methods=['GET'])
def get_staff_department():
    """Get the department assigned to current staff member - for future authorization"""
    try:
        # For now, return a mock department assignment
        # In future, this will get the actual staff's department from session/JWT token
        # Example: current_user = get_current_user_from_session()
        #          staff = Staff.query.filter_by(StaffId=current_user.staff_id).first()
        #          return staff.DepartmentId
        
        # Mock response - in real implementation, this would come from authentication
        mock_staff_department = {
            'staff_id': 'STAFF001',
            'staff_name': 'Dr. Nguyen Van A',
            'department_id': 5,  # Example: Emergency department
            'department_name': 'Cấp cứu-Hồi sức',
            'role': 'Doctor',
            'permissions': {
                'view_patients': True,
                'edit_patients': True,
                'discharge_patients': True,
                'view_all_departments': False  # Only see own department
            }
        }
        
        return jsonify(mock_staff_department)
        
    except Exception as e:
        print(f"Error in get_staff_department: {e}")
        return jsonify({'error': f'Authorization error: {str(e)}'}), 500

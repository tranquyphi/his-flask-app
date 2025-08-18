from flask import Blueprint, jsonify, request
from datetime import datetime
from models_main import db
from models import PatientDepartment, Patient, Department

# Create Blueprint for patient departments API routes
patient_depts_bp = Blueprint('patient_departments', __name__)

@patient_depts_bp.route('/patients/<int:patient_id>/departments', methods=['GET'])
def get_patient_departments(patient_id):
    """Get department history for a specific patient"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Query department history for the patient
        results = (
            db.session.query(
                PatientDepartment.id,
                PatientDepartment.PatientId,
                PatientDepartment.DepartmentId,
                PatientDepartment.Current,
                PatientDepartment.At.label('StartDate'),
                PatientDepartment.EndDate,
                PatientDepartment.Reason,
                Department.DepartmentName,
                Department.DepartmentType
            )
            .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
            .filter(PatientDepartment.PatientId == patient_id)
            .order_by(PatientDepartment.At.desc())
            .all()
        )
        
        # Convert results to dictionaries with proper formatting
        departments_data = []
        for r in results:
            row_dict = dict(r._mapping)
            # Ensure datetimes are serializable
            if row_dict.get('StartDate'):
                row_dict['StartDate'] = row_dict['StartDate'].isoformat()
            if row_dict.get('EndDate'):
                row_dict['EndDate'] = row_dict['EndDate'].isoformat()
            departments_data.append(row_dict)
        
        return jsonify({
            'patient_id': patient_id,
            'departments': departments_data,
            'count': len(departments_data)
        })
        
    except Exception as e:
        print(f"Error in get_patient_departments: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@patient_depts_bp.route('/patients/<int:patient_id>/department', methods=['POST'])
def assign_patient_department(patient_id):
    """Assign a patient to a department"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        new_department_id = data.get('DepartmentId')
        reason = data.get('Reason', '')
        
        # Check if department exists
        department = Department.query.get(new_department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Check if patient is already in this department
        current_assignment = PatientDepartment.query.filter_by(
            PatientId=patient_id,
            DepartmentId=new_department_id,
            Current=True
        ).first()
        
        if current_assignment:
            return jsonify({
                'error': 'Patient is already assigned to this department',
                'assignment': {
                    'PatientDepartmentId': current_assignment.id,
                    'DepartmentId': current_assignment.DepartmentId,
                    'At': current_assignment.At.isoformat() if current_assignment.At else None
                }
            }), 400
        
        # Start a transaction
        try:
            # End any current department assignment
            current_assignments = PatientDepartment.query.filter_by(
                PatientId=patient_id,
                Current=True
            ).all()
            
            for assignment in current_assignments:
                assignment.Current = False
                assignment.EndDate = datetime.now()
            
            # Create new department assignment
            new_assignment = PatientDepartment(
                PatientId=patient_id,
                DepartmentId=new_department_id,
                Current=True,
                At=datetime.now(),
                EndDate=None,
                Reason=reason if reason in ['DT', 'PT', 'KCK', 'CLS', 'KH'] else 'DT'
            )
            
            db.session.add(new_assignment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Patient assigned to department successfully',
                'assignment': {
                    'PatientDepartmentId': new_assignment.id,
                    'DepartmentId': new_assignment.DepartmentId,
                    'DepartmentName': department.DepartmentName,
                    'At': new_assignment.At.isoformat() if new_assignment.At else None
                }
            })
        
        except Exception as e:
            db.session.rollback()
            raise e
        
    except Exception as e:
        print(f"Error in assign_patient_department: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

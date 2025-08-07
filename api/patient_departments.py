from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db, PatientDepartment, Patient, Department

# Create Blueprint for patient department API routes
patient_dept_bp = Blueprint('patient_departments', __name__)

@patient_dept_bp.route('/patient_department_detail/<string:patient_id>', methods=['GET'])
def get_patient_department(patient_id):
    results = (
        db.session.query(
            PatientDepartment.PatientId,
            Patient.PatientAge,
            Patient.PatientAddress,
            Patient.PatientGender,
            Patient.PatientName,
            Department.DepartmentName
        )
        .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
        .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
        .filter(PatientDepartment.PatientId == patient_id)
        .all()
    )
    return jsonify([dict(r._mapping) for r in results])

@patient_dept_bp.route('/patient_department_detail', methods=['GET'])
def get_patient_departments():
    try:
        # Check if PatientId is provided as query parameter
        patient_id = request.args.get('PatientId')
        
        if patient_id:
            # Filter by PatientId if provided
            results = (
                db.session.query(
                    PatientDepartment.id,
                    PatientDepartment.PatientId,
                    PatientDepartment.DepartmentId,
                    PatientDepartment.Current,
                    PatientDepartment.At,
                    PatientDepartment.Reason,
                    Patient.PatientAge,
                    Patient.PatientAddress,
                    Patient.PatientGender,
                    Patient.PatientName,
                    Department.DepartmentName,
                    Department.DepartmentType
                )
                .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
                .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
                .filter(PatientDepartment.PatientId == patient_id)
                .all()
            )
        else:
            # Return all if no PatientId specified
            results = (
                db.session.query(
                    PatientDepartment.id,
                    PatientDepartment.PatientId,
                    PatientDepartment.DepartmentId,
                    PatientDepartment.Current,
                    PatientDepartment.At,
                    PatientDepartment.Reason,
                    Patient.PatientAge,
                    Patient.PatientAddress,
                    Patient.PatientGender,
                    Patient.PatientName,
                    Department.DepartmentName,
                    Department.DepartmentType
                )
                .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
                .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
                .all()
            )
        
        # Convert results to dictionaries with proper formatting
        data = []
        for r in results:
            row_dict = dict(r._mapping)
            # Ensure datetime is serializable
            if row_dict.get('At'):
                row_dict['At'] = row_dict['At'].isoformat()
            data.append(row_dict)
            
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_patient_departments: {e}")
        # Fallback to simple query
        try:
            items = PatientDepartment.query.all()
            return jsonify([{
                'id': item.id,
                'PatientId': item.PatientId,
                'DepartmentId': item.DepartmentId,
                'Current': item.Current,
                'At': item.At.isoformat() if item.At else None,
                'Reason': item.Reason
            } for item in items])
        except Exception as fallback_error:
            return jsonify({'error': f'Database error: {str(fallback_error)}'}), 500

@patient_dept_bp.route('/patient_department_detail', methods=['POST'])
def add_patient_department():
    try:
        data = request.json
        print(f"Adding patient department: {data}")
        
        # Business logic: When assigning a patient to a new department,
        # set all previous assignments for this patient to Historical (Current = False)
        if data.get('Current', True):
            # First, set all existing assignments for this patient to Historical
            existing_assignments = PatientDepartment.query.filter_by(
                PatientId=data['PatientId'],
                Current=True
            ).all()
            
            for assignment in existing_assignments:
                assignment.Current = False
                print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
        
        # Always create a new assignment since patients can be assigned multiple times
        # to the same department at different time intervals
        at_time = datetime.utcnow()
        if 'At' in data:
            at_time = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
        
        new_link = PatientDepartment(
            PatientId=data['PatientId'],
            DepartmentId=data['DepartmentId'],
            Current=data.get('Current', True),
            At=at_time,
            Reason=data.get('Reason', 'DT')
        )
        db.session.add(new_link)
        print(f"Created new assignment {new_link.PatientId}-{new_link.DepartmentId} at {at_time}")
        
        db.session.commit()
        return jsonify({"message": "Assignment processed successfully"}), 201
        
    except Exception as e:
        print(f"Error adding patient department: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_dept_bp.route('/patient_department_detail', methods=['PUT'])
def update_patient_department():
    try:
        data = request.json
        print(f"Updating patient department: {data}")
        
        # Since we removed unique constraints, we need to identify the specific record to update
        # We'll use a combination of PatientId, DepartmentId, and timestamp or record ID
        patient_id = data['PatientId']
        dept_id = data['DepartmentId']
        
        # Try to find the most recent current assignment to update
        # Or use a specific record ID if provided
        record_id = data.get('RecordId')  # Frontend should pass this for specific updates
        
        if record_id:
            # Update specific record by ID (if your table has an auto-increment ID)
            original_pd = PatientDepartment.query.filter_by(id=record_id).first()
        else:
            # Find the most recent current assignment for this patient-department combination
            original_pd = PatientDepartment.query.filter_by(
                PatientId=patient_id,
                DepartmentId=dept_id,
                Current=True
            ).order_by(PatientDepartment.At.desc()).first()
        
        if not original_pd:
            return jsonify({"error": "Assignment record not found"}), 404
        
        # For department changes, create new record and update old one
        new_dept_id = data.get('NewDepartmentId', dept_id)
        
        if str(original_pd.DepartmentId) != str(new_dept_id):
            print(f"Department changing from {original_pd.DepartmentId} to {new_dept_id}")
            
            # Business logic: When assigning to a new department, make all current assignments historical
            if data.get('Current', True):
                current_assignments = PatientDepartment.query.filter_by(
                    PatientId=patient_id,
                    Current=True
                ).all()
                
                for assignment in current_assignments:
                    assignment.Current = False
                    print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
            
            # Create new assignment for the new department
            at_time = datetime.utcnow()
            if 'At' in data:
                at_time = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
            
            new_assignment = PatientDepartment(
                PatientId=patient_id,
                DepartmentId=new_dept_id,
                Current=data.get('Current', True),
                At=at_time,
                Reason=data.get('Reason', 'DT')
            )
            db.session.add(new_assignment)
            print(f"Created new assignment {new_assignment.PatientId}-{new_assignment.DepartmentId}")
            
        else:
            # Same department, just update the existing record
            print(f"Updating same department assignment {original_pd.PatientId}-{original_pd.DepartmentId}")
            
            # Business logic: If setting this assignment to Current, make others Historical
            if data.get('Current', False) and not original_pd.Current:
                other_assignments = PatientDepartment.query.filter(
                    PatientDepartment.PatientId == patient_id,
                    PatientDepartment.Current == True
                ).all()
                
                for assignment in other_assignments:
                    if assignment != original_pd:  # Don't update the one we're currently editing
                        assignment.Current = False
                        print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
            
            # Update the existing assignment
            original_pd.Current = data.get('Current', original_pd.Current)
            original_pd.Reason = data.get('Reason', original_pd.Reason or 'DT')
            if 'At' in data:
                original_pd.At = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
            else:
                original_pd.At = datetime.utcnow()
            
        db.session.commit()
        return jsonify({"message": "Updated successfully"})
        
    except Exception as e:
        print(f"Error updating patient department: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_dept_bp.route('/patient_department_detail/<string:patient_id>/<int:department_id>', methods=['DELETE'])
def delete_patient_department(patient_id, department_id):
    """Delete a specific patient department assignment"""
    try:
        # Since we removed unique constraint, we need to be more specific
        # Delete the most recent current assignment for this patient-department combination
        pd = PatientDepartment.query.filter_by(
            PatientId=patient_id,
            DepartmentId=department_id,
            Current=True
        ).order_by(PatientDepartment.At.desc()).first()
        
        if not pd:
            # If no current assignment, try to find the most recent one
            pd = PatientDepartment.query.filter_by(
                PatientId=patient_id,
                DepartmentId=department_id
            ).order_by(PatientDepartment.At.desc()).first()
        
        if not pd:
            return jsonify({"error": "Assignment not found"}), 404
            
        db.session.delete(pd)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
        
    except Exception as e:
        print(f"Error deleting patient department: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_dept_bp.route('/patient_department_detail/record/<int:record_id>', methods=['DELETE'])
def delete_patient_department_by_id(record_id):
    """Delete a specific patient department assignment by record ID"""
    try:
        pd = PatientDepartment.query.get(record_id)
        if not pd:
            return jsonify({"error": "Assignment not found"}), 404
            
        db.session.delete(pd)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
        
    except Exception as e:
        print(f"Error deleting patient department by ID: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_dept_bp.route('/patient_department_detail/record/<int:record_id>', methods=['PUT'])
def update_patient_department_by_id(record_id):
    """Update a specific patient department assignment by record ID"""
    try:
        data = request.json
        print(f"Updating patient department by ID {record_id}: {data}")
        
        # Find the specific record
        pd = PatientDepartment.query.get(record_id)
        if not pd:
            return jsonify({"error": "Assignment not found"}), 404
        
        # Business logic: If setting this assignment to Current, make others Historical
        if data.get('Current', False) and not pd.Current:
            other_assignments = PatientDepartment.query.filter(
                PatientDepartment.PatientId == pd.PatientId,
                PatientDepartment.Current == True,
                PatientDepartment.id != record_id
            ).all()
            
            for assignment in other_assignments:
                assignment.Current = False
                print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
        
        # Update the specific record
        pd.DepartmentId = data.get('DepartmentId', pd.DepartmentId)
        pd.Current = data.get('Current', pd.Current)
        pd.Reason = data.get('Reason', pd.Reason or 'DT')
        if 'At' in data and data['At']:
            pd.At = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
        else:
            pd.At = datetime.utcnow()
            
        db.session.commit()
        return jsonify({"message": "Updated successfully"})
        
    except Exception as e:
        print(f"Error updating patient department by ID: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

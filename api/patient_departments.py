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
                    PatientDepartment.PatientId,
                    PatientDepartment.DepartmentId,
                    PatientDepartment.Current,
                    PatientDepartment.At,
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
                    PatientDepartment.PatientId,
                    PatientDepartment.DepartmentId,
                    PatientDepartment.Current,
                    PatientDepartment.At,
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
                'PatientId': item.PatientId,
                'DepartmentId': item.DepartmentId,
                'Current': item.Current,
                'At': item.At.isoformat() if item.At else None
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
        
        # Check if this exact assignment already exists
        existing = PatientDepartment.query.filter_by(
            PatientId=data['PatientId'],
            DepartmentId=data['DepartmentId']
        ).first()
        
        if existing:
            # Update existing assignment
            existing.Current = data.get('Current', True)
            if 'At' in data:
                existing.At = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
            else:
                existing.At = datetime.utcnow()
            print(f"Updated existing assignment {existing.PatientId}-{existing.DepartmentId}")
        else:
            # Create new assignment
            at_time = datetime.utcnow()
            if 'At' in data:
                at_time = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
            
            new_link = PatientDepartment(
                PatientId=data['PatientId'],
                DepartmentId=data['DepartmentId'],
                Current=data.get('Current', True),
                At=at_time
            )
            db.session.add(new_link)
            print(f"Created new assignment {new_link.PatientId}-{new_link.DepartmentId}")
        
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
        
        # For department changes, we need the original department ID
        # The frontend should send both the current and new department IDs
        original_dept_id = data.get('OriginalDepartmentId')
        patient_id = data['PatientId']
        new_dept_id = data['DepartmentId']
        
        # If no original department ID is provided, assume we're updating the current assignment
        if original_dept_id:
            # Find the original record to update/delete
            original_pd = PatientDepartment.query.filter_by(
                PatientId=patient_id, 
                DepartmentId=original_dept_id
            ).first()
        else:
            # Find any current assignment for this patient
            original_pd = PatientDepartment.query.filter_by(
                PatientId=patient_id,
                Current=True
            ).first()
        
        if not original_pd:
            return jsonify({"error": "Original assignment not found"}), 404
        
        # If the department is changing, create a new record and delete the old one
        if str(original_pd.DepartmentId) != str(new_dept_id):
            print(f"Department changing from {original_pd.DepartmentId} to {new_dept_id}")
            
            # Business logic: When assigning to a new department, make all other current assignments historical
            if data.get('Current', True):
                other_current = PatientDepartment.query.filter(
                    PatientDepartment.PatientId == patient_id,
                    PatientDepartment.Current == True
                ).all()
                
                for assignment in other_current:
                    assignment.Current = False
                    print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
            
            # Check if the new combination already exists
            existing_new = PatientDepartment.query.filter_by(
                PatientId=patient_id,
                DepartmentId=new_dept_id
            ).first()
            
            if existing_new:
                # Update the existing record
                existing_new.Current = data.get('Current', True)
                if 'At' in data:
                    existing_new.At = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
                else:
                    existing_new.At = datetime.utcnow()
                print(f"Updated existing assignment to new department {existing_new.PatientId}-{existing_new.DepartmentId}")
            else:
                # Create new assignment
                at_time = datetime.utcnow()
                if 'At' in data:
                    at_time = datetime.fromisoformat(data['At'].replace('Z', '+00:00'))
                
                new_assignment = PatientDepartment(
                    PatientId=patient_id,
                    DepartmentId=new_dept_id,
                    Current=data.get('Current', True),
                    At=at_time
                )
                db.session.add(new_assignment)
                print(f"Created new assignment {new_assignment.PatientId}-{new_assignment.DepartmentId}")
            
            # Delete the original assignment
            db.session.delete(original_pd)
            print(f"Deleted original assignment {original_pd.PatientId}-{original_pd.DepartmentId}")
            
        else:
            # Same department, just update the existing record
            print(f"Updating same department assignment {original_pd.PatientId}-{original_pd.DepartmentId}")
            
            # Business logic: If setting this assignment to Current, make others Historical
            if data.get('Current', False) and not original_pd.Current:
                other_assignments = PatientDepartment.query.filter(
                    PatientDepartment.PatientId == patient_id,
                    PatientDepartment.DepartmentId != original_pd.DepartmentId,
                    PatientDepartment.Current == True
                ).all()
                
                for assignment in other_assignments:
                    assignment.Current = False
                    print(f"Setting assignment {assignment.PatientId}-{assignment.DepartmentId} to Historical")
            
            # Update the existing assignment
            original_pd.Current = data.get('Current', original_pd.Current)
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
    pd = PatientDepartment.query.get((patient_id, department_id))
    if not pd:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(pd)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})

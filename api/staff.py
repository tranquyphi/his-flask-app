"""
Staff API endpoints
"""

from flask import Blueprint, jsonify, request
from models_main import db
from models.Staff import Staff
from models.Department import Department
from models.StaffDepartment import StaffDepartment
from sqlalchemy import desc
from datetime import datetime

staff_bp = Blueprint('staff_bp', __name__)

@staff_bp.route('/staff', methods=['GET'])
def get_all_staff():
    """Get all staff members with their current department"""
    try:
        # Get query parameters
        department_id = request.args.get('department_id', type=int)
        
        staff_list = Staff.query.all()
        result = []
        
        for staff in staff_list:
            # Only include available staff
            if not staff.StaffAvailable:
                continue
                
            staff_dict = staff.to_dict()
            current_dept_assignment = StaffDepartment.query.filter_by(
                StaffId=staff.StaffId, 
                Current=True
            ).first()
            
            if current_dept_assignment:
                department = Department.query.get(current_dept_assignment.DepartmentId)
                staff_dict['DepartmentId'] = department.DepartmentId
                staff_dict['DepartmentName'] = department.DepartmentName
                staff_dict['Position'] = current_dept_assignment.Position
                
                # Filter by department if specified
                if department_id and current_dept_assignment.DepartmentId != department_id:
                    continue
            else:
                staff_dict['DepartmentId'] = None
                staff_dict['DepartmentName'] = None
                staff_dict['Position'] = None
                
                # Skip staff without department if filtering by department
                continue
                
            result.append(staff_dict)
            
        return jsonify({'staff': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/staff/<int:staff_id>', methods=['GET'])
def get_staff(staff_id):
    """Get a specific staff member by ID"""
    try:
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        staff_dict = staff.to_dict()
        current_dept_assignment = StaffDepartment.query.filter_by(
            StaffId=staff.StaffId, 
            Current=True
        ).first()
        
        if current_dept_assignment:
            department = Department.query.get(current_dept_assignment.DepartmentId)
            staff_dict['DepartmentId'] = department.DepartmentId
            staff_dict['DepartmentName'] = department.DepartmentName
            staff_dict['Position'] = current_dept_assignment.Position
        else:
            staff_dict['DepartmentId'] = None
            staff_dict['DepartmentName'] = None
            staff_dict['Position'] = None
            
        return jsonify({'staff': staff_dict})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/staff', methods=['POST'])
def create_staff():
    """Create a new staff member"""
    try:
        data = request.json
        
        # Check if staff already exists
        if Staff.query.get(data.get('StaffId')):
            return jsonify({'error': 'Staff ID already exists'}), 400
            
        # Create new staff
        new_staff = Staff(
            StaffId=data.get('StaffId'),
            StaffName=data.get('StaffName'),
            StaffRole=data.get('StaffRole'),
            StaffAvailable=data.get('StaffAvailable', True)
        )
        
        db.session.add(new_staff)
        
        # If department provided, create department assignment
        department_id = data.get('DepartmentId')
        if department_id:
            # First check if department exists
            dept = Department.query.get(department_id)
            if not dept:
                return jsonify({'error': 'Department not found'}), 400
                
            # Create department assignment
            dept_assignment = StaffDepartment(
                StaffId=new_staff.StaffId,
                DepartmentId=department_id,
                Current=True,
                Position=data.get('Position')
            )
            db.session.add(dept_assignment)
            
        db.session.commit()
        return jsonify({'message': 'Staff created successfully', 'staffId': new_staff.StaffId}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update an existing staff member"""
    try:
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        data = request.json
        
        # Update staff details
        if 'StaffName' in data:
            staff.StaffName = data['StaffName']
        if 'StaffRole' in data:
            staff.StaffRole = data['StaffRole']
        if 'StaffAvailable' in data:
            staff.StaffAvailable = data['StaffAvailable']
            
        # Handle department assignment
        if 'DepartmentId' in data:
            # Get current assignment if any
            current_assignment = StaffDepartment.query.filter_by(
                StaffId=staff_id,
                Current=True
            ).first()
            
            # If department changed or no current assignment
            if not current_assignment or current_assignment.DepartmentId != data['DepartmentId']:
                # Set current assignment to inactive if exists
                if current_assignment:
                    current_assignment.Current = False
                    
                # Create new assignment
                new_assignment = StaffDepartment(
                    StaffId=staff_id,
                    DepartmentId=data['DepartmentId'],
                    Current=True,
                    Position=data.get('Position', current_assignment.Position if current_assignment else None)
                )
                db.session.add(new_assignment)
            # If position changed but department is the same
            elif current_assignment and 'Position' in data and current_assignment.Position != data['Position']:
                current_assignment.Position = data['Position']
                
        db.session.commit()
        return jsonify({'message': 'Staff updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Delete a staff member"""
    try:
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        # Delete all department assignments
        StaffDepartment.query.filter_by(StaffId=staff_id).delete()
        
        # Delete the staff
        db.session.delete(staff)
        db.session.commit()
        
        return jsonify({'message': 'Staff deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/staff/<int:staff_id>/history', methods=['GET'])
def get_staff_history(staff_id):
    """Get department assignment history for a staff member"""
    try:
        # Check if staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        # Get all department assignments for this staff
        assignments = StaffDepartment.query.filter_by(StaffId=staff_id).all()
        
        result = []
        for assignment in assignments:
            department = Department.query.get(assignment.DepartmentId)
            result.append({
                'StaffId': assignment.StaffId,
                'DepartmentId': assignment.DepartmentId,
                'DepartmentName': department.DepartmentName,
                'Current': assignment.Current,
                'Position': assignment.Position
            })
            
        return jsonify({'history': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get all departments for dropdown menus"""
    try:
        departments = Department.query.all()
        result = [dept.to_dict() for dept in departments]
        return jsonify({'departments': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@staff_bp.route('/staff/<int:staff_id>/department', methods=['POST'])
def assign_department(staff_id):
    """Assign staff to a department"""
    try:
        # Check if staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        data = request.json
        department_id = data.get('DepartmentId')
        position = data.get('Position')
        
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404
            
        # Get current assignment if any
        current_assignment = StaffDepartment.query.filter_by(
            StaffId=staff_id,
            Current=True
        ).first()
        
        # If there's a current assignment
        if current_assignment:
            # If department is the same, just update position if provided
            if current_assignment.DepartmentId == department_id:
                if position:
                    current_assignment.Position = position
                    
                db.session.commit()
                return jsonify({
                    'message': 'Department assignment updated successfully',
                    'departmentId': department_id,
                    'departmentName': department.DepartmentName
                })
            else:
                # Set current assignment to inactive
                current_assignment.Current = False
        
        # Create new department assignment
        new_assignment = StaffDepartment(
            StaffId=staff_id,
            DepartmentId=department_id,
            Position=position,
            Current=True
        )
        
        db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Department assignment updated successfully',
            'departmentId': department_id,
            'departmentName': department.DepartmentName
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

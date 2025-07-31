"""
Patient Assignment Management for Hospital Information System
Extension to authorization.py
"""

from enum import Enum
from datetime import datetime, timedelta

class AssignmentType(Enum):
    PRIMARY = "primary"          # Main responsible staff
    SECONDARY = "secondary"      # Assisting staff
    CONSULTANT = "consultant"    # Consulting specialist
    EMERGENCY = "emergency"      # Emergency temporary assignment

class AssignmentAuthority:
    """Manages who can assign staff to patients"""
    
    @staticmethod
    def can_assign_staff(assigner_staff, target_staff, patient_id, assignment_type=AssignmentType.PRIMARY):
        """
        Check if assigner_staff can assign target_staff to patient_id
        
        Args:
            assigner_staff: Staff making the assignment
            target_staff: Staff being assigned
            patient_id: Patient being assigned to
            assignment_type: Type of assignment
        
        Returns:
            bool: True if assignment is allowed
        """
        
        # Basic checks
        if not assigner_staff or not target_staff:
            return False
            
        # Get roles and departments
        assigner_role = StaffRole(assigner_staff['role'])
        target_role = StaffRole(target_staff['role'])
        assigner_dept = assigner_staff['department_id']
        target_dept = target_staff['department_id']
        
        # Rule 1: Doctors can assign anyone in their department
        if assigner_role == StaffRole.BAC_SI:
            if assigner_dept == target_dept:
                return True
            # Doctors can assign across departments for emergency
            if assignment_type == AssignmentType.EMERGENCY:
                return True
                
        # Rule 2: Head nurses can assign other nurses
        if assigner_role == StaffRole.DIEU_DUONG:
            # Check if assigner is head nurse (would need additional field in database)
            if AssignmentAuthority.is_head_nurse(assigner_staff['staff_id']):
                if target_role == StaffRole.DIEU_DUONG and assigner_dept == target_dept:
                    return True
                    
        # Rule 3: Emergency department special authority
        if assigner_staff['department_type'] == DepartmentType.CAP_CUU.value:
            if assignment_type == AssignmentType.EMERGENCY:
                return True
                
        # Rule 4: Self-assignment removal (staff can remove their own assignments)
        if assigner_staff['staff_id'] == target_staff['staff_id']:
            return True
            
        return False
    
    @staticmethod
    def can_remove_assignment(remover_staff, assignment_record):
        """Check if staff can remove a patient assignment"""
        
        remover_role = StaffRole(remover_staff['role'])
        assigned_staff_id = assignment_record['StaffId']
        
        # Doctors can remove any assignment in their department
        if remover_role == StaffRole.BAC_SI:
            return True
            
        # Staff can remove their own assignments
        if remover_staff['staff_id'] == assigned_staff_id:
            return True
            
        # Head nurses can remove nurse assignments
        if remover_role == StaffRole.DIEU_DUONG:
            if AssignmentAuthority.is_head_nurse(remover_staff['staff_id']):
                target_staff = get_staff_by_id(assigned_staff_id)
                if target_staff and target_staff['role'] == StaffRole.DIEU_DUONG.value:
                    return True
                    
        return False
    
    @staticmethod
    def get_assignment_rules(staff_role, department_type):
        """Get assignment rules for a specific role and department"""
        
        rules = {
            'can_assign': [],
            'can_remove': [],
            'assignment_types': [],
            'cross_department': False,
            'max_assignments': None
        }
        
        if staff_role == StaffRole.BAC_SI:
            rules.update({
                'can_assign': ['Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên'],
                'can_remove': ['any'],
                'assignment_types': [AssignmentType.PRIMARY, AssignmentType.SECONDARY, AssignmentType.CONSULTANT, AssignmentType.EMERGENCY],
                'cross_department': department_type == DepartmentType.CAP_CUU.value,
                'max_assignments': None  # No limit for doctors
            })
        elif staff_role == StaffRole.DIEU_DUONG:
            rules.update({
                'can_assign': ['Điều dưỡng'],
                'can_remove': ['own', 'other_nurses'],
                'assignment_types': [AssignmentType.PRIMARY, AssignmentType.SECONDARY],
                'cross_department': False,
                'max_assignments': 10  # Nurses limited to 10 patients
            })
        
        return rules
    
    @staticmethod
    def is_head_nurse(staff_id):
        """Check if nurse has head nurse privileges"""
        # TODO: Implement with database query or additional field
        # This could be a separate table or field in Staff table
        return False  # Placeholder
    
    @staticmethod
    def create_assignment(assigner_staff_id, target_staff_id, patient_id, assignment_type=AssignmentType.PRIMARY, duration_hours=None):
        """Create a new patient assignment"""
        
        assignment_data = {
            'StaffId': target_staff_id,
            'PatientId': patient_id,
            'AssignedBy': assigner_staff_id,
            'AssignmentType': assignment_type.value,
            'AssignedAt': datetime.now(),
            'IsActive': True
        }
        
        # Set expiration for emergency assignments
        if assignment_type == AssignmentType.EMERGENCY:
            if duration_hours:
                assignment_data['ExpiresAt'] = datetime.now() + timedelta(hours=duration_hours)
            else:
                assignment_data['ExpiresAt'] = datetime.now() + timedelta(hours=8)  # Default 8 hours
                
        # TODO: Insert into StaffPatientAssignment table
        return create_assignment_record(assignment_data)
    
    @staticmethod
    def get_patient_assignments(patient_id):
        """Get all active assignments for a patient"""
        # TODO: Query StaffPatientAssignment table
        return get_assignments_by_patient(patient_id)
    
    @staticmethod
    def get_staff_assignments(staff_id):
        """Get all active assignments for a staff member"""
        # TODO: Query StaffPatientAssignment table
        return get_assignments_by_staff(staff_id)

# Flask route examples for assignment management
def assignment_routes_example():
    """Example routes for patient assignment management"""
    
    @app.route('/api/patients/<int:patient_id>/assignments', methods=['POST'])
    @require_auth
    def assign_staff_to_patient(patient_id):
        """Assign staff to patient"""
        data = request.json
        current_staff = AuthorizationService.get_current_staff()
        target_staff_id = data.get('staff_id')
        assignment_type = AssignmentType(data.get('assignment_type', 'primary'))
        
        # Get target staff info
        target_staff = get_staff_by_id(target_staff_id)
        if not target_staff:
            return jsonify({'error': 'Target staff not found'}), 404
        
        # Check assignment authority
        if not AssignmentAuthority.can_assign_staff(current_staff, target_staff, patient_id, assignment_type):
            return jsonify({'error': 'Insufficient authority to make this assignment'}), 403
        
        # Create assignment
        assignment_id = AssignmentAuthority.create_assignment(
            current_staff['staff_id'], 
            target_staff_id, 
            patient_id, 
            assignment_type,
            data.get('duration_hours')
        )
        
        return jsonify({
            'assignment_id': assignment_id,
            'message': f'Staff {target_staff["StaffName"]} assigned to patient {patient_id}'
        })
    
    @app.route('/api/patients/<int:patient_id>/assignments', methods=['GET'])
    @require_auth
    @require_permission('Patient', 'read')
    def get_patient_assignments(patient_id):
        """Get all assignments for a patient"""
        assignments = AssignmentAuthority.get_patient_assignments(patient_id)
        return jsonify({'assignments': assignments})
    
    @app.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
    @require_auth
    def remove_assignment(assignment_id):
        """Remove a patient assignment"""
        current_staff = AuthorizationService.get_current_staff()
        
        # Get assignment record
        assignment = get_assignment_by_id(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404
        
        # Check removal authority
        if not AssignmentAuthority.can_remove_assignment(current_staff, assignment):
            return jsonify({'error': 'Insufficient authority to remove this assignment'}), 403
        
        # Remove assignment
        deactivate_assignment(assignment_id)
        
        return jsonify({'message': 'Assignment removed successfully'})
    
    @app.route('/api/staff/<int:staff_id>/assignments', methods=['GET'])
    @require_auth
    def get_staff_assignments(staff_id):
        """Get all assignments for a staff member"""
        current_staff = AuthorizationService.get_current_staff()
        
        # Staff can view their own assignments, doctors can view any in department
        if (current_staff['staff_id'] != staff_id and 
            current_staff['role'] != StaffRole.BAC_SI.value):
            return jsonify({'error': 'Can only view your own assignments'}), 403
        
        assignments = AssignmentAuthority.get_staff_assignments(staff_id)
        return jsonify({'assignments': assignments})

# Database schema enhancement for assignment management
ASSIGNMENT_SCHEMA_ENHANCEMENT = """
-- Enhanced StaffPatientAssignment table with assignment authority tracking
ALTER TABLE `StaffPatientAssignment` 
ADD COLUMN `AssignedBy` smallint(6) COMMENT 'Staff who made the assignment',
ADD COLUMN `AssignmentType` ENUM('primary', 'secondary', 'consultant', 'emergency') DEFAULT 'primary',
ADD COLUMN `ExpiresAt` datetime DEFAULT NULL COMMENT 'When assignment expires (for emergency)',
ADD COLUMN `AssignmentNote` varchar(255) DEFAULT '' COMMENT 'Notes about assignment',
ADD FOREIGN KEY (AssignedBy) REFERENCES Staff(StaffId);

-- Head nurse designation table
CREATE TABLE `HeadNurse` (
  `StaffId` smallint(6) PRIMARY KEY NOT NULL,
  `DepartmentId` smallint(6) NOT NULL,
  `AppointedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `IsActive` boolean DEFAULT 1,
  FOREIGN KEY (StaffId) REFERENCES Staff(StaffId),
  FOREIGN KEY (DepartmentId) REFERENCES Department(DepartmentId)
);

-- Assignment audit log
CREATE TABLE `AssignmentAuditLog` (
  `LogId` bigint(20) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `AssignmentId` int(10) NOT NULL,
  `Action` ENUM('created', 'modified', 'removed') NOT NULL,
  `PerformedBy` smallint(6) NOT NULL,
  `PerformedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `Reason` varchar(255) DEFAULT '',
  FOREIGN KEY (PerformedBy) REFERENCES Staff(StaffId)
);
"""

# Utility functions (to be implemented with actual database)
def get_staff_by_id(staff_id):
    """Get staff information by ID"""
    pass

def create_assignment_record(assignment_data):
    """Create assignment record in database"""
    pass

def get_assignments_by_patient(patient_id):
    """Get assignments for a patient"""
    pass

def get_assignments_by_staff(staff_id):
    """Get assignments for a staff member"""
    pass

def get_assignment_by_id(assignment_id):
    """Get assignment by ID"""
    pass

def deactivate_assignment(assignment_id):
    """Deactivate an assignment"""
    pass

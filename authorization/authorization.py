"""
Authorization Framework for Hospital Information System
"""
from functools import wraps
from flask import session, request, jsonify, abort
from enum import Enum

class StaffRole(Enum):
    BAC_SI = "Bác sĩ"
    DIEU_DUONG = "Điều dưỡng" 
    KY_THUAT_VIEN = "Kỹ thuật viên"
    KHAC = "Khác"

class DepartmentType(Enum):
    NOI_TRU = "Nội trú"
    CAP_CUU = "Cấp cứu"
    PHONG_KHAM = "Phòng khám"

class Permission(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"

# Authorization Rules
ROLE_PERMISSIONS = {
    StaffRole.BAC_SI: {
        'Patient': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE],
        'Visit': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE, Permission.APPROVE],
        'VisitDrug': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE],
        'VisitTest': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.APPROVE],
        'VisitProc': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.APPROVE],
        'Template': [Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.DELETE]
    },
    StaffRole.DIEU_DUONG: {
        'Patient': [Permission.READ, Permission.UPDATE],
        'Visit': [Permission.CREATE, Permission.READ, Permission.UPDATE],
        'VisitDrug': [Permission.READ, Permission.UPDATE],  # Administer only
        'VisitTest': [Permission.READ, Permission.UPDATE],  # Execute tests
        'VisitProc': [Permission.READ, Permission.UPDATE],  # Assist procedures
        'Template': [Permission.READ]
    },
    StaffRole.KY_THUAT_VIEN: {
        'Patient': [Permission.READ],
        'Visit': [Permission.READ],
        'VisitTest': [Permission.READ, Permission.UPDATE],  # Execute tests
        'VisitProc': [Permission.READ, Permission.UPDATE],  # Execute procedures
        'Template': [Permission.READ]
    },
    StaffRole.KHAC: {
        'Patient': [Permission.READ],
        'Visit': [Permission.READ]
    }
}

# Department-specific permissions
DEPARTMENT_SPECIAL_PERMISSIONS = {
    DepartmentType.CAP_CUU: {
        'cross_department_access': True,
        'emergency_override': True,
        'urgent_procedures': True
    },
    DepartmentType.NOI_TRU: {
        'long_term_planning': True,
        'full_history_access': True
    },
    DepartmentType.PHONG_KHAM: {
        'outpatient_only': True,
        'referral_system': True
    }
}

class AuthorizationService:
    @staticmethod
    def get_current_staff():
        """Get current logged-in staff from session"""
        if 'staff_id' not in session:
            return None
        # In real implementation, fetch from database
        return {
            'staff_id': session['staff_id'],
            'role': session.get('staff_role'),
            'department_id': session.get('department_id'),
            'department_type': session.get('department_type')
        }
    
    @staticmethod
    def has_permission(resource_type, action, target_patient_id=None, target_department_id=None):
        """Check if current staff has permission for specific action"""
        staff = AuthorizationService.get_current_staff()
        if not staff:
            return False
            
        role = StaffRole(staff['role'])
        
        # Check basic role permissions
        if resource_type not in ROLE_PERMISSIONS[role]:
            return False
            
        if Permission(action) not in ROLE_PERMISSIONS[role][resource_type]:
            return False
        
        # Department-based checks
        if target_department_id and target_department_id != staff['department_id']:
            # Check if emergency department has cross-department access
            if staff['department_type'] == DepartmentType.CAP_CUU.value:
                if DEPARTMENT_SPECIAL_PERMISSIONS[DepartmentType.CAP_CUU]['cross_department_access']:
                    return True
            return False
        
        # Patient assignment checks (for non-doctors)
        if target_patient_id and role != StaffRole.BAC_SI:
            # In real implementation, check StaffPatientAssignment table
            # For now, assume điều dưỡng can access assigned patients
            if role == StaffRole.DIEU_DUONG:
                return AuthorizationService.is_patient_assigned(staff['staff_id'], target_patient_id)
        
        return True
    
    @staticmethod
    def is_patient_assigned(staff_id, patient_id):
        """Check if staff is assigned to patient (implement with database query)"""
        # TODO: Query StaffPatientAssignment table
        return True  # Placeholder
    
    @staticmethod
    def can_access_department(target_department_id):
        """Check if staff can access specific department"""
        staff = AuthorizationService.get_current_staff()
        if not staff:
            return False
            
        # Own department access
        if staff['department_id'] == target_department_id:
            return True
            
        # Emergency department special access
        if staff['department_type'] == DepartmentType.CAP_CUU.value:
            return DEPARTMENT_SPECIAL_PERMISSIONS[DepartmentType.CAP_CUU]['cross_department_access']
            
        return False

# Decorators for Flask routes
def require_auth(f):
    """Require valid authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_permission(resource_type, action):
    """Require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract target IDs from request
            target_patient_id = request.json.get('PatientId') if request.json else None
            target_department_id = request.json.get('DepartmentId') if request.json else None
            
            if not AuthorizationService.has_permission(resource_type, action, target_patient_id, target_department_id):
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(*allowed_roles):
    """Require specific staff role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            staff = AuthorizationService.get_current_staff()
            if not staff or staff['role'] not in [role.value for role in allowed_roles]:
                return jsonify({'error': 'Insufficient role permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_department_access(f):
    """Require access to target department"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        target_department_id = request.json.get('DepartmentId') if request.json else None
        if target_department_id and not AuthorizationService.can_access_department(target_department_id):
            return jsonify({'error': 'Department access denied'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Example usage in Flask routes:
"""
@app.route('/api/visit', methods=['POST'])
@require_auth
@require_permission('Visit', 'create')
@require_department_access
def create_visit():
    # Only authenticated staff with visit creation permission
    # and department access can create visits
    pass

@app.route('/api/drug/prescribe', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI)
def prescribe_drug():
    # Only doctors can prescribe drugs
    pass

@app.route('/api/test/execute', methods=['PUT'])
@require_auth
@require_permission('VisitTest', 'update')
def execute_test():
    # Doctors, nurses, and technicians can execute tests
    pass
"""

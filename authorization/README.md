# Authorization Framework for Hospital Information System

This folder contains all authorization-related files for the Hospital Information System (HIS).

## Files Overview

### 📚 Documentation
- **`AUTHORIZATION_GUIDE.md`** - Complete authorization framework documentation
  - Detailed authorization flow and rules
  - Role-based permissions matrix
  - Department access control
  - Patient assignment authority
  - Real-world examples and scenarios
  - Implementation guidelines and testing

- **`AUTHORIZATION_QUICK_REFERENCE.md`** - Quick reference guide
  - Permissions matrix table
  - Common decorator patterns
  - Error codes and troubleshooting
  - API examples

### 🔧 Implementation Files
- **`authorization.py`** - Main authorization framework
  - Role and permission definitions
  - AuthorizationService class
  - Flask decorators (require_auth, require_role, require_permission)
  - Department access control logic

- **`patient_assignment_authority.py`** - Patient assignment management
  - AssignmentAuthority class
  - Assignment types and rules
  - Flask routes for assignment operations
  - Assignment audit logging

- **`flask_routes_example.py`** - Example Flask route implementations
  - Complete route examples with authorization
  - Authentication and permission checking
  - Error handling patterns
  - Best practices demonstration

### 🗄️ Database Files
- **`authorization_enhancement.sql`** - Optional database enhancements
  - User authentication table
  - Permission definitions
  - Role-permission mapping
  - Patient assignment tracking
  - Audit logging tables

## Authorization Framework Summary

### 🔐 Security Layers
1. **Authentication** - Valid staff login required
2. **Role-Based Access** - Actions based on staff role (Bác sĩ, Điều dưỡng, Kỹ thuật viên, Khác)
3. **Department Boundaries** - Access limited to assigned department (except emergency)
4. **Patient Assignment** - Nurses limited to assigned patients

### 👥 Role Hierarchy
```
Bác sĩ (Doctor) → Full department access, can prescribe/approve
    ↓
Điều dưỡng (Nurse) → Assigned patients, can administer/assist
    ↓  
Kỹ thuật viên (Technician) → Test/procedure execution only
    ↓
Khác (Other) → Read-only access
```

### 🏥 Department Types
- **Nội trú** (Inpatient) - Standard department boundaries
- **Cấp cứu** (Emergency) - Cross-department access allowed
- **Phòng khám** (Outpatient) - Limited outpatient procedures

### 🎯 Key Features
- ✅ Vietnamese medical terminology support
- ✅ Hospital hierarchy compliance
- ✅ Emergency override capabilities
- ✅ Patient assignment management
- ✅ Audit logging and security tracking
- ✅ Flask integration with decorators

## Quick Start

### 1. Basic Authorization Check
```python
from authorization.authorization import require_auth, require_role, StaffRole

@app.route('/api/prescribe')
@require_auth
@require_role(StaffRole.BAC_SI)  # Doctors only
def prescribe_drug():
    # Implementation here
```

### 2. Department Access Control
```python
@require_auth
@require_department_access
def access_patient():
    # Automatically checks department boundaries
```

### 3. Patient Assignment
```python
from authorization.patient_assignment_authority import AssignmentAuthority

# Check if staff can assign another staff to patient
can_assign = AssignmentAuthority.can_assign_staff(
    assigner_staff, target_staff, patient_id
)
```

## Integration with Main Application

### Import Authorization Framework
```python
# In your main Flask app
from authorization.authorization import (
    require_auth, require_role, require_permission,
    require_department_access, AuthorizationService
)
from authorization.patient_assignment_authority import AssignmentAuthority
```

### Database Setup
1. Execute core schema: `../exam.sql`
2. Optional enhancements: `authorization_enhancement.sql`
3. Configure staff roles and departments

### Configuration
- Set session secret key
- Configure department access rules
- Set up audit logging
- Define emergency override policies

## Security Considerations

### ⚠️ Important Security Notes
- Always validate session state
- Check staff availability (`StaffAvailable = 1`)
- Log all authorization decisions
- Rotate session secrets regularly
- Monitor failed access attempts

### 🔍 Testing Requirements
- Unit tests for each role's permissions
- Department boundary testing
- Patient assignment validation
- Emergency override scenarios
- Security penetration testing

## Related Files (Outside This Folder)
- `../exam.sql` - Core database schema with Staff, Department, Patient tables
- `../his.py` - Main Flask application entry point
- `../.vscode/prompts/` - AI assistance prompts for development

---

**Framework Version**: 1.0  
**Last Updated**: July 31, 2025  
**Compatibility**: Flask, MySQL/MariaDB, Python 3.7+  
**Status**: Ready for Implementation  

For detailed implementation guidance, see `AUTHORIZATION_GUIDE.md`  
For quick reference during development, see `AUTHORIZATION_QUICK_REFERENCE.md`

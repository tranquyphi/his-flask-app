# HIS Authorization Quick Reference

## Role Permissions Matrix

| Action | Bác sĩ | Điều dưỡng | Kỹ thuật viên | Khác |
|--------|---------|-------------|---------------|------|
| **Patient Management** |
| Create Patient | ✅ | ✅ | ❌ | ❌ |
| Read Patient | ✅ | ✅ (assigned) | ✅ (basic) | ✅ (basic) |
| Update Patient | ✅ | ✅ (assigned) | ❌ | ❌ |
| Delete Patient | ✅ | ❌ | ❌ | ❌ |
| **Visit Management** |
| Create Visit | ✅ | ✅ | ❌ | ❌ |
| Read Visit | ✅ | ✅ | ✅ | ✅ |
| Update Visit | ✅ | ✅ (own) | ❌ | ❌ |
| Delete Visit | ✅ | ❌ | ❌ | ❌ |
| **Drug Management** |
| Prescribe Drug | ✅ | ❌ | ❌ | ❌ |
| Administer Drug | ✅ | ✅ | ❌ | ❌ |
| View Prescriptions | ✅ | ✅ | ❌ | ❌ |
| **Test Management** |
| Order Test | ✅ | ❌ | ❌ | ❌ |
| Execute Test | ✅ | ✅ | ✅ | ❌ |
| Record Results | ✅ | ✅ | ✅ | ❌ |
| Approve Results | ✅ | ❌ | ❌ | ❌ |
| **Procedure Management** |
| Order Procedure | ✅ | ❌ | ❌ | ❌ |
| Perform Procedure | ✅ | ✅ (assist) | ✅ | ❌ |
| Approve Procedure | ✅ | ❌ | ❌ | ❌ |
| **Template Management** |
| Create Template | ✅ | ❌ | ❌ | ❌ |
| Use Template | ✅ | ✅ | ✅ | ❌ |
| Modify Template | ✅ | ❌ | ❌ | ❌ |
| **Patient Assignment Management** |
| Assign Staff to Patient | ✅ | ✅ (nurses only) | ❌ | ❌ |
| Remove Staff Assignment | ✅ | ✅ (own assignments) | ❌ | ❌ |
| View Patient Assignments | ✅ | ✅ | ✅ (limited) | ❌ |
| Override Assignments | ✅ | ❌ | ❌ | ❌ |

## Department Access Rules

### Standard Access
- **Own Department**: Full access according to role
- **Other Departments**: Access denied (except emergency)

### Emergency Department Special Rules
- **Cấp cứu staff**: Can access patients from ANY department
- **Emergency override**: Can perform urgent procedures cross-department
- **Cross-department visits**: Allowed for emergency situations

## Common Authorization Patterns

### Flask Route Decorators
```python
# Basic authentication required
@require_auth

# Role-based access
@require_role(StaffRole.BAC_SI)                    # Doctors only
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG)  # Doctors and nurses

# Permission-based access
@require_permission('Drug', 'create')              # Can prescribe drugs
@require_permission('Test', 'update')              # Can update tests

# Department access required
@require_department_access                         # Must have department access
```

### Example Route Combinations
```python
# Drug prescription - doctors only, same department
@require_auth
@require_role(StaffRole.BAC_SI)
@require_department_access

# Test execution - medical staff, same department
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG, StaffRole.KY_THUAT_VIEN)
@require_permission('Test', 'update')

# Emergency patient access - emergency staff, any department
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG)
# Special logic for emergency department in route handler
```

## Error Codes & Messages

| Code | Message | Meaning |
|------|---------|---------|
| 401 | Authentication required | Not logged in |
| 403 | Insufficient permissions | Role doesn't allow action |
| 403 | Department access denied | Different department |
| 403 | Patient not assigned | Nurse accessing unassigned patient |
| 403 | Emergency access requires emergency department | Non-emergency trying emergency access |

## Quick Troubleshooting

### "Permission Denied" Issues
1. Check staff role: `SELECT StaffRole FROM Staff WHERE StaffId = ?`
2. Check department: `SELECT DepartmentId FROM Staff WHERE StaffId = ?`
3. Check patient assignment: `SELECT * FROM StaffPatientAssignment WHERE StaffId = ? AND PatientId = ?`

### "Department Access Denied" Issues
1. Verify target department exists
2. Check if emergency department override should apply
3. Confirm staff department assignment is correct

### "Authentication Required" Issues
1. Check if session exists and is valid
2. Verify staff is active: `SELECT StaffAvailable FROM Staff WHERE StaffId = ?`
3. Check session timeout settings

## Implementation Files Reference

- `AUTHORIZATION_GUIDE.md` - Complete documentation (this file's companion)
- `authorization.py` - Main authorization framework
- `flask_routes_example.py` - Example route implementations  
- `patient_assignment_authority.py` - Patient assignment management
- `authorization_enhancement.sql` - Optional database enhancements
- `exam.sql` - Core database schema

## Patient Assignment Quick Rules

### **Who Can Assign Staff to Patients?**

| Assigner Role | Can Assign | Scope | Special Rules |
|---------------|------------|-------|---------------|
| **Bác sĩ** | Any staff | Same department | Emergency: cross-department |
| **Head Nurse** | Nurses only | Same department | Must be designated head nurse |
| **Emergency Staff** | Any staff | Any department | Time-limited assignments |
| **Regular Staff** | None | Self-removal only | Can remove own assignments |

### **Assignment API Examples**
```python
# Assign nurse to patient (doctor only)
POST /api/patients/123/assignments
{
  "staff_id": 456,
  "assignment_type": "primary"
}

# Remove assignment (doctor or self)
DELETE /api/assignments/789

# View patient assignments
GET /api/patients/123/assignments

# View staff assignments  
GET /api/staff/456/assignments
```

---
**Quick Reference Version**: 1.0  
**For Complete Details**: See AUTHORIZATION_GUIDE.md

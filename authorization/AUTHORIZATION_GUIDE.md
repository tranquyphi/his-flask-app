# Hospital Information System - Authorization Framework Documentation

## Overview
This document describes the complete authorization framework for the Hospital Information System (HIS), which implements **dual-layer security** based on **Staff Role** and **Department** assignments.

## Core Principles

### 1. Dual-Layer Authorization
- **Layer 1**: Role-based permissions (what actions a role can perform)
- **Layer 2**: Department-based access control (where actions can be performed)
- **Layer 3**: Patient assignment (which specific patients can be accessed)

### 2. Medical Hierarchy Respect
The system respects Vietnamese hospital hierarchy:
- **Bác sĩ** (Doctor): Highest level, can prescribe and approve
- **Điều dưỡng** (Nurse): Patient care, can administer treatments
- **Kỹ thuật viên** (Technician): Specialized tasks, test execution
- **Khác** (Other): Limited access, administrative roles

## Authorization Flow

### Step-by-Step Process
```
1. User Login → Session stores: staff_id, role, department_id, department_type
2. Action Request → Check role permissions
3. Department Check → Verify department access
4. Patient Check → Verify patient assignment (if applicable)
5. Grant/Deny → Execute action or return error
```

### Decision Matrix
```
Action Allowed = (Role Permission ✓) AND (Department Access ✓) AND (Patient Assignment ✓)
```

## Role-Based Permissions

### Bác sĩ (Doctor) - Level 4
**Permissions**: create, read, update, delete, approve
**Scope**: Department-wide access

| Resource | Actions |
|----------|---------|
| Patient | Full CRUD + approve |
| Visit | Full CRUD + approve |
| VisitDrug | Prescribe, modify, delete |
| VisitTest | Order, review, approve |
| VisitProc | Order, perform, approve |
| Template | Create, modify, delete |

### Điều dưỡng (Nurse) - Level 3
**Permissions**: read, write, limited_approve
**Scope**: Assigned patients only

| Resource | Actions |
|----------|---------|
| Patient | Read, update basic info |
| Visit | Create, read, update |
| VisitDrug | Administer (not prescribe) |
| VisitTest | Execute, record results |
| VisitProc | Assist, record progress |
| Template | Read only |

### Kỹ thuật viên (Technician) - Level 2
**Permissions**: read, write_tests_procedures
**Scope**: Test and procedure execution only

| Resource | Actions |
|----------|---------|
| Patient | Read basic info |
| Visit | Read only |
| VisitDrug | None |
| VisitTest | Execute, record results |
| VisitProc | Execute, record results |
| Template | Read only |

### Khác (Other) - Level 1
**Permissions**: read
**Scope**: Limited access

| Resource | Actions |
|----------|---------|
| Patient | Read basic info |
| Visit | Read only |
| VisitDrug | None |
| VisitTest | None |
| VisitProc | None |
| Template | None |

## Department-Based Access Control

### Standard Department Rules
- **Default**: Staff can only access their own department
- **Patients**: Must be in the same department as staff
- **Templates**: Department-specific templates only

### Special Department Permissions

#### Cấp cứu (Emergency Department)
```python
SPECIAL_PERMISSIONS = {
    'cross_department_access': True,    # Can access patients from any department
    'emergency_override': True,         # Can override some restrictions
    'urgent_procedures': True          # Can perform urgent procedures
}
```

#### Nội trú (Inpatient Department)
```python
SPECIAL_PERMISSIONS = {
    'long_term_planning': True,        # Extended treatment planning
    'full_history_access': True       # Complete patient history
}
```

#### Phòng khám (Outpatient Department)
```python
SPECIAL_PERMISSIONS = {
    'outpatient_only': True,           # Limited to outpatient procedures
    'referral_system': True           # Can refer to other departments
}
```

## Real-World Authorization Examples

### Example 1: Doctor Prescribing Drug
```
Staff: Dr. Nguyen (Bác sĩ, Nội trú, Department ID: 1)
Action: Prescribe drug for Patient #123 in Nội trú (Department ID: 1)

Authorization Check:
✅ Role Check: Doctors can prescribe drugs
✅ Department Check: Same department (1 = 1)
✅ Patient Check: Patient in same department
Result: GRANTED
```

### Example 2: Nurse Accessing Different Department
```
Staff: Ms. Linh (Điều dưỡng, Phòng khám, Department ID: 2)
Action: Read patient data in Nội trú (Department ID: 1)

Authorization Check:
✅ Role Check: Nurses can read patient data
❌ Department Check: Different department (2 ≠ 1)
❌ Cross-department: Phòng khám has no cross-department access
Result: DENIED
```

### Example 3: Emergency Doctor Cross-Department Access
```
Staff: Dr. Tran (Bác sĩ, Cấp cứu, Department ID: 3)
Action: Access patient in Nội trú (Department ID: 1)

Authorization Check:
✅ Role Check: Doctors can access patient data
❌ Department Check: Different department (3 ≠ 1)
✅ Emergency Override: Cấp cứu has cross_department_access
Result: GRANTED
```

### Example 4: Technician Attempting to Prescribe
```
Staff: Mr. Duc (Kỹ thuật viên, Nội trú, Department ID: 1)
Action: Prescribe drug for patient in same department

Authorization Check:
❌ Role Check: Technicians cannot prescribe drugs
Result: DENIED (fails at role level)
```

## Patient Assignment Authority

### Who Can Assign Staff to Patients

#### **Primary Assignment Authority**

**1. Bác sĩ (Doctors) - Full Assignment Authority**
- ✅ Can assign any staff to any patient in their department
- ✅ Can remove any assignment in their department
- ✅ Can change assignment types (primary, secondary, consultant)
- ✅ Can override existing assignments
- ✅ Emergency department doctors can assign across departments

**2. Department Head/Chief Doctor - Department-wide Authority**
- ✅ Can assign staff across the entire department
- ✅ Can resolve assignment conflicts
- ✅ Can delegate assignment authority

#### **Limited Assignment Authority**

**3. Head Nurse (Senior Điều dưỡng) - Nursing Assignment Authority**
- ✅ Can assign other nurses to patients
- ❌ Cannot assign doctors or technicians
- ✅ Department-specific only
- ✅ Can remove nurse assignments they created

#### **Special Assignment Cases**

**4. Emergency Department (Cấp cứu) - Emergency Assignment Authority**
- ✅ Can temporarily assign any available staff
- ✅ Cross-department emergency assignments
- ⏰ Time-limited assignments (default 8 hours)
- 🚨 Emergency override for critical situations

#### **Self-Management Authority**

**5. All Staff - Self-Assignment Management**
- ✅ Can remove their own patient assignments
- ✅ Can view their own assignment history
- ❌ Cannot assign themselves to new patients

### Assignment Types and Rules

#### **Assignment Types**
- **Primary**: Main responsible staff member
- **Secondary**: Assisting/supporting staff
- **Consultant**: Specialist consultation
- **Emergency**: Temporary emergency assignment

#### **Assignment Rules by Role**

| Role | Can Assign | Can Remove | Assignment Types | Cross-Department | Max Patients |
|------|------------|------------|------------------|------------------|--------------|
| **Bác sĩ** | Any staff in dept | Any in dept | All types | Emergency only | Unlimited |
| **Head Nurse** | Nurses only | Own + nurse assignments | Primary, Secondary | No | Unlimited |
| **Điều dưỡng** | Self-removal only | Own assignments | N/A | No | 10 patients |
| **Others** | None | Own assignments | N/A | No | Limited |

### Real-World Assignment Examples

#### **Example 1: Doctor Assigning Nurse**
```
Dr. Nguyen (Bác sĩ, Nội trú) assigns Nurse Linh (Điều dưỡng, Nội trú) to Patient #123

✅ ALLOWED:
- Assigner: Doctor has full assignment authority
- Target: Nurse in same department
- Patient: In same department
- Result: Assignment created successfully
```

#### **Example 2: Head Nurse Assigning Another Nurse**
```
Head Nurse Mai (Điều dưỡng, Nội trú) assigns Nurse Lan (Điều dưỡng, Nội trú) to Patient #456

✅ ALLOWED:
- Assigner: Head nurse with nursing assignment authority
- Target: Regular nurse in same department
- Patient: In same department
- Result: Assignment created with "assigned_by" = Head Nurse Mai
```

#### **Example 3: Emergency Cross-Department Assignment**
```
Dr. Tran (Bác sĩ, Cấp cứu) assigns Technician Duc (Kỹ thuật viên, Nội trú) for emergency procedure

✅ ALLOWED:
- Assigner: Emergency doctor with cross-department authority
- Target: Technician from different department
- Assignment Type: Emergency (8-hour limit)
- Result: Temporary assignment created with expiration
```

#### **Example 4: Nurse Trying to Assign Doctor**
```
Nurse Linh (Điều dưỡng, Nội trú) tries to assign Dr. Nguyen (Bác sĩ, Nội trú) to Patient #789

❌ DENIED:
- Assigner: Nurse has no authority to assign doctors
- Target: Doctor (higher hierarchy level)
- Result: "Insufficient authority to make this assignment"
```

## Database Schema Implementation

### Core Tables (Required)
From existing `exam.sql`:
- `Staff`: Contains StaffRole and DepartmentId
- `Department`: Contains DepartmentType
- `Patient`: Patient records
- `Visit`: Visit records with staff and department linkage

### Enhancement Tables (Optional)
From `authorization_enhancement.sql`:

#### User Authentication
```sql
CREATE TABLE `User` (
  `UserId` int(10) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) UNIQUE NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `StaffId` smallint(6) NOT NULL,
  `IsActive` boolean DEFAULT 1,
  FOREIGN KEY (StaffId) REFERENCES Staff(StaffId)
);
```

#### Permission System
```sql
CREATE TABLE `Permission` (
  `PermissionId` smallint(6) PRIMARY KEY NOT NULL,
  `PermissionName` varchar(50) NOT NULL,
  `ResourceType` ENUM('Patient', 'Visit', 'Drug', 'Test', 'Proc', 'Template') NOT NULL,
  `Action` ENUM('create', 'read', 'update', 'delete', 'approve') NOT NULL
);

CREATE TABLE `RolePermission` (
  `RoleId` ENUM('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác') NOT NULL,
  `PermissionId` smallint(6) NOT NULL,
  `DepartmentType` ENUM('Nội trú', 'Cấp cứu', 'Phòng khám', 'All') DEFAULT 'All',
  PRIMARY KEY (RoleId, PermissionId, DepartmentType)
);
```

#### Patient Assignment
```sql
CREATE TABLE `StaffPatientAssignment` (
  `StaffId` smallint(6) NOT NULL,
  `PatientId` int(10) NOT NULL,
  `AssignedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `IsActive` boolean DEFAULT 1,
  PRIMARY KEY (StaffId, PatientId)
);
```

## Flask Implementation

### Authorization Decorators
```python
@require_auth                    # Requires valid login
@require_role(StaffRole.BAC_SI)  # Requires specific role
@require_permission('Drug', 'create')  # Requires specific permission
@require_department_access       # Requires department access
```

### Example Route Implementation
```python
@app.route('/api/visits/<int:visit_id>/drugs', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI)  # Only doctors can prescribe
@require_department_access       # Must have department access
def prescribe_drug(visit_id):
    """Prescribe drug - doctors only in same department"""
    # Implementation here
```

## Security Features

### 1. Session Management
- Staff credentials stored in secure session
- Automatic session timeout
- Role and department cached for performance

### 2. Cross-Department Access Control
- Emergency department special privileges
- Audit logging for cross-department access
- Temporary access for emergency situations

### 3. Patient Assignment System
- Nurses access only assigned patients
- Dynamic assignment updates
- Assignment history tracking

### 4. Audit Logging
- All authorization decisions logged
- Failed access attempts tracked
- Department access violations flagged

## Configuration Options

### Role Hierarchy Levels
```python
ROLE_LEVELS = {
    'Bác sĩ': 4,        # Highest authority
    'Điều dưỡng': 3,    # Patient care authority
    'Kỹ thuật viên': 2, # Technical authority
    'Khác': 1           # Basic access
}
```

### Department Access Matrix
```python
DEPARTMENT_ACCESS = {
    'Cấp cứu': ['Nội trú', 'Phòng khám', 'Cấp cứu'],  # Can access all
    'Nội trú': ['Nội trú'],                            # Own department only
    'Phòng khám': ['Phòng khám']                       # Own department only
}
```

## Implementation Phases

### Phase 1: Basic Role Authorization
- Implement role-based decorators
- Basic permission checking
- Session management

### Phase 2: Department Boundaries
- Department access control
- Cross-department rules
- Emergency overrides

### Phase 3: Patient Assignment
- Nurse-patient assignments
- Fine-grained access control
- Assignment management UI

### Phase 4: Advanced Features
- Audit logging
- Temporary access grants
- Advanced reporting

## Testing Scenarios

### Unit Tests Required
1. **Role Permission Tests**
   - Each role's allowed actions
   - Forbidden actions return 403
   - Role hierarchy respect

2. **Department Boundary Tests**
   - Same department access allowed
   - Cross-department access denied
   - Emergency override working

3. **Patient Assignment Tests**
   - Nurse accessing assigned patient
   - Nurse denied unassigned patient
   - Doctor accessing any patient in department

4. **Edge Cases**
   - Inactive staff denied access
   - Missing session handling
   - Invalid department IDs

### Integration Tests Required
1. **End-to-End Workflows**
   - Complete visit creation process
   - Drug prescription to administration
   - Test ordering to result recording

2. **Security Penetration Tests**
   - Privilege escalation attempts
   - Session hijacking protection
   - SQL injection prevention

## Troubleshooting Guide

### Common Issues

#### "Insufficient permissions" Error
1. Check staff role in database
2. Verify department assignment
3. Confirm patient assignment (for nurses)
4. Check session validity

#### Cross-Department Access Denied
1. Verify department type in database
2. Check if emergency override should apply
3. Confirm target department exists
4. Review special permission settings

#### Template Access Issues
1. Confirm template belongs to staff's department
2. Check role permissions for template operations
3. Verify template is active/available

## File References

### Implementation Files
- `authorization.py`: Main authorization framework
- `flask_routes_example.py`: Example route implementations
- `authorization_enhancement.sql`: Optional database enhancements
- `exam.sql`: Core database schema

### Key Functions
- `AuthorizationService.has_permission()`: Main permission checker
- `require_auth`: Authentication decorator
- `require_role()`: Role-based decorator
- `require_department_access`: Department boundary decorator

## Maintenance Notes

### Regular Tasks
- Review role permissions quarterly
- Update department access rules as needed
- Monitor failed authorization attempts
- Clean up inactive patient assignments

### Security Updates
- Rotate session secrets regularly
- Update password hashing algorithms
- Review and update audit logs
- Test authorization boundaries

---

**Document Version**: 1.0  
**Last Updated**: July 31, 2025  
**Author**: GitHub Copilot  
**Review Status**: Ready for Implementation

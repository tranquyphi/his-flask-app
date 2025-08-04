"""
How to Add Authorization Later - Migration Guide
From his_testing_no_auth.py to his_with_auth.py
"""

# ==========================================
# STEP 1: Import Authorization Framework
# ==========================================

# Add these imports when ready for authorization
from authorization.authorization import (
    require_auth, require_role, require_permission,
    require_department_access, AuthorizationService, StaffRole
)

# ==========================================
# STEP 2: Add Decorators to Existing Routes
# ==========================================

# BEFORE (Phase 1 - No Auth):
@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.json
    patient_id = create_patient_record(data)
    return jsonify({'patient_id': patient_id})

# AFTER (Phase 2 - With Auth):
@app.route('/api/patients', methods=['POST'])
@require_auth  # ← Add authentication requirement
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG)  # ← Add role requirement
@require_department_access  # ← Add department boundary check
def create_patient():
    data = request.json
    # Remove hardcoded values, get from session
    current_staff = AuthorizationService.get_current_staff()
    data['CreatedBy'] = current_staff['staff_id']
    data['DepartmentId'] = current_staff['department_id']
    
    patient_id = create_patient_record(data)
    return jsonify({'patient_id': patient_id})

# ==========================================
# STEP 3: Replace Hardcoded Values with Session Data
# ==========================================

# BEFORE (Phase 1):
def create_visit():
    data = request.json
    data['StaffId'] = 1  # Hardcoded for testing
    data['DepartmentId'] = 1  # Hardcoded for testing
    visit_id = create_visit_record(data)
    return jsonify({'visit_id': visit_id})

# AFTER (Phase 2):
@require_auth
@require_permission('Visit', 'create')
def create_visit():
    data = request.json
    # Get from authenticated session
    current_staff = AuthorizationService.get_current_staff()
    data['StaffId'] = current_staff['staff_id']
    data['DepartmentId'] = current_staff['department_id']
    
    visit_id = create_visit_record(data)
    return jsonify({'visit_id': visit_id})

# ==========================================
# STEP 4: Add Login System
# ==========================================

# Replace testing routes with real authentication
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Authenticate against database
    staff = authenticate_staff(username, password)
    if staff:
        session['staff_id'] = staff['StaffId']
        session['staff_role'] = staff['StaffRole']
        session['department_id'] = staff['DepartmentId']
        session['department_type'] = staff['DepartmentType']
        
        return jsonify({'message': 'Login successful', 'staff': staff})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# ==========================================
# STEP 5: Migration Checklist
# ==========================================

"""
Authorization Migration Checklist:

□ 1. Import authorization framework
□ 2. Add @require_auth to all protected routes
□ 3. Add @require_role() based on business rules
□ 4. Add @require_permission() for specific actions
□ 5. Add @require_department_access where needed
□ 6. Replace hardcoded staff IDs with session data
□ 7. Replace hardcoded department IDs with session data
□ 8. Add real login/logout endpoints
□ 9. Remove testing/simulation endpoints
□ 10. Add error handling for authorization failures
□ 11. Test each role's access patterns
□ 12. Test department boundary enforcement
"""

# ==========================================
# STEP 6: Testing Both Phases
# ==========================================

"""
Phase 1 Testing (No Auth):
- Test all CRUD operations
- Validate database relationships
- Test business logic
- Test API responses
- Use simulation endpoints for different roles

Phase 2 Testing (With Auth):
- Test login/logout
- Test role-based access
- Test department boundaries
- Test unauthorized access (should fail)
- Test patient assignment rules
"""

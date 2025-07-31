"""
Example Flask routes with authorization implementation
"""
from flask import Flask, request, jsonify, session
from authorization import (
    require_auth, require_permission, require_role, require_department_access,
    StaffRole, AuthorizationService
)

app = Flask(__name__)

# Authentication
@app.route('/api/login', methods=['POST'])
def login():
    """Staff login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # TODO: Validate credentials against database
    # For demo, mock authentication
    staff = authenticate_staff(username, password)
    if staff:
        session['staff_id'] = staff['StaffId']
        session['staff_role'] = staff['StaffRole']
        session['department_id'] = staff['DepartmentId']
        session['department_type'] = staff['DepartmentType']
        
        return jsonify({
            'message': 'Login successful',
            'staff': {
                'id': staff['StaffId'],
                'name': staff['StaffName'],
                'role': staff['StaffRole'],
                'department': staff['DepartmentType']
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Patient Management
@app.route('/api/patients', methods=['GET'])
@require_auth
@require_permission('Patient', 'read')
def get_patients():
    """Get patients based on role and department"""
    staff = AuthorizationService.get_current_staff()
    
    if staff['role'] == StaffRole.BAC_SI.value:
        # Doctors can see all patients in their department
        patients = get_patients_by_department(staff['department_id'])
    elif staff['role'] == StaffRole.DIEU_DUONG.value:
        # Nurses see only assigned patients
        patients = get_assigned_patients(staff['staff_id'])
    else:
        # Technicians and others see limited patient info
        patients = get_limited_patient_info(staff['department_id'])
    
    return jsonify({'patients': patients})

@app.route('/api/patients', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG)
@require_department_access
def create_patient():
    """Create new patient - doctors and nurses only"""
    data = request.json
    
    # Validate department access
    target_department = data.get('DepartmentId')
    if not AuthorizationService.can_access_department(target_department):
        return jsonify({'error': 'Cannot create patient in this department'}), 403
    
    # Create patient logic
    patient_id = create_patient_record(data)
    return jsonify({'patient_id': patient_id, 'message': 'Patient created successfully'})

# Visit Management
@app.route('/api/visits', methods=['POST'])
@require_auth
@require_permission('Visit', 'create')
@require_department_access
def create_visit():
    """Create new visit"""
    data = request.json
    staff = AuthorizationService.get_current_staff()
    
    # Auto-assign current staff as visit staff
    data['StaffId'] = staff['staff_id']
    data['DepartmentId'] = staff['department_id']
    
    visit_id = create_visit_record(data)
    return jsonify({'visit_id': visit_id, 'message': 'Visit created successfully'})

@app.route('/api/visits/<int:visit_id>', methods=['PUT'])
@require_auth
@require_permission('Visit', 'update')
def update_visit(visit_id):
    """Update visit - check ownership or doctor override"""
    data = request.json
    staff = AuthorizationService.get_current_staff()
    
    # Get visit info to check ownership
    visit = get_visit_by_id(visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    # Check if staff can modify this visit
    if staff['role'] != StaffRole.BAC_SI.value:
        # Non-doctors can only modify their own visits
        if visit['StaffId'] != staff['staff_id']:
            return jsonify({'error': 'Can only modify your own visits'}), 403
    
    update_visit_record(visit_id, data)
    return jsonify({'message': 'Visit updated successfully'})

# Drug Prescription
@app.route('/api/visits/<int:visit_id>/drugs', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI)  # Only doctors can prescribe
def prescribe_drug(visit_id):
    """Prescribe drug - doctors only"""
    data = request.json
    
    # Verify visit belongs to same department
    visit = get_visit_by_id(visit_id)
    if not AuthorizationService.can_access_department(visit['DepartmentId']):
        return jsonify({'error': 'Cannot prescribe for this department'}), 403
    
    prescription_id = create_drug_prescription(visit_id, data)
    return jsonify({'prescription_id': prescription_id, 'message': 'Drug prescribed successfully'})

@app.route('/api/visits/<int:visit_id>/drugs/<drug_id>/administer', methods=['PUT'])
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG)  # Doctors and nurses
def administer_drug(visit_id, drug_id):
    """Administer drug - doctors and nurses"""
    data = request.json
    staff = AuthorizationService.get_current_staff()
    
    # Record who administered the drug
    data['AdministerStaffId'] = staff['staff_id']
    data['AdministerTime'] = datetime.now()
    
    update_drug_administration(visit_id, drug_id, data)
    return jsonify({'message': 'Drug administration recorded'})

# Test Management
@app.route('/api/visits/<int:visit_id>/tests', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI)  # Only doctors can order tests
def order_test(visit_id):
    """Order test - doctors only"""
    data = request.json
    
    test_order_id = create_test_order(visit_id, data)
    return jsonify({'test_order_id': test_order_id, 'message': 'Test ordered successfully'})

@app.route('/api/visits/<int:visit_id>/tests/<test_id>/execute', methods=['PUT'])
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG, StaffRole.KY_THUAT_VIEN)
def execute_test(visit_id, test_id):
    """Execute test - doctors, nurses, technicians"""
    data = request.json
    staff = AuthorizationService.get_current_staff()
    
    # Record who executed the test
    data['TestStaffId'] = staff['staff_id']
    data['TestTime'] = datetime.now()
    data['TestStatus'] = 'In progress'
    
    update_test_execution(visit_id, test_id, data)
    return jsonify({'message': 'Test execution recorded'})

@app.route('/api/visits/<int:visit_id>/tests/<test_id>/result', methods=['PUT'])
@require_auth
@require_role(StaffRole.BAC_SI, StaffRole.KY_THUAT_VIEN)  # Doctors and technicians
def update_test_result(visit_id, test_id):
    """Update test result - doctors and technicians"""
    data = request.json
    
    data['TestStatus'] = 'Completed'
    update_test_result_record(visit_id, test_id, data)
    return jsonify({'message': 'Test result updated'})

# Emergency Department Special Access
@app.route('/api/emergency/patient/<int:patient_id>', methods=['GET'])
@require_auth
@require_department_access
def emergency_patient_access(patient_id):
    """Emergency access to any patient - emergency department only"""
    staff = AuthorizationService.get_current_staff()
    
    # Check if staff is in emergency department
    if staff['department_type'] != 'Cấp cứu':
        return jsonify({'error': 'Emergency access requires emergency department assignment'}), 403
    
    # Emergency staff can access any patient
    patient = get_patient_full_info(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    return jsonify({'patient': patient, 'access_type': 'emergency'})

# Template Management
@app.route('/api/templates', methods=['POST'])
@require_auth
@require_role(StaffRole.BAC_SI)  # Only doctors can create templates
@require_permission('Template', 'create')
def create_template():
    """Create template - doctors only"""
    data = request.json
    staff = AuthorizationService.get_current_staff()
    
    # Templates are department-specific
    data['DepartmentId'] = staff['department_id']
    
    template_id = create_template_record(data)
    return jsonify({'template_id': template_id, 'message': 'Template created successfully'})

# Utility functions (implement with your database layer)
def authenticate_staff(username, password):
    """Authenticate staff credentials"""
    # TODO: Implement actual authentication
    pass

def get_patients_by_department(department_id):
    """Get all patients in department"""
    pass

def get_assigned_patients(staff_id):
    """Get patients assigned to specific staff"""
    pass

def create_patient_record(data):
    """Create new patient record"""
    pass

def create_visit_record(data):
    """Create new visit record"""
    pass

# Add more utility functions as needed...

if __name__ == '__main__':
    app.secret_key = 'your-secret-key'
    app.run(debug=True)

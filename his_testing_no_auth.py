"""
Flask Application Structure - Phase 1 (No Authorization)
Basic CRUD operations for testing business logic
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# ==========================================
# PHASE 1: Basic Routes (No Authorization)
# ==========================================

# Patient Management
@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients - no auth check for now"""
    # TODO: Add @require_auth later
    patients = get_all_patients()  # Implement with database
    return jsonify({'patients': patients})

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create patient - no auth check for now"""
    # TODO: Add @require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG) later
    data = request.json
    patient_id = create_patient_record(data)
    return jsonify({'patient_id': patient_id, 'message': 'Patient created'})

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient - no auth check for now"""
    # TODO: Add @require_permission('Patient', 'update') later
    data = request.json
    update_patient_record(patient_id, data)
    return jsonify({'message': 'Patient updated'})

# Visit Management
@app.route('/api/visits', methods=['POST'])
def create_visit():
    """Create visit - no auth check for now"""
    # TODO: Add @require_auth + @require_permission('Visit', 'create') later
    data = request.json
    
    # For testing, use hardcoded staff (will be from session later)
    data['StaffId'] = 1  # TODO: Get from session after auth implementation
    data['DepartmentId'] = 1  # TODO: Get from staff department after auth
    
    visit_id = create_visit_record(data)
    return jsonify({'visit_id': visit_id, 'message': 'Visit created'})

@app.route('/api/visits/<int:visit_id>/drugs', methods=['POST'])
def prescribe_drug(visit_id):
    """Prescribe drug - no auth check for now"""
    # TODO: Add @require_role(StaffRole.BAC_SI) later - doctors only
    data = request.json
    
    prescription_id = create_drug_prescription(visit_id, data)
    return jsonify({'prescription_id': prescription_id})

@app.route('/api/visits/<int:visit_id>/tests', methods=['POST'])
def order_test(visit_id):
    """Order test - no auth check for now"""
    # TODO: Add @require_role(StaffRole.BAC_SI) later - doctors only
    data = request.json
    
    test_order_id = create_test_order(visit_id, data)
    return jsonify({'test_order_id': test_order_id})

@app.route('/api/visits/<int:visit_id>/tests/<test_id>/execute', methods=['PUT'])
def execute_test(visit_id, test_id):
    """Execute test - no auth check for now"""
    # TODO: Add @require_role(BAC_SI, DIEU_DUONG, KY_THUAT_VIEN) later
    data = request.json
    
    # For testing, use hardcoded staff
    data['TestStaffId'] = 2  # TODO: Get from session after auth
    data['TestTime'] = datetime.now()
    data['TestStatus'] = 'In progress'
    
    update_test_execution(visit_id, test_id, data)
    return jsonify({'message': 'Test execution recorded'})

# Template Management
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get templates - no auth check for now"""
    # TODO: Add @require_auth later
    # TODO: Filter by department after auth implementation
    templates = get_all_templates()
    return jsonify({'templates': templates})

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create template - no auth check for now"""
    # TODO: Add @require_role(StaffRole.BAC_SI) later - doctors only
    data = request.json
    
    # For testing, use hardcoded department
    data['DepartmentId'] = 1  # TODO: Get from staff department after auth
    
    template_id = create_template_record(data)
    return jsonify({'template_id': template_id})

# ==========================================
# Testing Routes (Remove in Production)
# ==========================================

@app.route('/test/simulate-login/<int:staff_id>')
def simulate_login(staff_id):
    """Simulate login for testing - REMOVE in production"""
    # This allows testing different staff roles without auth
    staff = get_staff_by_id(staff_id)
    if staff:
        # Store in session for testing
        session['staff_id'] = staff['StaffId']
        session['staff_role'] = staff['StaffRole']
        session['department_id'] = staff['DepartmentId']
        return jsonify({'message': f'Simulated login as {staff["StaffName"]}'})
    return jsonify({'error': 'Staff not found'}), 404

@app.route('/test/current-user')
def get_current_user():
    """Get current simulated user - for testing only"""
    if 'staff_id' in session:
        return jsonify({
            'staff_id': session['staff_id'],
            'role': session.get('staff_role'),
            'department_id': session.get('department_id')
        })
    return jsonify({'message': 'No user logged in'})

# ==========================================
# Placeholder Functions (Implement with Database)
# ==========================================

def get_all_patients():
    """TODO: Implement with SQLAlchemy"""
    return []

def create_patient_record(data):
    """TODO: Implement with SQLAlchemy"""
    return 1

def update_patient_record(patient_id, data):
    """TODO: Implement with SQLAlchemy"""
    pass

def create_visit_record(data):
    """TODO: Implement with SQLAlchemy"""
    return 1

def create_drug_prescription(visit_id, data):
    """TODO: Implement with SQLAlchemy"""
    return 1

def create_test_order(visit_id, data):
    """TODO: Implement with SQLAlchemy"""
    return 1

def update_test_execution(visit_id, test_id, data):
    """TODO: Implement with SQLAlchemy"""
    pass

def get_all_templates():
    """TODO: Implement with SQLAlchemy"""
    return []

def create_template_record(data):
    """TODO: Implement with SQLAlchemy"""
    return 1

def get_staff_by_id(staff_id):
    """TODO: Implement with SQLAlchemy"""
    # Mock data for testing
    mock_staff = {
        1: {'StaffId': 1, 'StaffName': 'Dr. Nguyen', 'StaffRole': 'Bác sĩ', 'DepartmentId': 1},
        2: {'StaffId': 2, 'StaffName': 'Nurse Linh', 'StaffRole': 'Điều dưỡng', 'DepartmentId': 1},
        3: {'StaffId': 3, 'StaffName': 'Tech Duc', 'StaffRole': 'Kỹ thuật viên', 'DepartmentId': 1}
    }
    return mock_staff.get(staff_id)

if __name__ == '__main__':
    app.secret_key = 'test-secret-key'  # Change in production
    app.run(debug=True)

"""
Flask Application Structure - Phase 1 (No Authorization)
Basic CRUD operations for testing business logic
"""

from flask import Flask, request, jsonify, render_template, session
from datetime import datetime
import os
from models import (
    create_app, db, init_database, test_connection,
    get_all_patients, get_patient_by_id, create_patient_record, 
    update_patient_record, create_visit_record, get_visits_by_patient,
    get_staff_by_department, Patient, Visit, Staff, Department
)
from environment import create_example_routes

# Create app with database configuration
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

# Add environment variable demonstration routes
create_example_routes(app)

# ==========================================
# PHASE 1: Basic Routes (No Authorization)
# ==========================================

# Patient Management
@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients - no auth check for now"""
    # TODO: Add @require_auth later
    try:
        patients = get_all_patients()
        patients_data = []
        for patient in patients:
            patients_data.append({
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge,
                'PatientAddress': patient.PatientAddress,
                'Allergy': patient.Allergy,
                'PatientNote': patient.PatientNote
            })
        return jsonify({'patients': patients_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create patient - no auth check for now"""
    # TODO: Add @require_role(StaffRole.BAC_SI, StaffRole.DIEU_DUONG) later
    try:
        data = request.json
        patient_id = create_patient_record(data)
        return jsonify({'patient_id': patient_id, 'message': 'Patient created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient - no auth check for now"""
    # TODO: Add @require_permission('Patient', 'update') later
    try:
        data = request.json
        success = update_patient_record(patient_id, data)
        if success:
            return jsonify({'message': 'Patient updated'})
        else:
            return jsonify({'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Visit Management
@app.route('/api/visits', methods=['POST'])
def create_visit():
    """Create visit - no auth check for now"""
    # TODO: Add @require_auth + @require_permission('Visit', 'create') later
    try:
        data = request.json
        
        # For testing, use hardcoded staff (will be from session later)
        data['StaffId'] = 1  # TODO: Get from session after auth implementation
        data['DepartmentId'] = 1  # TODO: Get from staff department after auth
        
        visit_id = create_visit_record(data)
        return jsonify({'visit_id': visit_id, 'message': 'Visit created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
# Additional API Routes
# ==========================================

@app.route('/api/patients/<patient_id>/visits', methods=['GET'])
def get_patient_visits(patient_id):
    """Get all visits for a patient"""
    try:
        visits = get_visits_by_patient(patient_id)
        visits_data = []
        for visit in visits:
            visits_data.append({
                'VisitId': visit.VisitId,
                'PatientId': visit.PatientId,
                'DepartmentId': visit.DepartmentId,
                'VisitPurpose': visit.VisitPurpose,
                'VisitTime': visit.VisitTime.isoformat() if visit.VisitTime else None,
                'StaffId': visit.StaffId
            })
        return jsonify({'visits': visits_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        departments_data = []
        for dept in departments:
            departments_data.append({
                'DepartmentId': dept.DepartmentId,
                'DepartmentName': dept.DepartmentName,
                'DepartmentType': dept.DepartmentType
            })
        return jsonify({'departments': departments_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff', methods=['GET'])
def get_all_staff():
    """Get all staff"""
    try:
        staff = Staff.query.filter_by(StaffAvailable=True).all()
        staff_data = []
        for s in staff:
            staff_data.append({
                'StaffId': s.StaffId,
                'StaffName': s.StaffName,
                'StaffRole': s.StaffRole,
                'DepartmentId': s.DepartmentId
            })
        return jsonify({'staff': staff_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# Additional Helper Functions
# ==========================================

def create_drug_prescription(visit_id, data):
    """Create drug prescription for a visit"""
    try:
        from models import VisitDrug
        prescription = VisitDrug(
            VisitId=visit_id,
            DrugId=data.get('DrugId'),
            DrugRoute=data.get('DrugRoute'),
            DrugQuantity=data.get('DrugQuantity'),
            DrugTimes=data.get('DrugTimes'),
            DrugAtTime=data.get('DrugAtTime'),
            Note=data.get('Note'),
            IsCustom=data.get('IsCustom', False)
        )
        db.session.add(prescription)
        db.session.commit()
        return f"{visit_id}-{data.get('DrugId')}"
    except Exception as e:
        print(f"Error creating drug prescription: {e}")
        return 1

def create_test_order(visit_id, data):
    """Create test order for a visit"""
    try:
        from models import VisitTest
        test_order = VisitTest(
            VisitId=visit_id,
            TestId=data.get('TestId'),
            TestStatus='Ordered',
            TestStaffId=data.get('TestStaffId'),
            TestTime=data.get('TestTime'),
            IsCustom=data.get('IsCustom', False)
        )
        db.session.add(test_order)
        db.session.commit()
        return f"{visit_id}-{data.get('TestId')}"
    except Exception as e:
        print(f"Error creating test order: {e}")
        return 1

def update_test_execution(visit_id, test_id, data):
    """Update test execution status and results"""
    try:
        from models import VisitTest
        visit_test = VisitTest.query.filter_by(VisitId=visit_id, TestId=test_id).first()
        if visit_test:
            visit_test.TestStatus = data.get('TestStatus', visit_test.TestStatus)
            visit_test.TestStaffId = data.get('TestStaffId', visit_test.TestStaffId)
            visit_test.TestTime = data.get('TestTime', visit_test.TestTime)
            visit_test.TestResult = data.get('TestResult', visit_test.TestResult)
            visit_test.TestConclusion = data.get('TestConclusion', visit_test.TestConclusion)
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating test execution: {e}")
        return False

def get_all_templates():
    """Get all templates"""
    try:
        from models import Template
        templates = Template.query.all()
        templates_data = []
        for template in templates:
            templates_data.append({
                'TemplateId': template.TemplateId,
                'TemplateName': template.TemplateName,
                'DepartmentId': template.DepartmentId,
                'TemplateGroup': template.TemplateGroup,
                'TemplateType': template.TemplateType
            })
        return templates_data
    except Exception as e:
        print(f"Error getting templates: {e}")
        return []

def create_template_record(data):
    """Create a new template record"""
    try:
        from models import Template
        template = Template(
            TemplateName=data.get('TemplateName'),
            DepartmentId=data.get('DepartmentId'),
            TemplateGroup=data.get('TemplateGroup'),
            TemplateType=data.get('TemplateType')
        )
        db.session.add(template)
        db.session.commit()
        return template.TemplateId
    except Exception as e:
        print(f"Error creating template: {e}")
        return 1

def get_staff_by_id(staff_id):
    """Get staff by ID - real database implementation"""
    try:
        staff = Staff.query.get(staff_id)
        if staff:
            return {
                'StaffId': staff.StaffId,
                'StaffName': staff.StaffName,
                'StaffRole': staff.StaffRole,
                'DepartmentId': staff.DepartmentId
            }
        return None
    except Exception as e:
        print(f"Error getting staff: {e}")
        # Fallback to mock data for testing
        mock_staff = {
            1: {'StaffId': 1, 'StaffName': 'Dr. Nguyen', 'StaffRole': 'Bác sĩ', 'DepartmentId': 1},
            2: {'StaffId': 2, 'StaffName': 'Nurse Linh', 'StaffRole': 'Điều dưỡng', 'DepartmentId': 1},
            3: {'StaffId': 3, 'StaffName': 'Tech Duc', 'StaffRole': 'Kỹ thuật viên', 'DepartmentId': 1}
        }
        return mock_staff.get(staff_id)

# ==========================================
# Database Connection Test Route
# ==========================================

@app.route('/test/db-connection')
def test_db_connection():
    """Test database connection"""
    try:
        if test_connection():
            return jsonify({'status': 'success', 'message': 'Database connection successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        # Test database connection
        print("Testing database connection...")
        if test_connection():
            print("✓ Database connection successful!")
            print("✓ Starting Flask application...")
        else:
            print("✗ Database connection failed!")
            print("Please check your database configuration.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

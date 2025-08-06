
from flask import Flask, jsonify, request, Blueprint, render_template
from datetime import datetime
from models import (
    create_app, db,
    BodySite, BodySystem, Department, Drug, ICD, Patient, Proc, PatientDepartment,
    Sign, Staff, Template, Test, Visit, VisitDiagnosis, VisitDocuments, VisitImage,
    VisitDrug, VisitProc, VisitSign, VisitStaff, VisitTest, TestTemplate, DrugTemplate, SignTemplate #,PatientsWithDepartment
)
from api.patient_departments import patient_dept_bp

config_name = 'development'
app = create_app(config_name)

# Create Blueprint for API routes
bp = Blueprint('api', __name__)

# Generic API route generator for all ORM models
def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary with proper serialization"""
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        if value is not None:
            # Handle different data types
            if isinstance(value, datetime):
                result[c.name] = value.isoformat()
            elif isinstance(value, bytes):
                # Convert bytes to string (for text fields stored as bytes)
                try:
                    result[c.name] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # If it's binary data, convert to base64 or skip
                    result[c.name] = str(value)
            else:
                result[c.name] = value
        else:
            result[c.name] = None
    return result

def register_model_api(model, route_name):
    @bp.route(f"/{route_name}", methods=['GET'], endpoint=f"get_all_{route_name}")
    def get_all():
        try:
            items = model.query.all()
            return jsonify({route_name: [model_to_dict(item) for item in items]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Register routes for all ORM models BEFORE registering the blueprint
register_model_api(BodySite, 'body_site')
register_model_api(BodySystem, 'body_system')
register_model_api(Department, 'department')
register_model_api(Drug, 'drug')
register_model_api(ICD, 'icd')
register_model_api(Patient, 'patient')
register_model_api(Proc, 'proc')
register_model_api(PatientDepartment, 'patient_department')
register_model_api(Sign, 'sign')
register_model_api(Staff, 'staff')
register_model_api(Template, 'template')
register_model_api(Test, 'test')
register_model_api(Visit, 'visit')
register_model_api(VisitDiagnosis, 'visit_diagnosis')
register_model_api(VisitDocuments, 'visit_document')
register_model_api(VisitImage, 'visit_image')
register_model_api(VisitDrug, 'visit_drug')
register_model_api(VisitProc, 'visit_proc')
register_model_api(VisitSign, 'visit_sign')
register_model_api(VisitStaff, 'visit_staff')
register_model_api(VisitTest, 'visit_test')
register_model_api(TestTemplate, 'test_template')
register_model_api(DrugTemplate, 'drug_template')
register_model_api(SignTemplate, 'sign_template')
# register_model_api(PatientsWithDepartment, 'patient_with_department')

# Register the Blueprint with the app (AFTER all routes are defined)
app.register_blueprint(bp, url_prefix='/api')
app.register_blueprint(patient_dept_bp, url_prefix='/api')

# Add UI routes
@app.route('/patient_departments')
def patient_departments_page():
    return render_template('patient_departments.html')

@app.route('/test_datatables')
def test_datatables_page():
    return render_template('test_datatables.html')

@app.route('/mobile_test')
def mobile_test_page():
    with open('mobile-test.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

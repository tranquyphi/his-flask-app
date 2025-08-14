from flask import Flask, jsonify, request, Blueprint, render_template
from datetime import datetime
from models import (
    create_app, db,
    BodyPart, BodySite, BodySystem, Department, Drug, DrugGroup, ICD, Patient, Proc, PatientDepartment,
    Sign, Staff, Template, Test, Visit, VisitDiagnosis, VisitDocuments, VisitImage,
    VisitDrug, VisitProc, VisitSign, VisitStaff, VisitTest, TestTemplate, DrugTemplate, DrugTemplateDetail, SignTemplate, PatientsWithDepartment
)
from api.department_patients import dept_patients_bp
from api.body_sites import body_sites_bp
from api.body_parts import body_parts_bp
from api.excel_upload import excel_upload_bp
from api.signs import signs_bp
from api.sign_template import sign_template_bp
from api.sign_template_detail import sign_template_detail_bp
from api.drugs import drugs_bp
from api.drug_template import drug_template_bp
from api.drug_template_detail import drug_template_detail_bp
from api.drug_groups import drug_groups_bp
from api.visits import visits_bp
from api.patient_visits import patient_visits_bp
from api.v2_endpoints import v2_bp

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
register_model_api(DrugGroup, 'drug_group')
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

# register_model_api(TestTemplate, 'test_template')
# register_model_api(DrugTemplate, 'drug_template')
#register_model_api(SignTemplate, 'sign_template')

# Special API route for PatientsWithDepartment (uses custom methods)
@bp.route("/patients_with_department", methods=['GET'], endpoint="get_all_patients_with_department")
def get_all_patients_with_department():
    try:
        department_id = request.args.get('department_id')
        if department_id:
            # Get patients for specific department
            patients_data = PatientsWithDepartment.get_by_department(department_id)
        else:
            # Get all patients with their department information
            patients_data = PatientsWithDepartment.get_all_with_departments()
        return jsonify({'patients_with_department': patients_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register the Blueprint with the app (AFTER all routes are defined)
app.register_blueprint(bp, url_prefix='/api')
app.register_blueprint(dept_patients_bp, url_prefix='/api')
app.register_blueprint(body_sites_bp)
app.register_blueprint(body_parts_bp)
app.register_blueprint(excel_upload_bp)
app.register_blueprint(signs_bp, url_prefix='/api')
app.register_blueprint(sign_template_bp, url_prefix='/api')
app.register_blueprint(sign_template_detail_bp, url_prefix='/api')
app.register_blueprint(drugs_bp, url_prefix='/api')
app.register_blueprint(drug_template_bp, url_prefix='/api')
app.register_blueprint(drug_template_detail_bp, url_prefix='/api')
app.register_blueprint(drug_groups_bp, url_prefix='/api')
app.register_blueprint(visits_bp, url_prefix='/api')
app.register_blueprint(patient_visits_bp, url_prefix='/api')
app.register_blueprint(v2_bp, url_prefix='/api/v2')

# Add UI routes
@app.route('/')
def index():
    """Main index page with links to all available pages"""
    return render_template('index.html')

@app.route('/departments')
def departments_page():
    return render_template('departments.html')

@app.route('/department_patients/<int:department_id>')
def department_patients_specific(department_id):
    """Direct access to a specific department's patients - for authorized staff"""
    return render_template('department_patients_specific.html', department_id=department_id)

@app.route('/signs')
def signs_page():
    return render_template('signs.html')

@app.route('/sign-templates')
def sign_templates_page():
    return render_template('sign_templates.html')

@app.route('/sign-templates/<int:template_id>/details')
def sign_template_details_page(template_id):
    return render_template('sign_template_details.html', template_id=template_id)

@app.route('/drugs')
def drugs_page():
    return render_template('drugs.html')

@app.route('/drug-templates')
def drug_templates_page():
    return render_template('drug_templates.html')


@app.route('/drug-templates/<int:template_id>/details')
def drug_template_details_page(template_id):
    return render_template('drug_template_details.html', template_id=template_id)

@app.route('/drug-groups')
def drug_groups_page():
    return render_template('drug_groups.html')

@app.route('/visits')
def visits_page():
    return render_template('visits.html')

@app.route('/tests')
def tests_page():
    return render_template('tests.html')

@app.route('/procedures')
def procedures_page():
    return render_template('procedures.html')

@app.route('/staff')
def staff_page():
    return render_template('staff.html')

@app.route('/body-sites')
def body_sites_page():
    return render_template('body_sites.html')

@app.route('/patient-visits')
def patient_visits_page():
    return render_template('patient_visits.html')

@app.route('/patient-visits/<string:patient_id>')
def patient_visits_specific(patient_id):
    """Direct access to a specific patient's visits history"""
    return render_template('patient_visits.html', patient_id=patient_id)

@app.route('/test-patient-visits')
def test_patient_visits():
    """Test route for patient visits with fixed test patient ID"""
    return render_template('patient_visits.html', patient_id="2500073746")

@app.route('/test-patient-static')
def test_patient_static():
    """Static test page for patient visits that doesn't rely on JavaScript or API calls"""
    return render_template('test_patient_visits.html')

@app.route('/excel-upload')
def excel_upload_page():
    return render_template('excel_upload.html')

@app.route('/patients-with-departments')
def patients_with_departments_page():
    """Page showing all patients with their department information"""
    return render_template('patients_with_departments.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, jsonify, request, Blueprint
from models import (
    create_app, db,
    BodySite, BodySystem, Department, Drug, ICD, Patient, Proc, PatientDepartment,
    Sign, Staff, Template, Test, Visit, VisitDiagnosis, VisitDocuments, VisitImage,
    VisitDrug, VisitProc, VisitSign, VisitStaff, VisitTest, TestTemplate, DrugTemplate, SignTemplate,PatientsWithDepartment
)

config_name = 'development'
app = create_app(config_name)

# Create Blueprint for API routes
bp = Blueprint('api', __name__)

# Generic API route generator for all ORM models
def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def register_model_api(model, route_name):
    @bp.route(f"/{route_name}", methods=['GET'], endpoint=f"get_all_{route_name}")
    def get_all():
        try:
            items = model.query.all()
            return jsonify({route_name: [model_to_dict(item) for item in items]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Custom route for PatientDepartment with additional details
@bp.route('/patient_department_detail/<string:patient_id>', methods=['GET'])
def get_patient_department(patient_id):
    results = (
        db.session.query(
            PatientDepartment.PatientId,
            Patient.PatientAge,
            Patient.PatientAddress,
            Patient.PatientGender,
            Patient.PatientName,
            Department.DepartmentName
        )
        .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
        .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
        .filter(PatientDepartment.PatientId == patient_id)
        .all()
    )
    return jsonify([dict(r._mapping) for r in results]) 

# Custom route to get all patient departments with details
@bp.route('/patient_department_detail', methods=['GET'])
def get_patient_departments():
    # Check if PatientId is provided as query parameter
    patient_id = request.args.get('PatientId')
    
    if patient_id:
        # Filter by PatientId if provided
        results = (
            db.session.query(
                PatientDepartment.PatientId,
                Patient.PatientAge,
                Patient.PatientAddress,
                Patient.PatientGender,
                Patient.PatientName,
                Department.DepartmentName
            )
            .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
            .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
            .filter(PatientDepartment.PatientId == patient_id)
            .all()
        )
    else:
        # Return all if no PatientId specified
        results = (
            db.session.query(
                PatientDepartment.PatientId,
                Patient.PatientAge,
                Patient.PatientAddress,
                Patient.PatientGender,
                Patient.PatientName,
                Department.DepartmentName
            )
            .join(Patient, Patient.PatientId == PatientDepartment.PatientId)
            .join(Department, Department.DepartmentId == PatientDepartment.DepartmentId)
            .all()
        )
    return jsonify([dict(r._mapping) for r in results])

@bp.route('/patient_department_detail', methods=['POST'])
def add_patient_department():
    data = request.json
    new_link = PatientDepartment(
        PatientId=data['PatientId'],
        DepartmentId=data['DepartmentId']
    )
    db.session.add(new_link)
    db.session.commit()
    return jsonify({"message": "Added successfully"}), 201

@bp.route('/patient_department_detail/<string:patient_id>/<int:department_id>', methods=['DELETE'])
def delete_patient_department(patient_id, department_id):
    pd = PatientDepartment.query.get((patient_id, department_id))
    if not pd:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(pd)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})

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
register_model_api(PatientsWithDepartment, 'patient_with_department')

# Register the Blueprint with the app (AFTER all routes are defined)
app.register_blueprint(bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

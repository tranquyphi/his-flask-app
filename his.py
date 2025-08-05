
from flask import Flask, jsonify
from models import (
    create_app, db,
    BodySite, BodySystem, Department, Drug, ICD, Patient, Proc, PatientDepartment,
    Sign, Staff, Template, Test, Visit, VisitDiagnosis, VisitDocuments, VisitImage,
    VisitDrug, VisitProc, VisitSign, VisitStaff, VisitTest, TestTemplate, DrugTemplate, SignTemplate,PatientsWithDepartment
)

config_name = 'development'
app = create_app(config_name)

# Generic API route generator for all ORM models
def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def register_model_api(model, route_name):
    @app.route(f"/api/{route_name}", methods=['GET'], endpoint=f"get_all_{route_name}")
    def get_all():
        try:
            items = model.query.all()
            return jsonify({route_name: [model_to_dict(item) for item in items]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Register routes for all ORM models
register_model_api(BodySite, 'BodySite')
register_model_api(BodySystem, 'BodySystem')
register_model_api(Department, 'Department')
register_model_api(Drug, 'Drug')
register_model_api(ICD, 'ICD')
register_model_api(Patient, 'Patient')
register_model_api(Proc, 'Proc')
register_model_api(PatientDepartment, 'PatientDepartment')
register_model_api(Sign, 'Sign')
register_model_api(Staff, 'Staff')
register_model_api(Template, 'Template')
register_model_api(Test, 'Test')
register_model_api(Visit, 'Visit')
register_model_api(VisitDiagnosis, 'VisitDiagnosis')
register_model_api(VisitDocuments, 'VisitDocuments')
register_model_api(VisitImage, 'VisitImage')
register_model_api(VisitDrug, 'VisitDrug')
register_model_api(VisitProc, 'VisitProc')
register_model_api(VisitSign, 'VisitSign')
register_model_api(VisitStaff, 'VisitStaff')
register_model_api(VisitTest, 'VisitTest')
register_model_api(TestTemplate, 'TestTemplate')
register_model_api(DrugTemplate, 'DrugTemplate')
register_model_api(SignTemplate, 'SignTemplate')
register_model_api(PatientsWithDepartment, 'PatientsWithDepartment')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

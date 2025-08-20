"""
Patient Visits API Blueprint
Retrieve and manage visits for a specific patient
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import desc, asc
from models_main import db
from models import Patient, Visit, Department, Staff, VisitDiagnosis, PatientDepartment

patient_visits_bp = Blueprint('patient_visits', __name__)

@patient_visits_bp.route('/patient_visits/<string:patient_id>', methods=['GET'])
def get_patient_visits(patient_id):
    """Get all visits for a specific patient"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Query visits with related data
        results = (
            db.session.query(
                Visit.VisitId,
                Visit.PatientId, 
                Visit.DepartmentId,
                Visit.VisitPurpose,
                Visit.VisitTime,
                Visit.StaffId,
                Department.DepartmentName,
                Staff.StaffName,
                Staff.StaffRole
            )
            .join(Department, Department.DepartmentId == Visit.DepartmentId)
            .join(Staff, Staff.StaffId == Visit.StaffId)
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .all()
        )
        
        # Convert results to dictionaries
        visits_data = []
        for r in results:
            row_dict = dict(r._mapping)
            
            # Format datetime for JSON serialization
            if row_dict.get('VisitTime'):
                row_dict['VisitTime'] = row_dict['VisitTime'].isoformat()
            
            # Get diagnoses for each visit
            diagnoses = VisitDiagnosis.query.filter_by(VisitId=row_dict['VisitId']).all()
            row_dict['diagnoses'] = [
                {
                    'ICDCode': d.ICDCode,
                    'ActualDiagnosis': d.ActualDiagnosis
                } for d in diagnoses
            ]
            
            visits_data.append(row_dict)
        
        return jsonify({
            'patient': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge,
                'PatientAddress': patient.PatientAddress
            },
            'visits': visits_data,
            'total_visits': len(visits_data)
        })
        
    except Exception as e:
        print(f"Error in get_patient_visits: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@patient_visits_bp.route('/patient_visits/<string:patient_id>/summary', methods=['GET'])
def get_patient_visits_summary(patient_id):
    """Get summary of patient's visit history"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        # Count total visits
        total_visits = db.session.query(Visit).filter(Visit.PatientId == patient_id).count()
        
        # Count visits by department
        dept_visits = (
            db.session.query(
                Department.DepartmentName,
                db.func.count(Visit.VisitId).label('visit_count')
            )
            .join(Visit, Visit.DepartmentId == Visit.DepartmentId)
            .filter(Visit.PatientId == patient_id)
            .group_by(Department.DepartmentName)
            .order_by(desc('visit_count'))
            .all()
        )
        
        # Count unique departments from both visits and department assignments
        # This ensures we count departments even if patient has no visits
        all_dept_assignments = (
            db.session.query(
                Department.DepartmentName,
                db.func.count(PatientDepartment.id).label('assignment_count')
            )
            .join(PatientDepartment, PatientDepartment.DepartmentId == Department.DepartmentId)
            .filter(PatientDepartment.PatientId == patient_id)
            .group_by(Department.DepartmentName)
            .order_by(desc('assignment_count'))
            .all()
        )
        
        # Combine both sources to get unique departments
        unique_departments = set()
        dept_visits_dict = {}
        
        # Add departments from visits
        for dept in dept_visits:
            unique_departments.add(dept.DepartmentName)
            dept_visits_dict[dept.DepartmentName] = dept.visit_count
        
        # Add departments from assignments
        for dept in all_dept_assignments:
            unique_departments.add(dept.DepartmentName)
            if dept.DepartmentName not in dept_visits_dict:
                dept_visits_dict[dept.DepartmentName] = 0
        
        # Create final department visits list
        final_dept_visits = [
            {'department': dept_name, 'count': dept_visits_dict.get(dept_name, 0)}
            for dept_name in sorted(unique_departments, key=lambda x: dept_visits_dict.get(x, 0), reverse=True)
        ]
        
        # Count visits by purpose
        purpose_visits = (
            db.session.query(
                Visit.VisitPurpose,
                db.func.count(Visit.VisitId).label('visit_count')
            )
            .filter(Visit.PatientId == patient_id)
            .group_by(Visit.VisitPurpose)
            .order_by(desc('visit_count'))
            .all()
        )
        
        # Get first and most recent visit
        first_visit = (
            db.session.query(
                Visit.VisitTime,
                Visit.VisitPurpose,
                Department.DepartmentName
            )
            .join(Department, Department.DepartmentId == Visit.DepartmentId)
            .filter(Visit.PatientId == patient_id)
            .order_by(asc(Visit.VisitTime))
            .first()
        )
        
        latest_visit = (
            db.session.query(
                Visit.VisitTime,
                Visit.VisitPurpose,
                Department.DepartmentName
            )
            .join(Department, Department.DepartmentId == Visit.DepartmentId)
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .first()
        )
        
        # Common diagnoses
        common_diagnoses = (
            db.session.query(
                VisitDiagnosis.ActualDiagnosis,
                db.func.count(VisitDiagnosis.VisitId).label('diagnosis_count')
            )
            .join(Visit, Visit.VisitId == VisitDiagnosis.VisitId)
            .filter(Visit.PatientId == patient_id)
            .group_by(VisitDiagnosis.ActualDiagnosis)
            .order_by(desc('diagnosis_count'))
            .limit(5)
            .all()
        )
        
        return jsonify({
            'patient': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge
            },
            'visit_summary': {
                'total_visits': total_visits,
                'first_visit': {
                    'time': first_visit.VisitTime.isoformat() if first_visit and first_visit.VisitTime else None,
                    'purpose': first_visit.VisitPurpose if first_visit else None,
                    'department': first_visit.DepartmentName if first_visit else None
                },
                'latest_visit': {
                    'time': latest_visit.VisitTime.isoformat() if latest_visit and latest_visit.VisitTime else None,
                    'purpose': latest_visit.VisitPurpose if latest_visit else None,
                    'department': latest_visit.DepartmentName if latest_visit else None
                }
            },
            'department_visits': final_dept_visits,
            'purpose_visits': [
                {'purpose': purpose.VisitPurpose, 'count': purpose.visit_count} 
                for purpose in purpose_visits
            ],
            'common_diagnoses': [
                {'diagnosis': diag.ActualDiagnosis, 'count': diag.diagnosis_count} 
                for diag in common_diagnoses if diag.ActualDiagnosis
            ]
        })
        
    except Exception as e:
        print(f"Error in get_patient_visits_summary: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@patient_visits_bp.route('/patient_visits/<string:patient_id>/latest', methods=['GET'])
def get_patient_latest_visit(patient_id):
    """Get the most recent visit for a specific patient"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Query most recent visit with related data
        result = (
            db.session.query(
                Visit.VisitId,
                Visit.PatientId, 
                Visit.DepartmentId,
                Visit.VisitPurpose,
                Visit.VisitTime,
                Visit.StaffId,
                Department.DepartmentName,
                Staff.StaffName,
                Staff.StaffRole
            )
            .join(Department, Department.DepartmentId == Visit.DepartmentId)
            .join(Staff, Staff.StaffId == Visit.StaffId)
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .first()
        )
        
        if not result:
            return jsonify({
                'patient': {
                    'PatientId': patient.PatientId,
                    'PatientName': patient.PatientName
                },
                'visit': None,
                'message': 'No visits found for this patient'
            })
        
        # Convert result to dictionary
        visit_data = dict(result._mapping)
        
        # Format datetime for JSON serialization
        if visit_data.get('VisitTime'):
            visit_data['VisitTime'] = visit_data['VisitTime'].isoformat()
        
        # Get diagnoses for the visit
        diagnoses = VisitDiagnosis.query.filter_by(VisitId=visit_data['VisitId']).all()
        visit_data['diagnoses'] = [
            {
                'ICDCode': d.ICDCode,
                'ActualDiagnosis': d.ActualDiagnosis
            } for d in diagnoses
        ]
        
        return jsonify({
            'patient': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge
            },
            'visit': visit_data
        })
        
    except Exception as e:
        print(f"Error in get_patient_latest_visit: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@patient_visits_bp.route('/patient_visits/<string:patient_id>/create', methods=['POST'])
def create_patient_visit(patient_id):
    """Create a new visit for a specific patient"""
    try:
        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        payload = request.get_json(force=True) or {}
        required = ['DepartmentId', 'StaffId', 'VisitPurpose']
        missing = [f for f in required if f not in payload]
        
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Create new visit
        new_visit = Visit(
            PatientId=patient_id,
            DepartmentId=payload['DepartmentId'],
            StaffId=payload['StaffId'],
            VisitPurpose=payload['VisitPurpose'],
            VisitTime=datetime.now()
        )
        
        db.session.add(new_visit)
        db.session.commit()
        
        # Add diagnosis if provided
        if 'diagnosis' in payload and payload['diagnosis']:
            diagnosis = VisitDiagnosis(
                VisitId=new_visit.VisitId,
                ICDCode=payload.get('ICDCode'),
                ActualDiagnosis=payload['diagnosis']
            )
            db.session.add(diagnosis)
            db.session.commit()
        
        # Get complete visit data
        result = (
            db.session.query(
                Visit.VisitId,
                Visit.PatientId, 
                Visit.DepartmentId,
                Visit.VisitPurpose,
                Visit.VisitTime,
                Visit.StaffId,
                Department.DepartmentName,
                Staff.StaffName,
                Staff.StaffRole
            )
            .join(Department, Department.DepartmentId == Visit.DepartmentId)
            .join(Staff, Staff.StaffId == Visit.StaffId)
            .filter(Visit.VisitId == new_visit.VisitId)
            .first()
        )
        
        visit_data = dict(result._mapping)
        
        # Format datetime for JSON serialization
        if visit_data.get('VisitTime'):
            visit_data['VisitTime'] = visit_data['VisitTime'].isoformat()
        
        return jsonify({
            'message': 'Visit created successfully',
            'visit': visit_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_patient_visit: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

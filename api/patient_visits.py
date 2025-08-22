"""
Patient Visits API Blueprint
Retrieve and manage visits for a specific patient
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import desc, asc
from models_main import db
from models import Patient, Visit, Department, Staff, VisitDiagnosis, PatientDepartment, VisitStaff

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
                Visit.VisitPurpose,
                Visit.VisitTime
            )
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .all()
        )
        
        # Convert results to dictionaries and get related data
        visits_data = []
        for r in results:
            row_dict = dict(r._mapping)
            
            # Format datetime for JSON serialization
            if row_dict.get('VisitTime'):
                row_dict['VisitTime'] = row_dict['VisitTime'].isoformat()
            
            # Get staff information for this visit
            visit_staff = VisitStaff.query.filter_by(VisitId=row_dict['VisitId']).all()
            staff_info = []
            for vs in visit_staff:
                staff = Staff.query.get(vs.StaffId)
                if staff:
                    staff_info.append({
                        'StaffId': staff.StaffId,
                        'StaffName': staff.StaffName,
                        'StaffRole': staff.StaffRole
                    })
            
            row_dict['staff'] = staff_info
            
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
        
        # Get latest visit
        latest_visit = (
            db.session.query(Visit)
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .first()
        )
        
        summary = {
            'total_visits': total_visits,
            'purpose_breakdown': [
                {
                    'purpose': row.VisitPurpose or 'Không xác định',
                    'count': row.visit_count
                } for row in purpose_visits
            ],
            'latest_visit': None
        }
        
        if latest_visit:
            summary['latest_visit'] = {
                'VisitId': latest_visit.VisitId,
                'VisitTime': latest_visit.VisitTime.isoformat() if latest_visit.VisitTime else None,
                'VisitPurpose': latest_visit.VisitPurpose
            }
        
        return jsonify({
            'patient': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName
            },
            'summary': summary
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
        
        # Get latest visit
        latest_visit = (
            db.session.query(Visit)
            .filter(Visit.PatientId == patient_id)
            .order_by(desc(Visit.VisitTime))
            .first()
        )
        
        if not latest_visit:
            return jsonify({'error': 'No visits found for this patient'}), 404
        
        visit_data = latest_visit.to_dict()
        
        # Get staff information for this visit
        visit_staff = VisitStaff.query.filter_by(VisitId=latest_visit.VisitId).all()
        staff_info = []
        for vs in visit_staff:
            staff = Staff.query.get(vs.StaffId)
            if staff:
                staff_info.append({
                    'StaffId': staff.StaffId,
                    'StaffName': staff.StaffName,
                    'StaffRole': staff.StaffRole
                })
        
        visit_data['staff'] = staff_info
        
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
        required = ['StaffIds', 'VisitPurpose']
        missing = [f for f in required if f not in payload]
        
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Validate StaffIds
        staff_ids = payload['StaffIds']
        if not isinstance(staff_ids, list) or len(staff_ids) == 0:
            return jsonify({'error': 'StaffIds must be a non-empty list'}), 400
        
        staff_list = Staff.query.filter(Staff.StaffId.in_(staff_ids)).all()
        if len(staff_list) != len(staff_ids):
            return jsonify({'error': 'One or more StaffIds not found'}), 404
        
        # Create new visit
        new_visit = Visit(
            PatientId=patient_id,
            VisitPurpose=payload['VisitPurpose'],
            VisitTime=datetime.now()
        )
        
        db.session.add(new_visit)
        db.session.flush()  # Get the VisitId
        
        # Create VisitStaff associations
        for staff_id in staff_ids:
            visit_staff = VisitStaff(VisitId=new_visit.VisitId, StaffId=staff_id)
            db.session.add(visit_staff)
        
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
        visit_data = new_visit.to_dict()
        
        # Add staff information
        staff_info = []
        for staff in staff_list:
            staff_info.append({
                'StaffId': staff.StaffId,
                'StaffName': staff.StaffName,
                'StaffRole': staff.StaffRole
            })
        
        visit_data['staff'] = staff_info
        
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

"""
Patients API Blueprint
CRUD operations for Patient management
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import asc, text
from models_main import db
from models import Patient

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients', methods=['GET'])
def list_patients():
    """List all patients"""
    try:
        # Query all patients
        patients = Patient.query.all()
        
        # Convert to dict
        patients_data = []
        for patient in patients:
            patients_data.append({
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge,
                'PatientAddress': patient.PatientAddress,
                'PatientPhone': patient.PatientPhone,
                'PatientBHYT': patient.PatientBHYT
            })
            
        return jsonify({'patients': patients_data})
    except Exception as e:
        print(f"Error listing patients: {e}")
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/patients/<string:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient by ID"""
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        patient_data = {
            'PatientId': patient.PatientId,
            'PatientName': patient.PatientName,
            'PatientGender': patient.PatientGender,
            'PatientAge': patient.PatientAge,
            'PatientAddress': patient.PatientAddress,
            'PatientPhone': patient.PatientPhone,
            'PatientBHYT': patient.PatientBHYT,
            'PatientBHYTValid': patient.PatientBHYTValid,
            'PatientNote': patient.PatientNote,
            'Allergy': patient.Allergy,
            'History': patient.History
        }
            
        return jsonify({'patient': patient_data})
    except Exception as e:
        print(f"Error getting patient: {e}")
        return jsonify({'error': str(e)}), 500

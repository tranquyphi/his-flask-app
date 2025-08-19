"""
Patients API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.Patient import Patient

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Patients"])

# Pydantic models
class PatientResponse(BaseModel):
    PatientId: str
    PatientName: str
    PatientGender: Optional[str] = None
    PatientAge: Optional[str] = None
    PatientAddress: Optional[str] = None
    PatientPhone: Optional[str] = None
    PatientCCCD: Optional[str] = None
    PatientBHYT: Optional[str] = None
    PatientBHYTValid: Optional[bool] = None
    PatientRelative: Optional[str] = None
    Allergy: Optional[str] = None
    History: Optional[str] = None
    PatientNote: Optional[str] = None

class PatientCreate(BaseModel):
    PatientId: str
    PatientName: str
    PatientGender: Optional[str] = None
    PatientAge: Optional[str] = None
    PatientAddress: Optional[str] = None
    PatientPhone: Optional[str] = None
    PatientCCCD: Optional[str] = None
    PatientBHYT: Optional[str] = None
    PatientBHYTValid: Optional[bool] = None
    PatientRelative: Optional[str] = None
    Allergy: Optional[str] = None
    History: Optional[str] = None
    PatientNote: Optional[str] = None

@router.get("/patients", response_model=dict)
async def list_patients(
    search: Optional[str] = Query(None, description="Search term for patient name or ID"),
    limit: Optional[int] = Query(100, description="Maximum number of patients to return"),
    db: Session = Depends(get_db)
):
    """List all patients with optional search"""
    try:
        query = db.query(Patient)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Patient.PatientName.like(search_term)) |
                (Patient.PatientId.like(search_term))
            )
        
        patients = query.limit(limit).all()
        
        patients_data = []
        for patient in patients:
            patient_dict = {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge,
                'PatientAddress': patient.PatientAddress,
                'PatientPhone': patient.PatientPhone,
                'PatientCCCD': patient.PatientCCCD,
                'PatientBHYT': patient.PatientBHYT,
                'PatientBHYTValid': patient.PatientBHYTValid,
                'PatientRelative': patient.PatientRelative,
                'Allergy': patient.Allergy,
                'History': patient.History,
                'PatientNote': patient.PatientNote
            }
            patients_data.append(patient_dict)
            
        return {'patients': patients_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients/{patient_id}", response_model=dict)
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get a specific patient by ID"""
    try:
        patient = db.query(Patient).get(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        patient_data = {
            'PatientId': patient.PatientId,
            'PatientName': patient.PatientName,
            'PatientGender': patient.PatientGender,
            'PatientAge': patient.PatientAge,
            'PatientAddress': patient.PatientAddress,
            'PatientPhone': patient.PatientPhone,
            'PatientCCCD': patient.PatientCCCD,
            'PatientBHYT': patient.PatientBHYT,
            'PatientBHYTValid': patient.PatientBHYTValid,
            'PatientRelative': patient.PatientRelative,
            'Allergy': patient.Allergy,
            'History': patient.History,
            'PatientNote': patient.PatientNote
        }
        
        return {'patient': patient_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patients", response_model=dict)
async def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient"""
    try:
        # Check if patient ID already exists
        existing_patient = db.query(Patient).get(patient_data.PatientId)
        if existing_patient:
            raise HTTPException(status_code=400, detail="Patient ID already exists")
        
        new_patient = Patient(
            PatientId=patient_data.PatientId,
            PatientName=patient_data.PatientName,
            PatientGender=patient_data.PatientGender,
            PatientAge=patient_data.PatientAge,
            PatientAddress=patient_data.PatientAddress,
            PatientPhone=patient_data.PatientPhone,
            PatientCCCD=patient_data.PatientCCCD,
            PatientBHYT=patient_data.PatientBHYT,
            PatientBHYTValid=patient_data.PatientBHYTValid,
            PatientRelative=patient_data.PatientRelative,
            Allergy=patient_data.Allergy,
            History=patient_data.History,
            PatientNote=patient_data.PatientNote
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        patient_dict = {
            'PatientId': new_patient.PatientId,
            'PatientName': new_patient.PatientName,
            'PatientGender': new_patient.PatientGender,
            'PatientAge': new_patient.PatientAge,
            'PatientAddress': new_patient.PatientAddress,
            'PatientPhone': new_patient.PatientPhone,
            'PatientCCCD': new_patient.PatientCCCD,
            'PatientBHYT': new_patient.PatientBHYT,
            'PatientBHYTValid': new_patient.PatientBHYTValid,
            'PatientRelative': new_patient.PatientRelative,
            'Allergy': new_patient.Allergy,
            'History': new_patient.History,
            'PatientNote': new_patient.PatientNote
        }
        
        return {'patient': patient_dict, 'message': 'Patient created successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/patients/{patient_id}", response_model=dict)
async def update_patient(patient_id: str, patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Update an existing patient"""
    try:
        patient = db.query(Patient).get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update fields
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'PatientId':  # Don't update the primary key
                setattr(patient, field, value)
        
        db.commit()
        db.refresh(patient)
        
        patient_dict = {
            'PatientId': patient.PatientId,
            'PatientName': patient.PatientName,
            'PatientGender': patient.PatientGender,
            'PatientAge': patient.PatientAge,
            'PatientAddress': patient.PatientAddress,
            'PatientPhone': patient.PatientPhone,
            'PatientCCCD': patient.PatientCCCD,
            'PatientBHYT': patient.PatientBHYT,
            'PatientBHYTValid': patient.PatientBHYTValid,
            'PatientRelative': patient.PatientRelative,
            'Allergy': patient.Allergy,
            'History': patient.History,
            'PatientNote': patient.PatientNote
        }
        
        return {'patient': patient_dict, 'message': 'Patient updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/patients/{patient_id}", response_model=dict)
async def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Delete a patient"""
    try:
        patient = db.query(Patient).get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        db.delete(patient)
        db.commit()
        
        return {'message': 'Patient deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

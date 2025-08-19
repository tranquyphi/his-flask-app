"""
Patients with Department API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

# Import database models and session
from models_main import get_db
from models.Patient import Patient
from models.Department import Department  
from models.PatientDepartment import PatientDepartment

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Patients with Departments"])

@router.get("/patients_with_department", response_model=dict)
async def get_patients_with_department(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """Get all patients with their department information"""
    try:
        if department_id:
            # Get patients for specific department
            patients_data = await get_patients_by_department(department_id, db)
        else:
            # Get all patients with their department information
            patients_data = await get_all_patients_with_departments(db)
            
        return {'patients_with_department': patients_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_patients_with_departments(db: Session):
    """Get all patients with their department information, sorted by name"""
    try:
        patients = db.query(Patient).order_by(Patient.PatientName).all()
        result = []
        
        for patient in patients:
            # Get the most recent department assignment
            latest_assignment = db.query(PatientDepartment).filter_by(
                PatientId=patient.PatientId
            ).order_by(PatientDepartment.At.desc()).first()
            
            current_department = None
            current_department_id = None
            if latest_assignment:
                department = db.query(Department).get(latest_assignment.DepartmentId)
                current_department = department.DepartmentName if department else None
                current_department_id = department.DepartmentId if department else None
            
            # Create patient dict manually to avoid Flask context issues
            patient_dict = {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientAge': patient.PatientAge,
                'PatientGender': patient.PatientGender,
                'PatientAddress': patient.PatientAddress,
                'PatientPhone': patient.PatientPhone,
                'PatientCCCD': patient.PatientCCCD,
                'PatientBHYT': patient.PatientBHYT,
                'PatientBHYTValid': patient.PatientBHYTValid,
                'PatientRelative': patient.PatientRelative,
                'Allergy': patient.Allergy,
                'History': patient.History,
                'PatientNote': patient.PatientNote,
                'CurrentDepartment': current_department,
                'CurrentDepartmentId': current_department_id,
                'LastAssignmentDate': latest_assignment.At.isoformat() if latest_assignment else None
            }
            
            result.append(patient_dict)
            
        return result
    except Exception as e:
        raise Exception(f"Error getting patients with departments: {str(e)}")

async def get_patients_by_department(department_id: int, db: Session):
    """Get patients for a specific department"""
    try:
        # Get department info first
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Get current patients in the department
        current_assignments = db.query(PatientDepartment).filter_by(
            DepartmentId=department_id,
            Current=True
        ).all()
        
        result = []
        for assignment in current_assignments:
            patient = db.query(Patient).get(assignment.PatientId)
            if patient:
                patient_dict = {
                    'PatientId': patient.PatientId,
                    'PatientName': patient.PatientName,
                    'PatientAge': patient.PatientAge,
                    'PatientGender': patient.PatientGender,
                    'PatientAddress': patient.PatientAddress,
                    'PatientPhone': patient.PatientPhone,
                    'PatientCCCD': patient.PatientCCCD,
                    'PatientBHYT': patient.PatientBHYT,
                    'PatientBHYTValid': patient.PatientBHYTValid,
                    'PatientRelative': patient.PatientRelative,
                    'Allergy': patient.Allergy,
                    'History': patient.History,
                    'PatientNote': patient.PatientNote,
                    'DepartmentId': department.DepartmentId,
                    'DepartmentName': department.DepartmentName,
                    'AssignmentDate': assignment.At.isoformat(),
                    'Current': assignment.Current
                }
                result.append(patient_dict)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise Exception(f"Error getting patients by department: {str(e)}")

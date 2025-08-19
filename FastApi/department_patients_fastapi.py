"""
Department Patients API endpoints - FastAPI version  
CRUD operations for managing patient-department relationships and statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Import database models and session
from models_main import get_db
from models.Department import Department
from models.Patient import Patient
from models.PatientDepartment import PatientDepartment

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Department Patients"])

# Pydantic models
class DepartmentStatsResponse(BaseModel):
    current_patients: int
    total_patients: int
    recent_admissions: int

class PatientDepartmentResponse(BaseModel):
    PatientId: str
    DepartmentId: int
    Current: bool
    At: Optional[str] = None
    Reason: Optional[str] = None
    PatientName: Optional[str] = None
    DepartmentName: Optional[str] = None

@router.get("/department_stats/{department_id}", response_model=dict)
async def get_department_stats(department_id: int, db: Session = Depends(get_db)):
    """Get statistics for a specific department"""
    try:
        # Verify department exists
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Current patients count
        current_count = db.query(PatientDepartment).filter(
            PatientDepartment.DepartmentId == department_id,
            PatientDepartment.Current == True
        ).count()
        
        # Total patients ever assigned to this department
        total_count = db.query(PatientDepartment).filter(
            PatientDepartment.DepartmentId == department_id
        ).count()
        
        # Recent admissions (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_count = db.query(PatientDepartment).filter(
            PatientDepartment.DepartmentId == department_id,
            PatientDepartment.At >= week_ago,
            PatientDepartment.Current == True
        ).count()
        
        return {
            'current_patients': current_count,
            'total_patients': total_count,
            'recent_admissions': recent_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/department_patients/{department_id}", response_model=dict)
async def get_department_patients(department_id: int, db: Session = Depends(get_db)):
    """Get all patients currently assigned to a specific department"""
    try:
        # Verify department exists
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Get current patients in this department
        results = db.query(
            PatientDepartment.PatientId,
            PatientDepartment.DepartmentId,
            PatientDepartment.Current,
            PatientDepartment.At,
            Patient.PatientAge,
            Patient.PatientAddress,
            Patient.PatientGender,
            Patient.PatientName,
            Patient.PatientPhone,
            Patient.PatientCCCD,
            Patient.PatientBHYT,
            Patient.PatientBHYTValid,
            Patient.PatientRelative,
            Patient.Allergy,
            Patient.History,
            Patient.PatientNote,
            Department.DepartmentName,
            Department.DepartmentType
        ).join(
            Patient, PatientDepartment.PatientId == Patient.PatientId
        ).join(
            Department, PatientDepartment.DepartmentId == Department.DepartmentId
        ).filter(
            PatientDepartment.DepartmentId == department_id,
            PatientDepartment.Current == True
        ).order_by(PatientDepartment.At.desc()).all()
        
        patients_data = []
        for result in results:
            # Convert result to dictionary with all fields (matching Flask structure)
            patient_dict = {
                'PatientId': result.PatientId,
                'DepartmentId': result.DepartmentId,
                'Current': result.Current,
                'At': result.At.isoformat() if result.At else None,
                'PatientAge': result.PatientAge,
                'PatientAddress': result.PatientAddress,
                'PatientGender': result.PatientGender,
                'PatientName': result.PatientName,
                'PatientPhone': result.PatientPhone,
                'PatientCCCD': result.PatientCCCD,
                'PatientBHYT': result.PatientBHYT,
                'PatientBHYTValid': result.PatientBHYTValid,
                'PatientRelative': result.PatientRelative,
                'Allergy': result.Allergy,
                'History': result.History,
                'PatientNote': result.PatientNote,
                'DepartmentName': result.DepartmentName,
                'DepartmentType': result.DepartmentType
            }
            patients_data.append(patient_dict)
        
        return {
            'department': {
                'DepartmentId': department.DepartmentId,
                'DepartmentName': department.DepartmentName,
                'DepartmentType': department.DepartmentType
            },
            'patients': patients_data,
            'count': len(patients_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/departments/all", response_model=dict)
async def get_all_departments_with_stats(db: Session = Depends(get_db)):
    """Get all departments with their patient statistics"""
    try:
        departments = db.query(Department).all()
        
        departments_data = []
        for dept in departments:
            # Get current patient count for this department
            current_count = db.query(PatientDepartment).filter(
                PatientDepartment.DepartmentId == dept.DepartmentId,
                PatientDepartment.Current == True
            ).count()
            
            dept_dict = {
                'DepartmentId': dept.DepartmentId,
                'DepartmentName': dept.DepartmentName,
                'DepartmentType': dept.DepartmentType,
                'current_patients': current_count
            }
            departments_data.append(dept_dict)
        
        # Sort by department name
        departments_data.sort(key=lambda x: x['DepartmentName'])
        
        return {'departments': departments_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/department_access/{department_id}", response_model=dict)
async def check_department_access(department_id: int, db: Session = Depends(get_db)):
    """Check if current user has access to a specific department - for future authorization"""
    try:
        # Get department info
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # For now, allow access to all departments
        # In the future, this can be enhanced with proper authorization
        return {
            'has_access': True,
            'department_name': department.DepartmentName,
            'access_level': 'full'  # Can be 'read', 'write', 'full', etc.
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

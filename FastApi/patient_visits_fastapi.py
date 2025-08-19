"""
Patient Visits API endpoints - FastAPI version
Retrieve and manage visits for a specific patient with relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

# Import database models and session
from models_main import get_db
from models.Patient import Patient
from models.Visit import Visit
from models.Department import Department
from models.Staff import Staff
from models.VisitDiagnosis import VisitDiagnosis

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Patient Visits"])

# Pydantic models
class VisitResponse(BaseModel):
    VisitId: int
    PatientId: str
    DepartmentId: int
    VisitPurpose: Optional[str] = None
    VisitTime: Optional[str] = None
    StaffId: int
    DepartmentName: Optional[str] = None
    StaffName: Optional[str] = None
    StaffRole: Optional[str] = None

class VisitCreate(BaseModel):
    PatientId: str
    DepartmentId: int
    VisitPurpose: Optional[str] = None
    StaffId: int

@router.get("/patient_visits/{patient_id}", response_model=dict)
async def get_patient_visits(patient_id: str, db: Session = Depends(get_db)):
    """Get all visits for a specific patient"""
    try:
        # Check if patient exists
        patient = db.query(Patient).get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Query visits with related data
        results = db.query(
            Visit.VisitId,
            Visit.PatientId, 
            Visit.DepartmentId,
            Visit.VisitPurpose,
            Visit.VisitTime,
            Visit.StaffId,
            Department.DepartmentName,
            Staff.StaffName,
            Staff.StaffRole
        ).join(
            Department, Department.DepartmentId == Visit.DepartmentId
        ).join(
            Staff, Staff.StaffId == Visit.StaffId
        ).filter(
            Visit.PatientId == patient_id
        ).order_by(
            desc(Visit.VisitTime)
        ).all()
        
        # Convert results to dictionaries
        visits_data = []
        for r in results:
            visit_dict = {
                'VisitId': r.VisitId,
                'PatientId': r.PatientId,
                'DepartmentId': r.DepartmentId,
                'VisitPurpose': r.VisitPurpose,
                'VisitTime': r.VisitTime.isoformat() if r.VisitTime else None,
                'StaffId': r.StaffId,
                'DepartmentName': r.DepartmentName,
                'StaffName': r.StaffName,
                'StaffRole': r.StaffRole
            }
            visits_data.append(visit_dict)
        
        return {
            'patient_visits': visits_data,
            'patient_info': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientAge': patient.PatientAge,
                'PatientGender': patient.PatientGender
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visits/{visit_id}", response_model=dict)
async def get_visit_details(visit_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific visit"""
    try:
        # Query visit with related data
        result = db.query(
            Visit.VisitId,
            Visit.PatientId,
            Visit.DepartmentId,
            Visit.VisitPurpose,
            Visit.VisitTime,
            Visit.StaffId,
            Department.DepartmentName,
            Staff.StaffName,
            Staff.StaffRole,
            Patient.PatientName,
            Patient.PatientAge,
            Patient.PatientGender
        ).join(
            Department, Department.DepartmentId == Visit.DepartmentId
        ).join(
            Staff, Staff.StaffId == Visit.StaffId
        ).join(
            Patient, Patient.PatientId == Visit.PatientId
        ).filter(
            Visit.VisitId == visit_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Visit not found")
        
        # Get visit diagnoses
        diagnoses = db.query(VisitDiagnosis).filter(
            VisitDiagnosis.VisitId == visit_id
        ).all()
        
        diagnoses_data = []
        for diagnosis in diagnoses:
            diag_dict = {
                'DiagnosisId': diagnosis.DiagnosisId,
                'ICDCode': diagnosis.ICDCode,
                'DiagnosisDescription': diagnosis.DiagnosisDescription,
                'DiagnosisType': diagnosis.DiagnosisType
            }
            diagnoses_data.append(diag_dict)
        
        visit_dict = {
            'VisitId': result.VisitId,
            'PatientId': result.PatientId,
            'PatientName': result.PatientName,
            'PatientAge': result.PatientAge,
            'PatientGender': result.PatientGender,
            'DepartmentId': result.DepartmentId,
            'DepartmentName': result.DepartmentName,
            'VisitPurpose': result.VisitPurpose,
            'VisitTime': result.VisitTime.isoformat() if result.VisitTime else None,
            'StaffId': result.StaffId,
            'StaffName': result.StaffName,
            'StaffRole': result.StaffRole,
            'diagnoses': diagnoses_data
        }
        
        return {'visit': visit_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visits", response_model=dict)
async def create_visit(visit_data: VisitCreate, db: Session = Depends(get_db)):
    """Create a new patient visit"""
    try:
        # Validate patient exists
        patient = db.query(Patient).get(visit_data.PatientId)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate department exists
        department = db.query(Department).get(visit_data.DepartmentId)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Validate staff exists
        staff = db.query(Staff).get(visit_data.StaffId)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        new_visit = Visit(
            PatientId=visit_data.PatientId,
            DepartmentId=visit_data.DepartmentId,
            VisitPurpose=visit_data.VisitPurpose,
            StaffId=visit_data.StaffId,
            VisitTime=datetime.now()
        )
        
        db.add(new_visit)
        db.commit()
        db.refresh(new_visit)
        
        visit_dict = {
            'VisitId': new_visit.VisitId,
            'PatientId': new_visit.PatientId,
            'DepartmentId': new_visit.DepartmentId,
            'VisitPurpose': new_visit.VisitPurpose,
            'VisitTime': new_visit.VisitTime.isoformat() if new_visit.VisitTime else None,
            'StaffId': new_visit.StaffId,
            'DepartmentName': department.DepartmentName,
            'StaffName': staff.StaffName,
            'StaffRole': staff.StaffRole
        }
        
        return {'visit': visit_dict, 'message': 'Visit created successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visits", response_model=dict)
async def list_visits(
    department_id: Optional[int] = Query(None, description="Filter by department"),
    staff_id: Optional[int] = Query(None, description="Filter by staff member"),
    from_date: Optional[str] = Query(None, description="Filter visits from this date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter visits to this date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, description="Maximum number of visits to return"),
    db: Session = Depends(get_db)
):
    """List all visits with optional filters"""
    try:
        query = db.query(
            Visit.VisitId,
            Visit.PatientId,
            Visit.DepartmentId,
            Visit.VisitPurpose,
            Visit.VisitTime,
            Visit.StaffId,
            Department.DepartmentName,
            Staff.StaffName,
            Staff.StaffRole,
            Patient.PatientName
        ).join(
            Department, Department.DepartmentId == Visit.DepartmentId
        ).join(
            Staff, Staff.StaffId == Visit.StaffId
        ).join(
            Patient, Patient.PatientId == Visit.PatientId
        )
        
        # Apply filters
        if department_id:
            query = query.filter(Visit.DepartmentId == department_id)
            
        if staff_id:
            query = query.filter(Visit.StaffId == staff_id)
            
        if from_date:
            try:
                from_datetime = datetime.fromisoformat(from_date)
                query = query.filter(Visit.VisitTime >= from_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid from_date format. Use YYYY-MM-DD")
                
        if to_date:
            try:
                to_datetime = datetime.fromisoformat(to_date)
                query = query.filter(Visit.VisitTime <= to_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid to_date format. Use YYYY-MM-DD")
        
        results = query.order_by(desc(Visit.VisitTime)).limit(limit).all()
        
        visits_data = []
        for r in results:
            visit_dict = {
                'VisitId': r.VisitId,
                'PatientId': r.PatientId,
                'PatientName': r.PatientName,
                'DepartmentId': r.DepartmentId,
                'DepartmentName': r.DepartmentName,
                'VisitPurpose': r.VisitPurpose,
                'VisitTime': r.VisitTime.isoformat() if r.VisitTime else None,
                'StaffId': r.StaffId,
                'StaffName': r.StaffName,
                'StaffRole': r.StaffRole
            }
            visits_data.append(visit_dict)
        
        return {'visits': visits_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

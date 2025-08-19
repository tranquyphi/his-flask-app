"""
Visits API endpoints - FastAPI version
Basic CRUD operations for Visit management with relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import datetime

# Import database models and session
from models_main import get_db
from models.Visit import Visit
from models.Patient import Patient
from models.Department import Department
from models.Staff import Staff

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Visits"])

# Pydantic models
class VisitResponse(BaseModel):
    VisitId: int
    PatientId: str
    DepartmentId: int
    StaffId: int
    VisitPurpose: Optional[str] = None
    VisitTime: Optional[str] = None
    PatientName: Optional[str] = None
    DepartmentName: Optional[str] = None
    StaffName: Optional[str] = None

class VisitCreate(BaseModel):
    PatientId: str
    DepartmentId: int
    StaffId: int
    VisitPurpose: Optional[str] = None

class VisitUpdate(BaseModel):
    PatientId: Optional[str] = None
    DepartmentId: Optional[int] = None
    StaffId: Optional[int] = None
    VisitPurpose: Optional[str] = None

def visit_to_dict(visit, patient_name=None, department_name=None, staff_name=None):
    """Convert Visit to dictionary with optional related data"""
    result = {
        'VisitId': visit.VisitId,
        'PatientId': visit.PatientId,
        'DepartmentId': visit.DepartmentId,
        'StaffId': visit.StaffId,
        'VisitPurpose': visit.VisitPurpose,
        'VisitTime': visit.VisitTime.isoformat() if visit.VisitTime else None
    }
    
    # Add related information if available
    if patient_name:
        result['PatientName'] = patient_name
    if department_name:
        result['DepartmentName'] = department_name
    if staff_name:
        result['StaffName'] = staff_name
    
    return result

@router.get("/visits", response_model=dict)
async def list_visits(
    patient_id: Optional[str] = Query(None, description="Filter by PatientId"),
    department_id: Optional[int] = Query(None, description="Filter by DepartmentId"),
    staff_id: Optional[int] = Query(None, description="Filter by StaffId"),
    purpose: Optional[str] = Query(None, description="Filter by VisitPurpose"),
    date_from: Optional[str] = Query(None, description="Filter visits from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter visits to date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, description="Limit number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """List visits with optional filters and search"""
    try:
        # Base query with joins for related data
        query = db.query(
            Visit,
            Patient.PatientName,
            Department.DepartmentName,
            Staff.StaffName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).join(
            Department, Visit.DepartmentId == Department.DepartmentId, isouter=True
        ).join(
            Staff, Visit.StaffId == Staff.StaffId, isouter=True
        )
        
        # Apply filters
        if patient_id:
            query = query.filter(Visit.PatientId == patient_id)
            
        if department_id:
            query = query.filter(Visit.DepartmentId == department_id)
            
        if staff_id:
            query = query.filter(Visit.StaffId == staff_id)
            
        if purpose:
            query = query.filter(Visit.VisitPurpose.like(f"%{purpose}%"))
            
        if date_from:
            try:
                from_datetime = datetime.fromisoformat(date_from)
                query = query.filter(Visit.VisitTime >= from_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
                
        if date_to:
            try:
                to_datetime = datetime.fromisoformat(date_to)
                query = query.filter(Visit.VisitTime <= to_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
        
        # Apply pagination and ordering
        results = query.order_by(desc(Visit.VisitTime)).offset(offset).limit(limit).all()
        
        visits_data = []
        for visit, patient_name, department_name, staff_name in results:
            visit_dict = visit_to_dict(visit, patient_name, department_name, staff_name)
            visits_data.append(visit_dict)
        
        return {'visits': visits_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visits/{visit_id}", response_model=dict)
async def get_visit(visit_id: int, db: Session = Depends(get_db)):
    """Get a specific visit by ID"""
    try:
        result = db.query(
            Visit,
            Patient.PatientName,
            Department.DepartmentName,
            Staff.StaffName
        ).join(
            Patient, Visit.PatientId == Patient.PatientId, isouter=True
        ).join(
            Department, Visit.DepartmentId == Department.DepartmentId, isouter=True
        ).join(
            Staff, Visit.StaffId == Staff.StaffId, isouter=True
        ).filter(Visit.VisitId == visit_id).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Visit not found")
        
        visit, patient_name, department_name, staff_name = result
        visit_dict = visit_to_dict(visit, patient_name, department_name, staff_name)
        
        return {'visit': visit_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visits", response_model=dict)
async def create_visit(visit_data: VisitCreate, db: Session = Depends(get_db)):
    """Create a new visit"""
    try:
        # Validate foreign key relationships
        patient = db.query(Patient).get(visit_data.PatientId)
        if not patient:
            raise HTTPException(status_code=400, detail="Patient not found")
        
        department = db.query(Department).get(visit_data.DepartmentId)
        if not department:
            raise HTTPException(status_code=400, detail="Department not found")
        
        staff = db.query(Staff).get(visit_data.StaffId)
        if not staff:
            raise HTTPException(status_code=400, detail="Staff member not found")
        
        new_visit = Visit(
            PatientId=visit_data.PatientId,
            DepartmentId=visit_data.DepartmentId,
            StaffId=visit_data.StaffId,
            VisitPurpose=visit_data.VisitPurpose,
            VisitTime=datetime.now()
        )
        
        db.add(new_visit)
        db.commit()
        db.refresh(new_visit)
        
        visit_dict = visit_to_dict(
            new_visit,
            patient.PatientName,
            department.DepartmentName,
            staff.StaffName
        )
        
        return {'visit': visit_dict, 'message': 'Visit created successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/visits/{visit_id}", response_model=dict)
async def update_visit(visit_id: int, visit_data: VisitUpdate, db: Session = Depends(get_db)):
    """Update an existing visit"""
    try:
        visit = db.query(Visit).get(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        
        # Validate foreign key relationships if they're being updated
        patient_name, department_name, staff_name = None, None, None
        
        if visit_data.PatientId:
            patient = db.query(Patient).get(visit_data.PatientId)
            if not patient:
                raise HTTPException(status_code=400, detail="Patient not found")
            patient_name = patient.PatientName
            visit.PatientId = visit_data.PatientId
        
        if visit_data.DepartmentId:
            department = db.query(Department).get(visit_data.DepartmentId)
            if not department:
                raise HTTPException(status_code=400, detail="Department not found")
            department_name = department.DepartmentName
            visit.DepartmentId = visit_data.DepartmentId
        
        if visit_data.StaffId:
            staff = db.query(Staff).get(visit_data.StaffId)
            if not staff:
                raise HTTPException(status_code=400, detail="Staff member not found")
            staff_name = staff.StaffName
            visit.StaffId = visit_data.StaffId
        
        if visit_data.VisitPurpose is not None:
            visit.VisitPurpose = visit_data.VisitPurpose
        
        db.commit()
        db.refresh(visit)
        
        # Get current related data if not updated
        if not patient_name:
            patient = db.query(Patient).get(visit.PatientId)
            patient_name = patient.PatientName if patient else None
        
        if not department_name:
            department = db.query(Department).get(visit.DepartmentId)
            department_name = department.DepartmentName if department else None
        
        if not staff_name:
            staff = db.query(Staff).get(visit.StaffId)
            staff_name = staff.StaffName if staff else None
        
        visit_dict = visit_to_dict(visit, patient_name, department_name, staff_name)
        
        return {'visit': visit_dict, 'message': 'Visit updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/visits/{visit_id}", response_model=dict)
async def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    """Delete a visit"""
    try:
        visit = db.query(Visit).get(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        
        db.delete(visit)
        db.commit()
        
        return {'message': 'Visit deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

"""
Departments API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.Department import Department

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Departments"])

# Pydantic models for request/response
class DepartmentResponse(BaseModel):
    DepartmentId: int
    DepartmentName: str
    DepartmentType: Optional[str] = None

class DepartmentCreate(BaseModel):
    DepartmentName: str
    DepartmentType: Optional[str] = None

@router.get("/departments", response_model=dict)
async def get_all_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    try:
        departments = db.query(Department).all()
        result = [dept.to_dict() for dept in departments]
        return {'departments': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments/{department_id}", response_model=dict)
async def get_department(department_id: int, db: Session = Depends(get_db)):
    """Get a specific department by ID"""
    try:
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        return {'department': department.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/departments", response_model=dict)
async def create_department(dept_data: DepartmentCreate, db: Session = Depends(get_db)):
    """Create a new department"""
    try:
        new_dept = Department(
            DepartmentName=dept_data.DepartmentName,
            DepartmentType=dept_data.DepartmentType
        )
        
        db.add(new_dept)
        db.commit()
        db.refresh(new_dept)
        
        return {'department': new_dept.to_dict(), 'message': 'Department created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/departments/{department_id}", response_model=dict)
async def update_department(department_id: int, dept_data: DepartmentCreate, db: Session = Depends(get_db)):
    """Update an existing department"""
    try:
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
            
        department.DepartmentName = dept_data.DepartmentName
        if dept_data.DepartmentType:
            department.DepartmentType = dept_data.DepartmentType
            
        db.commit()
        db.refresh(department)
        
        return {'department': department.to_dict(), 'message': 'Department updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/departments/{department_id}", response_model=dict)
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    """Delete a department"""
    try:
        department = db.query(Department).get(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
            
        db.delete(department)
        db.commit()
        
        return {'message': 'Department deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

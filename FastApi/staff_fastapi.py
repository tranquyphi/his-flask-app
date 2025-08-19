"""
Staff API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

# Import database models and session
from models_main import get_db
from models.Staff import Staff
from models.Department import Department  
from models.StaffDepartment import StaffDepartment

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Staff"])

# Pydantic models for request/response
class StaffResponse(BaseModel):
    StaffId: int
    StaffName: str
    StaffRole: Optional[str] = None
    StaffAvailable: Optional[bool] = True
    DepartmentId: Optional[int] = None
    DepartmentName: Optional[str] = None

class StaffCreate(BaseModel):
    StaffName: str
    StaffRole: Optional[str] = None
    StaffAvailable: Optional[bool] = True

class StaffUpdate(BaseModel):
    StaffName: Optional[str] = None
    StaffRole: Optional[str] = None  
    StaffAvailable: Optional[bool] = None

@router.get("/staff", response_model=dict)
async def get_all_staff(db: Session = Depends(get_db)):
    """Get all staff members with their current department"""
    try:
        staff_list = db.query(Staff).all()
        result = []
        
        for staff in staff_list:
            # Create dict manually to avoid Flask context issues
            staff_dict = {
                'StaffId': staff.StaffId,
                'StaffName': staff.StaffName,
                'StaffRole': staff.StaffRole,
                'StaffAvailable': staff.StaffAvailable,
            }
            
            # Get current department manually
            current_dept_assignment = db.query(StaffDepartment).filter_by(
                StaffId=staff.StaffId, 
                Current=True
            ).first()
            
            if current_dept_assignment:
                department = db.query(Department).get(current_dept_assignment.DepartmentId)
                staff_dict['CurrentDepartmentId'] = department.DepartmentId if department else None
                staff_dict['CurrentDepartmentName'] = department.DepartmentName if department else None
            else:
                staff_dict['CurrentDepartmentId'] = None
                staff_dict['CurrentDepartmentName'] = None
                
            result.append(staff_dict)
            
        return {'staff': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/staff/{staff_id}", response_model=dict)
async def get_staff(staff_id: int, db: Session = Depends(get_db)):
    """Get a specific staff member by ID"""
    try:
        staff = db.query(Staff).get(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
            
        # Create dict manually to avoid Flask context issues
        staff_dict = {
            'StaffId': staff.StaffId,
            'StaffName': staff.StaffName,
            'StaffRole': staff.StaffRole,
            'StaffAvailable': staff.StaffAvailable,
        }
        
        # Get current department manually
        current_dept_assignment = db.query(StaffDepartment).filter_by(
            StaffId=staff.StaffId, 
            Current=True
        ).first()
        
        if current_dept_assignment:
            department = db.query(Department).get(current_dept_assignment.DepartmentId)
            staff_dict['CurrentDepartmentId'] = department.DepartmentId if department else None
            staff_dict['CurrentDepartmentName'] = department.DepartmentName if department else None
        else:
            staff_dict['CurrentDepartmentId'] = None
            staff_dict['CurrentDepartmentName'] = None
            
        return {'staff': staff_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/staff", response_model=dict)
async def create_staff(staff_data: StaffCreate, db: Session = Depends(get_db)):
    """Create a new staff member"""
    try:
        new_staff = Staff(
            StaffName=staff_data.StaffName,
            StaffRole=staff_data.StaffRole,
            StaffAvailable=staff_data.StaffAvailable
        )
        
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        
        # Return manual dict to avoid Flask context
        staff_dict = {
            'StaffId': new_staff.StaffId,
            'StaffName': new_staff.StaffName,
            'StaffRole': new_staff.StaffRole,
            'StaffAvailable': new_staff.StaffAvailable,
        }
        
        return {'staff': staff_dict, 'message': 'Staff created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/staff/{staff_id}", response_model=dict)  
async def update_staff(staff_id: int, staff_data: StaffUpdate, db: Session = Depends(get_db)):
    """Update an existing staff member"""
    try:
        staff = db.query(Staff).get(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
            
        # Update only provided fields
        update_data = staff_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(staff, field, value)
            
        db.commit()
        db.refresh(staff)
        
        return {'staff': staff.to_dict(), 'message': 'Staff updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/staff/{staff_id}", response_model=dict)
async def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    """Delete a staff member"""
    try:
        staff = db.query(Staff).get(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
            
        db.delete(staff)
        db.commit()
        
        return {'message': 'Staff deleted successfully'}
    except HTTPException:
        raise  
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

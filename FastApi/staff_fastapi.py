"""
Staff API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from enum import Enum

# Position enum to match database constraints
class StaffPosition(str, Enum):
    NV = "NV"      # Nhân viên (Staff)
    TK = "TK"      # Tình nguyện (Volunteer)
    PK = "PK"      # Phụ khoa (Assistant)
    DDT = "DDT"    # Điều dưỡng trưởng (Head Nurse)
    KTVT = "KTVT"  # Kỹ thuật viên (Technician)
    KHAC = "KHAC"  # Khác (Other)
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

class DepartmentAssignment(BaseModel):
    DepartmentId: int
    Position: Optional[StaffPosition] = None

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
                staff_dict['DepartmentId'] = department.DepartmentId if department else None
                staff_dict['DepartmentName'] = department.DepartmentName if department else None  # Changed from CurrentDepartmentName
                staff_dict['Position'] = current_dept_assignment.Position
            else:
                staff_dict['DepartmentId'] = None
                staff_dict['DepartmentName'] = None  # Changed from CurrentDepartmentName
                staff_dict['Position'] = None
                
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
            staff_dict['DepartmentId'] = department.DepartmentId if department else None
            staff_dict['DepartmentName'] = department.DepartmentName if department else None  # Changed from CurrentDepartmentName
            staff_dict['Position'] = current_dept_assignment.Position
        else:
            staff_dict['DepartmentId'] = None
            staff_dict['DepartmentName'] = None  # Changed from CurrentDepartmentName
            staff_dict['Position'] = None
            
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

@router.post("/staff/{staff_id}/department", response_model=dict)
async def assign_department(staff_id: int, assignment_data: DepartmentAssignment, db: Session = Depends(get_db)):
    """Assign staff to a department"""
    try:
        # Check if staff exists
        staff = db.query(Staff).get(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
            
        # Check if department exists
        department = db.query(Department).get(assignment_data.DepartmentId)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
            
        # Get current assignment if any
        current_assignment = db.query(StaffDepartment).filter_by(
            StaffId=staff_id,
            Current=True
        ).first()
        
        # If there's a current assignment
        if current_assignment:
            # If department is the same, just update position if provided
            if current_assignment.DepartmentId == assignment_data.DepartmentId:
                if assignment_data.Position:
                    current_assignment.Position = assignment_data.Position
                    
                db.commit()
                return {
                    'message': 'Department assignment updated successfully',
                    'departmentId': assignment_data.DepartmentId,
                    'departmentName': department.DepartmentName
                }
            else:
                # Set current assignment to inactive
                current_assignment.Current = False
        
        # Create new department assignment
        new_assignment = StaffDepartment(
            StaffId=staff_id,
            DepartmentId=assignment_data.DepartmentId,
            Position=assignment_data.Position,
            Current=True
        )
        
        db.add(new_assignment)
        db.commit()
        
        return {
            'message': 'Department assignment updated successfully',
            'departmentId': assignment_data.DepartmentId,
            'departmentName': department.DepartmentName
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/staff/{staff_id}/history", response_model=dict)
async def get_staff_history(staff_id: int, db: Session = Depends(get_db)):
    """Get department assignment history for a staff member"""
    try:
        # Check if staff exists
        staff = db.query(Staff).get(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
            
        # Get all department assignments for this staff
        assignments = db.query(StaffDepartment).filter_by(StaffId=staff_id).all()
        
        result = []
        for assignment in assignments:
            department = db.query(Department).get(assignment.DepartmentId)
            result.append({
                'StaffId': assignment.StaffId,
                'DepartmentId': assignment.DepartmentId,
                'DepartmentName': department.DepartmentName if department else None,
                'Current': assignment.Current,
                'Position': assignment.Position
            })
            
        return {'history': result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

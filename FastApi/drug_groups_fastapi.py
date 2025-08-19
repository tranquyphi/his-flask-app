"""
Drug Groups API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import asc

# Import database models and session
from models_main import get_db
from models.DrugGroup import DrugGroup

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Drug Groups"])

# Pydantic models
class DrugGroupResponse(BaseModel):
    DrugGroupId: int
    DrugGroupName: str
    DrugGroupDescription: Optional[str] = None

class DrugGroupCreate(BaseModel):
    DrugGroupName: str
    DrugGroupDescription: Optional[str] = None

def drug_group_to_dict(group):
    """Convert DrugGroup to dictionary"""
    return {
        'DrugGroupId': group.DrugGroupId,
        'DrugGroupName': group.DrugGroupName,
        'DrugGroupDescription': group.DrugGroupDescription
    }

@router.get("/drug-groups", response_model=dict)
async def list_drug_groups(
    q: Optional[str] = Query(None, description="Search term for drug group name"),
    db: Session = Depends(get_db)
):
    """List all drug groups with optional search"""
    try:
        query = db.query(DrugGroup)
        
        # Search by name if provided
        if q:
            query = query.filter(DrugGroup.DrugGroupName.ilike(f"%{q}%"))
        
        groups = query.order_by(asc(DrugGroup.DrugGroupName)).all()
        data = [drug_group_to_dict(group) for group in groups]
        return {'drug_groups': data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drug-groups/{group_id}", response_model=dict)
async def get_drug_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific drug group by ID"""
    try:
        group = db.query(DrugGroup).get(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Drug group not found")
        
        return {'drug_group': drug_group_to_dict(group)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drug-groups", response_model=dict)
async def create_drug_group(group_data: DrugGroupCreate, db: Session = Depends(get_db)):
    """Create a new drug group"""
    try:
        new_group = DrugGroup(
            DrugGroupName=group_data.DrugGroupName,
            DrugGroupDescription=group_data.DrugGroupDescription
        )
        
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        
        return {'drug_group': drug_group_to_dict(new_group), 'message': 'Drug group created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/drug-groups/{group_id}", response_model=dict)
async def update_drug_group(group_id: int, group_data: DrugGroupCreate, db: Session = Depends(get_db)):
    """Update an existing drug group"""
    try:
        group = db.query(DrugGroup).get(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Drug group not found")
        
        group.DrugGroupName = group_data.DrugGroupName
        if group_data.DrugGroupDescription is not None:
            group.DrugGroupDescription = group_data.DrugGroupDescription
        
        db.commit()
        db.refresh(group)
        
        return {'drug_group': drug_group_to_dict(group), 'message': 'Drug group updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/drug-groups/{group_id}", response_model=dict)
async def delete_drug_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a drug group"""
    try:
        group = db.query(DrugGroup).get(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Drug group not found")
        
        db.delete(group)
        db.commit()
        
        return {'message': 'Drug group deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

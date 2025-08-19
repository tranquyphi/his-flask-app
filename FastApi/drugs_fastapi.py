"""
Drugs API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import asc

# Import database models and session
from models_main import get_db
from models.Drug import Drug
from models.DrugGroup import DrugGroup

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Drugs"])

# Pydantic models
class DrugResponse(BaseModel):
    DrugId: int
    DrugName: str
    DrugChemical: Optional[str] = None
    DrugContent: Optional[str] = None
    DrugFormulation: Optional[str] = None
    DrugRemains: Optional[int] = None
    DrugGroupId: Optional[int] = None
    DrugGroupName: Optional[str] = None
    DrugTherapy: Optional[str] = None
    DrugRoute: Optional[str] = None
    DrugQuantity: Optional[str] = None
    CountStr: Optional[str] = None
    DrugAvailable: Optional[bool] = True
    DrugPriceBHYT: Optional[float] = None
    DrugPriceVP: Optional[float] = None
    DrugNote: Optional[str] = None
    Count: Optional[int] = None

class DrugCreate(BaseModel):
    DrugName: str
    DrugChemical: Optional[str] = None
    DrugContent: Optional[str] = None
    DrugFormulation: Optional[str] = None
    DrugRemains: Optional[int] = None
    DrugGroupId: Optional[int] = None
    DrugTherapy: Optional[str] = None
    DrugRoute: Optional[str] = None
    DrugQuantity: Optional[str] = None
    CountStr: Optional[str] = None
    DrugAvailable: Optional[bool] = True
    DrugPriceBHYT: Optional[float] = None
    DrugPriceVP: Optional[float] = None
    DrugNote: Optional[str] = None
    Count: Optional[int] = None

def drug_to_dict(drug, group_name=None):
    """Convert Drug to dictionary with optional group name"""
    return {
        'DrugId': drug.DrugId,
        'DrugName': drug.DrugName,
        'DrugChemical': drug.DrugChemical,
        'DrugGenericName': drug.DrugChemical,  # Alias for frontend
        'DrugContent': drug.DrugContent,
        'DrugFormulation': drug.DrugFormulation,
        'DrugRemains': drug.DrugRemains,
        'DrugGroupId': drug.DrugGroupId,
        'DrugGroup': group_name,  # Keep for backward compatibility
        'DrugGroupName': group_name,  # Add for frontend consistency
        'DrugTherapy': drug.DrugTherapy,
        'DrugRoute': drug.DrugRoute,
        'DrugQuantity': drug.DrugQuantity,
        'CountStr': drug.CountStr,
        'DrugAvailable': drug.DrugAvailable,
        'DrugPriceBHYT': drug.DrugPriceBHYT,
        'DrugPriceVP': drug.DrugPriceVP,
        'DrugNote': drug.DrugNote,
        'Count': drug.Count
    }

@router.get("/drugs", response_model=dict)
async def list_drugs(
    search: Optional[str] = Query(None, description="Search term for drug name or chemical"),
    group_id: Optional[int] = Query(None, description="Filter by drug group ID"),
    available_only: Optional[bool] = Query(None, description="Show only available drugs"),
    db: Session = Depends(get_db)
):
    """List drugs with optional filters and search"""
    try:
        query = db.query(Drug).join(DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId, isouter=True)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Drug.DrugName.like(search_term)) |
                (Drug.DrugChemical.like(search_term))
            )
        
        if group_id:
            query = query.filter(Drug.DrugGroupId == group_id)
            
        if available_only:
            query = query.filter(Drug.DrugAvailable == True)
        
        # Execute query with group names
        results = query.with_entities(
            Drug.DrugId,
            Drug.DrugName,
            Drug.DrugChemical,
            Drug.DrugContent,
            Drug.DrugFormulation,
            Drug.DrugRemains,
            Drug.DrugGroupId,
            DrugGroup.DrugGroupName,
            Drug.DrugTherapy,
            Drug.DrugRoute,
            Drug.DrugQuantity,
            Drug.CountStr,
            Drug.DrugAvailable,
            Drug.DrugPriceBHYT,
            Drug.DrugPriceVP,
            Drug.DrugNote,
            Drug.Count
        ).order_by(asc(Drug.DrugName)).all()
        
        drugs = []
        for result in results:
            drug_dict = {
                'DrugId': result.DrugId,
                'DrugName': result.DrugName,
                'DrugChemical': result.DrugChemical,
                'DrugGenericName': result.DrugChemical,
                'DrugContent': result.DrugContent,
                'DrugFormulation': result.DrugFormulation,
                'DrugRemains': result.DrugRemains,
                'DrugGroupId': result.DrugGroupId,
                'DrugGroup': result.DrugGroupName,
                'DrugGroupName': result.DrugGroupName,
                'DrugTherapy': result.DrugTherapy,
                'DrugRoute': result.DrugRoute,
                'DrugQuantity': result.DrugQuantity,
                'CountStr': result.CountStr,
                'DrugAvailable': result.DrugAvailable,
                'DrugPriceBHYT': result.DrugPriceBHYT,
                'DrugPriceVP': result.DrugPriceVP,
                'DrugNote': result.DrugNote,
                'Count': result.Count
            }
            drugs.append(drug_dict)
        
        return {'drugs': drugs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drugs/{drug_id}", response_model=dict)
async def get_drug(drug_id: int, db: Session = Depends(get_db)):
    """Get a specific drug by ID"""
    try:
        result = db.query(Drug).join(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId, isouter=True
        ).filter(Drug.DrugId == drug_id).with_entities(
            Drug.DrugId,
            Drug.DrugName,
            Drug.DrugChemical,
            Drug.DrugContent,
            Drug.DrugFormulation,
            Drug.DrugRemains,
            Drug.DrugGroupId,
            DrugGroup.DrugGroupName,
            Drug.DrugTherapy,
            Drug.DrugRoute,
            Drug.DrugQuantity,
            Drug.CountStr,
            Drug.DrugAvailable,
            Drug.DrugPriceBHYT,
            Drug.DrugPriceVP,
            Drug.DrugNote,
            Drug.Count
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        drug_dict = {
            'DrugId': result.DrugId,
            'DrugName': result.DrugName,
            'DrugChemical': result.DrugChemical,
            'DrugGenericName': result.DrugChemical,
            'DrugContent': result.DrugContent,
            'DrugFormulation': result.DrugFormulation,
            'DrugRemains': result.DrugRemains,
            'DrugGroupId': result.DrugGroupId,
            'DrugGroup': result.DrugGroupName,
            'DrugGroupName': result.DrugGroupName,
            'DrugTherapy': result.DrugTherapy,
            'DrugRoute': result.DrugRoute,
            'DrugQuantity': result.DrugQuantity,
            'CountStr': result.CountStr,
            'DrugAvailable': result.DrugAvailable,
            'DrugPriceBHYT': result.DrugPriceBHYT,
            'DrugPriceVP': result.DrugPriceVP,
            'DrugNote': result.DrugNote,
            'Count': result.Count
        }
        
        return {'drug': drug_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drugs", response_model=dict)
async def create_drug(drug_data: DrugCreate, db: Session = Depends(get_db)):
    """Create a new drug"""
    try:
        new_drug = Drug(**drug_data.dict())
        
        db.add(new_drug)
        db.commit()
        db.refresh(new_drug)
        
        # Get group name if group_id provided
        group_name = None
        if new_drug.DrugGroupId:
            group = db.query(DrugGroup).get(new_drug.DrugGroupId)
            group_name = group.DrugGroupName if group else None
        
        drug_dict = drug_to_dict(new_drug, group_name)
        
        return {'drug': drug_dict, 'message': 'Drug created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/drugs/{drug_id}", response_model=dict)
async def update_drug(drug_id: int, drug_data: DrugCreate, db: Session = Depends(get_db)):
    """Update an existing drug"""
    try:
        drug = db.query(Drug).get(drug_id)
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Update fields
        update_data = drug_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(drug, field, value)
        
        db.commit()
        db.refresh(drug)
        
        # Get group name if group_id provided
        group_name = None
        if drug.DrugGroupId:
            group = db.query(DrugGroup).get(drug.DrugGroupId)
            group_name = group.DrugGroupName if group else None
        
        drug_dict = drug_to_dict(drug, group_name)
        
        return {'drug': drug_dict, 'message': 'Drug updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/drugs/{drug_id}", response_model=dict)
async def delete_drug(drug_id: int, db: Session = Depends(get_db)):
    """Delete a drug"""
    try:
        drug = db.query(Drug).get(drug_id)
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        db.delete(drug)
        db.commit()
        
        return {'message': 'Drug deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

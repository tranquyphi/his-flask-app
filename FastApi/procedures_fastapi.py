"""
Procedures API endpoints - FastAPI version
Basic CRUD operations for procedures management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.Proc import Proc

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Procedures"])

# Pydantic models
class ProcedureResponse(BaseModel):
    ProcId: str
    ProcDesc: str
    ProcGroup: Optional[str] = None
    ProcBHYT: Optional[bool] = True
    ProcPriceBHYT: Optional[int] = None
    ProcPriceVP: Optional[int] = None
    ProcAvailable: Optional[bool] = True
    ProcNote: Optional[str] = None

class ProcedureCreate(BaseModel):
    ProcId: str
    ProcDesc: str
    ProcGroup: Optional[str] = None
    ProcBHYT: Optional[bool] = True
    ProcPriceBHYT: Optional[int] = None
    ProcPriceVP: Optional[int] = None
    ProcAvailable: Optional[bool] = True
    ProcNote: Optional[str] = None

@router.get("/procedures", response_model=dict)
async def list_procedures(db: Session = Depends(get_db)):
    """Get all procedures"""
    try:
        procedures = db.query(Proc).all()
        result = []
        for proc in procedures:
            proc_dict = {
                'ProcId': proc.ProcId,
                'ProcDesc': proc.ProcDesc,
                'ProcGroup': proc.ProcGroup,
                'ProcBHYT': proc.ProcBHYT,
                'ProcPriceBHYT': proc.ProcPriceBHYT,
                'ProcPriceVP': proc.ProcPriceVP,
                'ProcAvailable': proc.ProcAvailable,
                'ProcNote': proc.ProcNote
            }
            result.append(proc_dict)
        return {'procedures': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/procedures/{proc_id}", response_model=dict)
async def get_procedure(proc_id: str, db: Session = Depends(get_db)):
    """Get a specific procedure by ID"""
    try:
        proc = db.query(Proc).get(proc_id)
        if not proc:
            raise HTTPException(status_code=404, detail="Procedure not found")
        
        proc_dict = {
            'ProcId': proc.ProcId,
            'ProcDesc': proc.ProcDesc,
            'ProcGroup': proc.ProcGroup,
            'ProcBHYT': proc.ProcBHYT,
            'ProcPriceBHYT': proc.ProcPriceBHYT,
            'ProcPriceVP': proc.ProcPriceVP,
            'ProcAvailable': proc.ProcAvailable,
            'ProcNote': proc.ProcNote
        }
        return {'procedure': proc_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/procedures", response_model=dict)
async def create_procedure(proc_data: ProcedureCreate, db: Session = Depends(get_db)):
    """Create a new procedure"""
    try:
        new_proc = Proc(
            ProcId=proc_data.ProcId,
            ProcDesc=proc_data.ProcDesc,
            ProcGroup=proc_data.ProcGroup,
            ProcBHYT=proc_data.ProcBHYT,
            ProcPriceBHYT=proc_data.ProcPriceBHYT,
            ProcPriceVP=proc_data.ProcPriceVP,
            ProcAvailable=proc_data.ProcAvailable,
            ProcNote=proc_data.ProcNote
        )
        
        db.add(new_proc)
        db.commit()
        db.refresh(new_proc)
        
        proc_dict = {
            'ProcId': new_proc.ProcId,
            'ProcDesc': new_proc.ProcDesc,
            'ProcGroup': new_proc.ProcGroup,
            'ProcBHYT': new_proc.ProcBHYT,
            'ProcPriceBHYT': new_proc.ProcPriceBHYT,
            'ProcPriceVP': new_proc.ProcPriceVP,
            'ProcAvailable': new_proc.ProcAvailable,
            'ProcNote': new_proc.ProcNote
        }
        
        return {'procedure': proc_dict, 'message': 'Procedure created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

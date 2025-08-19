"""
Signs API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.Sign import Sign
from models.BodySystem import BodySystem

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Signs"])

@router.get("/signs", response_model=dict)
async def get_all_signs(
    system_id: Optional[int] = Query(None, description="Filter by body system ID"),
    db: Session = Depends(get_db)
):
    """Get all signs, optionally filtered by body system"""
    try:
        query = db.query(Sign)
        
        if system_id:
            query = query.filter(Sign.SystemId == system_id)
        
        signs = query.all()
        result = []
        
        for sign in signs:
            sign_dict = {
                'SignId': sign.SignId,
                'SignDesc': sign.SignDesc,
                'SignType': sign.SignType,
                'SystemId': sign.SystemId,
                'Speciality': sign.Speciality
            }
            result.append(sign_dict)
            
        return {'signs': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signs/{sign_id}", response_model=dict)
async def get_sign(sign_id: int, db: Session = Depends(get_db)):
    """Get a specific sign by ID"""
    try:
        sign = db.query(Sign).get(sign_id)
        if not sign:
            raise HTTPException(status_code=404, detail="Sign not found")
            
        sign_dict = {
            'SignId': sign.SignId,
            'SignDesc': sign.SignDesc,
            'SignType': sign.SignType,
            'SystemId': sign.SystemId,
            'Speciality': sign.Speciality
        }
        
        return {'sign': sign_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/body_system", response_model=dict)
async def get_all_body_systems(db: Session = Depends(get_db)):
    """Get all body systems"""
    try:
        body_systems = db.query(BodySystem).all()
        result = []
        
        for system in body_systems:
            system_dict = {
                'SystemId': system.SystemId,
                'SystemName': system.SystemName
            }
            result.append(system_dict)
            
        return {'body_systems': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

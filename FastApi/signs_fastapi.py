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
    q: Optional[str] = Query(None, description="Substring search in SignDesc"),
    type: Optional[str] = Query(None, description="SignType filter: 0 or 1"),
    system_id: Optional[int] = Query(None, description="Filter by body system ID"),
    speciality: Optional[str] = Query(None, description="Substring search in Speciality"),
    db: Session = Depends(get_db)
):
    """List signs with optional filters and search"""
    try:
        query = db.query(Sign, BodySystem.SystemName).join(BodySystem, Sign.SystemId == BodySystem.SystemId)
        
        if q:
            query = query.filter(Sign.SignDesc.ilike(f"%{q}%"))
        if type in ('0', '1'):
            query = query.filter(Sign.SignType == (type == '1'))
        if system_id:
            query = query.filter(Sign.SystemId == system_id)
        if speciality:
            query = query.filter(Sign.Speciality.ilike(f"%{speciality}%"))
        
        records = query.order_by(Sign.SignDesc.asc()).all()
        
        data = []
        for sign, system_name in records:
            sign_dict = {
                'SignId': sign.SignId,
                'SignDesc': sign.SignDesc,
                'SignType': 1 if sign.SignType else 0,
                'SystemId': sign.SystemId,
                'Speciality': sign.Speciality,
                'SystemName': system_name
            }
            data.append(sign_dict)
            
        return {'signs': data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signs/{sign_id}", response_model=dict)
async def get_sign(sign_id: int, db: Session = Depends(get_db)):
    """Get a specific sign by ID"""
    try:
        result = db.query(Sign, BodySystem.SystemName).join(
            BodySystem, Sign.SystemId == BodySystem.SystemId
        ).filter(Sign.SignId == sign_id).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Sign not found")
        
        sign, system_name = result
        sign_dict = {
            'SignId': sign.SignId,
            'SignDesc': sign.SignDesc,
            'SignType': 1 if sign.SignType else 0,
            'SystemId': sign.SystemId,
            'Speciality': sign.Speciality,
            'SystemName': system_name
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

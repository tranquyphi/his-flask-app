"""
Body Sites API endpoints - FastAPI version
Converted from Flask blueprint to FastAPI router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.BodySite import BodySite
from models.BodyPart import BodyPart

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Body Sites"])

# Pydantic models
class BodyPartResponse(BaseModel):
    BodyPartId: int
    BodyPartName: str

class BodySiteResponse(BaseModel):
    SiteId: int
    SiteName: str
    BodyPartId: Optional[int] = None
    BodyPartName: Optional[str] = None

class BodySiteCreate(BaseModel):
    SiteName: str
    BodyPartId: Optional[int] = None

@router.get("/body_parts", response_model=dict)
async def list_body_parts(db: Session = Depends(get_db)):
    """Get all body parts"""
    try:
        parts = db.query(BodyPart).order_by(BodyPart.BodyPartName).all()
        result = [
            {"BodyPartId": p.BodyPartId, "BodyPartName": p.BodyPartName} 
            for p in parts
        ]
        return {"body_parts": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/body_sites", response_model=dict)
async def list_body_sites(
    BodyPartId: Optional[int] = Query(None, description="Filter by body part ID"),
    db: Session = Depends(get_db)
):
    """Get all body sites, optionally filtered by body part"""
    try:
        query = db.query(
            BodySite.SiteId,
            BodySite.SiteName,
            BodySite.BodyPartId,
            BodyPart.BodyPartName
        ).join(BodyPart, BodySite.BodyPartId == BodyPart.BodyPartId, isouter=True)
        
        if BodyPartId:
            query = query.filter(BodySite.BodyPartId == BodyPartId)
            
        sites = query.order_by(BodySite.SiteName.asc()).all()
        
        result = [{
            "SiteId": s.SiteId,
            "SiteName": s.SiteName,
            "BodyPartId": s.BodyPartId,
            "BodyPartName": s.BodyPartName
        } for s in sites]
        
        return {"body_sites": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/body_sites/{site_id}", response_model=dict)
async def get_body_site(site_id: int, db: Session = Depends(get_db)):
    """Get a specific body site by ID"""
    try:
        site = db.query(
            BodySite.SiteId,
            BodySite.SiteName,
            BodySite.BodyPartId,
            BodyPart.BodyPartName
        ).join(BodyPart, BodySite.BodyPartId == BodyPart.BodyPartId, isouter=True) \
         .filter(BodySite.SiteId == site_id).first()
        
        if not site:
            raise HTTPException(status_code=404, detail="Body site not found")
        
        result = {
            "SiteId": site.SiteId,
            "SiteName": site.SiteName,
            "BodyPartId": site.BodyPartId,
            "BodyPartName": site.BodyPartName
        }
        
        return {"body_site": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/body_sites", response_model=dict)
async def create_body_site(site_data: BodySiteCreate, db: Session = Depends(get_db)):
    """Create a new body site"""
    try:
        new_site = BodySite(
            SiteName=site_data.SiteName,
            BodyPartId=site_data.BodyPartId
        )
        
        db.add(new_site)
        db.commit()
        db.refresh(new_site)
        
        site_dict = {
            'SiteId': new_site.SiteId,
            'SiteName': new_site.SiteName,
            'BodyPartId': new_site.BodyPartId
        }
        
        return {'body_site': site_dict, 'message': 'Body site created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/body_sites/{site_id}", response_model=dict)
async def update_body_site(site_id: int, site_data: BodySiteCreate, db: Session = Depends(get_db)):
    """Update an existing body site"""
    try:
        site = db.query(BodySite).get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Body site not found")
        
        site.SiteName = site_data.SiteName
        if site_data.BodyPartId is not None:
            site.BodyPartId = site_data.BodyPartId
        
        db.commit()
        db.refresh(site)
        
        site_dict = {
            'SiteId': site.SiteId,
            'SiteName': site.SiteName,
            'BodyPartId': site.BodyPartId
        }
        
        return {'body_site': site_dict, 'message': 'Body site updated successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/body_sites/{site_id}", response_model=dict)
async def delete_body_site(site_id: int, db: Session = Depends(get_db)):
    """Delete a body site"""
    try:
        site = db.query(BodySite).get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Body site not found")
        
        db.delete(site)
        db.commit()
        
        return {'message': 'Body site deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

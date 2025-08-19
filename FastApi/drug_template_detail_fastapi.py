"""
Drug Template Detail API endpoints - FastAPI version
CRUD operations for managing drug template details with relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import asc

# Import database models and session
from models_main import get_db
from models.DrugTemplate import DrugTemplate
from models.DrugTemplateDetail import DrugTemplateDetail
from models.Drug import Drug
from models.DrugGroup import DrugGroup
from models.Department import Department

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Drug Template Details"])

# Pydantic models
class DrugTemplateDetailResponse(BaseModel):
    DrugTemplateId: int
    DrugId: str
    DrugTemplateName: Optional[str] = None
    DepartmentName: Optional[str] = None
    DrugName: Optional[str] = None
    DrugChemical: Optional[str] = None
    DrugGenericName: Optional[str] = None
    DrugContent: Optional[str] = None
    DrugFormulation: Optional[str] = None
    DrugGroupId: Optional[str] = None
    DrugGroupName: Optional[str] = None
    DrugTherapy: Optional[str] = None
    DrugRoute: Optional[str] = None
    DrugAvailable: Optional[bool] = False
    DrugPriceBHYT: Optional[float] = 0
    DrugPriceVP: Optional[float] = 0
    DrugNote: Optional[str] = None

class DrugTemplateDetailCreate(BaseModel):
    DrugTemplateId: int
    DrugId: str

class DrugTemplateDetailBulkCreate(BaseModel):
    DrugTemplateId: int
    DrugIds: List[str]

def template_detail_to_dict(detail, drug=None, template_name=None, department_name=None, group_name=None):
    """Convert DrugTemplateDetail to dictionary with full drug information"""
    result = {
        'DrugTemplateId': detail.DrugTemplateId,
        'DrugId': detail.DrugId,
        'DrugTemplateName': template_name,
        'DepartmentName': department_name
    }
    
    # Add full drug information if available
    if drug:
        result.update({
            'DrugName': drug.DrugName,
            'DrugChemical': drug.DrugChemical,
            'DrugGenericName': drug.DrugChemical,  # Alias for frontend consistency
            'DrugContent': drug.DrugContent,
            'DrugFormulation': drug.DrugFormulation,
            'DrugGroupId': drug.DrugGroupId,
            'DrugGroup': group_name,  # Keep for backward compatibility
            'DrugGroupName': group_name,  # Add for frontend consistency
            'DrugTherapy': drug.DrugTherapy,
            'DrugRoute': drug.DrugRoute,
            'DrugAvailable': drug.DrugAvailable,
            'DrugPriceBHYT': drug.DrugPriceBHYT,
            'DrugPriceVP': drug.DrugPriceVP,
            'DrugNote': drug.DrugNote
        })
    else:
        # Set defaults if drug not found
        result.update({
            'DrugName': None,
            'DrugChemical': None,
            'DrugGenericName': None,
            'DrugContent': None,
            'DrugFormulation': None,
            'DrugGroupId': None,
            'DrugGroup': None,
            'DrugGroupName': None,
            'DrugTherapy': None,
            'DrugRoute': None,
            'DrugAvailable': False,
            'DrugPriceBHYT': 0,
            'DrugPriceVP': 0,
            'DrugNote': ''
        })
    
    return result

@router.get("/drug-templates/{template_id}/drugs", response_model=dict)
async def get_template_drugs(
    template_id: int,
    drug_name: Optional[str] = Query(None, description="Search by drug name or chemical"),
    drug_group_id: Optional[str] = Query(None, description="Filter by drug group ID"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    formulation: Optional[str] = Query(None, description="Filter by formulation"),
    db: Session = Depends(get_db)
):
    """Get all drugs in a specific template with filtering"""
    try:
        # Verify template exists
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        # Base query with joins for full drug information
        query = db.query(
            DrugTemplateDetail,
            Drug,
            DrugGroup.DrugGroupName,
            DrugTemplate.DrugTemplateName,
            Department.DepartmentName
        ).join(
            Drug, DrugTemplateDetail.DrugId == Drug.DrugId
        ).outerjoin(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId
        ).join(
            DrugTemplate, DrugTemplateDetail.DrugTemplateId == DrugTemplate.DrugTemplateId
        ).outerjoin(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId
        ).filter(
            DrugTemplateDetail.DrugTemplateId == template_id
        )
        
        # Apply filters
        if drug_name:
            query = query.filter(
                (Drug.DrugName.ilike(f"%{drug_name}%")) |
                (Drug.DrugChemical.ilike(f"%{drug_name}%"))
            )
        if drug_group_id:
            query = query.filter(Drug.DrugGroupId == drug_group_id)
        if available is not None:
            query = query.filter(Drug.DrugAvailable == available)
        if formulation:
            query = query.filter(Drug.DrugFormulation.ilike(f"%{formulation}%"))
        
        results = query.order_by(asc(Drug.DrugName)).all()
        
        drugs_data = []
        for detail, drug, group_name, template_name, dept_name in results:
            drug_dict = template_detail_to_dict(detail, drug, template_name, dept_name, group_name)
            drugs_data.append(drug_dict)
        
        return {
            'template_drugs': drugs_data,
            'template_info': {
                'DrugTemplateId': template_id,
                'DrugTemplateName': template.DrugTemplateName,
                'count': len(drugs_data)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drug-templates/{template_id}/drugs", response_model=dict)
async def add_drug_to_template(template_id: int, drug_data: DrugTemplateDetailCreate, db: Session = Depends(get_db)):
    """Add a single drug to a template"""
    try:
        # Verify template exists
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        # Verify drug exists
        drug = db.query(Drug).get(drug_data.DrugId)
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Check if association already exists
        existing = db.query(DrugTemplateDetail).filter(
            DrugTemplateDetail.DrugTemplateId == template_id,
            DrugTemplateDetail.DrugId == drug_data.DrugId
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Drug already exists in template")
        
        # Create new association
        new_detail = DrugTemplateDetail(
            DrugTemplateId=template_id,
            DrugId=drug_data.DrugId
        )
        
        db.add(new_detail)
        db.commit()
        
        # Get full drug information for response
        result = db.query(
            DrugTemplateDetail,
            Drug,
            DrugGroup.DrugGroupName,
            DrugTemplate.DrugTemplateName,
            Department.DepartmentName
        ).join(
            Drug, DrugTemplateDetail.DrugId == Drug.DrugId
        ).outerjoin(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId
        ).join(
            DrugTemplate, DrugTemplateDetail.DrugTemplateId == DrugTemplate.DrugTemplateId
        ).outerjoin(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId
        ).filter(
            DrugTemplateDetail.DrugTemplateId == template_id,
            DrugTemplateDetail.DrugId == drug_data.DrugId
        ).first()
        
        if result:
            detail, drug, group_name, template_name, dept_name = result
            drug_dict = template_detail_to_dict(detail, drug, template_name, dept_name, group_name)
        else:
            drug_dict = {'DrugTemplateId': template_id, 'DrugId': drug_data.DrugId}
        
        return {
            'message': 'Drug added to template successfully',
            'template_drug': drug_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drug-templates/{template_id}/drugs/bulk", response_model=dict)
async def add_drugs_to_template_bulk(template_id: int, bulk_data: DrugTemplateDetailBulkCreate, db: Session = Depends(get_db)):
    """Add multiple drugs to a template"""
    try:
        # Verify template exists
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        added_count = 0
        skipped_count = 0
        
        for drug_id in bulk_data.DrugIds:
            # Verify drug exists
            drug = db.query(Drug).get(drug_id)
            if not drug:
                skipped_count += 1
                continue
            
            # Check if association already exists
            existing = db.query(DrugTemplateDetail).filter(
                DrugTemplateDetail.DrugTemplateId == template_id,
                DrugTemplateDetail.DrugId == drug_id
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Create new association
            new_detail = DrugTemplateDetail(
                DrugTemplateId=template_id,
                DrugId=drug_id
            )
            
            db.add(new_detail)
            added_count += 1
        
        db.commit()
        
        return {
            'message': f'Bulk operation completed: {added_count} added, {skipped_count} skipped',
            'added_count': added_count,
            'skipped_count': skipped_count
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/drug-templates/{template_id}/drugs/{drug_id}", response_model=dict)
async def remove_drug_from_template(template_id: int, drug_id: str, db: Session = Depends(get_db)):
    """Remove a drug from a template"""
    try:
        # Find the association
        detail = db.query(DrugTemplateDetail).filter(
            DrugTemplateDetail.DrugTemplateId == template_id,
            DrugTemplateDetail.DrugId == drug_id
        ).first()
        
        if not detail:
            raise HTTPException(status_code=404, detail="Drug not found in template")
        
        db.delete(detail)
        db.commit()
        
        return {
            'message': 'Drug removed from template successfully',
            'DrugTemplateId': template_id,
            'DrugId': drug_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drug-templates/{template_id}/available-drugs", response_model=dict)
async def get_available_drugs_for_template(template_id: int, db: Session = Depends(get_db)):
    """Get drugs that can be added to the template (not already in template)"""
    try:
        # Verify template exists
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        # Get drugs already in template
        existing_drug_ids = db.query(DrugTemplateDetail.DrugId).filter(
            DrugTemplateDetail.DrugTemplateId == template_id
        ).subquery()
        
        # Get available drugs not in template
        available_drugs = db.query(
            Drug,
            DrugGroup.DrugGroupName
        ).outerjoin(
            DrugGroup, Drug.DrugGroupId == DrugGroup.DrugGroupId
        ).filter(
            ~Drug.DrugId.in_(existing_drug_ids),
            Drug.DrugAvailable == True
        ).order_by(asc(Drug.DrugName)).all()
        
        drugs_data = []
        for drug, group_name in available_drugs:
            drug_dict = {
                'DrugId': drug.DrugId,
                'DrugName': drug.DrugName,
                'DrugChemical': drug.DrugChemical,
                'DrugContent': drug.DrugContent,
                'DrugFormulation': drug.DrugFormulation,
                'DrugGroupId': drug.DrugGroupId,
                'DrugGroupName': group_name,
                'DrugTherapy': drug.DrugTherapy,
                'DrugRoute': drug.DrugRoute,
                'DrugAvailable': drug.DrugAvailable,
                'DrugPriceBHYT': drug.DrugPriceBHYT,
                'DrugPriceVP': drug.DrugPriceVP,
                'DrugNote': drug.DrugNote
            }
            drugs_data.append(drug_dict)
        
        return {
            'available_drugs': drugs_data,
            'count': len(drugs_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

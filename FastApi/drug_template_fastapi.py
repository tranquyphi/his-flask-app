"""
Drug Template API endpoints - FastAPI version
CRUD operations for managing drug templates with department relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from sqlalchemy import asc

# Import database models and session
from models_main import get_db
from models.DrugTemplate import DrugTemplate
from models.Department import Department

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Drug Templates"])

# Pydantic models
class DrugTemplateResponse(BaseModel):
    DrugTemplateId: int
    DrugTemplateName: str
    DepartmentId: int
    DepartmentName: Optional[str] = None
    DrugTemplateType: str

class DrugTemplateCreate(BaseModel):
    DrugTemplateName: str
    DepartmentId: int
    DrugTemplateType: str
    
    @validator('DrugTemplateType')
    def validate_template_type(cls, v):
        valid_types = ('BA', 'TD', 'PK', 'CC')
        if v not in valid_types:
            raise ValueError(f'DrugTemplateType must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('DrugTemplateName')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('DrugTemplateName cannot be empty')
        return v.strip()

class DrugTemplateUpdate(BaseModel):
    DrugTemplateName: Optional[str] = None
    DepartmentId: Optional[int] = None
    DrugTemplateType: Optional[str] = None
    
    @validator('DrugTemplateType')
    def validate_template_type(cls, v):
        if v is not None:
            valid_types = ('BA', 'TD', 'PK', 'CC')
            if v not in valid_types:
                raise ValueError(f'DrugTemplateType must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('DrugTemplateName')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('DrugTemplateName cannot be empty')
        return v.strip() if v else v

def drug_template_to_dict(template, department_name=None):
    """Convert DrugTemplate to dictionary with department name"""
    return {
        'DrugTemplateId': template.DrugTemplateId,
        'DrugTemplateName': template.DrugTemplateName,
        'DepartmentId': template.DepartmentId,
        'DepartmentName': department_name,
        'DrugTemplateType': template.DrugTemplateType
    }

@router.get("/drug-templates", response_model=dict)
async def list_drug_templates(
    q: Optional[str] = Query(None, description="Search term for template name"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    template_type: Optional[str] = Query(None, description="Filter by template type (BA, TD, PK, CC)"),
    db: Session = Depends(get_db)
):
    """List drug templates with optional filters and search"""
    try:
        # Get templates with department names
        query = db.query(DrugTemplate, Department.DepartmentName).outerjoin(
            Department, DrugTemplate.DepartmentId == Department.DepartmentId
        )

        # Apply filters
        if q:
            query = query.filter(DrugTemplate.DrugTemplateName.ilike(f"%{q}%"))
        if department_id:
            query = query.filter(DrugTemplate.DepartmentId == department_id)
        if template_type and template_type in ('BA', 'TD', 'PK', 'CC'):
            query = query.filter(DrugTemplate.DrugTemplateType == template_type)

        records = query.order_by(asc(DrugTemplate.DrugTemplateName)).all()
        
        templates_data = []
        for template, dept_name in records:
            template_dict = drug_template_to_dict(template, dept_name)
            templates_data.append(template_dict)
        
        return {'drug_templates': templates_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drug-templates/{template_id}", response_model=dict)
async def get_drug_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific drug template by ID"""
    try:
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        # Get department name if exists
        department = db.query(Department).get(template.DepartmentId) if template.DepartmentId else None
        department_name = department.DepartmentName if department else None
        
        template_dict = drug_template_to_dict(template, department_name)
        
        return {'drug_template': template_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/drug-templates", response_model=dict)
async def create_drug_template(template_data: DrugTemplateCreate, db: Session = Depends(get_db)):
    """Create a new drug template"""
    try:
        # Verify department exists
        department = db.query(Department).get(template_data.DepartmentId)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        # Create new template
        new_template = DrugTemplate(
            DrugTemplateName=template_data.DrugTemplateName,
            DepartmentId=template_data.DepartmentId,
            DrugTemplateType=template_data.DrugTemplateType
        )
        
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        template_dict = drug_template_to_dict(new_template, department.DepartmentName)
        
        return {'drug_template': template_dict}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/drug-templates/{template_id}", response_model=dict)
async def update_drug_template(template_id: int, template_data: DrugTemplateUpdate, db: Session = Depends(get_db)):
    """Update an existing drug template"""
    try:
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")

        # Update fields if provided
        if template_data.DrugTemplateName is not None:
            template.DrugTemplateName = template_data.DrugTemplateName
        
        if template_data.DepartmentId is not None:
            # Verify department exists
            department = db.query(Department).get(template_data.DepartmentId)
            if not department:
                raise HTTPException(status_code=404, detail="Department not found")
            template.DepartmentId = template_data.DepartmentId
        
        if template_data.DrugTemplateType is not None:
            template.DrugTemplateType = template_data.DrugTemplateType

        db.commit()
        
        # Get updated department name
        department = db.query(Department).get(template.DepartmentId) if template.DepartmentId else None
        department_name = department.DepartmentName if department else None
        
        template_dict = drug_template_to_dict(template, department_name)
        
        return {'drug_template': template_dict}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/drug-templates/{template_id}", response_model=dict)
async def delete_drug_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a drug template"""
    try:
        template = db.query(DrugTemplate).get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Drug template not found")
        
        # Check if template is being used by any drug template details
        # This would require importing DrugTemplateDetail model
        # For now, allow deletion - add foreign key constraint check later if needed
        
        db.delete(template)
        db.commit()
        
        return {'message': 'Template deleted', 'DrugTemplateId': template_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

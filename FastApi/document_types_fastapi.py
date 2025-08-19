"""
Document Types API endpoints - FastAPI version
CRUD operations for managing document types
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and session
from models_main import get_db
from models.DocumentType import DocumentType

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Document Types"])

# Pydantic models
class DocumentTypeResponse(BaseModel):
    DocumentTypeId: int
    DocumentTypeName: str

class DocumentTypeCreate(BaseModel):
    DocumentTypeName: str

class DocumentTypeUpdate(BaseModel):
    DocumentTypeName: str

@router.get("/document_types", response_model=dict)
async def list_document_types(db: Session = Depends(get_db)):
    """List all document types"""
    try:
        document_types = db.query(DocumentType).all()
        
        types_data = []
        for doc_type in document_types:
            type_dict = {
                'DocumentTypeId': doc_type.DocumentTypeId,
                'DocumentTypeName': doc_type.DocumentTypeName
            }
            types_data.append(type_dict)
        
        return {'document_types': types_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document_types/{type_id}", response_model=dict)
async def get_document_type(type_id: int, db: Session = Depends(get_db)):
    """Get a specific document type by ID"""
    try:
        document_type = db.query(DocumentType).get(type_id)
        if not document_type:
            raise HTTPException(status_code=404, detail="Document type not found")
        
        type_dict = {
            'DocumentTypeId': document_type.DocumentTypeId,
            'DocumentTypeName': document_type.DocumentTypeName
        }
        
        return {'document_type': type_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document_types", response_model=dict)
async def create_document_type(doc_type_data: DocumentTypeCreate, db: Session = Depends(get_db)):
    """Create a new document type"""
    try:
        # Create new document type
        new_doc_type = DocumentType(
            DocumentTypeName=doc_type_data.DocumentTypeName
        )
        
        db.add(new_doc_type)
        db.commit()
        db.refresh(new_doc_type)
        
        type_dict = {
            'DocumentTypeId': new_doc_type.DocumentTypeId,
            'DocumentTypeName': new_doc_type.DocumentTypeName
        }
        
        return {
            'message': 'Document type created successfully',
            'document_type': type_dict
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/document_types/{type_id}", response_model=dict)
async def update_document_type(type_id: int, doc_type_data: DocumentTypeUpdate, db: Session = Depends(get_db)):
    """Update an existing document type"""
    try:
        document_type = db.query(DocumentType).get(type_id)
        if not document_type:
            raise HTTPException(status_code=404, detail="Document type not found")
        
        # Update fields
        document_type.DocumentTypeName = doc_type_data.DocumentTypeName
        
        db.commit()
        
        type_dict = {
            'DocumentTypeId': document_type.DocumentTypeId,
            'DocumentTypeName': document_type.DocumentTypeName
        }
        
        return {
            'message': 'Document type updated successfully',
            'document_type': type_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document_types/{type_id}", response_model=dict)
async def delete_document_type(type_id: int, db: Session = Depends(get_db)):
    """Delete a document type"""
    try:
        document_type = db.query(DocumentType).get(type_id)
        if not document_type:
            raise HTTPException(status_code=404, detail="Document type not found")
        
        # Check if document type is being used by any documents
        # This would require importing PatientDocuments model
        # For now, allow deletion - add foreign key constraint check later if needed
        
        db.delete(document_type)
        db.commit()
        
        return {'message': 'Document type deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

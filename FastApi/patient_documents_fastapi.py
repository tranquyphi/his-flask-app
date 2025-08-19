"""
Patient Documents API endpoints - FastAPI version
CRUD operations for managing patient documents with relationships
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import uuid
import datetime

# Import database models and session
from models_main import get_db, DOCUMENTS_PATH
from models.PatientDocuments import PatientDocuments
from models.Patient import Patient
from models.DocumentType import DocumentType

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Patient Documents"])

# Pydantic models
class DocumentResponse(BaseModel):
    DocumentId: int
    PatientId: str
    DocumentTypeId: int
    DocumentFileName: str
    DocumentFilePath: str
    DocumentDescription: Optional[str] = None
    UploadDate: Optional[str] = None
    FileSize: Optional[int] = None
    MimeType: Optional[str] = None
    PatientName: Optional[str] = None
    DocumentTypeName: Optional[str] = None

class DocumentCreate(BaseModel):
    PatientId: str
    DocumentTypeId: int
    DocumentDescription: Optional[str] = None

def get_full_document_path():
    """Get the absolute path to the documents directory"""
    return os.path.join(os.getcwd(), DOCUMENTS_PATH.lstrip('/'))

def ensure_documents_dir():
    """Ensure the documents directory exists"""
    docs_path = get_full_document_path()
    if not os.path.exists(docs_path):
        os.makedirs(docs_path, exist_ok=True)
    return docs_path

@router.get("/patient_documents/{patient_id}", response_model=dict)
async def get_patient_documents(patient_id: str, db: Session = Depends(get_db)):
    """Get all documents for a specific patient"""
    try:
        # Verify patient exists
        patient = db.query(Patient).get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Query documents with related data
        results = db.query(
            PatientDocuments.DocumentId,
            PatientDocuments.PatientId,
            PatientDocuments.DocumentTypeId,
            PatientDocuments.DocumentFileName,
            PatientDocuments.DocumentFilePath,
            PatientDocuments.DocumentDescription,
            PatientDocuments.UploadDate,
            PatientDocuments.FileSize,
            PatientDocuments.MimeType,
            Patient.PatientName,
            DocumentType.DocumentTypeName
        ).join(
            Patient, PatientDocuments.PatientId == Patient.PatientId
        ).join(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        ).filter(
            PatientDocuments.PatientId == patient_id
        ).order_by(
            PatientDocuments.UploadDate.desc()
        ).all()
        
        documents_data = []
        for r in results:
            doc_dict = {
                'DocumentId': r.DocumentId,
                'PatientId': r.PatientId,
                'DocumentTypeId': r.DocumentTypeId,
                'DocumentFileName': r.DocumentFileName,
                'DocumentFilePath': r.DocumentFilePath,
                'DocumentDescription': r.DocumentDescription,
                'UploadDate': r.UploadDate.isoformat() if r.UploadDate else None,
                'FileSize': r.FileSize,
                'MimeType': r.MimeType,
                'PatientName': r.PatientName,
                'DocumentTypeName': r.DocumentTypeName
            }
            documents_data.append(doc_dict)
        
        return {
            'patient_documents': documents_data,
            'patient_info': {
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}", response_model=dict)
async def get_document_info(document_id: int, db: Session = Depends(get_db)):
    """Get information about a specific document"""
    try:
        result = db.query(
            PatientDocuments.DocumentId,
            PatientDocuments.PatientId,
            PatientDocuments.DocumentTypeId,
            PatientDocuments.DocumentFileName,
            PatientDocuments.DocumentFilePath,
            PatientDocuments.DocumentDescription,
            PatientDocuments.UploadDate,
            PatientDocuments.FileSize,
            PatientDocuments.MimeType,
            Patient.PatientName,
            DocumentType.DocumentTypeName
        ).join(
            Patient, PatientDocuments.PatientId == Patient.PatientId
        ).join(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        ).filter(
            PatientDocuments.DocumentId == document_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_dict = {
            'DocumentId': result.DocumentId,
            'PatientId': result.PatientId,
            'DocumentTypeId': result.DocumentTypeId,
            'DocumentFileName': result.DocumentFileName,
            'DocumentFilePath': result.DocumentFilePath,
            'DocumentDescription': result.DocumentDescription,
            'UploadDate': result.UploadDate.isoformat() if result.UploadDate else None,
            'FileSize': result.FileSize,
            'MimeType': result.MimeType,
            'PatientName': result.PatientName,
            'DocumentTypeName': result.DocumentTypeName
        }
        
        return {'document': doc_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/upload", response_model=dict)
async def upload_document(
    patient_id: str = Form(...),
    document_type_id: int = Form(...),
    document_description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new document for a patient"""
    try:
        # Validate patient exists
        patient = db.query(Patient).get(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate document type exists
        doc_type = db.query(DocumentType).get(document_type_id)
        if not doc_type:
            raise HTTPException(status_code=404, detail="Document type not found")
        
        # Ensure documents directory exists
        docs_path = ensure_documents_dir()
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(docs_path, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file size
        file_size = len(content)
        
        # Create document record
        new_document = PatientDocuments(
            PatientId=patient_id,
            DocumentTypeId=document_type_id,
            DocumentFileName=file.filename,
            DocumentFilePath=unique_filename,  # Store relative path
            DocumentDescription=document_description,
            UploadDate=datetime.datetime.now(),
            FileSize=file_size,
            MimeType=file.content_type
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        doc_dict = {
            'DocumentId': new_document.DocumentId,
            'PatientId': new_document.PatientId,
            'DocumentTypeId': new_document.DocumentTypeId,
            'DocumentFileName': new_document.DocumentFileName,
            'DocumentFilePath': new_document.DocumentFilePath,
            'DocumentDescription': new_document.DocumentDescription,
            'UploadDate': new_document.UploadDate.isoformat() if new_document.UploadDate else None,
            'FileSize': new_document.FileSize,
            'MimeType': new_document.MimeType,
            'PatientName': patient.PatientName,
            'DocumentTypeName': doc_type.DocumentTypeName
        }
        
        return {'document': doc_dict, 'message': 'Document uploaded successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Clean up uploaded file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/download")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download a document file"""
    try:
        document = db.query(PatientDocuments).get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Construct full file path
        docs_path = get_full_document_path()
        file_path = os.path.join(docs_path, document.DocumentFilePath)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return FileResponse(
            path=file_path,
            filename=document.DocumentFileName,
            media_type=document.MimeType
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=dict)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    try:
        document = db.query(PatientDocuments).get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from filesystem
        docs_path = get_full_document_path()
        file_path = os.path.join(docs_path, document.DocumentFilePath)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.delete(document)
        db.commit()
        
        return {'message': 'Document deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document_types", response_model=dict)
async def get_document_types(db: Session = Depends(get_db)):
    """Get all available document types"""
    try:
        doc_types = db.query(DocumentType).all()
        
        types_data = []
        for doc_type in doc_types:
            type_dict = {
                'DocumentTypeId': doc_type.DocumentTypeId,
                'DocumentTypeName': doc_type.DocumentTypeName
            }
            types_data.append(type_dict)
        
        return {'document_types': types_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Document models for the HIS system.
Includes DocumentType and PatientDocuments models.
"""
import os
from flask import current_app
from models import db

# Path to store document files - defined as global variable for easy migration
DOCUMENTS_PATH = '/static/documents'

class DocumentType(db.Model):
    __tablename__ = 'DocumentType'
    
    DocumentTypeId = db.Column(db.Integer, primary_key=True)
    DocumentTypeName = db.Column(db.String(25), nullable=False)
    
    # Relationships
    patient_documents = db.relationship('PatientDocuments', backref='document_type', lazy=True)
    
    def __repr__(self):
        return f'<DocumentType {self.DocumentTypeId}: {self.DocumentTypeName}>'
    
    def to_dict(self):
        """Convert DocumentType to dictionary"""
        return {
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.DocumentTypeName
        }

class PatientDocuments(db.Model):
    __tablename__ = 'PatientDocuments'
    
    DocumentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(20), db.ForeignKey('Patient.PatientId'), nullable=False)
    DocumentTypeId = db.Column(db.Integer, db.ForeignKey('DocumentType.DocumentTypeId'), nullable=True)
    document_links = db.Column(db.JSON, nullable=False, comment='Structured document links')
    metadata = db.Column(db.JSON, nullable=True, comment='Document metadata and properties')
    original_filename = db.Column(db.String(255), nullable=True, comment='Original file name')
    file_type = db.Column(db.String(50), nullable=True, comment='File MIME type')
    file_size = db.Column(db.Integer, nullable=True, comment='File size in bytes')
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                             onupdate=db.func.current_timestamp())
    
    # Relationships
    patient = db.relationship('Patient', backref='patient_documents', lazy=True)
    
    def __repr__(self):
        return f'<PatientDocument {self.DocumentId}: {self.original_filename} for {self.PatientId}>'
    
    def to_dict(self):
        """Convert PatientDocuments to dictionary"""
        return {
            'DocumentId': self.DocumentId,
            'PatientId': self.PatientId,
            'PatientName': self.patient.PatientName if self.patient else None,
            'PatientAge': self.patient.PatientAge if self.patient else None,
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.document_type.DocumentTypeName if self.document_type else None,
            'document_links': self.document_links,
            'metadata': self.metadata,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S') if self.upload_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None
        }

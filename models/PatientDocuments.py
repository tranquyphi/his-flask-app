"""
PatientDocuments Model
"""

from models_main import db

class PatientDocuments(db.Model):
    __tablename__ = 'PatientDocuments'
    
    DocumentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(20), db.ForeignKey('Patient.PatientId'), nullable=False)
    DocumentTypeId = db.Column(db.Integer, db.ForeignKey('DocumentType.DocumentTypeId'), nullable=True)
    document_links = db.Column(db.JSON, nullable=False, comment='Structured document links')
    document_metadata = db.Column('metadata', db.JSON, nullable=True, comment='Document metadata and properties')
    original_filename = db.Column(db.String(255), nullable=True, comment='Original file name')
    file_type = db.Column(db.String(50), nullable=True, comment='File MIME type')
    file_size = db.Column(db.Integer, nullable=True, comment='File size in bytes')
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                             onupdate=db.func.current_timestamp())
    
    # Relationships
    patient = db.relationship('Patient', backref='patient_documents', lazy=True)
    document_type = db.relationship('DocumentType', backref='patient_documents', lazy=True)
    
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
            'metadata': self.document_metadata,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S') if self.upload_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None
        }

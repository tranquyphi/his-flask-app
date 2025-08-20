"""
PatientDocuments Model
"""

from models_main import db

class PatientDocuments(db.Model):
    __tablename__ = 'PatientDocuments'
    
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    document_links = db.Column(db.JSON, nullable=False)
    document_metadata = db.Column(db.JSON)
    DocumentId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeId = db.Column(db.SmallInteger, db.ForeignKey('DocumentType.DocumentTypeId'))
    FileType = db.Column(db.String(50))
    FileSize = db.Column(db.Integer)
    UploadDate = db.Column(db.DateTime, default=db.func.current_timestamp())
    LastModified = db.Column(db.DateTime, default=db.func.current_timestamp())
    file_path = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
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
            'DocumentTypeId': self.DocumentTypeId,
            'document_links': self.document_links,
            'document_metadata': self.document_metadata,
            'FileType': self.FileType,
            'FileSize': self.FileSize,
            'UploadDate': self.UploadDate.strftime('%Y-%m-%d %H:%M:%S') if self.UploadDate else None,
            'LastModified': self.LastModified.strftime('%Y-%m-%d %H:%M:%S') if self.LastModified else None,
            'file_path': self.file_path,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S') if self.upload_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None
        }

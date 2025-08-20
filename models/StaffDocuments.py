"""
Staff, StaffDocumentType, StaffDocuments Models
"""

from models_main import db
from models.Staff import Staff

class StaffDocumentType(db.Model):
    __tablename__ = 'StaffDocumentType'
    DocumentTypeId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeName = db.Column(db.String(25), nullable=False)
    documents = db.relationship('StaffDocuments', backref='document_type', lazy=True)

    def __repr__(self):
        return f'<StaffDocumentType {self.DocumentTypeId}: {self.DocumentTypeName}>'

    def to_dict(self):
        return {
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.DocumentTypeName
        }

class StaffDocuments(db.Model):
    __tablename__ = 'StaffDocuments'
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    DocumentId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeId = db.Column(db.SmallInteger, db.ForeignKey('StaffDocumentType.DocumentTypeId'))
    document_links = db.Column(db.JSON, nullable=False)
    document_metadata = db.Column(db.JSON)
    FileSize = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    UploadDate = db.Column(db.DateTime, default=db.func.current_timestamp())
    LastModified = db.Column(db.DateTime, default=db.func.current_timestamp())
    original_filename = db.Column(db.String(255))
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    staff = db.relationship('Staff', backref='staff_documents', lazy=True)

    def __repr__(self):
        return f'<StaffDocument {self.DocumentId}: {self.original_filename} for {self.StaffId}>'

    def to_dict(self):
        return {
            'DocumentId': self.DocumentId,
            'StaffId': self.StaffId,
            'StaffName': self.staff.StaffName if self.staff else None,
            'StaffRole': self.staff.StaffRole if self.staff else None,
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.document_type.DocumentTypeName if self.document_type else None,
            'document_links': self.document_links,
            'document_metadata': self.document_metadata,
            'FileSize': self.FileSize,
            'file_type': self.file_type,
            'UploadDate': self.UploadDate.strftime('%Y-%m-%d %H:%M:%S') if self.UploadDate else None,
            'LastModified': self.LastModified.strftime('%Y-%m-%d %H:%M:%S') if self.LastModified else None,
            'original_filename': self.original_filename,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None
        }

"""
DocumentType Model - Represents document type classification
"""
# Import db from models_main to avoid circular import issues
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models_main import db

class DocumentType(db.Model):
    __tablename__ = 'DocumentType'
    
    DocumentTypeId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeName = db.Column(db.String(25), nullable=False)
    
    # Relationships - will be defined when we import PatientDocuments
    
    def __repr__(self):
        return f'<DocumentType {self.DocumentTypeId}: {self.DocumentTypeName}>'
    
    def to_dict(self):
        """Convert DocumentType to dictionary"""
        return {
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.DocumentTypeName
        }

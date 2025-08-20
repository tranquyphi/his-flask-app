"""
VisitDocuments Model
"""

from models_main import db
from sqlalchemy import JSON

class VisitDocuments(db.Model):
    __tablename__ = 'VisitDocuments'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'))
    document_links = db.Column(db.JSON, nullable=False)
    document_metadata = db.Column('metadata', db.JSON)
    DocumentId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeId = db.Column(db.SmallInteger, db.ForeignKey('DocumentType.DocumentTypeId'), nullable=False)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

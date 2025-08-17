"""
VisitDocuments Model
"""

from models_main import db
from sqlalchemy import JSON

class VisitDocuments(db.Model):
    __tablename__ = 'VisitDocuments'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    document_links = db.Column(JSON, nullable=False)
    doc_metadata = db.Column('metadata', JSON)  # Use column name mapping

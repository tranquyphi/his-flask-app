"""
VisitImage Model
"""

from models_main import db
from datetime import datetime

class VisitImage(db.Model):
    __tablename__ = 'VisitImage'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    ImageId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ImageType = db.Column(db.String(50))
    ImageData = db.Column(db.LargeBinary)
    ImageUrl = db.Column(db.String(255))
    Description = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

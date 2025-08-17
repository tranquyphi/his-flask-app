"""
VisitDrug Model
"""

from models_main import db
from datetime import datetime

class VisitDrug(db.Model):
    __tablename__ = 'VisitDrug'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    DrugId = db.Column(db.String(50), db.ForeignKey('Drug.DrugId'), primary_key=True)
    DrugRoute = db.Column(db.String(100))
    DrugQuantity = db.Column(db.Float)
    DrugTimes = db.Column(db.String(100))
    DrugAtTime = db.Column(db.DateTime)
    Note = db.Column(db.String(100))
    DrugStatus = db.Column(db.Enum('CD', 'TH', 'XONG', name='drug_status'), default='CD')
    IsCustom = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert VisitDrug to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'DrugId': self.DrugId,
            'DrugRoute': self.DrugRoute,
            'DrugQuantity': self.DrugQuantity,
            'DrugTimes': self.DrugTimes,
            'DrugAtTime': self.DrugAtTime.isoformat() if self.DrugAtTime else None,
            'Note': self.Note,
            'DrugStatus': self.DrugStatus,
            'IsCustom': self.IsCustom
        }

"""
VisitDiagnosis Model
"""

from models_main import db

class VisitDiagnosis(db.Model):
    __tablename__ = 'VisitDiagnosis'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ICDCode = db.Column(db.String(10), db.ForeignKey('ICD.ICDCode'), primary_key=True)
    ActualDiagnosis = db.Column(db.String(255))
    DiseaseType = db.Column(db.Enum('Bệnh chính', 'Bệnh kèm', 'Biến chứng', name='disease_type'))
    
    def to_dict(self):
        """Convert VisitDiagnosis to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'ICDCode': self.ICDCode,
            'ActualDiagnosis': self.ActualDiagnosis,
            'DiseaseType': self.DiseaseType
        }

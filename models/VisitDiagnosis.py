"""
VisitDiagnosis Model
"""

from models_main import db

class VisitDiagnosis(db.Model):
    __tablename__ = 'VisitDiagnosis'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    ICDCode = db.Column(db.String(10), db.ForeignKey('ICD.ICDCode'), nullable=False)
    ActualDiagnosis = db.Column(db.String(255))
    DiseaseType = db.Column(db.Enum('Bệnh chính', 'Bệnh kèm', 'Biến chứng', name='disease_type'))
    
    def to_dict(self):
        """Convert VisitDiagnosis to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'VisitId': self.VisitId,
            'ICDCode': self.ICDCode,
            'ActualDiagnosis': self.ActualDiagnosis,
            'DiseaseType': self.DiseaseType
        }

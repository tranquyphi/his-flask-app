"""
ICD Model
"""

from models_main import db

class ICD(db.Model):
    __tablename__ = 'ICD'
    
    ICDCode = db.Column(db.String(10), primary_key=True)
    ICDName = db.Column(db.String(255), nullable=False)
    ICDGroup = db.Column(db.String(100), default='')
    
    def __repr__(self):
        return f'<ICD {self.ICDCode}: {self.ICDName}>'

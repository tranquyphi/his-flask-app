"""
BodyPart Model
"""

from models_main import db

class BodyPart(db.Model):
    __tablename__ = 'BodyPart'
    
    BodyPartId = db.Column(db.SmallInteger, primary_key=True)
    BodyPartName = db.Column(db.String(50))
    
    # Relationships
    body_sites = db.relationship('BodySite', backref='body_part', lazy=True)
    
    def __repr__(self):
        return f'<BodyPart {self.BodyPartName}>'

"""
BodySystem Model
"""

from models_main import db

class BodySystem(db.Model):
    __tablename__ = 'BodySystem'
    
    SystemId = db.Column(db.Integer, primary_key=True)
    SystemName = db.Column(db.String(50), nullable=False)
    
    # Relationships
    signs = db.relationship('Sign', backref='body_system', lazy=True)
    
    def __repr__(self):
        return f'<BodySystem {self.SystemName}>'

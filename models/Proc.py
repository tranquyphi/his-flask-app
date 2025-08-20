"""
Proc Model
"""

from models_main import db

class Proc(db.Model):
    __tablename__ = 'Proc'
    
    ProcId = db.Column(db.String(50), primary_key=True)
    ProcDesc = db.Column(db.String(100))
    ProcGroup = db.Column(db.String(100))
    ProcBHYT = db.Column(db.Boolean, default=True)
    ProcPriceBHYT = db.Column(db.Integer, default=0)
    ProcPriceVP = db.Column(db.Integer, default=0)
    ProcAvailable = db.Column(db.Boolean, default=True)
    ProcNote = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Proc {self.ProcDesc}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

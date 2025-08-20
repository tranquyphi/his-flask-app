"""
Drug Model
"""

from models_main import db

class Drug(db.Model):
    __tablename__ = 'Drug'
    
    DrugId = db.Column(db.String(50), primary_key=True)
    DrugName = db.Column(db.String(255))
    DrugChemical = db.Column(db.String(255))
    DrugContent = db.Column(db.String(100))
    DrugFormulation = db.Column(db.String(50))
    DrugRemains = db.Column(db.SmallInteger)
    DrugGroupId = db.Column(db.Integer, db.ForeignKey('DrugGroup.DrugGroupId'))
    DrugTherapy = db.Column(db.String(200))
    DrugRoute = db.Column(db.String(50))
    DrugQuantity = db.Column(db.String(50))
    CountStr = db.Column(db.String(50))
    DrugAvailable = db.Column(db.Boolean, default=True)
    DrugPriceBHYT = db.Column(db.Integer, default=0)
    DrugPriceVP = db.Column(db.Integer, default=0)
    DrugNote = db.Column(db.String(100), default='')
    Count = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Drug {self.DrugName}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

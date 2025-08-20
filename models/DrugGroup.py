"""
DrugGroup Model
"""

from models_main import db

class DrugGroup(db.Model):
    __tablename__ = 'DrugGroup'
    
    DrugGroupId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DrugGroupName = db.Column(db.String(100), nullable=False)
    DrugGroupDescription = db.Column(db.String(255))
    
    # Relationships
    drugs = db.relationship('Drug', backref='drug_group', lazy=True)
    
    def __repr__(self):
        return f'<DrugGroup {self.DrugGroupName}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

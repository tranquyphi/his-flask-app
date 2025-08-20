"""
DrugTemplateDetail Model
"""

from models_main import db

class DrugTemplateDetail(db.Model):
    __tablename__ = 'DrugTemplateDetail'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DrugTemplateId = db.Column(db.SmallInteger, db.ForeignKey('DrugTemplate.DrugTemplateId'))
    DrugId = db.Column(db.String(50), db.ForeignKey('Drug.DrugId'))
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

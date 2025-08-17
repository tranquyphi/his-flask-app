"""
DrugTemplateDetail Model
"""

from models_main import db

class DrugTemplateDetail(db.Model):
    __tablename__ = 'DrugTemplateDetail'
    
    DrugTemplateId = db.Column(db.SmallInteger, db.ForeignKey('DrugTemplate.DrugTemplateId'), primary_key=True)
    DrugId = db.Column(db.String(20), db.ForeignKey('Drug.DrugId'), primary_key=True)

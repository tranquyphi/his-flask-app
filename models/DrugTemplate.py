"""
DrugTemplate Model
"""

from models_main import db

class DrugTemplate(db.Model):
    __tablename__ = 'DrugTemplate'
    
    DrugTemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DrugTemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    DrugTemplateType = db.Column(db.Enum('BA', 'TD', 'PK', 'CC', name='drug_template_type'), default='TD')

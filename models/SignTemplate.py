"""
SignTemplate Model
"""

from models_main import db

class SignTemplate(db.Model):
    __tablename__ = 'SignTemplate'
    
    SignTemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    SignTemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    SignTemplateType = db.Column(db.Enum('BA', 'TD', 'PK', 'CC', name='sign_template_type'), default='TD')

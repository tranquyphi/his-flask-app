"""
Template Model
"""

from models_main import db

class Template(db.Model):
    __tablename__ = 'Template'
    
    TemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    TemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    TemplateGroup = db.Column(db.Enum('Test', 'Sign', 'Drug', 'Proc', name='template_group'))
    TemplateType = db.Column(db.Enum('Bệnh án', 'Theo dõi', name='template_type'))
    
    def __repr__(self):
        return f'<Template {self.TemplateName}>'

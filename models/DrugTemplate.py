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
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

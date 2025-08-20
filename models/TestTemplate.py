"""
TestTemplate Model
"""

from models_main import db

class TestTemplate(db.Model):
    __tablename__ = 'TestTemplate'
    
    TestTemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    TestTemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    TestTemplateType = db.Column(db.Enum('BA', 'TD', 'PK', 'CC'), default='TD')
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

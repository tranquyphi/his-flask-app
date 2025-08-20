"""
TestTemplateDetail Model
"""

from models_main import db

class TestTemplateDetail(db.Model):
    __tablename__ = 'TestTemplateDetail'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    TestTemplateId = db.Column(db.SmallInteger, db.ForeignKey('TestTemplate.TestTemplateId'), nullable=False)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), nullable=False)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

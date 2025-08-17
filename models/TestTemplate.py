"""
TestTemplate Model
"""

from models_main import db

class TestTemplate(db.Model):
    __tablename__ = 'TestTemplate'
    
    TemplateId = db.Column(db.SmallInteger, db.ForeignKey('Template.TemplateId'), primary_key=True)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), primary_key=True)

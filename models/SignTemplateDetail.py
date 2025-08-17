"""
SignTemplateDetail Model
"""

from models_main import db

class SignTemplateDetail(db.Model):
    __tablename__ = 'SignTemplateDetail'
    
    SignTemplateId = db.Column(db.SmallInteger, db.ForeignKey('SignTemplate.SignTemplateId'), primary_key=True)
    SignId = db.Column(db.SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)

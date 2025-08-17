"""
Sign Model
"""

from models_main import db

class Sign(db.Model):
    __tablename__ = 'Sign'
    
    SignId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    SignDesc = db.Column(db.String(100))
    SignType = db.Column(db.Boolean, default=False)  # 0: cơ năng, 1: thực thể
    SystemId = db.Column(db.Integer, db.ForeignKey('BodySystem.SystemId'), nullable=False)
    Speciality = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Sign {self.SignDesc}>'

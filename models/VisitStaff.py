"""
VisitStaff Model
"""

from models_main import db

class VisitStaff(db.Model):
    __tablename__ = 'VisitStaff'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), primary_key=True)

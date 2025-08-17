"""
VisitTest Model
"""

from models_main import db
from datetime import datetime

class VisitTest(db.Model):
    __tablename__ = 'VisitTest'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), primary_key=True)
    TestStatus = db.Column(db.Enum('CD', 'TH', 'XONG', name='test_status'), default='CD')
    TestStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    TestTime = db.Column(db.DateTime)
    TestResult = db.Column(db.String(255))
    TestConclusion = db.Column(db.String(20))
    IsCustom = db.Column(db.Boolean, default=False)

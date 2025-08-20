"""
VisitTest Model
"""

from models_main import db
from datetime import datetime

class VisitTest(db.Model):
    __tablename__ = 'VisitTest'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), nullable=False)
    TestStatus = db.Column(db.Enum('CD', 'TH', 'XONG', name='test_status'), default='CD')
    TestStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    TestTime = db.Column(db.DateTime)
    TestResult = db.Column(db.String(255))
    TestConclusion = db.Column(db.String(20))
    IsCustom = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

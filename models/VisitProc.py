"""
VisitProc Model
"""

from models_main import db
from datetime import datetime

class VisitProc(db.Model):
    __tablename__ = 'VisitProc'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    ProcId = db.Column(db.String(50), db.ForeignKey('Proc.ProcId'), nullable=False)
    ProcStatus = db.Column(db.Enum('Ordered', 'In progress', 'Completed', 'Result', name='proc_status'), default='Ordered')
    ProcStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    ProcTime = db.Column(db.DateTime)
    IsCustom = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

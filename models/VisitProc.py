"""
VisitProc Model
"""

from models_main import db
from datetime import datetime

class VisitProc(db.Model):
    __tablename__ = 'VisitProc'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ProcId = db.Column(db.String(50), db.ForeignKey('Proc.ProcId'), primary_key=True)
    ProcStatus = db.Column(db.Enum('Ordered', 'In progress', 'Completed', 'Result', name='proc_status'), default='Ordered')
    ProcStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    ProcTime = db.Column(db.DateTime)
    IsCustom = db.Column(db.Boolean, default=False)

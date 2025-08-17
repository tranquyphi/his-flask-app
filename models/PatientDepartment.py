"""
PatientDepartment Model
"""

from models_main import db
from datetime import datetime

class PatientDepartment(db.Model):
    __tablename__ = 'PatientDepartment'
    
    # Add auto-increment ID as primary key to allow multiple assignments
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'), nullable=False)
    Current = db.Column(db.Boolean, default=False)
    At = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientDepartment {self.id}: {self.PatientId}-{self.DepartmentId} at {self.At}>'

"""
Department Model
"""

from models_main import db

class Department(db.Model):
    __tablename__ = 'Department'
    
    DepartmentId = db.Column(db.SmallInteger, primary_key=True)
    DepartmentName = db.Column(db.String(100))
    DepartmentType = db.Column(db.Enum('Nội trú', 'Cấp cứu', 'Phòng khám', name='department_type'))
    
    # Relationships
    staff = db.relationship('Staff', backref='department', lazy=True)
    visits = db.relationship('Visit', backref='department', lazy=True)
    templates = db.relationship('Template', backref='department', lazy=True)
    tests = db.relationship('Test', backref='in_charge_department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.DepartmentName}>'

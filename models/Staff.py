"""
Staff Model
"""

from models_main import db

class Staff(db.Model):
    __tablename__ = 'Staff'
    
    StaffId = db.Column(db.SmallInteger, primary_key=True)
    StaffName = db.Column(db.String(100))
    StaffRole = db.Column(db.Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    StaffAvailable = db.Column(db.Boolean, default=True)
    
    # Relationships
    visits = db.relationship('Visit', backref='attending_staff', lazy=True)
    
    def __repr__(self):
        return f'<Staff {self.StaffName} - {self.StaffRole}>'

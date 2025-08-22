"""
Staff Model
"""

from models_main import db

class Staff(db.Model):
    __tablename__ = 'Staff'
    
    StaffId = db.Column(db.SmallInteger, primary_key=True)
    StaffName = db.Column(db.String(100))
    StaffRole = db.Column(db.Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    StaffAvailable = db.Column(db.Boolean, default=True)
    
    # Relationships
    departments = db.relationship('Department', 
                               secondary='StaffDepartment',
                               primaryjoin='Staff.StaffId == StaffDepartment.StaffId',
                               secondaryjoin='and_(StaffDepartment.DepartmentId == Department.DepartmentId, StaffDepartment.Current == True)',
                               viewonly=True)
                               
    department_assignments = db.relationship('StaffDepartment', 
                                        backref='staff_member',
                                        lazy='dynamic')
    
    # visits = db.relationship('Visit', backref='attending_staff', lazy=True)  # Removed - visits no longer have StaffId
    
    @property
    def current_department(self):
        """Returns the current department of the staff member"""
        from models.StaffDepartment import StaffDepartment
        dept_assign = StaffDepartment.query.filter_by(StaffId=self.StaffId, Current=True).first()
        if dept_assign:
            from models.Department import Department
            return Department.query.get(dept_assign.DepartmentId)
        return None
    
    def __repr__(self):
        return f'<Staff {self.StaffName} - {self.StaffRole}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        current_dept = self.current_department
        return {
            'StaffId': self.StaffId,
            'StaffName': self.StaffName,
            'StaffRole': self.StaffRole,
            'StaffAvailable': self.StaffAvailable,
            'CurrentDepartmentId': current_dept.DepartmentId if current_dept else None,
            'CurrentDepartmentName': current_dept.DepartmentName if current_dept else None
        }

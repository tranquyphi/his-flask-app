"""
Department Model
"""

from models_main import db

class Department(db.Model):
    __tablename__ = 'Department'
    
    DepartmentId = db.Column(db.SmallInteger, primary_key=True)
    DepartmentName = db.Column(db.String(100))
    DepartmentType = db.Column(db.Enum('Nội trú','Cấp cứu','Phòng khám','CLS'))
    
    # Relationships
    staff_members = db.relationship('Staff', 
                                 secondary='StaffDepartment',
                                 primaryjoin='Department.DepartmentId == StaffDepartment.DepartmentId',
                                 secondaryjoin='and_(StaffDepartment.StaffId == Staff.StaffId, StaffDepartment.Current == True)',
                                 viewonly=True)
                                 
    staff_assignments = db.relationship('StaffDepartment', 
                                     backref='department',
                                     lazy='dynamic')
                                     
    visits = db.relationship('Visit', backref='department', lazy=True)
    templates = db.relationship('Template', backref='department', lazy=True)
    tests = db.relationship('Test', backref='in_charge_department', lazy=True)
    
    def get_current_staff(self):
        """Returns all staff currently assigned to this department"""
        from models.StaffDepartment import StaffDepartment
        from models.Staff import Staff
        
        staff_ids = db.session.query(StaffDepartment.StaffId).filter_by(
            DepartmentId=self.DepartmentId,
            Current=True
        ).all()
        
        return Staff.query.filter(Staff.StaffId.in_([s.StaffId for s in staff_ids])).all()
    
    def __repr__(self):
        return f'<Department {self.DepartmentName}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'DepartmentId': self.DepartmentId,
            'DepartmentName': self.DepartmentName,
            'DepartmentType': self.DepartmentType
        }

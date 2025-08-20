"""
StaffDepartment Model - Association model between Staff and Department
"""

from models_main import db

class StaffDepartment(db.Model):
    __tablename__ = 'StaffDepartment'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'), nullable=False)
    Current = db.Column(db.Boolean, default=True)
    Position = db.Column(db.Enum('NV', 'TK', 'PK', 'DDT', 'KTVT', 'KHAC', name='staff_position'), nullable=True)
    
    # Relationships (defined in Department and Staff models)
    
    def __repr__(self):
        return f'<StaffDepartment {self.id}: StaffId={self.StaffId} DepartmentId={self.DepartmentId} Current={self.Current}>'
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'StaffId': self.StaffId,
            'DepartmentId': self.DepartmentId,
            'Current': self.Current,
            'Position': self.Position
        }

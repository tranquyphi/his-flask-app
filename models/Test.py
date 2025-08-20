"""
Test Model
"""

from models_main import db

class Test(db.Model):
    __tablename__ = 'Test'
    
    TestId = db.Column(db.String(50), primary_key=True)
    TestName = db.Column(db.String(100))
    TestGroup = db.Column(db.String(100))
    TestPriceBHYT = db.Column(db.Integer, default=0)
    TestPriceVP = db.Column(db.Integer, default=0)
    TestAvailable = db.Column(db.Boolean, default=True)
    TestNote = db.Column(db.String(100), default='')
    TestType = db.Column(db.Enum('XN', 'SA', 'XQ', 'CT', 'TDCN', 'NS', name='test_type'))
    InChargeDepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    
    def __repr__(self):
        return f'<Test {self.TestName}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

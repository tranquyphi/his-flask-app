"""
Visit Model
"""

from models_main import db
from datetime import datetime

class Visit(db.Model):
    __tablename__ = 'Visit'
    
    VisitId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    VisitPurpose = db.Column(db.Enum(
        'Thường quy', 'Cấp cứu', 'Phòng khám', 'Nhận bệnh', 'Bệnh án',
        'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám', 'Khám chuyên khoa',
        name='visit_purpose'
    ))
    VisitTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    diagnoses = db.relationship('VisitDiagnosis', backref='visit', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('VisitDocuments', backref='visit', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('VisitImage', backref='visit', lazy=True, cascade='all, delete-orphan')
    drugs = db.relationship('VisitDrug', backref='visit', lazy=True, cascade='all, delete-orphan')
    procedures = db.relationship('VisitProc', backref='visit', lazy=True, cascade='all, delete-orphan')
    signs = db.relationship('VisitSign', backref='visit', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('VisitTest', backref='visit', lazy=True, cascade='all, delete-orphan')
    visit_staff = db.relationship('VisitStaff', backref='visit', lazy=True, cascade='all, delete-orphan')
    
    # Many-to-many relationship with Staff through VisitStaff
    staff = db.relationship('Staff', secondary='VisitStaff', lazy='subquery',
                           backref=db.backref('visits', lazy=True))
    
    def to_dict(self):
        """Convert Visit to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'PatientId': self.PatientId,
            'VisitPurpose': self.VisitPurpose,
            'VisitTime': self.VisitTime.isoformat() if self.VisitTime else None
        }
    
    def __repr__(self):
        return f'<Visit {self.VisitId}: {self.PatientId} - {self.VisitPurpose}>'


class VisitStaff(db.Model):
    """VisitStaff association table for many-to-many relationship between Visit and Staff"""
    __tablename__ = 'VisitStaff'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId', ondelete='CASCADE'), nullable=False)
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    
    # Additional relationship to Staff for easier access
    staff = db.relationship('Staff', backref='visit_staff_associations')
    
    def to_dict(self):
        """Convert VisitStaff to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'VisitId': self.VisitId,
            'StaffId': self.StaffId
        }
    
    def __repr__(self):
        return f'<VisitStaff {self.VisitId}:{self.StaffId}>'

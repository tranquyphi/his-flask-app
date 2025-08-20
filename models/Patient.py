"""
Patient Model
"""

from models_main import db

class Patient(db.Model):
    __tablename__ = 'Patient'
    
    PatientId = db.Column(db.String(10), primary_key=True)
    PatientName = db.Column(db.String(100))
    PatientGender = db.Column(db.Enum('Nam', 'Nữ', 'Khác', name='gender'))
    PatientAge = db.Column(db.String(20))
    PatientAddress = db.Column(db.String(255))
    Allergy = db.Column(db.String(255), default='')
    History = db.Column(db.Text)
    PatientImage = db.Column(db.LargeBinary, default=None)
    PatientNote = db.Column(db.String(100), default='')
    # Adding missing fields from schema
    PatientPhone = db.Column(db.String(20))
    PatientCCCD = db.Column(db.String(20))
    PatientBHYT = db.Column(db.String(20))
    PatientBHYTValid = db.Column(db.String(100))
    PatientRelative = db.Column(db.String(100))
    
    # Relationships
    visits = db.relationship('Visit', backref='patient', lazy=True)
    patient_departments = db.relationship('PatientDepartment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.PatientId}: {self.PatientName}>'
        
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'PatientId': self.PatientId,
            'PatientName': self.PatientName,
            'PatientGender': self.PatientGender,
            'PatientAge': self.PatientAge,
            'PatientAddress': self.PatientAddress,
            'Allergy': self.Allergy,
            'History': self.History,
            'PatientNote': self.PatientNote,
            'PatientPhone': self.PatientPhone,
            'PatientCCCD': self.PatientCCCD,
            'PatientBHYT': self.PatientBHYT,
            'PatientBHYTValid': self.PatientBHYTValid,
            'PatientRelative': self.PatientRelative
        }

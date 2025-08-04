"""
Database Models for HIS (Hospital Information System)
MariaDB/MySQL Database Connection and SQLAlchemy ORM Models
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON
import os
from config import config

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app(config_name=None):
    """Create and configure Flask application with database connection"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize database with app
    db.init_app(app)
    
    return app

# ===========================================
# ORM Models based on Database Schema
# ===========================================

class BodySite(db.Model):
    __tablename__ = 'BodySite'
    
    SiteId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SiteName = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<BodySite {self.SiteName}>'

class BodySystem(db.Model):
    __tablename__ = 'BodySystem'
    
    SystemId = db.Column(db.Integer, primary_key=True)
    SystemName = db.Column(db.String(50), nullable=False)
    
    # Relationships
    signs = db.relationship('Sign', backref='body_system', lazy=True)
    
    def __repr__(self):
        return f'<BodySystem {self.SystemName}>'

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

class Drug(db.Model):
    __tablename__ = 'Drug'
    
    DrugId = db.Column(db.String(50), primary_key=True)
    DrugName = db.Column(db.String(255))
    DrugChemical = db.Column(db.String(255))
    DrugContent = db.Column(db.String(100))
    DrugFormulation = db.Column(db.String(50))
    DrugRemains = db.Column(db.SmallInteger)
    DrugGroup = db.Column(db.String(100))
    DrugTherapy = db.Column(db.String(200))
    DrugRoute = db.Column(db.String(50))
    DrugQuantity = db.Column(db.String(50))
    CountStr = db.Column(db.String(50))
    DrugAvailable = db.Column(db.Boolean, default=True)
    DrugPriceBHYT = db.Column(db.Integer, default=0)
    DrugPriceVP = db.Column(db.Integer, default=0)
    DrugNote = db.Column(db.String(100), default='')
    Count = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Drug {self.DrugName}>'

class ICD(db.Model):
    __tablename__ = 'ICD'
    
    ICDCode = db.Column(db.String(10), primary_key=True)
    ICDName = db.Column(db.String(255), nullable=False)
    ICDGroup = db.Column(db.String(100), default='')
    
    def __repr__(self):
        return f'<ICD {self.ICDCode}: {self.ICDName}>'

class Patient(db.Model):
    __tablename__ = 'Patient'
    
    PatientId = db.Column(db.String(10), primary_key=True)
    PatientName = db.Column(db.String(100))
    PatientGender = db.Column(db.Enum('Nam', 'Nữ', 'Khác', name='gender'))
    PatientAge = db.Column(db.String(20))
    PatientAddress = db.Column(db.String(255))
    Allergy = db.Column(db.String(255), default='')
    History = db.Column(db.Text)
    PatientImage = db.Column(db.LargeBinary)
    PatientNote = db.Column(db.String(100), default='')
    
    # Relationships
    visits = db.relationship('Visit', backref='patient', lazy=True)
    patient_departments = db.relationship('PatientDepartment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.PatientId}: {self.PatientName}>'

class Proc(db.Model):
    __tablename__ = 'Proc'
    
    ProcId = db.Column(db.String(50), primary_key=True)
    ProcDesc = db.Column(db.String(100))
    ProcGroup = db.Column(db.String(100))
    ProcBHYT = db.Column(db.Boolean, default=True)
    ProcPriceBHYT = db.Column(db.Integer, default=0)
    ProcPriceVP = db.Column(db.Integer, default=0)
    ProcAvailable = db.Column(db.Boolean, default=True)
    ProcNote = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Proc {self.ProcDesc}>'

class PatientDepartment(db.Model):
    __tablename__ = 'PatientDepartment'
    
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), primary_key=True)
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'), primary_key=True)
    Current = db.Column(db.Boolean, default=False)
    At = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientDepartment {self.PatientId}-{self.DepartmentId}>'

class Sign(db.Model):
    __tablename__ = 'Sign'
    
    SignId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    SignDesc = db.Column(db.String(100))
    SignType = db.Column(db.Boolean, default=False)  # 0: cơ năng, 1: thực thể
    SystemId = db.Column(db.Integer, db.ForeignKey('BodySystem.SystemId'), nullable=False)
    Speciality = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Sign {self.SignDesc}>'

class Staff(db.Model):
    __tablename__ = 'Staff'
    
    StaffId = db.Column(db.SmallInteger, primary_key=True)
    StaffName = db.Column(db.String(100))
    StaffRole = db.Column(db.Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    StaffAvailable = db.Column(db.Boolean, default=True)
    
    # Relationships
    visits = db.relationship('Visit', backref='staff', lazy=True)
    
    def __repr__(self):
        return f'<Staff {self.StaffName} - {self.StaffRole}>'

class Template(db.Model):
    __tablename__ = 'Template'
    
    TemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    TemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    TemplateGroup = db.Column(db.Enum('Test', 'Sign', 'Drug', 'Proc', name='template_group'))
    TemplateType = db.Column(db.Enum('Bệnh án', 'Theo dõi', name='template_type'))
    
    def __repr__(self):
        return f'<Template {self.TemplateName}>'

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

class Visit(db.Model):
    __tablename__ = 'Visit'
    
    VisitId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'), nullable=False)
    VisitPurpose = db.Column(db.Enum(
        'Thường quy', 'Cấp cứu', 'Phòng khám', 'Nhận bệnh', 'Bệnh án',
        'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám', 'Khám chuyên khoa',
        name='visit_purpose'
    ))
    VisitTime = db.Column(db.DateTime)
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    
    # Relationships
    diagnoses = db.relationship('VisitDiagnosis', backref='visit', lazy=True)
    documents = db.relationship('VisitDocuments', backref='visit', lazy=True)
    drugs = db.relationship('VisitDrug', backref='visit', lazy=True)
    procedures = db.relationship('VisitProc', backref='visit', lazy=True)
    signs = db.relationship('VisitSign', backref='visit', lazy=True)
    tests = db.relationship('VisitTest', backref='visit', lazy=True)
    
    def __repr__(self):
        return f'<Visit {self.VisitId}: {self.PatientId} - {self.VisitPurpose}>'

# ===========================================
# Visit-related association tables
# ===========================================

class VisitDiagnosis(db.Model):
    __tablename__ = 'VisitDiagnosis'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ICDCode = db.Column(db.String(10), db.ForeignKey('ICD.ICDCode'), primary_key=True)
    ActualDiagnosis = db.Column(db.String(255))
    DiseaseType = db.Column(db.Enum('Bệnh chính', 'Bệnh kèm', 'Biến chứng', name='disease_type'))

class VisitDocuments(db.Model):
    __tablename__ = 'VisitDocuments'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    document_links = db.Column(JSON, nullable=False)
    doc_metadata = db.Column('metadata', JSON)  # Use column name mapping

class VisitDrug(db.Model):
    __tablename__ = 'VisitDrug'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    DrugId = db.Column(db.String(50), db.ForeignKey('Drug.DrugId'), primary_key=True)
    DrugRoute = db.Column(db.String(100))
    DrugQuantity = db.Column(db.Float)
    DrugTimes = db.Column(db.String(100))
    DrugAtTime = db.Column(db.DateTime)
    Note = db.Column(db.String(100))
    IsCustom = db.Column(db.Boolean, default=False)

class VisitProc(db.Model):
    __tablename__ = 'VisitProc'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ProcId = db.Column(db.String(50), db.ForeignKey('Proc.ProcId'), primary_key=True)
    ProcStatus = db.Column(db.Enum('Ordered', 'In progress', 'Completed', 'Result', name='proc_status'), default='Ordered')
    ProcStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    ProcTime = db.Column(db.DateTime)
    IsCustom = db.Column(db.Boolean, default=False)

class VisitSign(db.Model):
    __tablename__ = 'VisitSign'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    SignId = db.Column(db.SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)
    BodySiteId = db.Column(db.Integer, db.ForeignKey('BodySite.SiteId'))
    LeftRight = db.Column(db.Enum('trái', 'phải', 'cả hai bên', name='left_right'))
    Section = db.Column(db.Enum('toàn bộ', '1/3', '1/4', '1/5', name='section'))
    UpperLower = db.Column(db.Enum('trên', 'dưới', 'giữa', name='upper_lower'))
    FrontBack = db.Column(db.Enum('mặt trước', 'mặt sau', 'mặt trong', 'mặt ngoài', name='front_back'))
    SignValue = db.Column(db.Enum('', 'BT', 'Có DHBL', 'Có', 'Không', 'Ít', 'Vừa', 'Nhiều', 'Nhẹ', 'Tăng', 'Giảm', 'Như cũ', name='sign_value'))
    FollowUp = db.Column(db.Boolean, default=False)
    ForEmr = db.Column(db.Boolean, default=False)
    IsCustom = db.Column(db.Boolean, default=False)

class VisitStaff(db.Model):
    __tablename__ = 'VisitStaff'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    StaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'), primary_key=True)

class VisitTest(db.Model):
    __tablename__ = 'VisitTest'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), primary_key=True)
    TestStatus = db.Column(db.Enum('Ordered', 'In progress', 'Completed', 'Result', name='test_status'), default='Ordered')
    TestStaffId = db.Column(db.SmallInteger, db.ForeignKey('Staff.StaffId'))
    TestTime = db.Column(db.DateTime)
    TestResult = db.Column(db.String(255))
    TestConclusion = db.Column(db.String(20))
    IsCustom = db.Column(db.Boolean, default=False)

# ===========================================
# Template association tables
# ===========================================

class TestTemplate(db.Model):
    __tablename__ = 'TestTemplate'
    
    TemplateId = db.Column(db.SmallInteger, db.ForeignKey('Template.TemplateId'), primary_key=True)
    TestId = db.Column(db.String(50), db.ForeignKey('Test.TestId'), primary_key=True)

class DrugTemplate(db.Model):
    __tablename__ = 'DrugTemplate'
    
    TemplateId = db.Column(db.SmallInteger, db.ForeignKey('Template.TemplateId'), primary_key=True)
    DrugId = db.Column(db.String(50), db.ForeignKey('Drug.DrugId'), primary_key=True)

class SignTemplate(db.Model):
    __tablename__ = 'SignTemplate'
    
    TemplateId = db.Column(db.SmallInteger, db.ForeignKey('Template.TemplateId'), primary_key=True)
    SignId = db.Column(db.SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)

# ===========================================
# Database helper functions
# ===========================================

def init_database(app):
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def test_connection():
    """Test database connection"""
    try:
        # Simple query to test connection
        result = db.session.execute(db.text("SELECT 1"))
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# ===========================================
# Database Views as ORM Models
# ===========================================

class PatientWithDepartment(db.Model):
    """ORM Model for patients_with_department view"""
    __tablename__ = 'patients_with_department'
    __table_args__ = {'info': dict(is_view=True)}  # Mark as view for documentation
    
    PatientId = db.Column(db.String(10), primary_key=True)
    PatientName = db.Column(db.String(100))
    PatientGender = db.Column(db.Enum('Nam', 'Nữ', 'Khác', name='gender'))
    PatientAge = db.Column(db.String(20))
    PatientAddress = db.Column(db.String(255))
    Allergy = db.Column(db.String(255))
    History = db.Column(db.Text)
    PatientNote = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger)
    DepartmentName = db.Column(db.String(100))
    DepartmentType = db.Column(db.Enum('Nội trú', 'Cấp cứu', 'Phòng khám', name='department_type'))
    DepartmentAssignedAt = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'PatientId': self.PatientId,
            'PatientName': self.PatientName,
            'PatientGender': self.PatientGender,
            'PatientAge': self.PatientAge,
            'PatientAddress': self.PatientAddress,
            'Allergy': self.Allergy,
            'History': self.History,
            'PatientNote': self.PatientNote,
            'DepartmentId': self.DepartmentId,
            'DepartmentName': self.DepartmentName,
            'DepartmentType': self.DepartmentType,
            'DepartmentAssignedAt': self.DepartmentAssignedAt.isoformat() if self.DepartmentAssignedAt else None
        }
    
    def __repr__(self):
        return f'<PatientWithDepartment {self.PatientId}: {self.PatientName} - {self.DepartmentName}>'

class StaffWithDepartment(db.Model):
    """ORM Model for staff_with_department view"""
    __tablename__ = 'staff_with_department'
    __table_args__ = {'info': dict(is_view=True)}
    
    StaffId = db.Column(db.SmallInteger, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    FullName = db.Column(db.String(100))
    Role = db.Column(db.Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    Phone = db.Column(db.String(20))
    Email = db.Column(db.String(100))
    Address = db.Column(db.String(255))
    DateHired = db.Column(db.Date)
    Active = db.Column(db.Boolean)
    DepartmentId = db.Column(db.SmallInteger)
    DepartmentName = db.Column(db.String(100))
    DepartmentType = db.Column(db.Enum('Nội trú', 'Cấp cứu', 'Phòng khám', name='department_type'))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'StaffId': self.StaffId,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'FullName': self.FullName,
            'Role': self.Role,
            'Phone': self.Phone,
            'Email': self.Email,
            'Address': self.Address,
            'DateHired': self.DateHired.isoformat() if self.DateHired else None,
            'Active': self.Active,
            'DepartmentId': self.DepartmentId,
            'DepartmentName': self.DepartmentName,
            'DepartmentType': self.DepartmentType
        }
    
    def __repr__(self):
        return f'<StaffWithDepartment {self.StaffId}: {self.FullName} - {self.DepartmentName}>'

class VisitWithDetails(db.Model):
    """ORM Model for visits_with_details view"""
    __tablename__ = 'visits_with_details'
    __table_args__ = {'info': dict(is_view=True)}
    
    VisitId = db.Column(db.BigInteger, primary_key=True)
    PatientId = db.Column(db.String(10))
    PatientName = db.Column(db.String(100))
    StaffId = db.Column(db.SmallInteger)
    StaffName = db.Column(db.String(100))
    StaffRole = db.Column(db.Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    DepartmentId = db.Column(db.SmallInteger)
    DepartmentName = db.Column(db.String(100))
    VisitDate = db.Column(db.DateTime)
    VisitType = db.Column(db.String(50))
    ChiefComplaint = db.Column(db.Text)
    Diagnosis = db.Column(db.Text)
    Treatment = db.Column(db.Text)
    Status = db.Column(db.String(20))
    FollowUpDate = db.Column(db.Date)
    Notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'PatientId': self.PatientId,
            'PatientName': self.PatientName,
            'StaffId': self.StaffId,
            'StaffName': self.StaffName,
            'StaffRole': self.StaffRole,
            'DepartmentId': self.DepartmentId,
            'DepartmentName': self.DepartmentName,
            'VisitDate': self.VisitDate.isoformat() if self.VisitDate else None,
            'VisitType': self.VisitType,
            'ChiefComplaint': self.ChiefComplaint,
            'Diagnosis': self.Diagnosis,
            'Treatment': self.Treatment,
            'Status': self.Status,
            'FollowUpDate': self.FollowUpDate.isoformat() if self.FollowUpDate else None,
            'Notes': self.Notes
        }
    
    def __repr__(self):
        return f'<VisitWithDetails {self.VisitId}: {self.PatientName} - {self.DepartmentName}>'

# ===========================================
# Database query helper functions
# ===========================================

def get_all_patients():
    """Get all patients"""
    return Patient.query.all()

def get_all_patients_with_department():
    """Get all patients with their current department information using ORM"""
    try:
        # Using ORM to query the view - much cleaner and more maintainable
        patients = PatientWithDepartment.query.order_by(PatientWithDepartment.PatientId).all()
        return [patient.to_dict() for patient in patients]
    except Exception as e:
        print(f"Error querying patients_with_department view: {e}")
        # Fallback to regular patients table if view doesn't exist yet
        patients = Patient.query.all()
        patients_data = []
        for patient in patients:
            patients_data.append({
                'PatientId': patient.PatientId,
                'PatientName': patient.PatientName,
                'PatientGender': patient.PatientGender,
                'PatientAge': patient.PatientAge,
                'PatientAddress': patient.PatientAddress,
                'Allergy': patient.Allergy,
                'History': patient.History,
                'PatientNote': patient.PatientNote,
                'DepartmentId': None,
                'DepartmentName': None,
                'DepartmentType': None,
                'DepartmentAssignedAt': None
            })
        return patients_data

def get_patient_by_id(patient_id):
    """Get patient by ID"""
    return Patient.query.get(patient_id)

def create_patient_record(patient_data):
    """Create a new patient record"""
    patient = Patient(
        PatientId=patient_data.get('PatientId'),
        PatientName=patient_data.get('PatientName'),
        PatientGender=patient_data.get('PatientGender'),
        PatientAge=patient_data.get('PatientAge'),
        PatientAddress=patient_data.get('PatientAddress'),
        Allergy=patient_data.get('Allergy', ''),
        History=patient_data.get('History'),
        PatientNote=patient_data.get('PatientNote', '')
    )
    db.session.add(patient)
    db.session.commit()
    return patient.PatientId

def update_patient_record(patient_id, patient_data):
    """Update patient record"""
    patient = Patient.query.get(patient_id)
    if patient:
        for key, value in patient_data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        db.session.commit()
        return True
    return False

def create_visit_record(visit_data):
    """Create a new visit record"""
    visit = Visit(
        PatientId=visit_data.get('PatientId'),
        DepartmentId=visit_data.get('DepartmentId'),
        VisitPurpose=visit_data.get('VisitPurpose'),
        VisitTime=visit_data.get('VisitTime', datetime.utcnow()),
        StaffId=visit_data.get('StaffId')
    )
    db.session.add(visit)
    db.session.commit()
    return visit.VisitId

def get_visits_by_patient(patient_id):
    """Get all visits for a patient"""
    return Visit.query.filter_by(PatientId=patient_id).all()

def get_staff_by_department(department_id):
    """Get all staff in a department"""
    return Staff.query.filter_by(DepartmentId=department_id, StaffAvailable=True).all()

def get_all_staff_with_department():
    """Get all staff with their department information using ORM"""
    try:
        staff = StaffWithDepartment.query.order_by(StaffWithDepartment.StaffId).all()
        return [member.to_dict() for member in staff]
    except Exception as e:
        print(f"Error querying staff_with_department view: {e}")
        # Fallback to regular staff table if view doesn't exist yet
        staff = Staff.query.all()
        staff_data = []
        for member in staff:
            dept = Department.query.get(member.DepartmentId) if member.DepartmentId else None
            staff_data.append({
                'StaffId': member.StaffId,
                'FirstName': member.StaffName.split()[0] if member.StaffName else '',
                'LastName': ' '.join(member.StaffName.split()[1:]) if member.StaffName and len(member.StaffName.split()) > 1 else '',
                'FullName': member.StaffName,
                'Role': member.StaffRole,
                'Phone': None,
                'Email': None,
                'Address': None,
                'DateHired': None,
                'Active': member.StaffAvailable,
                'DepartmentId': member.DepartmentId,
                'DepartmentName': dept.DepartmentName if dept else None,
                'DepartmentType': dept.DepartmentType if dept else None
            })
        return staff_data

def get_all_visits_with_details():
    """Get all visits with detailed information using ORM"""
    try:
        visits = VisitWithDetails.query.order_by(VisitWithDetails.VisitId.desc()).all()
        return [visit.to_dict() for visit in visits]
    except Exception as e:
        print(f"Error querying visits_with_details view: {e}")
        # Fallback to regular visits table if view doesn't exist yet
        visits = Visit.query.all()
        visits_data = []
        for visit in visits:
            patient = Patient.query.get(visit.PatientId)
            staff = Staff.query.get(visit.StaffId)
            dept = Department.query.get(visit.DepartmentId)
            visits_data.append({
                'VisitId': visit.VisitId,
                'PatientId': visit.PatientId,
                'PatientName': patient.PatientName if patient else None,
                'StaffId': visit.StaffId,
                'StaffName': staff.StaffName if staff else None,
                'StaffRole': staff.StaffRole if staff else None,
                'DepartmentId': visit.DepartmentId,
                'DepartmentName': dept.DepartmentName if dept else None,
                'VisitDate': visit.VisitTime.isoformat() if visit.VisitTime else None,
                'VisitType': visit.VisitPurpose,
                'ChiefComplaint': None,
                'Diagnosis': None,
                'Treatment': None,
                'Status': None,
                'FollowUpDate': None,
                'Notes': None
            })
        return visits_data

def get_patient_with_department_by_id(patient_id):
    """Get a specific patient with department information using ORM"""
    try:
        return PatientWithDepartment.query.filter_by(PatientId=patient_id).first()
    except Exception as e:
        print(f"Error querying patient from view: {e}")
        return None

# Usage example:
if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        # Test database connection
        if test_connection():
            print("✓ Database connection established successfully!")
            print("✓ ORM models defined and ready to use")
        else:
            print("✗ Failed to connect to database")

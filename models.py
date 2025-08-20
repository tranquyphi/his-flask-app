"""
Consolidated Database Models for HIS (Hospital Information System)
All models in one file to eliminate circular import issues and improve maintainability
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON, Enum, BigInteger, SmallInteger, String, Text, Boolean, LargeBinary
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, and_
import os
from config import config

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Path to store document files - defined as global variable for easy migration
DOCUMENTS_PATH = '/static/documents'

def create_app(config_name=None):
    """Create and configure Flask application with database connection.
    Uses 'frontend' directory for Jinja templates (renamed from default 'templates').
    """
    app = Flask(__name__, template_folder='frontend', static_folder='static')
    
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize database with app
    db.init_app(app)
    
    # Register static versioning filter for cache management
    try:
        from utils.static_versioning import register_static_version_filter
        register_static_version_filter(app)
    except ImportError:
        # Fallback if utils not available
        @app.template_filter('static_version')
        def static_version_filter(filename):
            return app.config.get('STATIC_VERSION', '1.1')
    
    return app

def get_models():
    """Return all model classes"""
    return {
        'DocumentType': DocumentType,
        'StaffDocumentType': StaffDocumentType,
        'BodyPart': BodyPart,
        'BodySite': BodySite,
        'BodySystem': BodySystem,
        'Department': Department,
        'DrugGroup': DrugGroup,
        'Drug': Drug,
        'ICD': ICD,
        'Patient': Patient,
        'Proc': Proc,
        'PatientDepartment': PatientDepartment,
        'StaffDepartment': StaffDepartment,
        'Sign': Sign,
        'Staff': Staff,
        'Template': Template,
        'Test': Test,
        'Visit': Visit,
        'VisitDiagnosis': VisitDiagnosis,
        'VisitDocuments': VisitDocuments,
        'VisitImage': VisitImage,
        'VisitDrug': VisitDrug,
        'VisitProc': VisitProc,
        'VisitSign': VisitSign,
        'VisitStaff': VisitStaff,
        'VisitTest': VisitTest,
        'TestTemplate': TestTemplate,
        'DrugTemplate': DrugTemplate,
        'DrugTemplateDetail': DrugTemplateDetail,
        'SignTemplate': SignTemplate,
        'SignTemplateDetail': SignTemplateDetail,
        'PatientDocuments': PatientDocuments,
        'StaffDocuments': StaffDocuments,
        'PatientsWithDepartment': PatientsWithDepartment
    }

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
# Core Models
# ===========================================

class DocumentType(db.Model):
    __tablename__ = 'DocumentType'
    
    DocumentTypeId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeName = db.Column(String(100))
    # DocumentTypeDescription field doesn't exist in database schema
    
    def __repr__(self):
        return f'<DocumentType {self.DocumentTypeName}>'

class StaffDocumentType(db.Model):
    __tablename__ = 'StaffDocumentType'
    
    DocumentTypeId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeName = db.Column(String(100))
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.DocumentTypeName
        }
    
    def __repr__(self):
        return f'<StaffDocumentType {self.DocumentTypeName}>'

class BodyPart(db.Model):
    __tablename__ = 'BodyPart'
    
    BodyPartId = db.Column(SmallInteger, primary_key=True)
    BodyPartName = db.Column(String(100))
    
    def __repr__(self):
        return f'<BodyPart {self.BodyPartName}>'

class BodySite(db.Model):
    __tablename__ = 'BodySite'
    
    SiteId = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Database uses SiteId, not BodySiteId
    SiteName = db.Column(String(100))
    BodyPartId = db.Column(SmallInteger, db.ForeignKey('BodyPart.BodyPartId'))  # Database has this field
    
    def __repr__(self):
        return f'<BodySite {self.SiteName}>'

class BodySystem(db.Model):
    __tablename__ = 'BodySystem'
    
    SystemId = db.Column(db.Integer, primary_key=True)  # Database uses SystemId, not BodySystemId
    SystemName = db.Column(String(100))
    
    def __repr__(self):
        return f'<BodySystem {self.SystemName}>'

class Department(db.Model):
    __tablename__ = 'Department'
    
    DepartmentId = db.Column(SmallInteger, primary_key=True)
    DepartmentName = db.Column(String(100))
    DepartmentType = db.Column(String(50))  # Changed from Enum to String to allow any value
    
    # Relationships
    staff_members = relationship('Staff', 
                               secondary='StaffDepartment',
                               primaryjoin='Department.DepartmentId == StaffDepartment.DepartmentId',
                               secondaryjoin='and_(StaffDepartment.StaffId == Staff.StaffId, StaffDepartment.Current == True)',
                               viewonly=True)
                               
    staff_assignments = relationship('StaffDepartment', 
                                     backref='department',
                                     lazy='dynamic')
                                     
    visits = relationship('Visit', backref='department', lazy=True)
    templates = relationship('Template', backref='department', lazy=True)
    tests = relationship('Test', backref='in_charge_department', lazy=True)
    
    def get_current_staff(self):
        """Returns all staff currently assigned to this department"""
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

class DrugGroup(db.Model):
    __tablename__ = 'DrugGroup'
    
    DrugGroupId = db.Column(db.Integer, primary_key=True)  # Database uses Integer, not SmallInteger
    DrugGroupName = db.Column(String(100))
    DrugGroupDescription = db.Column(String(255))
    
    def __repr__(self):
        return f'<DrugGroup {self.DrugGroupName}>'

class Drug(db.Model):
    __tablename__ = 'Drug'
    
    DrugId = db.Column(String(50), primary_key=True)  # Database uses String, not SmallInteger
    DrugName = db.Column(String(255))
    DrugChemical = db.Column(String(255))
    DrugContent = db.Column(String(100))
    DrugFormulation = db.Column(String(50))
    DrugRemains = db.Column(SmallInteger)
    DrugGroupId = db.Column(db.Integer, db.ForeignKey('DrugGroup.DrugGroupId'))
    DrugTherapy = db.Column(String(200))
    DrugRoute = db.Column(String(50))
    DrugQuantity = db.Column(String(50))
    CountStr = db.Column(String(50))
    DrugAvailable = db.Column(Boolean, default=True)
    DrugPriceBHYT = db.Column(db.Integer, default=0)
    DrugPriceVP = db.Column(db.Integer, default=0)
    DrugNote = db.Column(String(100), default='')
    Count = db.Column(String(50))
    
    # Relationships
    drug_group = relationship('DrugGroup', backref='drugs')
    
    def __repr__(self):
        return f'<Drug {self.DrugName}>'

class ICD(db.Model):
    __tablename__ = 'ICD'
    
    ICDCode = db.Column(String(10), primary_key=True)  # Database uses ICDCode as primary key, not ICDId
    ICDName = db.Column(String(255))
    ICDGroup = db.Column(String(100), default='')
    
    def __repr__(self):
        return f'<ICD {self.ICDCode}: {self.ICDName}>'

class Patient(db.Model):
    __tablename__ = 'Patient'
    
    PatientId = db.Column(String(10), primary_key=True)
    PatientName = db.Column(String(100))
    PatientGender = db.Column(Enum('Nam', 'Nữ', 'Khác', name='gender'))
    PatientAge = db.Column(String(20))
    PatientAddress = db.Column(String(255))
    Allergy = db.Column(String(255), default='')
    History = db.Column(Text)
    PatientImage = db.Column(LargeBinary, default=None)
    PatientNote = db.Column(String(100), default='')
    # Adding missing fields from schema
    PatientPhone = db.Column(String(20))
    PatientCCCD = db.Column(String(20))
    PatientBHYT = db.Column(String(20))
    PatientBHYTValid = db.Column(String(100))
    PatientRelative = db.Column(String(100))
    
    # Relationships
    visits = relationship('Visit', backref='patient', lazy=True)
    patient_departments = relationship('PatientDepartment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.PatientId}: {self.PatientName}>'

class Proc(db.Model):
    __tablename__ = 'Proc'
    
    ProcId = db.Column(String(50), primary_key=True)  # Database uses String, not SmallInteger
    ProcDesc = db.Column(String(100))
    ProcGroup = db.Column(String(100))
    ProcBHYT = db.Column(Boolean, default=True)
    ProcPriceBHYT = db.Column(db.Integer, default=0)
    ProcPriceVP = db.Column(db.Integer, default=0)
    ProcAvailable = db.Column(Boolean, default=True)
    ProcNote = db.Column(String(100))
    
    def __repr__(self):
        return f'<Proc {self.ProcDesc}>'

class Sign(db.Model):
    __tablename__ = 'Sign'
    
    SignId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    SignDesc = db.Column(String(100))  # Database uses SignDesc, not SignName
    SignType = db.Column(Boolean, default=False)  # 0 if functional, 1 if physical
    SystemId = db.Column(db.Integer, db.ForeignKey('BodySystem.SystemId'), nullable=False)
    Speciality = db.Column(String(100))
    
    def __repr__(self):
        return f'<Sign {self.SignDesc}>'

class Staff(db.Model):
    __tablename__ = 'Staff'
    
    StaffId = db.Column(SmallInteger, primary_key=True)
    StaffName = db.Column(String(100))
    StaffRole = db.Column(Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác', name='staff_role'))
    StaffAvailable = db.Column(Boolean, default=True)
    
    # Relationships
    departments = relationship('Department', 
                               secondary='StaffDepartment',
                               primaryjoin='Staff.StaffId == StaffDepartment.StaffId',
                               secondaryjoin='and_(StaffDepartment.DepartmentId == Department.DepartmentId, StaffDepartment.Current == True)',
                               viewonly=True)
                               
    department_assignments = relationship('StaffDepartment', 
                                        backref='staff_member',
                                        lazy='dynamic')
    
    visits = relationship('Visit', backref='attending_staff', lazy=True)
    
    @property
    def current_department(self):
        """Returns the current department of the staff member"""
        dept_assign = StaffDepartment.query.filter_by(StaffId=self.StaffId, Current=True).first()
        if dept_assign:
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

class Template(db.Model):
    __tablename__ = 'Template'
    
    TemplateId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    TemplateName = db.Column(String(100))
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    
    def __repr__(self):
        return f'<Template {self.TemplateName}>'

class Test(db.Model):
    __tablename__ = 'Test'
    
    TestId = db.Column(String(50), primary_key=True)  # Database uses String, not SmallInteger
    TestName = db.Column(String(100))
    TestGroup = db.Column(String(100))
    TestPriceBHYT = db.Column(db.Integer, default=0)
    TestPriceVP = db.Column(db.Integer, default=0)
    TestAvailable = db.Column(Boolean, default=True)
    TestNote = db.Column(String(100), default='')
    TestType = db.Column(Enum('XN','SA','XQ','CT','TDCN','NS'))
    InChargeDepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    
    def __repr__(self):
        return f'<Test {self.TestName}>'

# ===========================================
# Association Models
# ===========================================

class PatientDepartment(db.Model):
    __tablename__ = 'PatientDepartment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Database uses 'id' not 'PatientDepartmentId'
    PatientId = db.Column(String(10), db.ForeignKey('Patient.PatientId'))
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    Current = db.Column(Boolean, default=True)
    At = db.Column(db.DateTime, default=datetime.utcnow)  # Database uses 'At' not 'AssignmentDate'
    Reason = db.Column(String(10), default='DT')  # Database has Reason field
    EndDate = db.Column(db.DateTime, nullable=True)  # Database has EndDate field
    
    def __repr__(self):
        return f'<PatientDepartment {self.PatientId} -> {self.DepartmentId}>'

class StaffDepartment(db.Model):
    __tablename__ = 'StaffDepartment'
    
    # Note: This table doesn't have a separate primary key in the database
    # It uses a composite key of StaffId + DepartmentId
    StaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'), primary_key=True)
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'), primary_key=True)
    Current = db.Column(Boolean, default=True)
    Position = db.Column(String(50), default='NV')  # Position field for staff in department
    
    def __repr__(self):
        return f'<StaffDepartment {self.StaffId} -> {self.DepartmentId}>'

# ===========================================
# Visit Models
# ===========================================

class Visit(db.Model):
    __tablename__ = 'Visit'
    
    VisitId = db.Column(BigInteger, primary_key=True, autoincrement=True)
    PatientId = db.Column(String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'), nullable=False)
    VisitPurpose = db.Column(Enum(
        'Thường quy', 'Cấp cứu', 'Phòng khám', 'Nhận bệnh', 'Bệnh án',
        'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám', 'Khám chuyên khoa',
        name='visit_purpose'
    ))
    VisitTime = db.Column(db.DateTime)
    StaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    
    # Relationships
    diagnoses = relationship('VisitDiagnosis', backref='visit', lazy=True, cascade='all, delete-orphan')
    documents = relationship('VisitDocuments', backref='visit', lazy=True, cascade='all, delete-orphan')
    images = relationship('VisitImage', backref='visit', lazy=True, cascade='all, delete-orphan')
    drugs = relationship('VisitDrug', backref='visit', lazy=True, cascade='all, delete-orphan')
    procedures = relationship('VisitProc', backref='visit', lazy=True, cascade='all, delete-orphan')
    signs = relationship('VisitSign', backref='visit', lazy=True, cascade='all, delete-orphan')
    tests = relationship('VisitTest', backref='visit', lazy=True, cascade='all, delete-orphan')
    visit_staff = relationship('VisitStaff', backref='visit', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert Visit to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'PatientId': self.PatientId,
            'DepartmentId': self.DepartmentId,
            'VisitPurpose': self.VisitPurpose,
            'VisitTime': self.VisitTime.isoformat() if self.VisitTime else None,
            'StaffId': self.StaffId
        }
    
    def __repr__(self):
        return f'<Visit {self.VisitId}: {self.PatientId} - {self.VisitPurpose}>'

class VisitDiagnosis(db.Model):
    __tablename__ = 'VisitDiagnosis'
    
    # Database doesn't have VisitDiagnosisId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ICDCode = db.Column(String(10), db.ForeignKey('ICD.ICDCode'), primary_key=True)  # Database uses ICDCode, not ICDId
    ActualDiagnosis = db.Column(String(255))
    DiseaseType = db.Column(Enum('Bệnh chính','Bệnh kèm','Biến chứng'))
    
    def __repr__(self):
        return f'<VisitDiagnosis {self.VisitId} -> {self.ICDCode}>'

class VisitDocuments(db.Model):
    __tablename__ = 'VisitDocuments'
    
    # Database doesn't have VisitDocumentsId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    DocumentTypeId = db.Column(SmallInteger, db.ForeignKey('DocumentType.DocumentTypeId'), primary_key=True)
    document_links = db.Column(JSON, nullable=False)
    document_metadata = db.Column(JSON)  # Renamed from 'metadata' to avoid reserved word conflict
    
    def __repr__(self):
        return f'<VisitDocuments {self.VisitId} -> {self.DocumentTypeId}>'

class VisitImage(db.Model):
    __tablename__ = 'VisitImage'
    
    ImageId = db.Column(BigInteger, primary_key=True, autoincrement=True)  # Database uses ImageId, not VisitImageId
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    ImageType = db.Column(String(50))
    ImageData = db.Column(LargeBinary, nullable=False)
    ImageUrl = db.Column(String(255))
    Description = db.Column(String(255))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VisitImage {self.ImageId}>'

class VisitDrug(db.Model):
    __tablename__ = 'VisitDrug'
    
    # Database doesn't have VisitDrugId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    DrugId = db.Column(String(50), db.ForeignKey('Drug.DrugId'), primary_key=True)  # Database uses String, not SmallInteger
    DrugRoute = db.Column(String(100))
    DrugQuantity = db.Column(db.Float)
    DrugTimes = db.Column(String(100))
    DrugAtTime = db.Column(db.DateTime)
    Note = db.Column(String(100))
    DrugStatus = db.Column(Enum('CD','TH','XONG'), default='CD')
    IsCustom = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<VisitDrug {self.VisitId} -> {self.DrugId}>'

class VisitProc(db.Model):
    __tablename__ = 'VisitProc'
    
    # Database doesn't have VisitProcId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ProcId = db.Column(String(50), db.ForeignKey('Proc.ProcId'), primary_key=True)  # Database uses String, not SmallInteger
    ProcStatus = db.Column(Enum('Ordered','In progress','Completed','Result'), default='Ordered')
    ProcStaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'))
    ProcTime = db.Column(db.DateTime)
    IsCustom = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<VisitProc {self.VisitId} -> {self.ProcId}>'

class VisitSign(db.Model):
    __tablename__ = 'VisitSign'
    
    # Database doesn't have VisitSignId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    SignId = db.Column(SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)
    BodySiteId = db.Column(db.Integer, db.ForeignKey('BodySite.SiteId'))
    LeftRight = db.Column(Enum('trái','phải','cả hai bên'))
    Section = db.Column(Enum('toàn bộ','1/3','1/4','1/5'))
    UpperLower = db.Column(Enum('trên','dưới','giữa'))
    FrontBack = db.Column(Enum('mặt trước','mặt sau','mặt trong','mặt ngoài'))
    SignValue = db.Column(Enum('','BT','Có DHBL','Có','Không','Ít','Vừa','Nhiều','Nhẹ','Tăng','Giảm','Như cũ'))
    FollowUp = db.Column(Boolean, default=False)
    ForEmr = db.Column(Boolean, default=False)
    IsCustom = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<VisitSign {self.VisitId} -> {self.SignId}>'

class VisitStaff(db.Model):
    __tablename__ = 'VisitStaff'
    
    # Database doesn't have VisitStaffId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    StaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'), primary_key=True)
    
    def __repr__(self):
        return f'<VisitStaff {self.VisitId} -> {self.StaffId}>'

class VisitTest(db.Model):
    __tablename__ = 'VisitTest'
    
    # Database doesn't have VisitTestId, uses composite key
    VisitId = db.Column(BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    TestId = db.Column(String(50), db.ForeignKey('Test.TestId'), primary_key=True)  # Database uses String, not SmallInteger
    TestStatus = db.Column(Enum('CD','TH','XONG'), default='CD')
    TestStaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'))
    TestTime = db.Column(db.DateTime)
    TestResult = db.Column(String(255))
    TestConclusion = db.Column(String(20))
    IsCustom = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<VisitTest {self.VisitId} -> {self.TestId}>'

# ===========================================
# Template Models
# ===========================================

class TestTemplate(db.Model):
    __tablename__ = 'TestTemplate'
    
    TestTemplateId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    TestTemplateName = db.Column(String(100))
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    TestTemplateType = db.Column(Enum('BA','TD','PK','CC'), default='TD')
    
    def __repr__(self):
        return f'<TestTemplate {self.TestTemplateName}>'

class DrugTemplate(db.Model):
    __tablename__ = 'DrugTemplate'
    
    DrugTemplateId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    DrugTemplateName = db.Column(String(100))
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    DrugTemplateType = db.Column(Enum('BA','TD','PK','CC'), default='TD')
    
    def __repr__(self):
        return f'<DrugTemplate {self.DrugTemplateName}>'

class DrugTemplateDetail(db.Model):
    __tablename__ = 'DrugTemplateDetail'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Database uses 'id', not 'DrugTemplateDetailId'
    DrugTemplateId = db.Column(SmallInteger, db.ForeignKey('DrugTemplate.DrugTemplateId'))
    DrugId = db.Column(String(50), db.ForeignKey('Drug.DrugId'))  # Database uses String, not SmallInteger
    
    def __repr__(self):
        return f'<DrugTemplateDetail {self.DrugTemplateId} -> {self.DrugId}>'

class SignTemplate(db.Model):
    __tablename__ = 'SignTemplate'
    
    SignTemplateId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    SignTemplateName = db.Column(String(100))
    DepartmentId = db.Column(SmallInteger, db.ForeignKey('Department.DepartmentId'))
    SignTemplateType = db.Column(Enum('BA','TD','PK','CC'), default='TD')
    
    def __repr__(self):
        return f'<SignTemplate {self.SignTemplateName}>'

class SignTemplateDetail(db.Model):
    __tablename__ = 'SignTemplateDetail'
    
    # Database doesn't have SignTemplateDetailId, uses composite key
    SignTemplateId = db.Column(SmallInteger, db.ForeignKey('SignTemplate.SignTemplateId'), primary_key=True)
    SignId = db.Column(SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)
        
    def __repr__(self):
        return f'<SignTemplateDetail {self.SignTemplateId} -> {self.SignId}>'

# ===========================================
# Document and Service Models
# ===========================================

class PatientDocuments(db.Model):
    __tablename__ = 'PatientDocuments'
    
    # Database schema order: PatientId, document_links, metadata, DocumentId, DocumentTypeId, FileType, FileSize, UploadDate, LastModified, file_path, original_filename, file_type, file_size, upload_date, last_modified
    PatientId = db.Column(String(20), db.ForeignKey('Patient.PatientId'), nullable=False)
    document_links = db.Column(JSON, nullable=False)
    document_metadata = db.Column('metadata', JSON)  # Map 'metadata' column to 'document_metadata' attribute
    DocumentId = db.Column(SmallInteger, primary_key=True, autoincrement=True)
    DocumentTypeId = db.Column(SmallInteger, db.ForeignKey('DocumentType.DocumentTypeId'))
    FileType = db.Column(String(50))
    FileSize = db.Column(db.Integer)
    UploadDate = db.Column(db.DateTime, default=datetime.utcnow)
    LastModified = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(String(255))
    original_filename = db.Column(String(255))
    file_type = db.Column(String(50))
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'DocumentId': self.DocumentId,
            'PatientId': self.PatientId,
            'DocumentTypeId': self.DocumentTypeId,
            'document_links': self.document_links,
            'metadata': self.document_metadata,  # Return as 'metadata' to match API expectations
            'FileType': self.FileType,
            'FileSize': self.FileSize,
            'UploadDate': self.UploadDate.isoformat() if self.UploadDate else None,
            'LastModified': self.LastModified.isoformat() if self.LastModified else None,
            'file_path': self.file_path,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    def __repr__(self):
        return f'<PatientDocuments {self.PatientId} -> {self.DocumentTypeId}>'

class StaffDocuments(db.Model):
    __tablename__ = 'StaffDocuments'
    
    DocumentId = db.Column(SmallInteger, primary_key=True, autoincrement=True)  # Database uses DocumentId, not StaffDocumentsId
    StaffId = db.Column(SmallInteger, db.ForeignKey('Staff.StaffId'), nullable=False)
    DocumentTypeId = db.Column(SmallInteger, db.ForeignKey('DocumentType.DocumentTypeId'))
    document_links = db.Column(JSON, nullable=False)
    document_metadata = db.Column(JSON)
    FileSize = db.Column(db.Integer)
    file_type = db.Column(String(50))
    UploadDate = db.Column(db.DateTime, default=datetime.utcnow)
    LastModified = db.Column(db.DateTime, default=datetime.utcnow)
    original_filename = db.Column(String(255))
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'DocumentId': self.DocumentId,
            'StaffId': self.StaffId,
            'DocumentTypeId': self.DocumentTypeId,
            'document_links': self.document_links,
            'document_metadata': self.document_metadata,
            'FileSize': self.FileSize,
            'file_type': self.file_type,
            'UploadDate': self.UploadDate.isoformat() if self.UploadDate else None,
            'LastModified': self.LastModified.isoformat() if self.LastModified else None,
            'original_filename': self.original_filename,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    def __repr__(self):
        return f'<StaffDocuments {self.StaffId} -> {self.DocumentTypeId}>'

class PatientsWithDepartment(db.Model):
    __tablename__ = 'PatientsWithDepartment'
    
    PatientId = db.Column(String(10), primary_key=True)
    PatientName = db.Column(String(100))
    DepartmentId = db.Column(SmallInteger)
    DepartmentName = db.Column(String(100))
    AssignmentDate = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<PatientsWithDepartment {self.PatientId}: {self.PatientName} -> {self.DepartmentName}>'

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

# ===========================================
# ORM Models based on Database Schema
# ===========================================

class BodyPart(db.Model):
    __tablename__ = 'BodyPart'
    
    BodyPartId = db.Column(db.SmallInteger, primary_key=True)
    BodyPartName = db.Column(db.String(50))
    
    # Relationships
    body_sites = db.relationship('BodySite', backref='body_part', lazy=True)
    
    def __repr__(self):
        return f'<BodyPart {self.BodyPartName}>'

class BodySite(db.Model):
    __tablename__ = 'BodySite'
    
    SiteId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SiteName = db.Column(db.String(100), nullable=False)
    BodyPartId = db.Column(db.SmallInteger, db.ForeignKey('BodyPart.BodyPartId'))
    
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

class DrugGroup(db.Model):
    __tablename__ = 'DrugGroup'
    
    DrugGroupId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DrugGroupName = db.Column(db.String(100), nullable=False)
    DrugGroupDescription = db.Column(db.String(255))
    
    # Relationships
    drugs = db.relationship('Drug', backref='drug_group', lazy=True)
    
    def __repr__(self):
        return f'<DrugGroup {self.DrugGroupName}>'

class Drug(db.Model):
    __tablename__ = 'Drug'
    
    DrugId = db.Column(db.String(50), primary_key=True)
    DrugName = db.Column(db.String(255))
    DrugChemical = db.Column(db.String(255))
    DrugContent = db.Column(db.String(100))
    DrugFormulation = db.Column(db.String(50))
    DrugRemains = db.Column(db.SmallInteger)
    DrugGroupId = db.Column(db.Integer, db.ForeignKey('DrugGroup.DrugGroupId'))
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
    
    # Add auto-increment ID as primary key to allow multiple assignments
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(10), db.ForeignKey('Patient.PatientId'), nullable=False)
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'), nullable=False)
    Current = db.Column(db.Boolean, default=False)
    At = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PatientDepartment {self.id}: {self.PatientId}-{self.DepartmentId} at {self.At}>'

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
    visits = db.relationship('Visit', backref='attending_staff', lazy=True)
    
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
    diagnoses = db.relationship('VisitDiagnosis', backref='visit', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('VisitDocuments', backref='visit', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('VisitImage', backref='visit', lazy=True, cascade='all, delete-orphan')
    drugs = db.relationship('VisitDrug', backref='visit', lazy=True, cascade='all, delete-orphan')
    procedures = db.relationship('VisitProc', backref='visit', lazy=True, cascade='all, delete-orphan')
    signs = db.relationship('VisitSign', backref='visit', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('VisitTest', backref='visit', lazy=True, cascade='all, delete-orphan')
    visit_staff = db.relationship('VisitStaff', backref='visit', lazy=True, cascade='all, delete-orphan')
    
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

# ===========================================
# Visit-related association tables
# ===========================================

class VisitDiagnosis(db.Model):
    __tablename__ = 'VisitDiagnosis'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    ICDCode = db.Column(db.String(10), db.ForeignKey('ICD.ICDCode'), primary_key=True)
    ActualDiagnosis = db.Column(db.String(255))
    DiseaseType = db.Column(db.Enum('Bệnh chính', 'Bệnh kèm', 'Biến chứng', name='disease_type'))
    
    def to_dict(self):
        """Convert VisitDiagnosis to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'ICDCode': self.ICDCode,
            'ActualDiagnosis': self.ActualDiagnosis,
            'DiseaseType': self.DiseaseType
        }

class VisitDocuments(db.Model):
    __tablename__ = 'VisitDocuments'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    document_links = db.Column(JSON, nullable=False)
    doc_metadata = db.Column('metadata', JSON)  # Use column name mapping

class VisitImage(db.Model):
    __tablename__ = 'VisitImage'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), nullable=False)
    ImageId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ImageType = db.Column(db.String(50))
    ImageData = db.Column(db.LargeBinary)
    ImageUrl = db.Column(db.String(255))
    Description = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class VisitDrug(db.Model):
    __tablename__ = 'VisitDrug'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    DrugId = db.Column(db.String(50), db.ForeignKey('Drug.DrugId'), primary_key=True)
    DrugRoute = db.Column(db.String(100))
    DrugQuantity = db.Column(db.Float)
    DrugTimes = db.Column(db.String(100))
    DrugAtTime = db.Column(db.DateTime)
    Note = db.Column(db.String(100))
    DrugStatus = db.Column(db.Enum('CD', 'TH', 'XONG', name='drug_status'), default='CD')
    IsCustom = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert VisitDrug to dictionary for JSON serialization"""
        return {
            'VisitId': self.VisitId,
            'DrugId': self.DrugId,
            'DrugRoute': self.DrugRoute,
            'DrugQuantity': self.DrugQuantity,
            'DrugTimes': self.DrugTimes,
            'DrugAtTime': self.DrugAtTime.isoformat() if self.DrugAtTime else None,
            'Note': self.Note,
            'DrugStatus': self.DrugStatus,
            'IsCustom': self.IsCustom
        }

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
    TestStatus = db.Column(db.Enum('CD', 'TH', 'XONG', name='test_status'), default='CD')
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
    
    DrugTemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    DrugTemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    DrugTemplateType = db.Column(db.Enum('BA', 'TD', 'PK', 'CC', name='drug_template_type'), default='TD')

class DrugTemplateDetail(db.Model):
    __tablename__ = 'DrugTemplateDetail'
    
    DrugTemplateId = db.Column(db.SmallInteger, db.ForeignKey('DrugTemplate.DrugTemplateId'), primary_key=True)
    DrugId = db.Column(db.String(20), db.ForeignKey('Drug.DrugId'), primary_key=True)

class SignTemplate(db.Model):
    __tablename__ = 'SignTemplate'
    
    SignTemplateId = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    SignTemplateName = db.Column(db.String(100))
    DepartmentId = db.Column(db.SmallInteger, db.ForeignKey('Department.DepartmentId'))
    SignTemplateType = db.Column(db.Enum('BA', 'TD', 'PK', 'CC', name='sign_template_type'), default='TD')

class SignTemplateDetail(db.Model):
    __tablename__ = 'SignTemplateDetail'
    
    SignTemplateId = db.Column(db.SmallInteger, db.ForeignKey('SignTemplate.SignTemplateId'), primary_key=True)
    SignId = db.Column(db.SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)

class PatientsWithDepartment:
    """
    Service class that provides patient information with department details
    Uses relationships to fetch department names instead of IDs
    Not a direct ORM model to avoid table conflicts
    """
    
    @classmethod
    def get_all_with_departments(cls):
        """Get all patients with their department information, sorted by name"""
        try:
            patients = Patient.query.order_by(Patient.PatientName).all()
            result = []
            
            for patient in patients:
                # Get the most recent department assignment
                latest_assignment = PatientDepartment.query.filter_by(
                    PatientId=patient.PatientId
                ).order_by(PatientDepartment.At.desc()).first()
                
                current_department = None
                if latest_assignment:
                    department = Department.query.get(latest_assignment.DepartmentId)
                    current_department = department.DepartmentName if department else None
                
                # Get all department assignments
                all_assignments = PatientDepartment.query.filter_by(
                    PatientId=patient.PatientId
                ).order_by(PatientDepartment.At.desc()).all()
                
                all_departments = []
                for assignment in all_assignments:
                    department = Department.query.get(assignment.DepartmentId)
                    all_departments.append({
                        'DepartmentName': department.DepartmentName if department else 'Unknown',
                        'AssignedDate': assignment.At.strftime('%Y-%m-%d %H:%M:%S') if assignment.At else None
                    })
                
                patient_data = {
                    'PatientId': patient.PatientId,
                    'PatientName': patient.PatientName,
                    'PatientAge': patient.PatientAge,
                    'PatientGender': patient.PatientGender,
                    'PatientAddress': patient.PatientAddress,
                    'Allergy': patient.Allergy,
                    'History': patient.History,
                    'PatientNote': patient.PatientNote,
                    'CurrentDepartment': current_department,
                    'AllDepartments': all_departments
                }
                result.append(patient_data)
            
            return result
        except Exception as e:
            print(f"Error in get_all_with_departments: {e}")
            return []
    
    @classmethod
    def get_by_department(cls, department_id):
        """Get patients in a specific department"""
        try:
            # Get patient IDs that are assigned to this department
            patient_assignments = PatientDepartment.query.filter_by(DepartmentId=department_id).all()
            patient_ids = [assignment.PatientId for assignment in patient_assignments]
            
            if not patient_ids:
                return []
            
            # Get patients with these IDs
            patients = Patient.query.filter(Patient.PatientId.in_(patient_ids)).order_by(Patient.PatientName).all()
            result = []
            
            for patient in patients:
                # Get department info
                department = Department.query.get(department_id)
                department_name = department.DepartmentName if department else 'Unknown'
                
                # Get assignment date for this department
                assignment = PatientDepartment.query.filter_by(
                    PatientId=patient.PatientId,
                    DepartmentId=department_id
                ).order_by(PatientDepartment.At.desc()).first()
                
                patient_data = {
                    'PatientId': patient.PatientId,
                    'PatientName': patient.PatientName,
                    'PatientAge': patient.PatientAge,
                    'PatientGender': patient.PatientGender,
                    'PatientAddress': patient.PatientAddress,
                    'Allergy': patient.Allergy,
                    'History': patient.History,
                    'PatientNote': patient.PatientNote,
                    'CurrentDepartment': department_name,
                    'AssignedDate': assignment.At.strftime('%Y-%m-%d %H:%M:%S') if assignment and assignment.At else None
                }
                result.append(patient_data)
            
            return result
        except Exception as e:
            print(f"Error in get_by_department: {e}")
            return []


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

# Document models
class DocumentType(db.Model):
    __tablename__ = 'DocumentType'
    
    DocumentTypeId = db.Column(db.Integer, primary_key=True)
    DocumentTypeName = db.Column(db.String(25), nullable=False)
    
    # Relationships
    patient_documents = db.relationship('PatientDocuments', backref='document_type', lazy=True)
    
    def __repr__(self):
        return f'<DocumentType {self.DocumentTypeId}: {self.DocumentTypeName}>'
    
    def to_dict(self):
        """Convert DocumentType to dictionary"""
        return {
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.DocumentTypeName
        }

class PatientDocuments(db.Model):
    __tablename__ = 'PatientDocuments'
    
    DocumentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PatientId = db.Column(db.String(20), db.ForeignKey('Patient.PatientId'), nullable=False)
    DocumentTypeId = db.Column(db.Integer, db.ForeignKey('DocumentType.DocumentTypeId'), nullable=True)
    document_links = db.Column(db.JSON, nullable=False, comment='Structured document links')
    document_metadata = db.Column('metadata', db.JSON, nullable=True, comment='Document metadata and properties')
    original_filename = db.Column(db.String(255), nullable=True, comment='Original file name')
    file_type = db.Column(db.String(50), nullable=True, comment='File MIME type')
    file_size = db.Column(db.Integer, nullable=True, comment='File size in bytes')
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                             onupdate=db.func.current_timestamp())
    
    # Relationships
    patient = db.relationship('Patient', backref='patient_documents', lazy=True)
    
    def __repr__(self):
        return f'<PatientDocument {self.DocumentId}: {self.original_filename} for {self.PatientId}>'
    
    def to_dict(self):
        """Convert PatientDocuments to dictionary"""
        return {
            'DocumentId': self.DocumentId,
            'PatientId': self.PatientId,
            'PatientName': self.patient.PatientName if self.patient else None,
            'PatientAge': self.patient.PatientAge if self.patient else None,
            'DocumentTypeId': self.DocumentTypeId,
            'DocumentTypeName': self.document_type.DocumentTypeName if self.document_type else None,
            'document_links': self.document_links,
            'metadata': self.document_metadata,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S') if self.upload_date else None,
            'last_modified': self.last_modified.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified else None
        }

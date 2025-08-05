from typing import List, Optional

from sqlalchemy import CHAR, Column, DateTime, Double, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, LONGBLOB, LONGTEXT, SMALLINT, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

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
class Base(DeclarativeBase):
    pass


class BodySite(Base):
    __tablename__ = 'BodySite'

    SiteId: Mapped[int] = mapped_column(INTEGER(5), primary_key=True)
    SiteName: Mapped[str] = mapped_column(String(100))


class BodySystem(Base):
    __tablename__ = 'BodySystem'

    SystemId: Mapped[int] = mapped_column(INTEGER(1), primary_key=True)
    SystemName: Mapped[str] = mapped_column(String(50))

    Sign: Mapped[List['Sign']] = relationship('Sign', back_populates='BodySystem_')


class Department(Base):
    __tablename__ = 'Department'

    DepartmentId: Mapped[int] = mapped_column(SMALLINT(6), primary_key=True)
    DepartmentName: Mapped[Optional[str]] = mapped_column(String(100))
    DepartmentType: Mapped[Optional[str]] = mapped_column(Enum('Nội trú', 'Cấp cứu', 'Phòng khám'), comment='Loại khoa')

    Staff: Mapped[List['Staff']] = relationship('Staff', back_populates='Department_')
    Template: Mapped[List['Template']] = relationship('Template', back_populates='Department_')
    Test: Mapped[List['Test']] = relationship('Test', back_populates='Department_')
    Visit: Mapped[List['Visit']] = relationship('Visit', back_populates='Department_')


class Drug(Base):
    __tablename__ = 'Drug'
    __table_args__ = (
        Index('idx_drug_available', 'DrugAvailable'),
    )

    DrugId: Mapped[str] = mapped_column(String(50), primary_key=True)
    DrugName: Mapped[Optional[str]] = mapped_column(String(255))
    DrugChemical: Mapped[Optional[str]] = mapped_column(String(255))
    DrugContent: Mapped[Optional[str]] = mapped_column(String(100))
    DrugFormulation: Mapped[Optional[str]] = mapped_column(String(50))
    DrugRemains: Mapped[Optional[int]] = mapped_column(SMALLINT(6))
    DrugGroup: Mapped[Optional[str]] = mapped_column(String(100))
    DrugTherapy: Mapped[Optional[str]] = mapped_column(String(200))
    DrugRoute: Mapped[Optional[str]] = mapped_column(String(50))
    DrugQuantity: Mapped[Optional[str]] = mapped_column(String(50))
    CountStr: Mapped[Optional[str]] = mapped_column(String(50))
    DrugAvailable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))
    DrugPriceBHYT: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    DrugPriceVP: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    DrugNote: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("''"), comment='Ghi chú về thuốc')
    Count: Mapped[Optional[str]] = mapped_column(String(50))

    Template: Mapped[List['Template']] = relationship('Template', secondary='DrugTemplate', back_populates='Drug_')


class ICD(Base):
    __tablename__ = 'ICD'

    ICDCode: Mapped[str] = mapped_column(String(10), primary_key=True, comment='Mã ICD')
    ICDName: Mapped[str] = mapped_column(String(255), comment='Tên ICD')
    ICDGroup: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("''"), comment='Nhóm ICD')


class Patient(Base):
    __tablename__ = 'Patient'

    PatientId: Mapped[str] = mapped_column(String(10), primary_key=True)
    PatientName: Mapped[Optional[str]] = mapped_column(String(100))
    PatientGender: Mapped[Optional[str]] = mapped_column(Enum('Nam', 'Nữ', 'Khác'), comment='Giới tính')
    PatientAge: Mapped[Optional[str]] = mapped_column(CHAR(20), comment='Tuổi')
    PatientAddress: Mapped[Optional[str]] = mapped_column(String(255))
    Allergy: Mapped[Optional[str]] = mapped_column(String(255), server_default=text("''"), comment='Tiền sử dị ứng')
    History: Mapped[Optional[str]] = mapped_column(Text, comment='Tiền sử bệnh')
    PatientImage: Mapped[Optional[bytes]] = mapped_column(LONGBLOB, comment='Hình ảnh bệnh nhân')
    PatientNote: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("''"), comment='Ghi chú về bệnh nhân')

    Visit: Mapped[List['Visit']] = relationship('Visit', back_populates='Patient_')


t_PatientsWithDepartment = Table(
    'PatientsWithDepartment', Base.metadata,
    Column('PatientName', String(100)),
    Column('PatientGender', Enum('Nam', 'Nữ', 'Khác')),
    Column('PatientAge', CHAR(20)),
    Column('PatientImage', LONGBLOB),
    Column('DepartmentId', SMALLINT(6))
)


class Proc(Base):
    __tablename__ = 'Proc'

    ProcId: Mapped[str] = mapped_column(String(50), primary_key=True)
    ProcDesc: Mapped[Optional[str]] = mapped_column(String(100))
    ProcGroup: Mapped[Optional[str]] = mapped_column(String(100))
    ProcBHYT: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))
    ProcPriceBHYT: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    ProcPriceVP: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    ProcAvailable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))
    ProcNote: Mapped[Optional[str]] = mapped_column(String(100), comment='Ghi chú về thủ thuật')


t_PatientDepartment = Table(
    'PatientDepartment', Base.metadata,
    Column('PatientId', String(10), nullable=False),
    Column('DepartmentId', SMALLINT(6)),
    Column('Current', TINYINT(1), server_default=text('0'), comment='1 nếu là khoa hiện tại của bệnh nhân'),
    Column('At', TIMESTAMP, server_default=text('current_timestamp()')),
    ForeignKeyConstraint(['DepartmentId'], ['Department.DepartmentId'], name='PatientDepartment_ibfk_1'),
    ForeignKeyConstraint(['PatientId'], ['Patient.PatientId'], name='PatientDepartment_Patient_FK'),
    Index('DepartmentId', 'DepartmentId'),
    Index('PatientDepartment_Patient', 'PatientId', 'DepartmentId', unique=True),
    Index('idx_patient_current_dept', 'PatientId', 'Current')
)


class Sign(Base):
    __tablename__ = 'Sign'
    __table_args__ = (
        ForeignKeyConstraint(['SystemId'], ['BodySystem.SystemId'], name='Sign_ibfk_1'),
        Index('SystemId', 'SystemId')
    )

    SignId: Mapped[int] = mapped_column(SMALLINT(6), primary_key=True)
    SystemId: Mapped[int] = mapped_column(INTEGER(1))
    SignDesc: Mapped[Optional[str]] = mapped_column(String(100))
    SignType: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'), comment='0 nếu là dấu hiệu cơ năng, 1 nếu là dấu hiệu thực thể')
    Speciality: Mapped[Optional[str]] = mapped_column(String(100))

    BodySystem_: Mapped['BodySystem'] = relationship('BodySystem', back_populates='Sign')
    Template: Mapped[List['Template']] = relationship('Template', secondary='SignTemplate', back_populates='Sign_')


class Staff(Base):
    __tablename__ = 'Staff'
    __table_args__ = (
        ForeignKeyConstraint(['DepartmentId'], ['Department.DepartmentId'], name='Staff_ibfk_1'),
        Index('DepartmentId', 'DepartmentId'),
        Index('idx_staff_available', 'StaffAvailable', 'DepartmentId')
    )

    StaffId: Mapped[int] = mapped_column(SMALLINT(6), primary_key=True)
    StaffName: Mapped[Optional[str]] = mapped_column(String(100))
    StaffRole: Mapped[Optional[str]] = mapped_column(Enum('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác'), comment='Vai trò: Bác sĩ...')
    DepartmentId: Mapped[Optional[int]] = mapped_column(SMALLINT(6))
    StaffAvailable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'), comment='1 nếu nhân viên có thể làm việc, 0 nếu không')

    Department_: Mapped[Optional['Department']] = relationship('Department', back_populates='Staff')
    Visit: Mapped[List['Visit']] = relationship('Visit', secondary='VisitStaff', back_populates='Staff_')
    Visit_: Mapped[List['Visit']] = relationship('Visit', back_populates='Staff1')


class Template(Base):
    __tablename__ = 'Template'
    __table_args__ = (
        ForeignKeyConstraint(['DepartmentId'], ['Department.DepartmentId'], name='Template_ibfk_1'),
        Index('DepartmentId', 'DepartmentId')
    )

    TemplateId: Mapped[int] = mapped_column(SMALLINT(6), primary_key=True)
    TemplateName: Mapped[Optional[str]] = mapped_column(String(100))
    DepartmentId: Mapped[Optional[int]] = mapped_column(SMALLINT(6), comment='Khoa của tập mẫu')
    TemplateGroup: Mapped[Optional[str]] = mapped_column(Enum('Test', 'Sign', 'Drug', 'Proc'), comment='Loại của tập mẫu')
    TemplateType: Mapped[Optional[str]] = mapped_column(Enum('Bệnh án', 'Theo dõi'), comment='Loại ghi nhận')

    Drug_: Mapped[List['Drug']] = relationship('Drug', secondary='DrugTemplate', back_populates='Template')
    Sign_: Mapped[List['Sign']] = relationship('Sign', secondary='SignTemplate', back_populates='Template')
    Department_: Mapped[Optional['Department']] = relationship('Department', back_populates='Template')
    Test: Mapped[List['Test']] = relationship('Test', secondary='TestTemplate', back_populates='Template_')


class Test(Base):
    __tablename__ = 'Test'
    __table_args__ = (
        ForeignKeyConstraint(['InChargeDepartmentId'], ['Department.DepartmentId'], name='Test_Department_FK'),
        Index('Test_Department_FK', 'InChargeDepartmentId'),
        Index('idx_test_available', 'TestAvailable')
    )

    TestId: Mapped[str] = mapped_column(String(50), primary_key=True)
    TestName: Mapped[Optional[str]] = mapped_column(String(100))
    TestGroup: Mapped[Optional[str]] = mapped_column(String(100))
    TestPriceBHYT: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    TestPriceVP: Mapped[Optional[int]] = mapped_column(INTEGER(10), server_default=text('0'))
    TestAvailable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))
    TestNote: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("''"), comment='Ghi chú về xét nghiệm')
    TestType: Mapped[Optional[str]] = mapped_column(Enum('XN', 'SA', 'XQ', 'CT', 'TDCN', 'NS'))
    InChargeDepartmentId: Mapped[Optional[int]] = mapped_column(SMALLINT(6))

    Template_: Mapped[List['Template']] = relationship('Template', secondary='TestTemplate', back_populates='Test')
    Department_: Mapped[Optional['Department']] = relationship('Department', back_populates='Test')


t_DrugTemplate = Table(
    'DrugTemplate', Base.metadata,
    Column('TemplateId', SMALLINT(6), nullable=False),
    Column('DrugId', String(50), nullable=False),
    ForeignKeyConstraint(['DrugId'], ['Drug.DrugId'], name='DrugTemplate_ibfk_1'),
    ForeignKeyConstraint(['TemplateId'], ['Template.TemplateId'], name='DrugTemplate_ibfk_2'),
    Index('DrugTemplate_Drug', 'DrugId', 'TemplateId', unique=True),
    Index('TemplateId', 'TemplateId')
)


t_SignTemplate = Table(
    'SignTemplate', Base.metadata,
    Column('TemplateId', SMALLINT(6), nullable=False),
    Column('SignId', SMALLINT(6), nullable=False),
    ForeignKeyConstraint(['SignId'], ['Sign.SignId'], name='SignTemplate_ibfk_1'),
    ForeignKeyConstraint(['TemplateId'], ['Template.TemplateId'], name='SignTemplate_ibfk_2'),
    Index('SignTemplate_Sign', 'SignId', 'TemplateId', unique=True),
    Index('TemplateId', 'TemplateId')
)


t_TestTemplate = Table(
    'TestTemplate', Base.metadata,
    Column('TemplateId', SMALLINT(6), nullable=False),
    Column('TestId', String(50), nullable=False),
    ForeignKeyConstraint(['TemplateId'], ['Template.TemplateId'], name='TestTemplate_ibfk_2'),
    ForeignKeyConstraint(['TestId'], ['Test.TestId'], name='TestTemplate_ibfk_1'),
    Index('TemplateId', 'TemplateId'),
    Index('TestTemplate_Test', 'TestId', 'TemplateId', unique=True)
)


class Visit(Base):
    __tablename__ = 'Visit'
    __table_args__ = (
        ForeignKeyConstraint(['DepartmentId'], ['Department.DepartmentId'], name='Visit_ibfk_2'),
        ForeignKeyConstraint(['PatientId'], ['Patient.PatientId'], name='Visit_Patient_FK'),
        ForeignKeyConstraint(['StaffId'], ['Staff.StaffId'], name='Visit_ibfk_3'),
        Index('DepartmentId', 'DepartmentId'),
        Index('StaffId', 'StaffId'),
        # Index('idx_visit_patient_date', 'PatientId', 'VisitTime'),
        # Index('idx_visit_time', 'VisitTime')
    )

    VisitId: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    PatientId: Mapped[str] = mapped_column(String(10), comment='Mã bệnh nhân')
    DepartmentId: Mapped[int] = mapped_column(SMALLINT(6))
    StaffId: Mapped[int] = mapped_column(SMALLINT(6), comment='Nhân viên thăm khám')
    VisitPurpose: Mapped[Optional[str]] = mapped_column(Enum('Thường quy', 'Cấp cứu', 'Phòng khám', 'Nhận bệnh', 'Bệnh án', 'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám', 'Khám chuyên khoa'), comment='Loại của lần thăm khám')
    # VisitTime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    Staff_: Mapped[List['Staff']] = relationship('Staff', secondary='VisitStaff', back_populates='Visit')
    Department_: Mapped['Department'] = relationship('Department', back_populates='Visit')
    Patient_: Mapped['Patient'] = relationship('Patient', back_populates='Visit')
    Staff1: Mapped['Staff'] = relationship('Staff', back_populates='Visit_')
    VisitImage: Mapped[List['VisitImage']] = relationship('VisitImage', back_populates='Visit_')


t_VisitDiagnosis = Table(
    'VisitDiagnosis', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('ICDCode', String(10), comment='mã ICD chẩn đoán'),
    Column('ActualDiagnosis', String(255), comment='Chẩn đoán thực tế'),
    Column('DiseaseType', Enum('Bệnh chính', 'Bệnh kèm', 'Biến chứng')),
    ForeignKeyConstraint(['ICDCode'], ['ICD.ICDCode'], name='VisitDiagnosis_ICD_FK'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], onupdate='CASCADE', name='VisitDiagnosis_ibfk_1'),
    Index('VisitDiagnosis_ICD_FK', 'ICDCode'),
    Index('VisitDiagnosis_Visit', 'VisitId', 'ICDCode', unique=True)
)


t_VisitDocuments = Table(
    'VisitDocuments', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('document_links', LONGTEXT, nullable=False, comment='Structured document links'),
    Column('metadata', LONGTEXT, comment='Document metadata and properties'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitDocuments_Visit_FK'),
    Index('VisitDocuments_Visit_FK', 'VisitId')
)


t_VisitDrug = Table(
    'VisitDrug', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('DrugId', String(50)),
    Column('DrugRoute', String(100)),
    Column('DrugQuantity', Double(asdecimal=True)),
    Column('DrugTimes', String(100)),
    Column('DrugAtTime', DateTime),
    Column('Note', String(100)),
    Column('DrugStatus', Enum('CD', 'TH', 'XONG'), server_default=text("'CD'")),
    ForeignKeyConstraint(['DrugId'], ['Drug.DrugId'], name='VisitDrug_ibfk_2'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitDrug_ibfk_1'),
    Index('VisitId', 'VisitId'),
    Index('Visit_VisitDrug', 'DrugId', 'VisitId', unique=True)
)


class VisitImage(Base):
    __tablename__ = 'VisitImage'
    __table_args__ = (
        ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitImage_Visit_FK'),
        Index('VisitId', 'VisitId')
    )

    VisitId: Mapped[int] = mapped_column(BIGINT(20))
    ImageId: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    ImageData: Mapped[bytes] = mapped_column(LONGBLOB, comment='Binary image data')
    ImageType: Mapped[Optional[str]] = mapped_column(String(50), comment='Type of image (e.g. wound, burn, scan, etc.)')
    ImageUrl: Mapped[Optional[str]] = mapped_column(String(255), comment='Optional: URL if stored externally')
    Description: Mapped[Optional[str]] = mapped_column(String(255), comment='Description or notes about the image')
    CreatedAt: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('current_timestamp()'))

    Visit_: Mapped['Visit'] = relationship('Visit', back_populates='VisitImage')


t_VisitProc = Table(
    'VisitProc', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('ProcId', String(50)),
    Column('ProcStatus', Enum('Ordered', 'In progress', 'Completed', 'Result'), server_default=text("'Ordered'"), comment='Trạng thái của thủ thuật'),
    Column('ProcStaffId', SMALLINT(6), comment='Nhân viên thực hiện thủ thuật'),
    Column('ProcTime', DateTime, comment='Thời gian thực hiện'),
    Column('IsCustom', TINYINT(1), server_default=text('0'), comment='1 nếu bác sĩ tự thêm (không từ template)'),
    ForeignKeyConstraint(['ProcId'], ['Proc.ProcId'], name='VisitProc_ibfk_2'),
    ForeignKeyConstraint(['ProcStaffId'], ['Staff.StaffId'], name='VisitProc_ibfk_3'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitProc_ibfk_1'),
    Index('ProcStaffId', 'ProcStaffId'),
    Index('VisitId', 'VisitId'),
    Index('Visit_VisitProc', 'ProcId', 'VisitId', unique=True)
)


t_VisitSign = Table(
    'VisitSign', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('SignId', SMALLINT(6)),
    Column('BodySiteId', INTEGER(5), comment='Vùng cơ thể có dấu hiệu'),
    Column('LeftRight', Enum('trái', 'phải', 'cả hai bên'), comment='Vị trí của dấu hiệu'),
    Column('Section', Enum('toàn bộ', '1/3', '1/4', '1/5'), comment='Vị trí của dấu hiệu'),
    Column('UpperLower', Enum('trên', 'dưới', 'giữa'), comment='Vị trí của dấu hiệu'),
    Column('FrontBack', Enum('mặt trước', 'mặt sau', 'mặt trong', 'mặt ngoài'), comment='Vị trí của dấu hiệu'),
    Column('SignValue', Enum('', 'BT', 'Có DHBL', 'Có', 'Không', 'Ít', 'Vừa', 'Nhiều', 'Nhẹ', 'Tăng', 'Giảm', 'Như cũ'), comment='Giá trị của dấu hiệu'),
    Column('FollowUp', TINYINT(1), server_default=text('0')),
    Column('ForEmr', TINYINT(1), server_default=text('0')),
    Column('IsCustom', TINYINT(1), server_default=text('0'), comment='1 nếu bác sĩ tự thêm (không từ template)'),
    ForeignKeyConstraint(['BodySiteId'], ['BodySite.SiteId'], name='VisitSign_ibfk_3'),
    ForeignKeyConstraint(['SignId'], ['Sign.SignId'], name='VisitSign_ibfk_1'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitSign_ibfk_2'),
    Index('BodySiteId', 'BodySiteId'),
    Index('VisitId', 'VisitId'),
    Index('Visit_VisitSign', 'SignId', 'VisitId', unique=True)
)


t_VisitStaff = Table(
    'VisitStaff', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('StaffId', SMALLINT(6), nullable=False),
    ForeignKeyConstraint(['StaffId'], ['Staff.StaffId'], name='VisitStaff_ibfk_2'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitStaff_ibfk_1'),
    Index('VisitId', 'VisitId'),
    Index('Visit_VisitStaff', 'StaffId', 'VisitId', unique=True)
)


t_VisitTest = Table(
    'VisitTest', Base.metadata,
    Column('VisitId', BIGINT(20), nullable=False),
    Column('TestId', String(50)),
    Column('TestStatus', Enum('CD', 'TH', 'XONG'), server_default=text("'CD'")),
    Column('TestStaffId', SMALLINT(6), comment='Nhân viên thực hiện xét nghiệm'),
    Column('TestTime', DateTime, comment='Thời gian thực hiện'),
    Column('TestResult', String(255), comment='Kết quả'),
    Column('TestConclusion', String(20)),
    Column('IsCustom', TINYINT(1), server_default=text('0'), comment='1 nếu bác sĩ tự thêm (không từ template)'),
    ForeignKeyConstraint(['TestId'], ['Test.TestId'], name='VisitTest_ibfk_2'),
    ForeignKeyConstraint(['TestStaffId'], ['Staff.StaffId'], name='VisitTest_ibfk_3'),
    ForeignKeyConstraint(['VisitId'], ['Visit.VisitId'], name='VisitTest_ibfk_1'),
    Index('TestStaffId', 'TestStaffId'),
    Index('VisitId', 'VisitId'),
    Index('Visit_VisitTest', 'TestId', 'VisitId', unique=True)
)

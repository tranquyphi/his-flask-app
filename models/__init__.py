"""
Models package for HIS (Hospital Information System)
Contains separated model files for better maintainability
"""

# Direct imports of all model classes
from .DocumentType import DocumentType
from .BodyPart import BodyPart
from .BodySite import BodySite
from .BodySystem import BodySystem
from .Department import Department
from .DrugGroup import DrugGroup
from .Drug import Drug
from .ICD import ICD
from .Patient import Patient
from .Proc import Proc
from .PatientDepartment import PatientDepartment
from .Sign import Sign
from .Staff import Staff
from .StaffDepartment import StaffDepartment
from .Template import Template
from .Test import Test
from .Visit import Visit

# Visit-related association models
from .VisitDiagnosis import VisitDiagnosis
from .VisitDocuments import VisitDocuments
from .VisitImage import VisitImage
from .VisitDrug import VisitDrug
from .VisitProc import VisitProc
from .VisitSign import VisitSign
from .Visit import VisitStaff
from .VisitTest import VisitTest

# Template-related association models
from .TestTemplate import TestTemplate
from .DrugTemplate import DrugTemplate
from .DrugTemplateDetail import DrugTemplateDetail
from .SignTemplate import SignTemplate
from .SignTemplateDetail import SignTemplateDetail

# Document and service models
from .PatientDocuments import PatientDocuments
from .PatientsWithDepartment import PatientsWithDepartment

# Make all models available at package level
__all__ = [
    # Core models
    'DocumentType', 'BodyPart', 'BodySite', 'BodySystem', 'Department',
    'DrugGroup', 'Drug', 'ICD', 'Patient', 'Proc', 'PatientDepartment',
    'Sign', 'Staff', 'StaffDepartment', 'Template', 'Test', 'Visit',
    
    # Visit-related association models
    'VisitDiagnosis', 'VisitDocuments', 'VisitImage', 'VisitDrug', 
    'VisitProc', 'VisitSign', 'VisitStaff', 'VisitTest',
    
    # Template-related association models
    'TestTemplate', 'DrugTemplate', 'DrugTemplateDetail', 
    'SignTemplate', 'SignTemplateDetail',
    
    # Document and service models
    'PatientDocuments', 'PatientsWithDepartment'
]

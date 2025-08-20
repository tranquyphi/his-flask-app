"""
PatientsWithDepartment Service Class
"""

from models_main import db

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
            # Import here to avoid circular imports
            from models.Patient import Patient
            from models.Department import Department
            from models.PatientDepartment import PatientDepartment
            
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
                    'AllDepartments': all_departments,
                    'At': latest_assignment.At.isoformat() if latest_assignment and latest_assignment.At else None
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
            # Import here to avoid circular imports
            from models.Patient import Patient
            from models.Department import Department
            from models.PatientDepartment import PatientDepartment
            
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
                    'AssignedDate': assignment.At.strftime('%Y-%m-%d %H:%M:%S') if assignment and assignment.At else None,
                    'At': assignment.At.isoformat() if assignment and assignment.At else None
                }
                result.append(patient_data)
            
            return result
        except Exception as e:
            print(f"Error in get_by_department: {e}")
            return []

import os
try:
    import pandas as pd  # type: ignore
    _PANDAS_AVAILABLE = True
except Exception:
    pd = None  # type: ignore
    _PANDAS_AVAILABLE = False
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
import tempfile

# Import the functions from separate files
from api.excel_functions1 import import_drugs, import_icd, import_patients
from api.excel_functions2 import import_procedures, import_signs, import_staff
from api.excel_functions3 import import_tests

excel_upload_bp = Blueprint('excel_upload', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@excel_upload_bp.route('/excel/upload')
def excel_upload_page():
    """Render the Excel upload interface"""
    if not _PANDAS_AVAILABLE:
        return render_template('excel_upload.html', default_table='', error='Pandas library not installed on server')
    # Get table parameter if provided
    table = request.args.get('table', '')
    return render_template('excel_upload.html', default_table=table)
    
@excel_upload_bp.route('/api/upload/tables')
def get_available_tables():
    """Return a list of tables that support Excel upload"""
    if not _PANDAS_AVAILABLE:
        return jsonify({"error": "pandas not installed"}), 503
    tables = [
        {
            "id": "body_parts", 
            "name": "Body Parts", 
            "description": "Anatomical body parts like Head, Arm, Leg, etc.",
            "template_available": True,
            "columns": [
                {"name": "BodyPartId", "type": "number", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "BodyPartName", "type": "text", "required": True, "description": "Name of the body part"}
            ]
        },
        {
            "id": "body_sites", 
            "name": "Body Sites", 
            "description": "Specific sites on body parts like Forehead, Upper arm, etc.",
            "template_available": True,
            "columns": [
                {"name": "SiteId", "type": "number", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "SiteName", "type": "text", "required": True, "description": "Name of the body site"},
                {"name": "BodyPartId", "type": "number", "required": True, "description": "ID of the associated body part"}
            ]
        },
        {
            "id": "departments", 
            "name": "Departments", 
            "description": "Hospital departments and units",
            "template_available": True,
            "columns": [
                {"name": "DepartmentId", "type": "number", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "DepartmentName", "type": "text", "required": True, "description": "Name of the department"},
                {"name": "DepartmentType", "type": "text", "required": True, "description": "Type of department (Nội trú, Cấp cứu, Phòng khám)"}
            ]
        },
        {
            "id": "drugs", 
            "name": "Drugs", 
            "description": "Medications and pharmaceutical products",
            "template_available": True,
            "columns": [
                {"name": "DrugId", "type": "text", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "DrugName", "type": "text", "required": True, "description": "Name of the drug"},
                {"name": "DrugChemical", "type": "text", "required": False, "description": "Chemical composition"},
                {"name": "DrugContent", "type": "text", "required": False, "description": "Content/strength information"},
                {"name": "DrugFormulation", "type": "text", "required": False, "description": "Form of the drug (tablet, liquid, etc.)"},
                {"name": "DrugRemains", "type": "number", "required": False, "description": "Remaining quantity in stock"},
                {"name": "DrugGroupId", "type": "integer", "required": False, "description": "Drug group ID (integer)"},
                {"name": "DrugPriceBHYT", "type": "number", "required": False, "description": "Price for insured patients"},
                {"name": "DrugPriceVP", "type": "number", "required": False, "description": "Price for non-insured patients"}
            ]
        },
        {
            "id": "icd", 
            "name": "ICD Codes", 
            "description": "International Classification of Diseases codes",
            "template_available": True,
            "columns": [
                {"name": "ICDCode", "type": "text", "required": True, "description": "ICD code identifier"},
                {"name": "ICDName", "type": "text", "required": True, "description": "Description of the condition/diagnosis"},
                {"name": "ICDGroup", "type": "text", "required": False, "description": "Classification group"}
            ]
        },
        {
            "id": "patients", 
            "name": "Patients", 
            "description": "Patient demographic information",
            "template_available": True,
            "columns": [
                {"name": "PatientId", "type": "text", "required": True, "description": "Unique patient identifier"},
                {"name": "PatientName", "type": "text", "required": True, "description": "Full name of patient"},
                {"name": "PatientGender", "type": "text", "required": True, "description": "Gender (Nam, Nữ, Khác)"},
                {"name": "PatientAge", "type": "text", "required": True, "description": "Age or date of birth"},
                {"name": "PatientAddress", "type": "text", "required": False, "description": "Residential address"},
                {"name": "Allergy", "type": "text", "required": False, "description": "Known allergies"},
                {"name": "PatientNote", "type": "text", "required": False, "description": "Additional notes"}
            ]
        },
        {
            "id": "procedures", 
            "name": "Procedures", 
            "description": "Medical procedures and services",
            "template_available": True,
            "columns": [
                {"name": "ProcId", "type": "text", "required": True, "description": "Procedure code/identifier"},
                {"name": "ProcDesc", "type": "text", "required": True, "description": "Description of procedure"},
                {"name": "ProcGroup", "type": "text", "required": False, "description": "Category/group of procedure"},
                {"name": "ProcBHYT", "type": "boolean", "required": False, "description": "Covered by insurance (True/False)"},
                {"name": "ProcPriceBHYT", "type": "number", "required": False, "description": "Price for insured patients"},
                {"name": "ProcPriceVP", "type": "number", "required": False, "description": "Price for non-insured patients"},
                {"name": "ProcAvailable", "type": "boolean", "required": False, "description": "Currently available (True/False)"}
            ]
        },
        {
            "id": "signs", 
            "name": "Signs & Symptoms", 
            "description": "Clinical signs and symptoms for examinations",
            "template_available": True,
            "columns": [
                {"name": "SignId", "type": "number", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "SignDesc", "type": "text", "required": True, "description": "Description of the sign/symptom"},
                {"name": "SignType", "type": "boolean", "required": True, "description": "Type (0: cơ năng, 1: thực thể)"},
                {"name": "SystemId", "type": "number", "required": True, "description": "Associated body system ID"},
                {"name": "Speciality", "type": "text", "required": False, "description": "Medical specialty"}
            ]
        },
        {
            "id": "staff", 
            "name": "Staff", 
            "description": "Hospital staff and healthcare providers",
            "template_available": True,
            "columns": [
                {"name": "StaffId", "type": "number", "required": False, "description": "Unique ID (optional for new records)"},
                {"name": "StaffName", "type": "text", "required": True, "description": "Full name of staff member"},
                {"name": "StaffRole", "type": "text", "required": True, "description": "Role (Bác sĩ, Điều dưỡng, Kỹ thuật viên, Khác)"},
                {"name": "DepartmentId", "type": "number", "required": True, "description": "Associated department ID"},
                {"name": "StaffAvailable", "type": "boolean", "required": False, "description": "Currently available (True/False)"}
            ]
        },
        {
            "id": "tests", 
            "name": "Medical Tests", 
            "description": "Laboratory and diagnostic tests",
            "template_available": True,
            "columns": [
                {"name": "TestId", "type": "text", "required": True, "description": "Test code/identifier"},
                {"name": "TestDesc", "type": "text", "required": True, "description": "Description of test"},
                {"name": "TestUnit", "type": "text", "required": False, "description": "Unit of measurement"},
                {"name": "TestMale", "type": "text", "required": False, "description": "Normal range for males"},
                {"name": "TestFemale", "type": "text", "required": False, "description": "Normal range for females"},
                {"name": "TestPriceBHYT", "type": "number", "required": False, "description": "Price for insured patients"},
                {"name": "TestPriceVP", "type": "number", "required": False, "description": "Price for non-insured patients"},
                {"name": "DepartmentId", "type": "number", "required": True, "description": "Department responsible for the test"}
            ]
        }
    ]
    return jsonify({"tables": tables})

@excel_upload_bp.route('/api/upload/template/<string:table_name>')
def generate_template(table_name):
    """Generate a template Excel file for the specified table"""
    import io
    from flask import send_file
    
    # Define column headers based on table name
    if table_name == 'body_parts':
        columns = ['BodyPartId', 'BodyPartName']
        sample_data = [
            [1, 'Head'],
            [2, 'Chest'],
            [3, 'Abdomen']
        ]
    elif table_name == 'body_sites':
        columns = ['SiteId', 'SiteName', 'BodyPartId']
        sample_data = [
            [1, 'Forehead', 1],
            [2, 'Temple', 1],
            [3, 'Upper Chest', 2]
        ]
    elif table_name == 'departments':
        columns = ['DepartmentId', 'DepartmentName', 'DepartmentType']
        sample_data = [
            [1, 'Internal Medicine', 'Nội trú'],
            [2, 'Emergency', 'Cấp cứu'],
            [3, 'Outpatient Clinic', 'Phòng khám']
        ]
    elif table_name == 'drugs':
        columns = ['DrugId', 'DrugName', 'DrugChemical', 'DrugContent', 'DrugFormulation', 
                   'DrugRemains', 'DrugGroup', 'DrugPriceBHYT', 'DrugPriceVP']
        sample_data = [
            ['PARA500', 'Paracetamol', 'Acetaminophen', '500mg', 'Tablet', 100, 'Analgesic', 2000, 3000],
            ['AMOX250', 'Amoxicillin', 'Amoxicillin Trihydrate', '250mg', 'Capsule', 50, 'Antibiotic', 5000, 7500],
            ['IBUP400', 'Ibuprofen', 'Ibuprofen', '400mg', 'Tablet', 75, 'NSAID', 3000, 4500]
        ]
    elif table_name == 'icd':
        columns = ['ICDCode', 'ICDName', 'ICDGroup']
        sample_data = [
            ['A00', 'Cholera', 'Intestinal infectious diseases'],
            ['I21', 'Acute myocardial infarction', 'Cardiovascular diseases'],
            ['J45', 'Asthma', 'Respiratory diseases']
        ]
    elif table_name == 'patients':
        columns = ['PatientId', 'PatientName', 'PatientGender', 'PatientAge', 'PatientAddress', 'Allergy', 'PatientNote']
        sample_data = [
            ['PT001', 'Nguyen Van A', 'Nam', '45', 'Hanoi', 'Penicillin', 'Hypertension patient'],
            ['PT002', 'Tran Thi B', 'Nữ', '32', 'Ho Chi Minh City', 'None', ''],
            ['PT003', 'Le Van C', 'Nam', '28', 'Da Nang', 'Aspirin', 'Asthma history']
        ]
    elif table_name == 'procedures':
        columns = ['ProcId', 'ProcDesc', 'ProcGroup', 'ProcBHYT', 'ProcPriceBHYT', 'ProcPriceVP', 'ProcAvailable']
        sample_data = [
            ['PRO001', 'X-ray Chest', 'Radiology', True, 100000, 150000, True],
            ['PRO002', 'Complete Blood Count', 'Laboratory', True, 50000, 75000, True],
            ['PRO003', 'CT Scan Brain', 'Radiology', True, 1000000, 1500000, True]
        ]
    elif table_name == 'signs':
        columns = ['SignId', 'SignDesc', 'SignType', 'SystemId', 'Speciality']
        sample_data = [
            [1, 'Headache', 0, 1, 'Neurology'],
            [2, 'Fever', 0, 5, 'General'],
            [3, 'Rash', 1, 3, 'Dermatology']
        ]
    elif table_name == 'staff':
        columns = ['StaffId', 'StaffName', 'StaffRole', 'DepartmentId', 'StaffAvailable']
        sample_data = [
            [1, 'Dr. Nguyen Van X', 'Bác sĩ', 1, True],
            [2, 'Nurse Tran Thi Y', 'Điều dưỡng', 2, True],
            [3, 'Tech Le Van Z', 'Kỹ thuật viên', 3, True]
        ]
    elif table_name == 'tests':
        columns = ['TestId', 'TestDesc', 'TestUnit', 'TestMale', 'TestFemale', 'TestPriceBHYT', 'TestPriceVP', 'DepartmentId']
        sample_data = [
            ['CBC', 'Complete Blood Count', '', '', '', 50000, 75000, 4],
            ['GLU', 'Blood Glucose', 'mmol/L', '3.9-6.1', '3.9-6.1', 20000, 30000, 4],
            ['CHOL', 'Total Cholesterol', 'mmol/L', '<5.2', '<5.2', 25000, 40000, 4]
        ]
    else:
        return jsonify({'error': f'Template not available for {table_name}'}), 404
        
    # Create DataFrame with sample data
    df = pd.DataFrame(sample_data, columns=columns)
    
    # Create Excel file in memory
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name=table_name.title())
    
    # Add a instructions sheet
    instructions_data = [
        ['Template Instructions'],
        ['1. Do not modify the column headers'],
        ['2. Fill in the required fields for each row'],
        ['3. For new records, you can leave ID fields empty'],
        ['4. For existing records, include the ID to update them']
    ]
    instr_df = pd.DataFrame(instructions_data)
    instr_df.to_excel(writer, index=False, sheet_name='Instructions', header=False)
    
    # Save and return the file
    writer.close()
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'{table_name}_template.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@excel_upload_bp.route('/api/upload/excel/<string:table_name>', methods=['POST'])
def upload_excel(table_name):
    """
    Upload Excel file and import it to the specified database table.
    Required: POST request with 'file' in form-data
    Optional: 'sheet_name' in form-data (defaults to first sheet if not provided)
    """
    from models_main import db
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Save file to temporary location
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        # Get sheet name if provided
        sheet_name = request.form.get('sheet_name', 0)  # Default to first sheet if not specified
        
        try:
            # Read Excel file
            df = pd.read_excel(temp_path, sheet_name=sheet_name)
            
            # Handle different table types
            if table_name == 'body_parts':
                from models import BodyPart
                result = import_body_parts(df, db)
            elif table_name == 'body_sites':
                from models import BodySite
                result = import_body_sites(df, db)
            elif table_name == 'departments':
                from models import Department
                result = import_departments(df, db)
            elif table_name == 'drugs':
                from models import Drug
                result = import_drugs(df, db)
            elif table_name == 'icd':
                from models import ICD
                result = import_icd(df, db)
            elif table_name == 'patients':
                from models import Patient
                result = import_patients(df, db)
            elif table_name == 'procedures':
                from models import Proc
                result = import_procedures(df, db)
            elif table_name == 'signs':
                from models import Sign
                result = import_signs(df, db)
            elif table_name == 'staff':
                from models import Staff
                result = import_staff(df, db)
            elif table_name == 'tests':
                from models import Test
                result = import_tests(df, db)
            else:
                return jsonify({'error': f'Table {table_name} not supported for import'}), 400
            
            # Clean up temp file
            os.unlink(temp_path)
            os.rmdir(temp_dir)
            
            return jsonify(result)
        
        except Exception as e:
            # Clean up temp file
            try:
                os.unlink(temp_path)
                os.rmdir(temp_dir)
            except:
                pass
                
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'File type not allowed. Please upload .xlsx or .xls files.'}), 400

def import_body_parts(df, db):
    """Import BodyPart data from DataFrame to database"""
    import pandas as pd
    from models import BodyPart
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['BodyPartName']
    
    # Check if all required columns are present
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Process data
    total_rows = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Check for missing required values
            if pd.isna(row['BodyPartName']) or not str(row['BodyPartName']).strip():
                errors.append(f"Error in row {idx+2}: Missing BodyPartName")
                skipped += 1
                continue
            
            # Check if BodyPartId is provided for updates
            if 'BodyPartId' in df.columns and not pd.isna(row['BodyPartId']):
                body_part_id = str(row['BodyPartId']).strip()
                existing = BodyPart.query.get(body_part_id)
                
                if existing:
                    # Update existing record
                    existing.BodyPartName = row['BodyPartName']
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_body_part = BodyPart(
                        BodyPartId=body_part_id,
                        BodyPartName=row['BodyPartName']
                    )
                    db.session.add(new_body_part)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                # Create new record without specifying ID (auto-increment)
                new_body_part = BodyPart(
                    BodyPartName=row['BodyPartName']
                )
                db.session.add(new_body_part)
                db.session.commit()  # Commit each row individually
                imported += 1
                
        except Exception as e:
            db.session.rollback()  # Reset session state after constraint violation
            errors.append(f"Error in row {idx+2}: {str(e)}")
            skipped += 1
    
    # Return results (no final commit needed since we commit each row)
    return {
        'success': True,
        'total_rows': total_rows,
        'imported': imported,
        'updated': updated,
        'skipped': skipped,
        'errors': errors
    }

def import_body_sites(df, db):
    """Import BodySite data from DataFrame to database"""
    import pandas as pd
    from models import BodySite, BodyPart
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['SiteName', 'BodyPartId']
    
    # Check if all required columns are present
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Process data
    total_rows = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Check for missing required values
            if pd.isna(row['SiteName']) or not str(row['SiteName']).strip():
                errors.append(f"Error in row {idx+2}: Missing SiteName")
                skipped += 1
                continue
            
            if pd.isna(row['BodyPartId']):
                errors.append(f"Error in row {idx+2}: Missing BodyPartId")
                skipped += 1
                continue
            
            # Validate BodyPartId exists
            body_part_id = str(row['BodyPartId']).strip()
            body_part = BodyPart.query.get(body_part_id)
            if not body_part:
                errors.append(f"Error in row {idx+2}: BodyPartId '{body_part_id}' does not exist")
                skipped += 1
                continue
            
            # Optional fields with default values
            site_desc = row['SiteDesc'] if 'SiteDesc' in df.columns and not pd.isna(row['SiteDesc']) else ''
            
            # Check if SiteId is provided for updates
            if 'SiteId' in df.columns and not pd.isna(row['SiteId']):
                site_id = str(row['SiteId']).strip()
                existing = BodySite.query.get(site_id)
                
                if existing:
                    # Update existing record
                    existing.SiteName = row['SiteName']
                    existing.SiteDesc = site_desc
                    existing.BodyPartId = body_part_id
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_site = BodySite(
                        SiteId=site_id,
                        SiteName=row['SiteName'],
                        SiteDesc=site_desc,
                        BodyPartId=body_part_id
                    )
                    db.session.add(new_site)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                # Create new record without specifying ID (auto-increment)
                new_site = BodySite(
                    SiteName=row['SiteName'],
                    SiteDesc=site_desc,
                    BodyPartId=body_part_id
                )
                db.session.add(new_site)
                db.session.commit()  # Commit each row individually
                imported += 1
                
        except Exception as e:
            db.session.rollback()  # Reset session state after constraint violation
            errors.append(f"Error in row {idx+2}: {str(e)}")
            skipped += 1
    
    # Return results (no final commit needed since we commit each row)
    return {
        'success': True,
        'total_rows': total_rows,
        'imported': imported,
        'updated': updated,
        'skipped': skipped,
        'errors': errors
    }
        
# Department import function
def import_departments(df, db):
    """Import Department data from DataFrame to database"""
    import pandas as pd
    from models import Department
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['DepartmentName', 'DepartmentType']
    
    # Check if all required columns are present
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Validate DepartmentType values
    valid_types = ['Nội trú', 'Cấp cứu', 'Phòng khám']
    invalid_types = []
    for idx, row in df.iterrows():
        if pd.notna(row['DepartmentType']) and row['DepartmentType'] not in valid_types:
            invalid_types.append(f"Row {idx+2}: {row['DepartmentType']}")
    
    if invalid_types:
        return {'error': f'Invalid DepartmentType values. Must be one of: {", ".join(valid_types)}. Found: {", ".join(invalid_types)}'}
    
    # Process data
    total_rows = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Check for missing required values
            if pd.isna(row['DepartmentName']) or not str(row['DepartmentName']).strip():
                errors.append(f"Error in row {idx+2}: Missing DepartmentName")
                skipped += 1
                continue
                
            if pd.isna(row['DepartmentType']) or not str(row['DepartmentType']).strip():
                errors.append(f"Error in row {idx+2}: Missing DepartmentType")
                skipped += 1
                continue
            
            # Check if DepartmentId is provided for updating
            if 'DepartmentId' in df.columns and not pd.isna(row['DepartmentId']):
                dept_id = str(row['DepartmentId']).strip()
                existing = Department.query.get(dept_id)
                
                if existing:
                    # Update existing record
                    existing.DepartmentName = row['DepartmentName']
                    existing.DepartmentType = row['DepartmentType']
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_dept = Department(
                        DepartmentId=dept_id,
                        DepartmentName=row['DepartmentName'],
                        DepartmentType=row['DepartmentType']
                    )
                    db.session.add(new_dept)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                # Create new record with auto-generated ID
                new_dept = Department(
                    DepartmentName=row['DepartmentName'],
                    DepartmentType=row['DepartmentType']
                )
                db.session.add(new_dept)
                db.session.commit()  # Commit each row individually
                imported += 1
                
        except Exception as e:
            db.session.rollback()  # Reset session state after constraint violation
            errors.append(f"Error in row {idx+2}: {str(e)}")
            skipped += 1
    
    # Return results (no final commit needed since we commit each row)
    return {
        'success': True,
        'total_rows': total_rows,
        'imported': imported,
        'updated': updated,
        'skipped': skipped,
        'errors': errors
    }

# Procedure import function
def import_procedures(df, db):
    """Import Proc data from DataFrame to database"""
    import pandas as pd
    from models import Proc
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['ProcId', 'ProcDesc']
    
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
            if pd.isna(row['ProcId']) or not str(row['ProcId']).strip():
                errors.append(f"Error in row {idx+2}: Missing ProcId")
                skipped += 1
                continue
                
            if pd.isna(row['ProcDesc']) or not str(row['ProcDesc']).strip():
                errors.append(f"Error in row {idx+2}: Missing ProcDesc")
                skipped += 1
                continue
            
            # Optional fields with default values
            proc_group = row['ProcGroup'] if 'ProcGroup' in df.columns and not pd.isna(row['ProcGroup']) else ''
            proc_bhyt = bool(row['ProcBHYT']) if 'ProcBHYT' in df.columns and not pd.isna(row['ProcBHYT']) else True
            proc_price_bhyt = int(row['ProcPriceBHYT']) if 'ProcPriceBHYT' in df.columns and not pd.isna(row['ProcPriceBHYT']) else 0
            proc_price_vp = int(row['ProcPriceVP']) if 'ProcPriceVP' in df.columns and not pd.isna(row['ProcPriceVP']) else 0
            proc_available = bool(row['ProcAvailable']) if 'ProcAvailable' in df.columns and not pd.isna(row['ProcAvailable']) else True
            proc_note = row['ProcNote'] if 'ProcNote' in df.columns and not pd.isna(row['ProcNote']) else ''
            
            # Handle boolean values from Excel
            if isinstance(proc_bhyt, str):
                proc_bhyt = proc_bhyt.lower() in ['true', 'yes', '1', 't', 'y']
            if isinstance(proc_available, str):
                proc_available = proc_available.lower() in ['true', 'yes', '1', 't', 'y']
            
            # Check if record exists
            proc_id = str(row['ProcId']).strip()
            existing = Proc.query.get(proc_id)
            
            if existing:
                # Update existing record
                existing.ProcDesc = row['ProcDesc']
                existing.ProcGroup = proc_group
                existing.ProcBHYT = proc_bhyt
                existing.ProcPriceBHYT = proc_price_bhyt
                existing.ProcPriceVP = proc_price_vp
                existing.ProcAvailable = proc_available
                existing.ProcNote = proc_note
                db.session.commit()  # Commit each row individually
                updated += 1
            else:
                # Create new record
                new_proc = Proc(
                    ProcId=proc_id,
                    ProcDesc=row['ProcDesc'],
                    ProcGroup=proc_group,
                    ProcBHYT=proc_bhyt,
                    ProcPriceBHYT=proc_price_bhyt,
                    ProcPriceVP=proc_price_vp,
                    ProcAvailable=proc_available,
                    ProcNote=proc_note
                )
                db.session.add(new_proc)
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

# Sign import function
def import_signs(df, db):
    """Import Sign data from DataFrame to database"""
    import pandas as pd
    from models import Sign, BodySystem
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['SignDesc', 'SignType', 'SystemId']
    
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
            if pd.isna(row['SignDesc']) or not str(row['SignDesc']).strip():
                errors.append(f"Error in row {idx+2}: Missing SignDesc")
                skipped += 1
                continue
                
            if pd.isna(row['SystemId']):
                errors.append(f"Error in row {idx+2}: Missing SystemId")
                skipped += 1
                continue
            
            # Convert SignType to boolean
            sign_type = False
            if not pd.isna(row['SignType']):
                if isinstance(row['SignType'], bool):
                    sign_type = row['SignType']
                elif isinstance(row['SignType'], (int, float)):
                    sign_type = bool(int(row['SignType']))
                elif isinstance(row['SignType'], str):
                    sign_type = row['SignType'].lower() in ['true', 'yes', '1', 't', 'y']
            
            # Verify SystemId exists
            system_id = int(row['SystemId'])
            body_system = BodySystem.query.get(system_id)
            if not body_system:
                errors.append(f"Error in row {idx+2}: SystemId {system_id} does not exist")
                skipped += 1
                continue
            
            # Optional fields with default values
            speciality = row['Speciality'] if 'Speciality' in df.columns and not pd.isna(row['Speciality']) else ''
            
            # Check if SignId is provided for updating
            if 'SignId' in df.columns and not pd.isna(row['SignId']):
                sign_id = int(row['SignId'])
                existing = Sign.query.get(sign_id)
                
                if existing:
                    # Update existing record
                    existing.SignDesc = row['SignDesc']
                    existing.SignType = sign_type
                    existing.SystemId = system_id
                    existing.Speciality = speciality
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_sign = Sign(
                        SignId=sign_id,
                        SignDesc=row['SignDesc'],
                        SignType=sign_type,
                        SystemId=system_id,
                        Speciality=speciality
                    )
                    db.session.add(new_sign)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                # Create new record with auto-generated ID
                new_sign = Sign(
                    SignDesc=row['SignDesc'],
                    SignType=sign_type,
                    SystemId=system_id,
                    Speciality=speciality
                )
                db.session.add(new_sign)
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

# Staff import function
def import_staff(df, db):
    """Import Staff data from DataFrame to database"""
    import pandas as pd
    from models import Staff, Department
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['StaffName', 'StaffRole', 'DepartmentId']
    
    # Check if all required columns are present
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Validate role values
    valid_roles = ['Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác']
    invalid_roles = []
    for idx, row in df.iterrows():
        if row['StaffRole'] not in valid_roles:
            invalid_roles.append(f"Row {idx+2}: {row['StaffRole']}")
    
    if invalid_roles:
        return {'error': f'Invalid StaffRole values. Must be one of: {", ".join(valid_roles)}. Found: {", ".join(invalid_roles)}'}
    
    # Process data
    total_rows = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Check for missing required values
            if pd.isna(row['StaffName']) or not str(row['StaffName']).strip():
                errors.append(f"Error in row {idx+2}: Missing StaffName")
                skipped += 1
                continue
                
            if pd.isna(row['StaffRole']) or not str(row['StaffRole']).strip():
                errors.append(f"Error in row {idx+2}: Missing StaffRole")
                skipped += 1
                continue
                
            if pd.isna(row['DepartmentId']):
                errors.append(f"Error in row {idx+2}: Missing DepartmentId")
                skipped += 1
                continue
            
            # Verify DepartmentId exists
            dept_id = int(row['DepartmentId'])
            department = Department.query.get(dept_id)
            if not department:
                errors.append(f"Error in row {idx+2}: DepartmentId {dept_id} does not exist")
                skipped += 1
                continue
            
            # Optional fields with default values
            staff_available = True
            if 'StaffAvailable' in df.columns and not pd.isna(row['StaffAvailable']):
                if isinstance(row['StaffAvailable'], bool):
                    staff_available = row['StaffAvailable']
                elif isinstance(row['StaffAvailable'], (int, float)):
                    staff_available = bool(int(row['StaffAvailable']))
                elif isinstance(row['StaffAvailable'], str):
                    staff_available = row['StaffAvailable'].lower() in ['true', 'yes', '1', 't', 'y']
            
            # Check if StaffId is provided for updating
            if 'StaffId' in df.columns and not pd.isna(row['StaffId']):
                staff_id = int(row['StaffId'])
                existing = Staff.query.get(staff_id)
                
                if existing:
                    # Update existing record
                    existing.StaffName = row['StaffName']
                    existing.StaffRole = row['StaffRole']
                    existing.DepartmentId = dept_id
                    existing.StaffAvailable = staff_available
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_staff = Staff(
                        StaffId=staff_id,
                        StaffName=row['StaffName'],
                        StaffRole=row['StaffRole'],
                        DepartmentId=dept_id,
                        StaffAvailable=staff_available
                    )
                    db.session.add(new_staff)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                # Create new record with auto-generated ID
                new_staff = Staff(
                    StaffName=row['StaffName'],
                    StaffRole=row['StaffRole'],
                    DepartmentId=dept_id,
                    StaffAvailable=staff_available
                )
                db.session.add(new_staff)
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

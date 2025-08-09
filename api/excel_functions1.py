# Drug import function
def import_drugs(df, db):
    """Import Drug data from DataFrame to database"""
    import pandas as pd
    from models import Drug
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['DrugName']
    
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
            if pd.isna(row['DrugName']) or not str(row['DrugName']).strip():
                errors.append(f"Error in row {idx+2}: Missing DrugName")
                skipped += 1
                continue
            
            # Optional fields with default values
            drug_chemical = row['DrugChemical'] if 'DrugChemical' in df.columns and not pd.isna(row['DrugChemical']) else ''
            drug_content = row['DrugContent'] if 'DrugContent' in df.columns and not pd.isna(row['DrugContent']) else ''
            drug_formulation = row['DrugFormulation'] if 'DrugFormulation' in df.columns and not pd.isna(row['DrugFormulation']) else ''
            drug_remains = int(row['DrugRemains']) if 'DrugRemains' in df.columns and not pd.isna(row['DrugRemains']) else 0
            drug_group = row['DrugGroup'] if 'DrugGroup' in df.columns and not pd.isna(row['DrugGroup']) else ''
            drug_price_bhyt = int(row['DrugPriceBHYT']) if 'DrugPriceBHYT' in df.columns and not pd.isna(row['DrugPriceBHYT']) else 0
            drug_price_vp = int(row['DrugPriceVP']) if 'DrugPriceVP' in df.columns and not pd.isna(row['DrugPriceVP']) else 0
            
            # Check if DrugId is provided 
            if 'DrugId' in df.columns and not pd.isna(row['DrugId']):
                drug_id = str(row['DrugId']).strip()
                existing = Drug.query.get(drug_id)
                
                if existing:
                    # Update existing record
                    existing.DrugName = row['DrugName']
                    existing.DrugChemical = drug_chemical
                    existing.DrugContent = drug_content
                    existing.DrugFormulation = drug_formulation
                    existing.DrugRemains = drug_remains
                    existing.DrugGroup = drug_group
                    existing.DrugPriceBHYT = drug_price_bhyt
                    existing.DrugPriceVP = drug_price_vp
                    db.session.commit()  # Commit each row individually
                    updated += 1
                else:
                    # Create new record with specified ID
                    new_drug = Drug(
                        DrugId=drug_id,
                        DrugName=row['DrugName'],
                        DrugChemical=drug_chemical,
                        DrugContent=drug_content,
                        DrugFormulation=drug_formulation,
                        DrugRemains=drug_remains,
                        DrugGroup=drug_group,
                        DrugPriceBHYT=drug_price_bhyt,
                        DrugPriceVP=drug_price_vp
                    )
                    db.session.add(new_drug)
                    db.session.commit()  # Commit each row individually
                    imported += 1
            else:
                errors.append(f"Error in row {idx+2}: DrugId is required")
                skipped += 1
                continue
                
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

# ICD import function
def import_icd(df, db):
    """Import ICD data from DataFrame to database"""
    import pandas as pd
    from models import ICD
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['ICDCode', 'ICDName']
    
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
            if pd.isna(row['ICDCode']) or not str(row['ICDCode']).strip():
                errors.append(f"Error in row {idx+2}: Missing ICDCode")
                skipped += 1
                continue
                
            if pd.isna(row['ICDName']) or not str(row['ICDName']).strip():
                errors.append(f"Error in row {idx+2}: Missing ICDName")
                skipped += 1
                continue
            
            # Optional fields with default values
            icd_group = row['ICDGroup'] if 'ICDGroup' in df.columns and not pd.isna(row['ICDGroup']) else ''
            
            # Check if record exists
            icd_code = str(row['ICDCode']).strip()
            existing = ICD.query.get(icd_code)
            
            if existing:
                # Update existing record
                existing.ICDName = row['ICDName']
                existing.ICDGroup = icd_group
                db.session.commit()  # Commit each row individually
                updated += 1
            else:
                # Create new record
                new_icd = ICD(
                    ICDCode=icd_code,
                    ICDName=row['ICDName'],
                    ICDGroup=icd_group
                )
                db.session.add(new_icd)
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

# Patient import function
def import_patients(df, db):
    """Import Patient data from DataFrame to database"""
    import pandas as pd
    from models import Patient
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['PatientId', 'PatientName', 'PatientGender', 'PatientAge']
    
    # Check if all required columns are present
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return {'error': f'Missing required columns: {", ".join(missing)}'}
    
    # Validate gender values
    valid_genders = ['Nam', 'Nữ', 'Khác']
    invalid_genders = []
    for idx, row in df.iterrows():
        if row['PatientGender'] not in valid_genders:
            invalid_genders.append(f"Row {idx+2}: {row['PatientGender']}")
    
    if invalid_genders:
        return {'error': f'Invalid PatientGender values. Must be one of: {", ".join(valid_genders)}. Found: {", ".join(invalid_genders)}'}
    
    # Process data
    total_rows = len(df)
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Check for missing required values
            if pd.isna(row['PatientId']) or not str(row['PatientId']).strip():
                errors.append(f"Error in row {idx+2}: Missing PatientId")
                skipped += 1
                continue
                
            if pd.isna(row['PatientName']) or not str(row['PatientName']).strip():
                errors.append(f"Error in row {idx+2}: Missing PatientName")
                skipped += 1
                continue
                
            if pd.isna(row['PatientGender']) or not str(row['PatientGender']).strip():
                errors.append(f"Error in row {idx+2}: Missing PatientGender")
                skipped += 1
                continue
                
            if pd.isna(row['PatientAge']) or not str(row['PatientAge']).strip():
                errors.append(f"Error in row {idx+2}: Missing PatientAge")
                skipped += 1
                continue
            
            # Optional fields with default values
            patient_address = row['PatientAddress'] if 'PatientAddress' in df.columns and not pd.isna(row['PatientAddress']) else ''
            patient_allergy = row['Allergy'] if 'Allergy' in df.columns and not pd.isna(row['Allergy']) else ''
            patient_note = row['PatientNote'] if 'PatientNote' in df.columns and not pd.isna(row['PatientNote']) else ''
            
            # Check if record exists
            patient_id = str(row['PatientId']).strip()
            existing = Patient.query.get(patient_id)
            
            if existing:
                # Update existing record
                existing.PatientName = row['PatientName']
                existing.PatientGender = row['PatientGender']
                existing.PatientAge = row['PatientAge']
                existing.PatientAddress = patient_address
                existing.Allergy = patient_allergy
                existing.PatientNote = patient_note
                db.session.commit()  # Commit each row individually
                updated += 1
            else:
                # Create new record
                new_patient = Patient(
                    PatientId=patient_id,
                    PatientName=row['PatientName'],
                    PatientGender=row['PatientGender'],
                    PatientAge=row['PatientAge'],
                    PatientAddress=patient_address,
                    Allergy=patient_allergy,
                    PatientNote=patient_note
                )
                db.session.add(new_patient)
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

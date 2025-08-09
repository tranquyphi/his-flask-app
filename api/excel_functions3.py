# Test import function
def import_tests(df, db):
    """Import Test data from DataFrame to database"""
    import pandas as pd
    from models import Test, Department
    
    # Clean dataframe - remove empty rows and trim whitespace
    df = df.dropna(how='all')
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Define required columns
    required_cols = ['TestId', 'TestDesc', 'DepartmentId']
    
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
            if pd.isna(row['TestId']) or not str(row['TestId']).strip():
                errors.append(f"Error in row {idx+2}: Missing TestId")
                skipped += 1
                continue
                
            if pd.isna(row['TestDesc']) or not str(row['TestDesc']).strip():
                errors.append(f"Error in row {idx+2}: Missing TestDesc")
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
            test_unit = row['TestUnit'] if 'TestUnit' in df.columns and not pd.isna(row['TestUnit']) else ''
            test_male = row['TestMale'] if 'TestMale' in df.columns and not pd.isna(row['TestMale']) else ''
            test_female = row['TestFemale'] if 'TestFemale' in df.columns and not pd.isna(row['TestFemale']) else ''
            test_price_bhyt = int(row['TestPriceBHYT']) if 'TestPriceBHYT' in df.columns and not pd.isna(row['TestPriceBHYT']) else 0
            test_price_vp = int(row['TestPriceVP']) if 'TestPriceVP' in df.columns and not pd.isna(row['TestPriceVP']) else 0
            
            # Check if record exists
            test_id = str(row['TestId']).strip()
            existing = Test.query.get(test_id)
            
            if existing:
                # Update existing record
                existing.TestDesc = row['TestDesc']
                existing.TestUnit = test_unit
                existing.TestMale = test_male
                existing.TestFemale = test_female
                existing.TestPriceBHYT = test_price_bhyt
                existing.TestPriceVP = test_price_vp
                existing.DepartmentId = dept_id
                db.session.commit()  # Commit each row individually
                updated += 1
            else:
                # Create new record
                new_test = Test(
                    TestId=test_id,
                    TestDesc=row['TestDesc'],
                    TestUnit=test_unit,
                    TestMale=test_male,
                    TestFemale=test_female,
                    TestPriceBHYT=test_price_bhyt,
                    TestPriceVP=test_price_vp,
                    DepartmentId=dept_id
                )
                db.session.add(new_test)
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

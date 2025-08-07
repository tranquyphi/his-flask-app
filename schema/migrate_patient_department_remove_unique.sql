-- Migration script to update PatientDepartment table
-- This script adds an auto-increment ID column and removes the composite primary key

-- Step 1: Drop the composite primary key constraint
ALTER TABLE PatientDepartment DROP PRIMARY KEY;

-- Step 2: Add an auto-increment ID column as the new primary key
ALTER TABLE PatientDepartment ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;

-- Step 3: Add indexes for better performance (since we removed the composite primary key)
CREATE INDEX idx_patient_dept ON PatientDepartment(PatientId, DepartmentId);
CREATE INDEX idx_patient_current ON PatientDepartment(PatientId, Current);
CREATE INDEX idx_department_current ON PatientDepartment(DepartmentId, Current);
CREATE INDEX idx_at_time ON PatientDepartment(At);

-- Step 4: Verify the structure
DESCRIBE PatientDepartment;

-- Optional: Show some sample data to verify the migration
SELECT * FROM PatientDepartment LIMIT 5;

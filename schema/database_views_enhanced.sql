-- Database Views for HIS System
-- ========================================

-- View: patients_with_department
-- Purpose: Show patients with their current department information
-- This view joins Patient table with PatientDepartment (where Current = true) and Department tables
-- to display the current department for each patient

CREATE OR REPLACE VIEW patients_with_department AS
SELECT 
    p.PatientId,
    p.PatientName,
    p.PatientGender,
    p.PatientAge,
    p.PatientAddress,
    p.Allergy,
    p.History,
    p.PatientNote,
    d.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    pd.At as DepartmentAssignedAt
FROM Patient p
LEFT JOIN PatientDepartment pd ON p.PatientId = pd.PatientId AND pd.Current = TRUE
LEFT JOIN Department d ON pd.DepartmentId = d.DepartmentId;

-- View: staff_with_department
-- Purpose: Show staff with their department information
-- This view joins Staff table with Department table to display department names instead of IDs

CREATE OR REPLACE VIEW staff_with_department AS
SELECT 
    s.StaffId,
    s.FirstName,
    s.LastName,
    CONCAT(s.FirstName, ' ', s.LastName) as FullName,
    s.Role,
    s.Phone,
    s.Email,
    s.Address,
    s.DateHired,
    s.Active,
    d.DepartmentId,
    d.DepartmentName,
    d.DepartmentType
FROM Staff s
LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId;

-- View: visits_with_details
-- Purpose: Show visits with patient and staff names, department information
-- This view provides a comprehensive view of visits with all related entity names

CREATE OR REPLACE VIEW visits_with_details AS
SELECT 
    v.VisitId,
    v.PatientId,
    p.PatientName,
    v.StaffId,
    CONCAT(s.FirstName, ' ', s.LastName) as StaffName,
    s.Role as StaffRole,
    v.DepartmentId,
    d.DepartmentName,
    v.VisitDate,
    v.VisitType,
    v.ChiefComplaint,
    v.Diagnosis,
    v.Treatment,
    v.Status,
    v.FollowUpDate,
    v.Notes
FROM Visit v
LEFT JOIN Patient p ON v.PatientId = p.PatientId
LEFT JOIN Staff s ON v.StaffId = s.StaffId
LEFT JOIN Department d ON v.DepartmentId = d.DepartmentId;

-- View: tests_with_details
-- Purpose: Show tests with patient, staff, and department information
-- This view provides a comprehensive view of tests with all related entity names

CREATE OR REPLACE VIEW tests_with_details AS
SELECT 
    t.TestId,
    t.TestDate,
    t.PatientId,
    p.PatientName,
    t.StaffId,
    CONCAT(s.FirstName, ' ', s.LastName) as StaffName,
    t.DepartmentId,
    d.DepartmentName,
    t.TestType,
    t.TestResult,
    t.Status,
    t.Notes
FROM Test t
LEFT JOIN Patient p ON t.PatientId = p.PatientId
LEFT JOIN Staff s ON t.StaffId = s.StaffId
LEFT JOIN Department d ON t.DepartmentId = d.DepartmentId;

-- View: prescriptions_with_details
-- Purpose: Show prescriptions with visit, patient, drug, and staff information
-- This view provides a comprehensive view of prescriptions with all related entity names

CREATE OR REPLACE VIEW prescriptions_with_details AS
SELECT 
    pr.PrescriptionId,
    pr.VisitId,
    v.PatientId,
    p.PatientName,
    pr.DrugId,
    dr.DrugName,
    dr.Unit,
    pr.Quantity,
    pr.Dosage,
    pr.Instructions,
    pr.PrescribedDate,
    v.StaffId,
    CONCAT(s.FirstName, ' ', s.LastName) as StaffName
FROM Prescription pr
LEFT JOIN Visit v ON pr.VisitId = v.VisitId
LEFT JOIN Patient p ON v.PatientId = p.PatientId
LEFT JOIN Drug dr ON pr.DrugId = dr.DrugId
LEFT JOIN Staff s ON v.StaffId = s.StaffId;

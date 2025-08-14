-- Database view for all patients with department information
-- Shows department names instead of IDs, sorted by patient name then by time

CREATE OR REPLACE VIEW patients_with_department AS
SELECT 
    p.PatientId,
    p.PatientName,
    p.PatientGender,
    p.PatientAge,
    p.PatientAddress,
    p.Allergy,
    p.PatientNote,
    d.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    pd.Current,
    pd.At,
    pd.Reason,
    -- Calculate days since admission for current patients
    CASE 
        WHEN pd.Current = 1 THEN DATEDIFF(NOW(), pd.At)
        ELSE NULL 
    END AS DaysAdmitted
FROM Patient p
LEFT JOIN PatientDepartment pd ON p.PatientId = pd.PatientId
LEFT JOIN Department d ON pd.DepartmentId = d.DepartmentId
ORDER BY p.PatientName ASC, pd.At DESC;

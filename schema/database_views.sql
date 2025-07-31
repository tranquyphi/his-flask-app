-- Database Views for Hospital Information System
-- These views simplify complex queries and provide convenient data access

-- ===========================================
-- Patient Management Views
-- ===========================================

-- View: Current Patient Status with Department
CREATE VIEW `PatientCurrentStatus` AS
SELECT 
    p.PatientId,
    p.PatientName,
    p.PatientGender,
    p.PatientAge,
    p.PatientAddress,
    p.Allergy,
    pd.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    pd.AdmissionType,
    s.StaffId AS PrimaryStaffId,
    s.StaffName AS PrimaryStaffName,
    s.StaffRole AS PrimaryStaffRole
FROM Patient p
LEFT JOIN PatientDepartment pd ON p.PatientId = pd.PatientId AND pd.Current = 1
LEFT JOIN Department d ON pd.DepartmentId = d.DepartmentId
LEFT JOIN Staff s ON d.DepartmentId = s.DepartmentId AND s.StaffRole = 'Bác sĩ'
WHERE s.StaffAvailable = 1;

-- View: Patient Visit History Summary
CREATE VIEW `PatientVisitHistory` AS
SELECT 
    p.PatientId,
    p.PatientName,
    COUNT(v.VisitId) AS TotalVisits,
    MAX(v.VisitTime) AS LastVisitTime,
    MIN(v.VisitTime) AS FirstVisitTime,
    COUNT(CASE WHEN v.VisitPurpose = 'Cấp cứu' THEN 1 END) AS EmergencyVisits,
    COUNT(CASE WHEN v.VisitPurpose = 'Thường quy' THEN 1 END) AS RoutineVisits,
    COUNT(CASE WHEN v.VisitPurpose = 'Tái khám' THEN 1 END) AS FollowUpVisits
FROM Patient p
LEFT JOIN Visit v ON p.PatientId = v.PatientId
GROUP BY p.PatientId, p.PatientName;

-- ===========================================
-- Visit Management Views
-- ===========================================

-- View: Complete Visit Information
CREATE VIEW `VisitComplete` AS
SELECT 
    v.VisitId,
    v.PatientId,
    p.PatientName,
    p.PatientAge,
    p.PatientGender,
    v.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    v.VisitPurpose,
    v.VisitTime,
    v.StaffId,
    s.StaffName,
    s.StaffRole,
    -- Template information
    v.TestTemplateId,
    tt.TemplateName AS TestTemplateName,
    v.SignTemplateId,
    st.TemplateName AS SignTemplateName,
    v.DrugTemplateId,
    dt.TemplateName AS DrugTemplateName,
    v.ProcTemplateId,
    pt.TemplateName AS ProcTemplateName
FROM Visit v
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Department d ON v.DepartmentId = d.DepartmentId
JOIN Staff s ON v.StaffId = s.StaffId
LEFT JOIN Template tt ON v.TestTemplateId = tt.TemplateId
LEFT JOIN Template st ON v.SignTemplateId = st.TemplateId
LEFT JOIN Template dt ON v.DrugTemplateId = dt.TemplateId
LEFT JOIN Template pt ON v.ProcTemplateId = pt.TemplateId;

-- View: Active Visits by Department
CREATE VIEW `ActiveVisitsByDepartment` AS
SELECT 
    d.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    COUNT(v.VisitId) AS ActiveVisits,
    COUNT(CASE WHEN v.VisitPurpose = 'Cấp cứu' THEN 1 END) AS EmergencyVisits,
    COUNT(CASE WHEN v.VisitPurpose = 'Thường quy' THEN 1 END) AS RoutineVisits,
    COUNT(DISTINCT v.PatientId) AS UniquePatients,
    COUNT(DISTINCT v.StaffId) AS ActiveStaff
FROM Department d
LEFT JOIN Visit v ON d.DepartmentId = v.DepartmentId 
    AND DATE(v.VisitTime) = CURDATE()
GROUP BY d.DepartmentId, d.DepartmentName, d.DepartmentType;

-- ===========================================
-- Medical Activity Views
-- ===========================================

-- View: Drug Prescriptions with Details
CREATE VIEW `DrugPrescriptionDetails` AS
SELECT 
    vd.VisitId,
    v.PatientId,
    p.PatientName,
    v.VisitTime,
    vd.DrugId,
    dr.DrugName,
    dr.DrugChemical,
    dr.DrugFormulation,
    vd.DrugRoute,
    vd.DrugQuantity,
    vd.DrugTimes,
    vd.DrugAtTime,
    vd.Note,
    s.StaffName AS PrescribedBy,
    s.StaffRole,
    d.DepartmentName
FROM VisitDrug vd
JOIN Visit v ON vd.VisitId = v.VisitId
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Drug dr ON vd.DrugId = dr.DrugId
JOIN Staff s ON v.StaffId = s.StaffId
JOIN Department d ON v.DepartmentId = d.DepartmentId;

-- View: Test Results Summary
CREATE VIEW `TestResultsSummary` AS
SELECT 
    vt.VisitId,
    v.PatientId,
    p.PatientName,
    v.VisitTime,
    vt.TestId,
    t.TestName,
    t.TestGroup,
    vt.TestStatus,
    vt.TestTime,
    vt.TestResult,
    vt.TestConclusion,
    s1.StaffName AS OrderedBy,
    s2.StaffName AS ExecutedBy,
    s2.StaffRole AS ExecutedByRole,
    d.DepartmentName
FROM VisitTest vt
JOIN Visit v ON vt.VisitId = v.VisitId
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Test t ON vt.TestId = t.TestId
JOIN Staff s1 ON v.StaffId = s1.StaffId  -- Who ordered the test
LEFT JOIN Staff s2 ON vt.TestStaffId = s2.StaffId  -- Who executed the test
JOIN Department d ON v.DepartmentId = d.DepartmentId;

-- View: Procedure Status Tracking
CREATE VIEW `ProcedureStatusTracking` AS
SELECT 
    vp.VisitId,
    v.PatientId,
    p.PatientName,
    v.VisitTime,
    vp.ProcId,
    pr.ProcDesc,
    pr.ProcGroup,
    vp.ProcStatus,
    vp.ProcTime,
    s1.StaffName AS OrderedBy,
    s2.StaffName AS ExecutedBy,
    s2.StaffRole AS ExecutedByRole,
    d.DepartmentName,
    CASE 
        WHEN vp.ProcStatus = 'Ordered' THEN 'Đã chỉ định'
        WHEN vp.ProcStatus = 'In progress' THEN 'Đang thực hiện'
        WHEN vp.ProcStatus = 'Completed' THEN 'Hoàn thành'
        WHEN vp.ProcStatus = 'Result' THEN 'Có kết quả'
    END AS ProcStatusVietnamese
FROM VisitProc vp
JOIN Visit v ON vp.VisitId = v.VisitId
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Proc pr ON vp.ProcId = pr.ProcId
JOIN Staff s1 ON v.StaffId = s1.StaffId  -- Who ordered the procedure
LEFT JOIN Staff s2 ON vp.ProcStaffId = s2.StaffId  -- Who executed the procedure
JOIN Department d ON v.DepartmentId = d.DepartmentId;

-- ===========================================
-- Staff and Department Views
-- ===========================================

-- View: Staff Workload Summary
CREATE VIEW `StaffWorkloadSummary` AS
SELECT 
    s.StaffId,
    s.StaffName,
    s.StaffRole,
    d.DepartmentName,
    d.DepartmentType,
    s.StaffAvailable,
    COUNT(v.VisitId) AS TodayVisits,
    COUNT(CASE WHEN v.VisitPurpose = 'Cấp cứu' THEN 1 END) AS EmergencyVisits,
    COUNT(vt.TestId) AS TestsToExecute,
    COUNT(vp.ProcId) AS ProceduresToExecute,
    MAX(v.VisitTime) AS LastVisitTime
FROM Staff s
LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId
LEFT JOIN Visit v ON s.StaffId = v.StaffId AND DATE(v.VisitTime) = CURDATE()
LEFT JOIN VisitTest vt ON s.StaffId = vt.TestStaffId AND vt.TestStatus IN ('Ordered', 'In progress')
LEFT JOIN VisitProc vp ON s.StaffId = vp.ProcStaffId AND vp.ProcStatus IN ('Ordered', 'In progress')
GROUP BY s.StaffId, s.StaffName, s.StaffRole, d.DepartmentName, d.DepartmentType, s.StaffAvailable;

-- View: Department Performance Metrics
CREATE VIEW `DepartmentPerformanceMetrics` AS
SELECT 
    d.DepartmentId,
    d.DepartmentName,
    d.DepartmentType,
    COUNT(DISTINCT s.StaffId) AS TotalStaff,
    COUNT(CASE WHEN s.StaffAvailable = 1 THEN 1 END) AS AvailableStaff,
    COUNT(CASE WHEN s.StaffRole = 'Bác sĩ' THEN 1 END) AS Doctors,
    COUNT(CASE WHEN s.StaffRole = 'Điều dưỡng' THEN 1 END) AS Nurses,
    COUNT(CASE WHEN s.StaffRole = 'Kỹ thuật viên' THEN 1 END) AS Technicians,
    COUNT(DISTINCT v.PatientId) AS TotalPatients,
    COUNT(v.VisitId) AS TotalVisits,
    AVG(CASE WHEN v.VisitTime IS NOT NULL THEN 1 ELSE 0 END) AS VisitRate
FROM Department d
LEFT JOIN Staff s ON d.DepartmentId = s.DepartmentId
LEFT JOIN Visit v ON d.DepartmentId = v.DepartmentId AND v.VisitTime >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY d.DepartmentId, d.DepartmentName, d.DepartmentType;

-- ===========================================
-- Template Usage Views
-- ===========================================

-- View: Template Usage Statistics
CREATE VIEW `TemplateUsageStats` AS
SELECT 
    t.TemplateId,
    t.TemplateName,
    t.TemplateGroup,
    t.TemplateType,
    d.DepartmentName,
    COUNT(CASE WHEN t.TemplateGroup = 'Test' THEN v.TestTemplateId END) AS TestUsageCount,
    COUNT(CASE WHEN t.TemplateGroup = 'Sign' THEN v.SignTemplateId END) AS SignUsageCount,
    COUNT(CASE WHEN t.TemplateGroup = 'Drug' THEN v.DrugTemplateId END) AS DrugUsageCount,
    COUNT(CASE WHEN t.TemplateGroup = 'Proc' THEN v.ProcTemplateId END) AS ProcUsageCount,
    MAX(v.VisitTime) AS LastUsedTime,
    COUNT(DISTINCT v.StaffId) AS UsedByStaffCount
FROM Template t
LEFT JOIN Department d ON t.DepartmentId = d.DepartmentId
LEFT JOIN Visit v ON (
    (t.TemplateGroup = 'Test' AND t.TemplateId = v.TestTemplateId) OR
    (t.TemplateGroup = 'Sign' AND t.TemplateId = v.SignTemplateId) OR
    (t.TemplateGroup = 'Drug' AND t.TemplateId = v.DrugTemplateId) OR
    (t.TemplateGroup = 'Proc' AND t.TemplateId = v.ProcTemplateId)
)
GROUP BY t.TemplateId, t.TemplateName, t.TemplateGroup, t.TemplateType, d.DepartmentName;

-- ===========================================
-- Patient Signs and Symptoms Views
-- ===========================================

-- View: Patient Signs Summary
CREATE VIEW `PatientSignsSummary` AS
SELECT 
    vs.VisitId,
    v.PatientId,
    p.PatientName,
    v.VisitTime,
    COUNT(vs.SignId) AS TotalSigns,
    COUNT(CASE WHEN vs.SignValue IN ('Có DHBL', 'Nhiều', 'Tăng') THEN 1 END) AS AbnormalSigns,
    COUNT(CASE WHEN vs.SignValue = 'BT' THEN 1 END) AS NormalSigns,
    COUNT(CASE WHEN vs.FollowUp = 1 THEN 1 END) AS FollowUpSigns,
    COUNT(CASE WHEN vs.IsCustom = 1 THEN 1 END) AS CustomSigns,
    s.StaffName AS RecordedBy,
    d.DepartmentName
FROM VisitSign vs
JOIN Visit v ON vs.VisitId = v.VisitId
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Staff s ON v.StaffId = s.StaffId
JOIN Department d ON v.DepartmentId = d.DepartmentId
GROUP BY vs.VisitId, v.PatientId, p.PatientName, v.VisitTime, s.StaffName, d.DepartmentName;

-- ===========================================
-- Emergency and Priority Views
-- ===========================================

-- View: Emergency Cases Dashboard
CREATE VIEW `EmergencyCasesDashboard` AS
SELECT 
    v.VisitId,
    v.PatientId,
    p.PatientName,
    p.PatientAge,
    p.PatientGender,
    v.VisitTime,
    v.DepartmentId,
    d.DepartmentName,
    s.StaffName AS AttendingStaff,
    COUNT(vt.TestId) AS PendingTests,
    COUNT(vp.ProcId) AS PendingProcedures,
    COUNT(vs.SignId) AS RecordedSigns,
    TIMESTAMPDIFF(HOUR, v.VisitTime, NOW()) AS HoursInSystem
FROM Visit v
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Department d ON v.DepartmentId = d.DepartmentId
JOIN Staff s ON v.StaffId = s.StaffId
LEFT JOIN VisitTest vt ON v.VisitId = vt.VisitId AND vt.TestStatus IN ('Ordered', 'In progress')
LEFT JOIN VisitProc vp ON v.VisitId = vp.VisitId AND vp.ProcStatus IN ('Ordered', 'In progress')
LEFT JOIN VisitSign vs ON v.VisitId = vs.VisitId
WHERE v.VisitPurpose = 'Cấp cứu' 
    AND v.VisitTime >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY v.VisitId, v.PatientId, p.PatientName, p.PatientAge, p.PatientGender, 
         v.VisitTime, v.DepartmentId, d.DepartmentName, s.StaffName;

-- ===========================================
-- Financial and Resource Views
-- ===========================================

-- View: Treatment Cost Summary
CREATE VIEW `TreatmentCostSummary` AS
SELECT 
    v.VisitId,
    v.PatientId,
    p.PatientName,
    v.VisitTime,
    d.DepartmentName,
    COALESCE(SUM(dr.DrugPriceBHYT), 0) AS DrugCostBHYT,
    COALESCE(SUM(dr.DrugPriceVP), 0) AS DrugCostVP,
    COALESCE(SUM(t.TestPriceBHYT), 0) AS TestCostBHYT,
    COALESCE(SUM(t.TestPriceVP), 0) AS TestCostVP,
    COALESCE(SUM(pr.ProcPriceBHYT), 0) AS ProcCostBHYT,
    COALESCE(SUM(pr.ProcPriceVP), 0) AS ProcCostVP,
    (COALESCE(SUM(dr.DrugPriceBHYT), 0) + COALESCE(SUM(t.TestPriceBHYT), 0) + COALESCE(SUM(pr.ProcPriceBHYT), 0)) AS TotalBHYTCost,
    (COALESCE(SUM(dr.DrugPriceVP), 0) + COALESCE(SUM(t.TestPriceVP), 0) + COALESCE(SUM(pr.ProcPriceVP), 0)) AS TotalVPCost
FROM Visit v
JOIN Patient p ON v.PatientId = p.PatientId
JOIN Department d ON v.DepartmentId = d.DepartmentId
LEFT JOIN VisitDrug vd ON v.VisitId = vd.VisitId
LEFT JOIN Drug dr ON vd.DrugId = dr.DrugId
LEFT JOIN VisitTest vt ON v.VisitId = vt.VisitId
LEFT JOIN Test t ON vt.TestId = t.TestId
LEFT JOIN VisitProc vp ON v.VisitId = vp.VisitId
LEFT JOIN Proc pr ON vp.ProcId = pr.ProcId
GROUP BY v.VisitId, v.PatientId, p.PatientName, v.VisitTime, d.DepartmentName;

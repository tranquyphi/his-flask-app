-- =============================================================================
-- AUDIT SYSTEM FOR HOSPITAL INFORMATION SYSTEM
-- Tracks all changes to critical tables with full history
-- =============================================================================
USE `examdb`; -- Ensure you are using the correct database
-- Generic audit log table for all table changes
CREATE TABLE `AuditLog` (
  `AuditId` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `TableName` varchar(50) NOT NULL COMMENT 'Name of the table that was changed',
  `RecordId` varchar(50) NOT NULL COMMENT 'ID of the record that was changed',
  `Operation` ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL COMMENT 'Type of operation',
  `FieldName` varchar(100) DEFAULT NULL COMMENT 'Name of the field that was changed',
  `OldValue` TEXT DEFAULT NULL COMMENT 'Previous value before change',
  `NewValue` TEXT DEFAULT NULL COMMENT 'New value after change',
  `ChangeDate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'When the change occurred',
  `ChangedBy` smallint(6) NOT NULL COMMENT 'Staff member who made the change',
  `ChangeReason` varchar(255) DEFAULT NULL COMMENT 'Reason for the change',
  `SessionId` varchar(100) DEFAULT NULL COMMENT 'Application session ID',
  `IPAddress` varchar(45) DEFAULT NULL COMMENT 'IP address of the user',
  
  INDEX `idx_audit_table_record` (`TableName`, `RecordId`),
  INDEX `idx_audit_date` (`ChangeDate`),
  INDEX `idx_audit_user` (`ChangedBy`),
  FOREIGN KEY (`ChangedBy`) REFERENCES `Staff`(`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Patient-specific audit table for detailed tracking
CREATE TABLE `PatientAudit` (
  `AuditId` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `PatientId` int(10) NOT NULL,
  `Operation` ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  `ChangeDate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `ChangedBy` smallint(6) NOT NULL,
  `ChangeReason` varchar(255) DEFAULT NULL,
  
  -- Store complete record state before change
  `OldPatientName` varchar(100),
  `OldPatientGender` ENUM('Nam','Nữ','Khác'),
  `OldPatientAge` int(3),
  `OldPatientAddress` varchar(255),
  `OldAllergy` varchar(255),
  `OldHistory` text,
  `OldPatientNote` varchar(100),
  
  -- Store complete record state after change
  `NewPatientName` varchar(100),
  `NewPatientGender` ENUM('Nam','Nữ','Khác'),
  `NewPatientAge` int(3),
  `NewPatientAddress` varchar(255),
  `NewAllergy` varchar(255),
  `NewHistory` text,
  `NewPatientNote` varchar(100),
  
  INDEX `idx_patient_audit_date` (`PatientId`, `ChangeDate`),
  INDEX `idx_patient_audit_user` (`ChangedBy`),
  FOREIGN KEY (`PatientId`) REFERENCES `Patient`(`PatientId`),
  FOREIGN KEY (`ChangedBy`) REFERENCES `Staff`(`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Visit-specific audit table
CREATE TABLE `VisitAudit` (
  `AuditId` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `VisitId` bigint(20) NOT NULL,
  `Operation` ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  `ChangeDate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `ChangedBy` smallint(6) NOT NULL,
  `ChangeReason` varchar(255) DEFAULT NULL,
  
  -- Before change state
  `OldPatientId` int(10),
  `OldDepartmentId` smallint(6),
  `OldVisitPurpose` varchar(50),
  `OldVisitTime` datetime,
  `OldStaffId` smallint(6),
  
  -- After change state
  `NewPatientId` int(10),
  `NewDepartmentId` smallint(6),
  `NewVisitPurpose` varchar(50),
  `NewVisitTime` datetime,
  `NewStaffId` smallint(6),
  
  INDEX `idx_visit_audit_date` (`VisitId`, `ChangeDate`),
  FOREIGN KEY (`VisitId`) REFERENCES `Visit`(`VisitId`),
  FOREIGN KEY (`ChangedBy`) REFERENCES `Staff`(`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Drug prescription audit table
CREATE TABLE `VisitDrugAudit` (
  `AuditId` bigint(20) PRIMARY KEY AUTO_INCREMENT,
  `VisitId` bigint(20) NOT NULL,
  `DrugId` varchar(50) NOT NULL,
  `Operation` ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
  `ChangeDate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `ChangedBy` smallint(6) NOT NULL,
  `ChangeReason` varchar(255) DEFAULT NULL,
  
  -- Before change
  `OldDrugRoute` varchar(100),
  `OldDrugQuantity` double,
  `OldDrugTimes` varchar(100),
  `OldNote` varchar(100),
  
  -- After change
  `NewDrugRoute` varchar(100),
  `NewDrugQuantity` double,
  `NewDrugTimes` varchar(100),
  `NewNote` varchar(100),
  
  INDEX `idx_drug_audit_visit` (`VisitId`, `ChangeDate`),
  FOREIGN KEY (`VisitId`) REFERENCES `Visit`(`VisitId`),
  FOREIGN KEY (`DrugId`) REFERENCES `Drug`(`DrugId`),
  FOREIGN KEY (`ChangedBy`) REFERENCES `Staff`(`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================================================
-- MYSQL TRIGGERS FOR AUTOMATIC AUDIT LOGGING
-- =============================================================================

-- Patient table triggers
DELIMITER //

CREATE TRIGGER `Patient_Insert_Audit` 
AFTER INSERT ON `Patient`
FOR EACH ROW
BEGIN
  INSERT INTO PatientAudit (
    PatientId, Operation, ChangedBy, ChangeReason,
    NewPatientName, NewPatientGender, NewPatientAge, 
    NewPatientAddress, NewAllergy, NewHistory, NewPatientNote
  ) VALUES (
    NEW.PatientId, 'INSERT', @current_user_id, 'New patient registration',
    NEW.PatientName, NEW.PatientGender, NEW.PatientAge,
    NEW.PatientAddress, NEW.Allergy, NEW.History, NEW.PatientNote
  );
  
  INSERT INTO AuditLog (TableName, RecordId, Operation, ChangedBy, ChangeReason)
  VALUES ('Patient', NEW.PatientId, 'INSERT', @current_user_id, 'New patient created');
END//

CREATE TRIGGER `Patient_Update_Audit`
AFTER UPDATE ON `Patient`
FOR EACH ROW
BEGIN
  INSERT INTO PatientAudit (
    PatientId, Operation, ChangedBy, ChangeReason,
    OldPatientName, OldPatientGender, OldPatientAge, 
    OldPatientAddress, OldAllergy, OldHistory, OldPatientNote,
    NewPatientName, NewPatientGender, NewPatientAge, 
    NewPatientAddress, NewAllergy, NewHistory, NewPatientNote
  ) VALUES (
    NEW.PatientId, 'UPDATE', @current_user_id, @change_reason,
    OLD.PatientName, OLD.PatientGender, OLD.PatientAge,
    OLD.PatientAddress, OLD.Allergy, OLD.History, OLD.PatientNote,
    NEW.PatientName, NEW.PatientGender, NEW.PatientAge,
    NEW.PatientAddress, NEW.Allergy, NEW.History, NEW.PatientNote
  );
END//

CREATE TRIGGER `Patient_Delete_Audit`
BEFORE DELETE ON `Patient`
FOR EACH ROW
BEGIN
  INSERT INTO PatientAudit (
    PatientId, Operation, ChangedBy, ChangeReason,
    OldPatientName, OldPatientGender, OldPatientAge, 
    OldPatientAddress, OldAllergy, OldHistory, OldPatientNote
  ) VALUES (
    OLD.PatientId, 'DELETE', @current_user_id, @change_reason,
    OLD.PatientName, OLD.PatientGender, OLD.PatientAge,
    OLD.PatientAddress, OLD.Allergy, OLD.History, OLD.PatientNote
  );
END//

-- Visit table triggers
CREATE TRIGGER `Visit_Insert_Audit`
AFTER INSERT ON `Visit`
FOR EACH ROW
BEGIN
  INSERT INTO VisitAudit (
    VisitId, Operation, ChangedBy, ChangeReason,
    NewPatientId, NewDepartmentId, NewVisitPurpose, NewVisitTime, NewStaffId
  ) VALUES (
    NEW.VisitId, 'INSERT', @current_user_id, 'New visit created',
    NEW.PatientId, NEW.DepartmentId, NEW.VisitPurpose, NEW.VisitTime, NEW.StaffId
  );
END//

CREATE TRIGGER `Visit_Update_Audit`
AFTER UPDATE ON `Visit`
FOR EACH ROW
BEGIN
  INSERT INTO VisitAudit (
    VisitId, Operation, ChangedBy, ChangeReason,
    OldPatientId, OldDepartmentId, OldVisitPurpose, OldVisitTime, OldStaffId,
    NewPatientId, NewDepartmentId, NewVisitPurpose, NewVisitTime, NewStaffId
  ) VALUES (
    NEW.VisitId, 'UPDATE', @current_user_id, @change_reason,
    OLD.PatientId, OLD.DepartmentId, OLD.VisitPurpose, OLD.VisitTime, OLD.StaffId,
    NEW.PatientId, NEW.DepartmentId, NEW.VisitPurpose, NEW.VisitTime, NEW.StaffId
  );
END//

-- VisitDrug table triggers
CREATE TRIGGER `VisitDrug_Insert_Audit`
AFTER INSERT ON `VisitDrug`
FOR EACH ROW
BEGIN
  INSERT INTO VisitDrugAudit (
    VisitId, DrugId, Operation, ChangedBy, ChangeReason,
    NewDrugRoute, NewDrugQuantity, NewDrugTimes, NewNote
  ) VALUES (
    NEW.VisitId, NEW.DrugId, 'INSERT', @current_user_id, 'Drug prescribed',
    NEW.DrugRoute, NEW.DrugQuantity, NEW.DrugTimes, NEW.Note
  );
END//

CREATE TRIGGER `VisitDrug_Update_Audit`
AFTER UPDATE ON `VisitDrug`
FOR EACH ROW
BEGIN
  INSERT INTO VisitDrugAudit (
    VisitId, DrugId, Operation, ChangedBy, ChangeReason,
    OldDrugRoute, OldDrugQuantity, OldDrugTimes, OldNote,
    NewDrugRoute, NewDrugQuantity, NewDrugTimes, NewNote
  ) VALUES (
    NEW.VisitId, NEW.DrugId, 'UPDATE', @current_user_id, @change_reason,
    OLD.DrugRoute, OLD.DrugQuantity, OLD.DrugTimes, OLD.Note,
    NEW.DrugRoute, NEW.DrugQuantity, NEW.DrugTimes, NEW.Note
  );
END//

CREATE TRIGGER `VisitDrug_Delete_Audit`
BEFORE DELETE ON `VisitDrug`
FOR EACH ROW
BEGIN
  INSERT INTO VisitDrugAudit (
    VisitId, DrugId, Operation, ChangedBy, ChangeReason,
    OldDrugRoute, OldDrugQuantity, OldDrugTimes, OldNote
  ) VALUES (
    OLD.VisitId, OLD.DrugId, 'DELETE', @current_user_id, @change_reason,
    OLD.DrugRoute, OLD.DrugQuantity, OLD.DrugTimes, OLD.Note
  );
END//

DELIMITER ;

-- =============================================================================
-- PROCEDURES FOR AUDIT MANAGEMENT
-- =============================================================================

DELIMITER //

-- Procedure to set current user for audit logging
CREATE PROCEDURE SetCurrentUser(IN user_id SMALLINT, IN reason VARCHAR(255))
BEGIN
  SET @current_user_id = user_id;
  SET @change_reason = reason;
END//

-- Procedure to get audit history for a patient
CREATE PROCEDURE GetPatientAuditHistory(IN patient_id INT)
BEGIN
  SELECT 
    a.ChangeDate,
    s.StaffName as ChangedBy,
    a.Operation,
    a.ChangeReason,
    CASE 
      WHEN a.OldPatientName != a.NewPatientName THEN CONCAT('Name: ', a.OldPatientName, ' → ', a.NewPatientName)
      WHEN a.OldPatientAge != a.NewPatientAge THEN CONCAT('Age: ', a.OldPatientAge, ' → ', a.NewPatientAge)
      WHEN a.OldPatientAddress != a.NewPatientAddress THEN CONCAT('Address: ', a.OldPatientAddress, ' → ', a.NewPatientAddress)
      ELSE 'Other changes'
    END as ChangeDescription
  FROM PatientAudit a
  JOIN Staff s ON a.ChangedBy = s.StaffId
  WHERE a.PatientId = patient_id
  ORDER BY a.ChangeDate DESC;
END//

-- Procedure to get visit audit history
CREATE PROCEDURE GetVisitAuditHistory(IN visit_id BIGINT)
BEGIN
  SELECT 
    a.ChangeDate,
    s.StaffName as ChangedBy,
    a.Operation,
    a.ChangeReason,
    CASE 
      WHEN a.OldVisitTime != a.NewVisitTime THEN CONCAT('Visit Time: ', a.OldVisitTime, ' → ', a.NewVisitTime)
      WHEN a.OldDepartmentId != a.NewDepartmentId THEN CONCAT('Department changed')
      ELSE 'Other changes'
    END as ChangeDescription
  FROM VisitAudit a
  JOIN Staff s ON a.ChangedBy = s.StaffId
  WHERE a.VisitId = visit_id
  ORDER BY a.ChangeDate DESC;
END//

-- Procedure to get drug prescription changes
CREATE PROCEDURE GetDrugPrescriptionAudit(IN visit_id BIGINT)
BEGIN
  SELECT 
    da.ChangeDate,
    s.StaffName as ChangedBy,
    d.DrugName,
    da.Operation,
    da.ChangeReason,
    CONCAT('Quantity: ', da.OldDrugQuantity, ' → ', da.NewDrugQuantity) as QuantityChange,
    CONCAT('Route: ', da.OldDrugRoute, ' → ', da.NewDrugRoute) as RouteChange
  FROM VisitDrugAudit da
  JOIN Staff s ON da.ChangedBy = s.StaffId
  JOIN Drug d ON da.DrugId = d.DrugId
  WHERE da.VisitId = visit_id
  ORDER BY da.ChangeDate DESC;
END//

DELIMITER ;

-- =============================================================================
-- VIEWS FOR AUDIT REPORTING
-- =============================================================================

-- Complete audit trail view
CREATE VIEW `AuditTrailComplete` AS
SELECT 
  al.AuditId,
  al.TableName,
  al.RecordId,
  al.Operation,
  al.ChangeDate,
  s.StaffName as ChangedBy,
  s.StaffRole,
  d.DepartmentName as ChangedByDepartment,
  al.ChangeReason,
  al.IPAddress
FROM AuditLog al
JOIN Staff s ON al.ChangedBy = s.StaffId
LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId
ORDER BY al.ChangeDate DESC;

-- Recent changes summary
CREATE VIEW `RecentChangesSummary` AS
SELECT 
  DATE(ChangeDate) as ChangeDay,
  TableName,
  Operation,
  COUNT(*) as ChangeCount,
  COUNT(DISTINCT ChangedBy) as UniqueUsers
FROM AuditLog
WHERE ChangeDate >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY DATE(ChangeDate), TableName, Operation
ORDER BY ChangeDay DESC, ChangeCount DESC;

-- Patient data integrity view
CREATE VIEW `PatientDataIntegrity` AS
SELECT 
  p.PatientId,
  p.PatientName,
  COUNT(pa.AuditId) as TotalChanges,
  MAX(pa.ChangeDate) as LastModified,
  COUNT(DISTINCT pa.ChangedBy) as ModifiedByCount
FROM Patient p
LEFT JOIN PatientAudit pa ON p.PatientId = pa.PatientId
GROUP BY p.PatientId, p.PatientName;

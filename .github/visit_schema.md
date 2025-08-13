-- examdb.Visit definition

CREATE TABLE `Visit` (
  `VisitId` bigint(20) NOT NULL AUTO_INCREMENT,
  `PatientId` varchar(10) NOT NULL COMMENT 'Mã bệnh nhân',
  `DepartmentId` smallint(6) NOT NULL,
  `VisitPurpose` enum('Thường quy','Cấp cứu','Phòng khám','Nhận bệnh','Bệnh án','Đột xuất','Hội chẩn','Xuất viện','Tái khám','Khám chuyên khoa') DEFAULT NULL COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime DEFAULT NULL,
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám',
  PRIMARY KEY (`VisitId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `StaffId` (`StaffId`),
  KEY `idx_visit_time` (`VisitTime`),
  KEY `idx_visit_patient_date` (`PatientId`,`VisitTime`),
  CONSTRAINT `Visit_Patient_FK` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`),
  CONSTRAINT `Visit_ibfk_2` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `Visit_ibfk_3` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitDiagnosis definition

CREATE TABLE `VisitDiagnosis` (
  `VisitId` bigint(20) NOT NULL,
  `ICDCode` varchar(10) DEFAULT NULL COMMENT 'mã ICD chẩn đoán',
  `ActualDiagnosis` varchar(255) DEFAULT NULL COMMENT 'Chẩn đoán thực tế',
  `DiseaseType` enum('Bệnh chính','Bệnh kèm','Biến chứng') DEFAULT NULL,
  UNIQUE KEY `VisitDiagnosis_Visit` (`VisitId`,`ICDCode`),
  KEY `VisitDiagnosis_ICD_FK` (`ICDCode`),
  CONSTRAINT `VisitDiagnosis_ICD_FK` FOREIGN KEY (`ICDCode`) REFERENCES `ICD` (`ICDCode`),
  CONSTRAINT `VisitDiagnosis_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitDocuments definition

CREATE TABLE `VisitDocuments` (
  `VisitId` bigint(20) NOT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties' CHECK (json_valid(`metadata`)),
  KEY `VisitDocuments_Visit_FK` (`VisitId`),
  CONSTRAINT `VisitDocuments_Visit_FK` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitDrug definition

CREATE TABLE `VisitDrug` (
  `VisitId` bigint(20) NOT NULL,
  `DrugId` varchar(50) DEFAULT NULL,
  `DrugRoute` varchar(100) DEFAULT NULL,
  `DrugQuantity` double DEFAULT NULL,
  `DrugTimes` varchar(100) DEFAULT NULL,
  `DrugAtTime` datetime DEFAULT NULL,
  `Note` varchar(100) DEFAULT NULL,
  `DrugStatus` enum('CD','TH','XONG') DEFAULT 'CD',
  UNIQUE KEY `Visit_VisitDrug` (`DrugId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  CONSTRAINT `VisitDrug_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitDrug_ibfk_2` FOREIGN KEY (`DrugId`) REFERENCES `Drug` (`DrugId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitImage definition

CREATE TABLE `VisitImage` (
  `VisitId` bigint(20) NOT NULL,
  `ImageId` bigint(20) NOT NULL AUTO_INCREMENT,
  `ImageType` varchar(50) DEFAULT NULL COMMENT 'Type of image (e.g. wound, burn, scan, etc.)',
  `ImageData` longblob NOT NULL COMMENT 'Binary image data',
  `ImageUrl` varchar(255) DEFAULT NULL COMMENT 'Optional: URL if stored externally',
  `Description` varchar(255) DEFAULT NULL COMMENT 'Description or notes about the image',
  `CreatedAt` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`ImageId`),
  KEY `VisitId` (`VisitId`),
  CONSTRAINT `VisitImage_Visit_FK` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitProc definition

CREATE TABLE `VisitProc` (
  `VisitId` bigint(20) NOT NULL,
  `ProcId` varchar(50) DEFAULT NULL,
  `ProcStatus` enum('Ordered','In progress','Completed','Result') DEFAULT 'Ordered' COMMENT 'Trạng thái của thủ thuật',
  `ProcStaffId` smallint(6) DEFAULT NULL COMMENT 'Nhân viên thực hiện thủ thuật',
  `ProcTime` datetime DEFAULT NULL COMMENT 'Thời gian thực hiện',
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  UNIQUE KEY `Visit_VisitProc` (`ProcId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  KEY `ProcStaffId` (`ProcStaffId`),
  CONSTRAINT `VisitProc_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitProc_ibfk_2` FOREIGN KEY (`ProcId`) REFERENCES `Proc` (`ProcId`),
  CONSTRAINT `VisitProc_ibfk_3` FOREIGN KEY (`ProcStaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitSign definition

CREATE TABLE `VisitSign` (
  `VisitId` bigint(20) NOT NULL,
  `SignId` smallint(6) DEFAULT NULL,
  `BodySiteId` int(5) DEFAULT NULL COMMENT 'Vùng cơ thể có dấu hiệu',
  `LeftRight` enum('trái','phải','cả hai bên') DEFAULT NULL COMMENT 'Vị trí của dấu hiệu',
  `Section` enum('toàn bộ','1/3','1/4','1/5') DEFAULT NULL COMMENT 'Vị trí của dấu hiệu',
  `UpperLower` enum('trên','dưới','giữa') DEFAULT NULL COMMENT 'Vị trí của dấu hiệu',
  `FrontBack` enum('mặt trước','mặt sau','mặt trong','mặt ngoài') DEFAULT NULL COMMENT 'Vị trí của dấu hiệu',
  `SignValue` enum('','BT','Có DHBL','Có','Không','Ít','Vừa','Nhiều','Nhẹ','Tăng','Giảm','Như cũ') DEFAULT NULL COMMENT 'Giá trị của dấu hiệu',
  `FollowUp` tinyint(1) DEFAULT 0,
  `ForEmr` tinyint(1) DEFAULT 0,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  UNIQUE KEY `Visit_VisitSign` (`SignId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  KEY `BodySiteId` (`BodySiteId`),
  CONSTRAINT `VisitSign_ibfk_1` FOREIGN KEY (`SignId`) REFERENCES `Sign` (`SignId`),
  CONSTRAINT `VisitSign_ibfk_2` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitSign_ibfk_3` FOREIGN KEY (`BodySiteId`) REFERENCES `BodySite` (`SiteId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitStaff definition

CREATE TABLE `VisitStaff` (
  `VisitId` bigint(20) NOT NULL,
  `StaffId` smallint(6) NOT NULL,
  UNIQUE KEY `Visit_VisitStaff` (`StaffId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  CONSTRAINT `VisitStaff_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitStaff_ibfk_2` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitTest definition

CREATE TABLE `VisitTest` (
  `VisitId` bigint(20) NOT NULL,
  `TestId` varchar(50) DEFAULT NULL,
  `TestStatus` enum('CD','TH','XONG') DEFAULT 'CD',
  `TestStaffId` smallint(6) DEFAULT NULL COMMENT 'Nhân viên thực hiện xét nghiệm',
  `TestTime` datetime DEFAULT NULL COMMENT 'Thời gian thực hiện',
  `TestResult` varchar(255) DEFAULT NULL COMMENT 'Kết quả',
  `TestConclusion` varchar(20) DEFAULT NULL,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  UNIQUE KEY `Visit_VisitTest` (`TestId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  KEY `TestStaffId` (`TestStaffId`),
  CONSTRAINT `VisitTest_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitTest_ibfk_2` FOREIGN KEY (`TestId`) REFERENCES `Test` (`TestId`),
  CONSTRAINT `VisitTest_ibfk_3` FOREIGN KEY (`TestStaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
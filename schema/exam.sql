CREATE DATABASE `examdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

CREATE TABLE `BodySite` (
  `SiteId` int(5) NOT NULL AUTO_INCREMENT,
  `SiteName` varchar(100) NOT NULL,
  PRIMARY KEY (`SiteId`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `BodySystem` (
  `SystemId` int(10) NOT NULL,
  `SystemName` varchar(50) NOT NULL,
  PRIMARY KEY (`SystemId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) NOT NULL,
  `DepartmentName` varchar(100) DEFAULT NULL,
  `DepartmentType` enum('Nội trú','Cấp cứu','Phòng khám') DEFAULT NULL COMMENT 'Loại khoa',
  PRIMARY KEY (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Drug` (
  `DrugId` varchar(50) NOT NULL,
  `DrugName` varchar(255) DEFAULT NULL,
  `DrugChemical` varchar(255) DEFAULT NULL,
  `DrugContent` varchar(100) DEFAULT NULL,
  `DrugFormulation` varchar(50) DEFAULT NULL,
  `DrugRemains` smallint(6) DEFAULT NULL,
  `DrugGroup` varchar(100) DEFAULT NULL,
  `DrugTherapy` varchar(200) DEFAULT NULL,
  `DrugRoute` varchar(50) DEFAULT NULL,
  `DrugQuantity` varchar(50) DEFAULT NULL,
  `CountStr` varchar(50) DEFAULT NULL,
  `DrugAvailable` tinyint(1) DEFAULT 1,
  `DrugPriceBHYT` int(10) DEFAULT 0,
  `DrugPriceVP` int(10) DEFAULT 0,
  `DrugNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về thuốc',
  `Count` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`DrugId`),
  KEY `idx_drug_available` (`DrugAvailable`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `DrugTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `DrugId` varchar(50) NOT NULL,
  UNIQUE KEY `DrugTemplate_Drug` (`DrugId`,`TemplateId`),
  KEY `TemplateId` (`TemplateId`),
  CONSTRAINT `DrugTemplate_ibfk_1` FOREIGN KEY (`DrugId`) REFERENCES `Drug` (`DrugId`),
  CONSTRAINT `DrugTemplate_ibfk_2` FOREIGN KEY (`TemplateId`) REFERENCES `Template` (`TemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ICD` (
  `ICDCode` varchar(10) NOT NULL COMMENT 'Mã ICD',
  `ICDName` varchar(255) NOT NULL COMMENT 'Tên ICD',
  `ICDGroup` varchar(100) DEFAULT '' COMMENT 'Nhóm ICD',
  PRIMARY KEY (`ICDCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Patient` (
  `PatientId` int(10) NOT NULL,
  `PatientName` varchar(100) DEFAULT NULL,
  `PatientGender` enum('Nam','Nữ','Khác') DEFAULT NULL COMMENT 'Giới tính',
  `PatientAge` int(3) DEFAULT NULL COMMENT 'Tuổi',
  `PatientAddress` varchar(255) DEFAULT NULL,
  `Allergy` varchar(255) DEFAULT '' COMMENT 'Tiền sử dị ứng',
  `History` text DEFAULT NULL COMMENT 'Tiền sử bệnh',
  `PatientImage` longblob DEFAULT NULL COMMENT 'Hình ảnh bệnh nhân',
  `PatientNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về bệnh nhân',
  PRIMARY KEY (`PatientId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `PatientDepartment` (
  `PatientId` int(10) NOT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL,
  `Current` tinyint(1) DEFAULT 0 COMMENT '1 nếu là khoa hiện tại của bệnh nhân',
  `AdmissionType` enum('Vào khoa','Cấp cứu','Phòng khám','Khám chuyên khoa') DEFAULT 'Vào khoa',
  UNIQUE KEY `PatientDepartment_Patient` (`PatientId`,`DepartmentId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `idx_patient_current_dept` (`PatientId`,`Current`),
  CONSTRAINT `PatientDepartment_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `PatientDepartment_ibfk_2` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Proc` (
  `ProcId` varchar(50) NOT NULL,
  `ProcDesc` varchar(100) DEFAULT NULL,
  `ProcGroup` varchar(100) DEFAULT NULL,
  `ProcBHYT` tinyint(1) DEFAULT 1,
  `ProcPriceBHYT` int(10) DEFAULT 0,
  `ProcPriceVP` int(10) DEFAULT 0,
  `ProcAvailable` tinyint(1) DEFAULT 1,
  `ProcNote` varchar(100) DEFAULT NULL COMMENT 'Ghi chú về thủ thuật',
  PRIMARY KEY (`ProcId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ProcTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `ProcId` varchar(50) NOT NULL,
  UNIQUE KEY `ProcTemplate_Proc` (`ProcId`,`TemplateId`),
  KEY `TemplateId` (`TemplateId`),
  CONSTRAINT `ProcTemplate_ibfk_1` FOREIGN KEY (`ProcId`) REFERENCES `Proc` (`ProcId`),
  CONSTRAINT `ProcTemplate_ibfk_2` FOREIGN KEY (`TemplateId`) REFERENCES `Template` (`TemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Sign` (
  `SignId` smallint(6) NOT NULL,
  `SignDesc` varchar(100) DEFAULT NULL,
  `SignType` tinyint(1) DEFAULT 0 COMMENT '0 nếu là dấu hiệu cơ năng, 1 nếu là dấu hiệu thực thể',
  `SystemId` int(10) NOT NULL,
  PRIMARY KEY (`SignId`),
  KEY `SystemId` (`SystemId`),
  CONSTRAINT `Sign_ibfk_1` FOREIGN KEY (`SystemId`) REFERENCES `BodySystem` (`SystemId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `SignTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `SignId` smallint(6) NOT NULL,
  UNIQUE KEY `SignTemplate_Sign` (`SignId`,`TemplateId`),
  KEY `TemplateId` (`TemplateId`),
  CONSTRAINT `SignTemplate_ibfk_1` FOREIGN KEY (`SignId`) REFERENCES `Sign` (`SignId`),
  CONSTRAINT `SignTemplate_ibfk_2` FOREIGN KEY (`TemplateId`) REFERENCES `Template` (`TemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Staff` (
  `StaffId` smallint(6) NOT NULL,
  `StaffName` varchar(100) DEFAULT NULL,
  `StaffRole` enum('Bác sĩ','Điều dưỡng','Kỹ thuật viên','Khác') DEFAULT NULL COMMENT 'Vai trò: Bác sĩ...',
  `DepartmentId` smallint(6) DEFAULT NULL,
  `StaffAvailable` tinyint(1) DEFAULT 1 COMMENT '1 nếu nhân viên có thể làm việc, 0 nếu không',
  PRIMARY KEY (`StaffId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `idx_staff_available` (`StaffAvailable`,`DepartmentId`),
  CONSTRAINT `Staff_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Template` (
  `TemplateId` smallint(6) NOT NULL,
  `TemplateName` varchar(100) DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL COMMENT 'Khoa của tập mẫu',
  `TemplateGroup` enum('Test','Sign','Drug','Proc') DEFAULT NULL COMMENT 'Loại của tập mẫu',
  `TemplateType` enum('Bệnh án','Theo dõi') DEFAULT NULL COMMENT 'Loại ghi nhận',
  PRIMARY KEY (`TemplateId`),
  KEY `DepartmentId` (`DepartmentId`),
  CONSTRAINT `Template_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Test` (
  `TestId` varchar(50) NOT NULL,
  `TestName` varchar(100) DEFAULT NULL,
  `TestGroup` varchar(100) DEFAULT NULL,
  `TestPriceBHYT` int(10) DEFAULT 0,
  `TestPriceVP` int(10) DEFAULT 0,
  `TestAvailable` tinyint(1) DEFAULT 1,
  `TestNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về xét nghiệm',
  `TestType` enum('XN','SA','XQ','CT','TDCN','NS') DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`TestId`),
  KEY `Test_Department_FK` (`DepartmentId`),
  KEY `idx_test_available` (`TestAvailable`),
  CONSTRAINT `Test_Department_FK` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `TestTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `TestId` varchar(50) NOT NULL,
  UNIQUE KEY `TestTemplate_Test` (`TestId`,`TemplateId`),
  KEY `TemplateId` (`TemplateId`),
  CONSTRAINT `TestTemplate_ibfk_1` FOREIGN KEY (`TestId`) REFERENCES `Test` (`TestId`),
  CONSTRAINT `TestTemplate_ibfk_2` FOREIGN KEY (`TemplateId`) REFERENCES `Template` (`TemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Visit` (
  `VisitId` bigint(20) NOT NULL AUTO_INCREMENT,
  `PatientId` int(10) NOT NULL COMMENT 'Mã bệnh nhân',
  `DepartmentId` smallint(6) NOT NULL,
  `VisitPurpose` enum('Thường quy','Cấp cứu','Phòng khám','Nhận bệnh','Bệnh án','Đột xuất','Hội chẩn','Xuất viện','Tái khám','Khám chuyên khoa') DEFAULT NULL COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime DEFAULT NULL,
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám',
  PRIMARY KEY (`VisitId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `StaffId` (`StaffId`),
  KEY `idx_visit_time` (`VisitTime`),
  KEY `idx_visit_patient_date` (`PatientId`,`VisitTime`),
  CONSTRAINT `Visit_ibfk_1` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`),
  CONSTRAINT `Visit_ibfk_2` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `Visit_ibfk_3` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

CREATE TABLE `VisitDocuments` (
  `VisitId` bigint(20) NOT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties' CHECK (json_valid(`metadata`)),
  KEY `VisitDocuments_Visit_FK` (`VisitId`),
  CONSTRAINT `VisitDocuments_Visit_FK` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `VisitDrug` (
  `VisitId` bigint(20) NOT NULL,
  `DrugId` varchar(50) DEFAULT NULL,
  `DrugRoute` varchar(100) DEFAULT NULL,
  `DrugQuantity` double DEFAULT NULL,
  `DrugTimes` varchar(100) DEFAULT NULL,
  `DrugAtTime` datetime DEFAULT NULL,
  `Note` varchar(100) DEFAULT NULL,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  UNIQUE KEY `Visit_VisitDrug` (`DrugId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  CONSTRAINT `VisitDrug_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitDrug_ibfk_2` FOREIGN KEY (`DrugId`) REFERENCES `Drug` (`DrugId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

CREATE TABLE `VisitStaff` (
  `VisitId` bigint(20) NOT NULL,
  `StaffId` smallint(6) NOT NULL,
  UNIQUE KEY `Visit_VisitStaff` (`StaffId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  CONSTRAINT `VisitStaff_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitStaff_ibfk_2` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `VisitTest` (
  `VisitId` bigint(20) NOT NULL,
  `TestId` varchar(50) DEFAULT NULL,
  `TestStatus` enum('Ordered','In progress','Completed','Result') DEFAULT 'Ordered' COMMENT 'Trạng thái của xét nghiệm',
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



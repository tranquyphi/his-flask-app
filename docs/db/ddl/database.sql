-- examdb.BodyPart definition

CREATE TABLE `BodyPart` (
  `BodyPartId` smallint(5) unsigned NOT NULL,
  `BodyPartName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`BodyPartId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.BodySystem definition

CREATE TABLE `BodySystem` (
  `SystemId` int NOT NULL,
  `SystemName` varchar(50) NOT NULL,
  PRIMARY KEY (`SystemId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Department definition

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) NOT NULL,
  `DepartmentName` varchar(100) DEFAULT NULL,
  `DepartmentType` enum('Nội trú','Cấp cứu','Phòng khám','CLS') DEFAULT NULL COMMENT 'Loại khoa',
  PRIMARY KEY (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.DocumentType definition

CREATE TABLE `DocumentType` (
  `DocumentTypeId` tinyint(4) NOT NULL AUTO_INCREMENT,
  `DocumentTypeName` varchar(25) NOT NULL,
  PRIMARY KEY (`DocumentTypeId`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.DrugGroup definition

CREATE TABLE `DrugGroup` (
  `DrugGroupId` int(10) unsigned NOT NULL,
  `DrugGroupName` varchar(100) DEFAULT NULL,
  `DrugGroupDescription` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`DrugGroupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.ICD definition

CREATE TABLE `ICD` (
  `ICDCode` varchar(10) NOT NULL COMMENT 'Mã ICD',
  `ICDName` varchar(255) NOT NULL COMMENT 'Tên ICD',
  `ICDGroup` varchar(100) DEFAULT '' COMMENT 'Nhóm ICD',
  PRIMARY KEY (`ICDCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Patient definition

CREATE TABLE `Patient` (
  `PatientId` varchar(10) NOT NULL,
  `PatientName` varchar(100) DEFAULT NULL,
  `PatientGender` enum('Nam','Nữ','Khác') DEFAULT NULL COMMENT 'Giới tính',
  `PatientAge` char(20) DEFAULT NULL COMMENT 'Tuổi',
  `PatientAddress` varchar(255) DEFAULT NULL,
  `Allergy` varchar(255) DEFAULT '' COMMENT 'Tiền sử dị ứng',
  `History` text DEFAULT NULL COMMENT 'Tiền sử bệnh',
  `PatientImage` longblob DEFAULT NULL COMMENT 'Hình ảnh bệnh nhân',
  `PatientNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về bệnh nhân',
  `PatientPhone` varchar(20) DEFAULT NULL,
  `PatientCCCD` varchar(20) DEFAULT NULL,
  `PatientBHYT` varchar(20) DEFAULT NULL,
  `PatientBHYTValid` varchar(100) DEFAULT NULL,
  `PatientRelative` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`PatientId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Proc definition

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


-- examdb.Staff definition

CREATE TABLE `Staff` (
  `StaffId` smallint(6) NOT NULL,
  `StaffName` varchar(100) DEFAULT NULL,
  `StaffRole` enum('Bác sĩ','Điều dưỡng','Kỹ thuật viên','Khác') DEFAULT NULL COMMENT 'Vai trò: Bác sĩ...',
  `StaffAvailable` tinyint(1) DEFAULT 1 COMMENT '1 nếu nhân viên có thể làm việc, 0 nếu không',
  PRIMARY KEY (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.StaffDocumentType definition

CREATE TABLE `StaffDocumentType` (
  `DocumentTypeId` tinyint(4) NOT NULL AUTO_INCREMENT,
  `DocumentTypeName` varchar(25) NOT NULL,
  PRIMARY KEY (`DocumentTypeId`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.BodySite definition

CREATE TABLE `BodySite` (
  `SiteId` int(5) NOT NULL AUTO_INCREMENT,
  `SiteName` varchar(100) NOT NULL,
  `BodyPartId` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`SiteId`),
  KEY `BodySite_BodyPart_FK` (`BodyPartId`),
  CONSTRAINT `BodySite_BodyPart_FK` FOREIGN KEY (`BodyPartId`) REFERENCES `BodyPart` (`BodyPartId`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Drug definition

CREATE TABLE `Drug` (
  `DrugId` varchar(50) NOT NULL,
  `DrugName` varchar(255) DEFAULT NULL,
  `DrugChemical` varchar(255) DEFAULT NULL,
  `DrugContent` varchar(100) DEFAULT NULL,
  `DrugFormulation` varchar(50) DEFAULT NULL,
  `DrugRemains` smallint(6) DEFAULT NULL,
  `DrugGroupId` int(10) unsigned DEFAULT NULL,
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
  KEY `idx_drug_available` (`DrugAvailable`),
  KEY `Drug_DrugGroup_FK` (`DrugGroupId`),
  CONSTRAINT `Drug_DrugGroup_FK` FOREIGN KEY (`DrugGroupId`) REFERENCES `DrugGroup` (`DrugGroupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.DrugTemplate definition

CREATE TABLE `DrugTemplate` (
  `DrugTemplateId` smallint(6) NOT NULL AUTO_INCREMENT,
  `DrugTemplateName` varchar(100) DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL COMMENT 'Khoa của tập mẫu',
  `DrugTemplateType` enum('BA','TD','PK','CC') DEFAULT 'TD' COMMENT 'Loại ghi nhận',
  PRIMARY KEY (`DrugTemplateId`),
  KEY `DrugTemplate_ibfk_1` (`DepartmentId`),
  CONSTRAINT `DrugTemplate_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.DrugTemplateDetail definition

CREATE TABLE `DrugTemplateDetail` (
  `DrugTemplateId` smallint(6) DEFAULT NULL,
  `DrugId` varchar(50) DEFAULT NULL,
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `DrugTemplateDetail_DrugTemplate_FK` (`DrugTemplateId`),
  KEY `DrugTemplateDetail_Drug_FK` (`DrugId`) USING BTREE,
  CONSTRAINT `DrugTemplateDetail_DrugTemplate_FK` FOREIGN KEY (`DrugTemplateId`) REFERENCES `DrugTemplate` (`DrugTemplateId`),
  CONSTRAINT `DrugTemplateDetail_Drug_FK` FOREIGN KEY (`DrugId`) REFERENCES `Drug` (`DrugId`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.PatientDepartment definition

CREATE TABLE `PatientDepartment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PatientId` varchar(10) NOT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL,
  `Current` tinyint(1) DEFAULT 0 COMMENT '1 nếu là khoa hiện tại của bệnh nhân\r\n0 nếu là khoa cũ của bệnh nhân',
  `At` timestamp NULL DEFAULT current_timestamp(),
  `Reason` enum('DT','PT','KCK','CLS','KH') DEFAULT 'DT',
  `EndDate` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_patient_current_dept` (`PatientId`,`Current`),
  KEY `idx_patient_dept` (`PatientId`,`DepartmentId`),
  KEY `idx_patient_current` (`PatientId`,`Current`),
  KEY `idx_department_current` (`DepartmentId`,`Current`),
  KEY `idx_at_time` (`At`),
  CONSTRAINT `PatientDepartment_Patient_FK` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`),
  CONSTRAINT `PatientDepartment_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.PatientDocuments definition

CREATE TABLE `PatientDocuments` (
  `PatientId` varchar(10) NOT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `document_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties',
  `DocumentId` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `DocumentTypeId` tinyint(4) DEFAULT NULL,
  `FileType` varchar(50) DEFAULT NULL,
  `FileSize` int(11) DEFAULT NULL,
  `UploadDate` datetime DEFAULT current_timestamp(),
  `LastModified` datetime DEFAULT current_timestamp(),
  `file_path` varchar(255) DEFAULT NULL COMMENT 'Path to the stored file',
  `original_filename` varchar(255) DEFAULT NULL COMMENT 'Original file name',
  `file_type` varchar(50) DEFAULT NULL COMMENT 'File MIME type',
  `file_size` int(11) DEFAULT NULL COMMENT 'File size in bytes',
  `upload_date` datetime DEFAULT current_timestamp(),
  `last_modified` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  KEY `VisitDocuments_Visit_FK` (`PatientId`),
  KEY `VisitDocuments_DocumentId_IDX` (`DocumentId`,`PatientId`) USING BTREE,
  KEY `PatientDocuments_DocumentType_FK` (`DocumentTypeId`),
  CONSTRAINT `PatientDocuments_DocumentType_FK` FOREIGN KEY (`DocumentTypeId`) REFERENCES `DocumentType` (`DocumentTypeId`),
  CONSTRAINT `PatientDocuments_Patient_FK` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Sign definition

CREATE TABLE `Sign` (
  `SignId` smallint(6) NOT NULL AUTO_INCREMENT,
  `SignDesc` varchar(100) DEFAULT NULL,
  `SignType` tinyint(1) DEFAULT 0 COMMENT '0 nếu là dấu hiệu cơ năng, 1 nếu là dấu hiệu thực thể',
  `SystemId` int NOT NULL,
  `Speciality` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`SignId`),
  KEY `SystemId` (`SystemId`),
  CONSTRAINT `Sign_ibfk_1` FOREIGN KEY (`SystemId`) REFERENCES `BodySystem` (`SystemId`)
) ENGINE=InnoDB AUTO_INCREMENT=679 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.SignTemplate definition

CREATE TABLE `SignTemplate` (
  `SignTemplateId` smallint(6) NOT NULL AUTO_INCREMENT,
  `SignTemplateName` varchar(100) DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL COMMENT 'Khoa của tập mẫu',
  `SignTemplateType` enum('BA','TD','PK','CC') DEFAULT 'TD' COMMENT 'Loại ghi nhận',
  PRIMARY KEY (`SignTemplateId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `Template_TemplateId_IDX` (`SignTemplateId`) USING BTREE,
  CONSTRAINT `SignTemplate_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.SignTemplateDetail definition

CREATE TABLE `SignTemplateDetail` (
  `SignTemplateId` smallint(6) DEFAULT NULL,
  `SignId` smallint(6) DEFAULT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `SignTemplateDetail_SignTemplateId_IDX` (`SignTemplateId`,`SignId`) USING BTREE,
  KEY `SignTemplateDetail_Sign_FK` (`SignId`),
  CONSTRAINT `SignTemplateDetail_SignTemplate_FK` FOREIGN KEY (`SignTemplateId`) REFERENCES `SignTemplate` (`SignTemplateId`),
  CONSTRAINT `SignTemplateDetail_Sign_FK` FOREIGN KEY (`SignId`) REFERENCES `Sign` (`SignId`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.StaffDepartment definition

CREATE TABLE `StaffDepartment` (
  `StaffId` smallint(6) NOT NULL,
  `DepartmentId` smallint(6) NOT NULL,
  `Current` tinyint(1) NOT NULL DEFAULT 1,
  `Position` enum('NV','TK','PK','DDT','KTVT','KHAC') DEFAULT 'NV',
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `StaffDepartment_Staff_FK` (`StaffId`),
  KEY `StaffDepartment_Department_FK` (`DepartmentId`),
  CONSTRAINT `StaffDepartment_Department_FK` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `StaffDepartment_Staff_FK` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB AUTO_INCREMENT=160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.StaffDocuments definition

CREATE TABLE `StaffDocuments` (
  `StaffId` smallint(6) NOT NULL,
  `DocumentId` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `DocumentTypeId` tinyint(4) DEFAULT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `document_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties' CHECK (json_valid(`document_metadata`)),
  `FileSize` int(11) DEFAULT NULL,
  `file_type` varchar(50) DEFAULT NULL COMMENT 'File MIME type',
  `UploadDate` datetime DEFAULT current_timestamp(),
  `LastModified` datetime DEFAULT current_timestamp(),
  `original_filename` varchar(255) DEFAULT NULL COMMENT 'Original file name',
  `last_modified` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`DocumentId`),
  KEY `StafftDocuments_DocumentId_IDX` (`DocumentId`,`StaffId`) USING BTREE,
  KEY `StaffDocuments_DocumentType_FK` (`DocumentTypeId`),
  KEY `StaffDocuments_StaffId_FK` (`StaffId`),
  CONSTRAINT `StaffDocuments_DocumentType_FK` FOREIGN KEY (`DocumentTypeId`) REFERENCES `StaffDocumentType` (`DocumentTypeId`),
  CONSTRAINT `StaffDocuments_StaffId_FK` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Test definition

CREATE TABLE `Test` (
  `TestId` varchar(50) NOT NULL,
  `TestName` varchar(100) DEFAULT NULL,
  `TestGroup` varchar(100) DEFAULT NULL,
  `TestPriceBHYT` int(10) DEFAULT 0,
  `TestPriceVP` int(10) DEFAULT 0,
  `TestAvailable` tinyint(1) DEFAULT 1,
  `TestNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về xét nghiệm',
  `TestType` enum('XN','SA','XQ','CT','TDCN','NS') DEFAULT NULL,
  `InChargeDepartmentId` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`TestId`),
  KEY `Test_Department_FK` (`InChargeDepartmentId`),
  KEY `idx_test_available` (`TestAvailable`),
  CONSTRAINT `Test_Department_FK` FOREIGN KEY (`InChargeDepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.TestTemplate definition

CREATE TABLE `TestTemplate` (
  `TestTemplateId` smallint(6) NOT NULL AUTO_INCREMENT,
  `TestTemplateName` varchar(100) DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL COMMENT 'Khoa của tập mẫu',
  `TestTemplateType` enum('BA','TD','PK','CC') DEFAULT 'TD' COMMENT 'Loại ghi nhận',
  PRIMARY KEY (`TestTemplateId`),
  KEY `TestTemplate_ibfk_1_copy` (`DepartmentId`),
  CONSTRAINT `TestTemplate_ibfk_1_copy` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.TestTemplateDetail definition

CREATE TABLE `TestTemplateDetail` (
  `TestTemplateId` smallint(6) DEFAULT NULL,
  `TestId` varchar(20) DEFAULT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `TestTemplateDetail_Test_FK` (`TestId`),
  KEY `TestTemplateDetail_TestTemplate_FK` (`TestTemplateId`),
  CONSTRAINT `TestTemplateDetail_Test_FK` FOREIGN KEY (`TestId`) REFERENCES `Test` (`TestId`),
  CONSTRAINT `TestTemplateDetail_TestTemplate_FK` FOREIGN KEY (`TestTemplateId`) REFERENCES `TestTemplate` (`TestTemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Visit definition

CREATE TABLE `Visit` (
  `VisitId` bigint(20) NOT NULL AUTO_INCREMENT,
  `PatientId` varchar(10) NOT NULL COMMENT 'Mã bệnh nhân',
  `DepartmentId` smallint(6) NOT NULL,
  `VisitPurpose` enum('Thường quy','Cấp cứu','Phòng khám','Nhận bệnh','Bệnh án','Đột xuất','Hội chẩn','Xuất viện','Tái khám','Khám chuyên khoa') DEFAULT NULL COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime DEFAULT current_timestamp(),
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám',
  PRIMARY KEY (`VisitId`),
  KEY `DepartmentId` (`DepartmentId`),
  KEY `StaffId` (`StaffId`),
  KEY `idx_visit_time` (`VisitTime`),
  KEY `idx_visit_patient_date` (`PatientId`,`VisitTime`),
  CONSTRAINT `Visit_Patient_FK` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`),
  CONSTRAINT `Visit_ibfk_2` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `Visit_ibfk_3` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitDiagnosis definition

CREATE TABLE `VisitDiagnosis` (
  `VisitId` bigint(20) NOT NULL,
  `ICDCode` varchar(10) DEFAULT NULL COMMENT 'mã ICD chẩn đoán',
  `ActualDiagnosis` varchar(255) DEFAULT NULL COMMENT 'Chẩn đoán thực tế',
  `DiseaseType` enum('Bệnh chính','Bệnh kèm','Biến chứng') DEFAULT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
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
  `DocumentId` smallint(5) unsigned DEFAULT NULL,
  `DocumentTypeId` tinyint(4) NOT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `VisitDocuments_Visit_FK` (`VisitId`),
  KEY `VisitDocuments_DocumentId_IDX` (`DocumentId`,`VisitId`) USING BTREE,
  KEY `VisitDocuments_DocumentType_FK` (`DocumentTypeId`),
  CONSTRAINT `VisitDocuments_DocumentType_FK` FOREIGN KEY (`DocumentTypeId`) REFERENCES `DocumentType` (`DocumentTypeId`),
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
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
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
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
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
  `SignValue` enum('BT','Có DHBL','Có','Không','Ít','Vừa','Nhiều','Nhẹ','Tăng','Giảm','Như cũ') DEFAULT 'BT' COMMENT 'Giá trị của dấu hiệu',
  `FollowUp` tinyint(1) DEFAULT 0,
  `ForEmr` tinyint(1) DEFAULT 0,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)',
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
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
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
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
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Visit_VisitTest` (`TestId`,`VisitId`),
  KEY `VisitId` (`VisitId`),
  KEY `TestStaffId` (`TestStaffId`),
  CONSTRAINT `VisitTest_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`),
  CONSTRAINT `VisitTest_ibfk_2` FOREIGN KEY (`TestId`) REFERENCES `Test` (`TestId`),
  CONSTRAINT `VisitTest_ibfk_3` FOREIGN KEY (`TestStaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
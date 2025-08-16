-- examdb.DocumentType definition

CREATE TABLE `DocumentType` (
  `DocumentTypeId` tinyint(4) NOT NULL AUTO_INCREMENT,
  `DocumentTypeName` varchar(25) NOT NULL,
  PRIMARY KEY (`DocumentTypeId`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


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


-- examdb.PatientDocuments definition

CREATE TABLE `PatientDocuments` (
  `PatientId` varchar(20) NOT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties' CHECK (json_valid(`metadata`)),
  `DocumentId` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `DocumentTypeId` tinyint(4) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
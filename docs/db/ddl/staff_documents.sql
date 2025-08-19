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


-- examdb.StaffDocuments definition

CREATE TABLE `StaffDocuments` (
  `StaffId` smallint(6) NOT NULL,
  `DocumentId` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `DocumentTypeId` tinyint(4) DEFAULT NULL,
  `document_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'Structured document links' CHECK (json_valid(`document_links`)),
  `document_metadata` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'Document metadata and properties' CHECK (json_valid(`document_metadata`)),
  `FileSize` int(11) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
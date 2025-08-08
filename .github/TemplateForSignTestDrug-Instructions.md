# Business logic
In the visits, the staff records signs, indicates test and drugs for patient.
The signs, tests, drugs are predefined in Sign, Test, Drug table.
Some diseases, conditions  have the shared signs, drugs and tests which should be collected in the separated sets.
The staff can use these set called templates to batch insert in the VisitSign, VisitTest, VisitDrug.
The staff can insert the sign, test, drug more which does not belong to templates.
# Tables
DDL as follows:
-- examdb.Drug definition

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


-- examdb.DrugTemplate definition

CREATE TABLE `DrugTemplate` (
  `DrugTemplateId` smallint(6) NOT NULL AUTO_INCREMENT,
  `DrugTemplateName` varchar(100) DEFAULT NULL,
  `DepartmentId` smallint(6) DEFAULT NULL COMMENT 'Khoa của tập mẫu',
  `DrugTemplateType` enum('BA','TD','PK','CC') DEFAULT 'TD' COMMENT 'Loại ghi nhận',
  PRIMARY KEY (`DrugTemplateId`),
  KEY `DrugTemplate_ibfk_1` (`DepartmentId`),
  CONSTRAINT `DrugTemplate_ibfk_1` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.DrugTemplateDetail definition

CREATE TABLE `DrugTemplateDetail` (
  `DrugTemplateId` smallint(6) DEFAULT NULL,
  `DrugId` varchar(20) DEFAULT NULL,
  KEY `DrugTemplateDetail_DrugTemplate_FK` (`DrugTemplateId`),
  KEY `DrugTemplateDetail_Drug_FK` (`DrugId`) USING BTREE,
  CONSTRAINT `DrugTemplateDetail_DrugTemplate_FK` FOREIGN KEY (`DrugTemplateId`) REFERENCES `DrugTemplate` (`DrugTemplateId`),
  CONSTRAINT `DrugTemplateDetail_Sign_FK` FOREIGN KEY (`DrugId`) REFERENCES `Drug` (`DrugId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Sign definition

CREATE TABLE `Sign` (
  `SignId` smallint(6) NOT NULL AUTO_INCREMENT,
  `SignDesc` varchar(100) DEFAULT NULL,
  `SignType` tinyint(1) DEFAULT 0 COMMENT '0 nếu là dấu hiệu cơ năng, 1 nếu là dấu hiệu thực thể',
  `SystemId` int(1) NOT NULL,
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
  KEY `SignTemplateDetail_SignTemplateId_IDX` (`SignTemplateId`,`SignId`) USING BTREE,
  KEY `SignTemplateDetail_Sign_FK` (`SignId`),
  CONSTRAINT `SignTemplateDetail_SignTemplate_FK` FOREIGN KEY (`SignTemplateId`) REFERENCES `SignTemplate` (`SignTemplateId`),
  CONSTRAINT `SignTemplateDetail_Sign_FK` FOREIGN KEY (`SignId`) REFERENCES `Sign` (`SignId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


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
  KEY `TestTemplateDetail_Sign_FK` (`TestId`),
  KEY `TestTemplateDetail_TestTemplate_FK` (`TestTemplateId`),
  CONSTRAINT `TestTemplateDetail_Sign_FK` FOREIGN KEY (`TestId`) REFERENCES `Test` (`TestId`),
  CONSTRAINT `TestTemplateDetail_TestTemplate_FK` FOREIGN KEY (`TestTemplateId`) REFERENCES `TestTemplate` (`TestTemplateId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
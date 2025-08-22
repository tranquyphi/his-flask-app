-- examdb.Department definition

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) NOT NULL,
  `DepartmentName` varchar(100) DEFAULT NULL,
  `DepartmentType` enum('Nội trú','Cấp cứu','Phòng khám','CLS') DEFAULT NULL COMMENT 'Loại khoa',
  PRIMARY KEY (`DepartmentId`)
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


-- examdb.Staff definition

CREATE TABLE `Staff` (
  `StaffId` smallint(6) NOT NULL,
  `StaffName` varchar(100) DEFAULT NULL,
  `StaffRole` enum('Bác sĩ','Điều dưỡng','Kỹ thuật viên','Khác') DEFAULT NULL COMMENT 'Vai trò: Bác sĩ...',
  `StaffAvailable` tinyint(1) DEFAULT 1 COMMENT '1 nếu nhân viên có thể làm việc, 0 nếu không',
  PRIMARY KEY (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


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
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


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
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Visit definition

CREATE TABLE `Visit` (
  `VisitId` bigint(20) NOT NULL AUTO_INCREMENT,
  `PatientId` varchar(10) NOT NULL COMMENT 'Mã bệnh nhân',
  `VisitPurpose` enum('Thường quy','Cấp cứu','Phòng khám','Nhận bệnh','Bệnh án','Đột xuất','Hội chẩn','Xuất viện','Tái khám','Khám chuyên khoa') DEFAULT NULL COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime DEFAULT current_timestamp(),
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám',
  PRIMARY KEY (`VisitId`),
  KEY `StaffId` (`StaffId`),
  KEY `idx_visit_time` (`VisitTime`),
  KEY `idx_visit_patient_date` (`PatientId`,`VisitTime`),
  CONSTRAINT `Visit_Patient_FK` FOREIGN KEY (`PatientId`) REFERENCES `Patient` (`PatientId`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.VisitStaff definition

CREATE TABLE `VisitStaff` (
  `VisitId` bigint(20) NOT NULL,
  `StaffId` smallint(6) NOT NULL,
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Visit_VisitStaff` (`StaffId`,`VisitId`),
  KEY `VisitStaff_ibfk_1` (`VisitId`),
  CONSTRAINT `VisitStaff_ibfk_1` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `VisitStaff_ibfk_2` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
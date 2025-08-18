-- examdb.Department definition

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) NOT NULL,
  `DepartmentName` varchar(100) DEFAULT NULL,
  `DepartmentType` enum('Nội trú','Cấp cứu','Phòng khám') DEFAULT NULL COMMENT 'Loại khoa',
  PRIMARY KEY (`DepartmentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.Staff definition

CREATE TABLE `Staff` (
  `StaffId` smallint(6) NOT NULL,
  `StaffName` varchar(100) DEFAULT NULL,
  `StaffRole` enum('Bác sĩ','Điều dưỡng','Kỹ thuật viên','Khác') DEFAULT NULL COMMENT 'Vai trò: Bác sĩ...',
  `StaffAvailable` tinyint(1) DEFAULT 1 COMMENT '1 nếu nhân viên có thể làm việc, 0 nếu không',
  PRIMARY KEY (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.StaffDepartment definition

CREATE TABLE `StaffDepartment` (
  `StaffId` smallint(6) NOT NULL,
  `DepartmentId` smallint(6) NOT NULL,
  `Current` tinyint(1) NOT NULL DEFAULT 1,
  `Position` enum('NV','TK','PK','DDT','KTVT','KHAC') DEFAULT NULL,
  KEY `StaffDepartment_Staff_FK` (`StaffId`),
  KEY `StaffDepartment_Department_FK` (`DepartmentId`),
  CONSTRAINT `StaffDepartment_Department_FK` FOREIGN KEY (`DepartmentId`) REFERENCES `Department` (`DepartmentId`),
  CONSTRAINT `StaffDepartment_Staff_FK` FOREIGN KEY (`StaffId`) REFERENCES `Staff` (`StaffId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
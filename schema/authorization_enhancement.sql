-- Optional authorization enhancement tables
-- (Only add if you need more granular control than role-based)

-- User authentication table
CREATE TABLE `User` (
  `UserId` int(10) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) UNIQUE NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `StaffId` smallint(6) NOT NULL,
  `IsActive` boolean DEFAULT 1,
  `LastLogin` datetime,
  `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (StaffId) REFERENCES Staff(StaffId)
);

-- Permission definitions
CREATE TABLE `Permission` (
  `PermissionId` smallint(6) PRIMARY KEY NOT NULL,
  `PermissionName` varchar(50) NOT NULL,
  `ResourceType` ENUM('Patient', 'Visit', 'Drug', 'Test', 'Proc', 'Template') NOT NULL,
  `Action` ENUM('create', 'read', 'update', 'delete', 'approve') NOT NULL
);

-- Role-Permission mapping
CREATE TABLE `RolePermission` (
  `RoleId` ENUM('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác') NOT NULL,
  `PermissionId` smallint(6) NOT NULL,
  `DepartmentType` ENUM('Nội trú', 'Cấp cứu', 'Phòng khám', 'All') DEFAULT 'All',
  PRIMARY KEY (RoleId, PermissionId, DepartmentType),
  FOREIGN KEY (PermissionId) REFERENCES Permission(PermissionId)
);

-- Patient assignment for fine-grained access
CREATE TABLE `StaffPatientAssignment` (
  `StaffId` smallint(6) NOT NULL,
  `PatientId` int(10) NOT NULL,
  `AssignedAt` datetime DEFAULT CURRENT_TIMESTAMP,
  `IsActive` boolean DEFAULT 1,
  PRIMARY KEY (StaffId, PatientId),
  FOREIGN KEY (StaffId) REFERENCES Staff(StaffId),
  FOREIGN KEY (PatientId) REFERENCES Patient(PatientId)
);

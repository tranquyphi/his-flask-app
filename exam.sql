
DROP DATABASE `examdb`;
CREATE DATABASE `examdb`;
GRANT ALL PRIVILEGES ON `examdb`.* TO 'bvthanghoa'@'*.*' IDENTIFIED BY '57PhanKeBinh';
FLUSH PRIVILEGES;
USE `examdb`;

CREATE TABLE `Patient` (
  `PatientId` int(10) PRIMARY KEY NOT NULL,
  `AdminissionId` int(10) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `LastName` varchar(200) NOT NULL,
  `Age` varchar(20) NOT NULL
);

CREATE TABLE `EmrSample` (
  `EmrSampleId` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `EmrSampleName` varchar(100) DEFAULT null
);

CREATE TABLE `PatientDepartment` (
  `PatientId` int(10) NOT NULL,
  `DepartmentId` smallint(6),
  `Current` tinyint(1) DEFAULT 0 COMMENT '1 nếu là khoa hiện tại của bệnh nhân',
  `EmrId` int(10) UNIQUE NOT NULL COMMENT 'Mã bệnh án',

);

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) PRIMARY KEY NOT NULL,
  `DepartmentName` varchar(100)
);

CREATE TABLE `Staff` (
  `StaffId` smallint(6) PRIMARY KEY NOT NULL,
  `StaffName` varchar(100),
  `StaffRole` ENUM ('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác') COMMENT 'Vai trò: Bác sĩ...',
  `DepartmentId` smallint(6)
);

CREATE TABLE `Visit` (
  `VisitId` bigint(20) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `DepartmentId` int(10) NOT NULL,
  `VisitType` ENUM ('Cấp cứu', 'Phóng khám','Nhận bệnh', 'Bệnh án', 'Thường quy', 'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám') COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime,
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám'
);

CREATE TABLE `Drug` (
  `id` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `DrugId` varchar(50) UNIQUE NOT NULL,
  `DrugName` varchar(255),
  `DrugChemical` varchar(255),
  `DrugContent` varchar(100),
  `DrugFormulation` varchar(50),
  `DrugRemains` smallint(6),
  `DrugGroup` varchar(100),
  `DrugTherapy` varchar(200),
  `DrugRoute` varchar(50),
  `Count` varchar(50),
  `CountStr` varchar(50),
  `DrugAvailable` boolean,
  `DrugPriceBHYT` int(10) DEFAULT 0,
  `DrugPriceVP` int(10) DEFAULT 0,
  `DrugNote` varchar(100) 
);

CREATE TABLE `VisitDrug` (
  `VisitId` bigint(20) NOT NULL,
  `DrugId` varchar(50) NOT NULL,
  `DrugRoute` varchar(100),
  `DrugQuantity` double,
  `DrugTimes` varchar(100),
  `DrugAtTime` datetime,
  `Note` varchar(100)
);

    
CREATE TABLE `Procedure` (
  `ProcedureId` varchar(50) UNIQUE NOT NULL,
  `ProcedureDesc` varchar(100),
  `ProcedureGroup` varchar(100),
  `ProcedureBHYT` tinyint(1) DEFAULT 1,
  `ProcedurePriceBHYT` int(10) DEFAULT 0,
  `ProcedurePriceVP` int(10) DEFAULT 0,
  `ProcedureAvailable` bool
);

CREATE TABLE `VisitProcedure` (
  `id` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `VisitId` bigint(20) NOT NULL,
  `ProcedureId` varchar(50) NOT NULL
);

CREATE TABLE `Test` (
  `id` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `TestId` varchar(50) UNIQUE NOT NULL,
  `TestDesc` varchar(100),
  `TestType` ENUM ('XN', 'CDHA', 'TDCN'),
  `TestSystem` varchar(50),
  `TestAvailable` bool
);

CREATE TABLE `VisitTest` (
  `id` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `VisitId` bigint(20) NOT NULL,
  `TestId` varchar(50) NOT NULL,
  `TestResult` varchar(255)
);

CREATE TABLE `Sign` (
  `id` smallint(6) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `EmrSampleId` smallint(6),
  `SignId` smallint(6) UNIQUE,
  `SignDesc` varchar(100),
  `SignDefault` varchar(100),
  `SubSystemId` varchar(50)
);

CREATE TABLE `VisitSign` (
  `id` bigint(20) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `VisitId` bigint(20) NOT NULL,
  `SignId` smallint(6) NOT NULL,
  `SignValue` ENUM ('BT', 'Có DHBL', 'Không', '(+)', '(++)', '(+++)', '(+-)'),
  `FollowUp` tinyint(1) DEFAULT 0,
  `ForEmr` tinyint(1) DEFAULT 0,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm'
);

ALTER TABLE
  `VisitDrug` ADD UNIQUE `Visit_VisitDrug`(`DrugId`, `VisitId`);
ALTER TABLE
  `VisitProcedure` ADD UNIQUE `Visit_VisitProcedure`(`ProcedureId`, `VisitId`);
ALTER TABLE
  `VisitTest` ADD UNIQUE `Visit_VisitTest`(`TestId`, `VisitId`);
ALTER TABLE
  `VisitSign` ADD UNIQUE `Visit_VisitSign`(`SignId`, `VisitId`);

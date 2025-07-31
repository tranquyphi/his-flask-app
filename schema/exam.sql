
DROP DATABASE `examdb`;
CREATE DATABASE `examdb`;
GRANT ALL PRIVILEGES ON `examdb`.* TO 'bvthanghoa'@'*.*' IDENTIFIED BY '57PhanKeBinh';
FLUSH PRIVILEGES;
USE `examdb`; 
--The predefined tables containing predefined data for the exam system

CREATE TABLE `Department` (
  `DepartmentId` smallint(6) PRIMARY KEY NOT NULL,
  `DepartmentName` varchar(100),
  `DepartmentType` ENUM ('Nội trú', 'Cấp cứu', 'Phòng khám') COMMENT 'Loại khoa'
);
CREATE TABLE `Staff` (
  `StaffId` smallint(6) PRIMARY KEY NOT NULL,
  `StaffName` varchar(100),
  `StaffRole` ENUM ('Bác sĩ', 'Điều dưỡng', 'Kỹ thuật viên', 'Khác') COMMENT 'Vai trò: Bác sĩ...',
  `DepartmentId` smallint(6),
  `StaffAvailable` boolean DEFAULT 1 COMMENT '1 nếu nhân viên có thể làm việc, 0 nếu không'
);



--The body system table, which contains the body systems used in the exam system

CREATE TABLE `BodySystem` (
  `SystemId` int(10) NOT NULL PRIMARY KEY,
  `SystemTitle` varchar(100) NOT NULL
);

--The sign table, which contains the signs used in the exam system

CREATE TABLE `Sign` (
  `SignId` smallint(6) PRIMARY KEY NOT NULL,
  `SignDesc` varchar(100),
  `SignType` tinyint(1) DEFAULT 0 COMMENT '0 nếu là dấu hiệu cơ năng, 1 nếu là dấu hiệu thực thể',
  `SystemId` int(10) NOT NULL
);
CREATE TABLE `Drug` (
  `DrugId` varchar(50) PRIMARY KEY NOT NULL,
  `DrugName` varchar(255),
  `DrugChemical` varchar(255),
  `DrugContent` varchar(100),
  `DrugFormulation` varchar(50),
  `DrugRemains` smallint(6),
  `DrugGroup` varchar(100),
  `DrugTherapy` varchar(200),
  `DrugRoute` varchar(50),
  `DrugQuantity` varchar(50),
  `CountStr` varchar(50),
  `DrugAvailable` boolean DEFAULT 1,
  `DrugPriceBHYT` int(10) DEFAULT 0,
  `DrugPriceVP` int(10) DEFAULT 0,
  `DrugNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về thuốc'
);
CREATE TABLE `Proc` (
  `ProcId` varchar(50) PRIMARY KEY NOT NULL,
  `ProcDesc` varchar(100),
  `ProcGroup` varchar(100),
  `ProcBHYT` tinyint(1) DEFAULT 1,
  `ProcPriceBHYT` int(10) DEFAULT 0,
  `ProcPriceVP` int(10) DEFAULT 0,
  `ProcAvailable` boolean DEFAULT 1,
  `ProcNote` varchar(100) COMMENT 'Ghi chú về thủ thuật'
);

CREATE TABLE `Test` (
  `TestId` varchar(50) PRIMARY KEY NOT NULL,
  `TestName` varchar(100),
  `TestGroup` varchar(100),
  `TestPriceBHYT` int(10) DEFAULT 0,
  `TestPriceVP` int(10) DEFAULT 0,
  `TestAvailable` boolean DEFAULT 1,
  `TestNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về xét nghiệm'
);

--The template table, which contains the templates for the exam system
-- A template can have multiple signs, tests, drugs, and procedures associated with it
CREATE TABLE `Template` (
  `TemplateId` smallint(6) PRIMARY KEY NOT NULL,
  `TemplateName` varchar(100),
  `DepartmentId` smallint(6) COMMENT 'Khoa của tập mẫu',
  `TemplateGroup` ENUM ('Test', 'Sign', 'Drug', 'Proc') COMMENT 'Loại của tập mẫu',
  `TemplateType` ENUM ('Bệnh án', 'Theo dõi') COMMENT 'Loại ghi nhận' -- IGNORE
);
--Template for signs to be used in each visit
CREATE TABLE `SignTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `SignId` smallint(6) NOT NULL
);
--Template for tests to be used in each visit
CREATE TABLE `TestTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `TestId` varchar(50) NOT NULL
);
--Template for drugs to be used in each visit
CREATE TABLE `DrugTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `DrugId` varchar(50) NOT NULL
);
--Template for procedures to be used in each visit
CREATE TABLE `ProcTemplate` (
  `TemplateId` smallint(6) NOT NULL,
  `ProcId` varchar(50) NOT NULL
);
-- The patient table, which contains the patients in the exam system
CREATE TABLE `Patient` (
  `PatientId` int(10) PRIMARY KEY NOT NULL,
  `PatientName` varchar(100),
  `PatientGender` ENUM ('Nam', 'Nữ', 'Khác') COMMENT 'Giới tính',
  `PatientAge` int(3) COMMENT 'Tuổi',
  `PatientAddress` varchar(255),
  `Allergy` varchar(255) DEFAULT '' COMMENT 'Tiền sử dị ứng',
  `History` text COMMENT 'Tiền sử bệnh',  
  `PatientImage` longblob COMMENT 'Hình ảnh bệnh nhân',
  `PatientNote` varchar(100) DEFAULT '' COMMENT 'Ghi chú về bệnh nhân'
);

-- Department of the patient- A patient can be in multiple departments, but only one department is current
CREATE TABLE `PatientDepartment` (
  `PatientId` int(10) NOT NULL,
  `DepartmentId` smallint(6),
  `Current` tinyint(1) DEFAULT 0 COMMENT '1 nếu là khoa hiện tại của bệnh nhân',
  `AdmissionType` ENUM('Vào khoa', 'Cấp cứu', 'Phòng khám','Khám chuyên khoa') DEFAULT 'Vào khoa'
);

--The visit table, which records the visits 
CREATE TABLE `Visit` (
  `VisitId` bigint(20) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `PatientId` int(10) NOT NULL COMMENT 'Mã bệnh nhân',

  `DepartmentId` smallint(6) NOT NULL,
  `VisitPurpose` ENUM ('Thường quy','Cấp cứu', 'Phòng khám','Nhận bệnh', 'Bệnh án',  'Đột xuất', 'Hội chẩn', 'Xuất viện', 'Tái khám','Khám chuyên khoa') COMMENT 'Loại của lần thăm khám',
  `VisitTime` datetime,
  `TestTemplateId` smallint(6) COMMENT 'Tập mẫu triệu chứng',
  `SignTemplateId` smallint(6) COMMENT 'Tập mẫu dấu hiệu',
  `DrugTemplateId` smallint(6) COMMENT 'Tập mẫu thuốc',
  `ProcTemplateId` smallint(6) COMMENT 'Tập mẫu thủ thuật',
  `StaffId` smallint(6) NOT NULL COMMENT 'Nhân viên thăm khám'
);
-- For each visit there is a records of signs, images,drugs, procedures, tests, and staff involved. 
-- Except for the staff, there is one at least but not all. That is a visit has only signs, or drugs, or procedures, or tests, or staff.  


CREATE TABLE `VisitImage` (
  `VisitId` bigint(20) NOT NULL,
  `ImageId` longblob
);
--The sign table, which records the actual signs for each visit
-- A visit can have multiple signs associated with it
CREATE TABLE `VisitSign` (
  `VisitId` bigint(20) NOT NULL,
  `SignId` smallint(6),
  `SignValue` ENUM ('BT', 'Có DHBL', 'Không', 'Ít', 'Vừa', 'Nhiều','Nhẹ','Tăng','Giảm',"Như cũ"),
  `FollowUp` tinyint(1) DEFAULT 0,
  `ForEmr` tinyint(1) DEFAULT 0,
  `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm'
);
--the drug table, which records the drugs prescribed for each visit
CREATE TABLE `VisitDrug` (
  `VisitId` bigint(20) NOT NULL,
  `DrugId` varchar(50),
  `DrugRoute` varchar(100),
  `DrugQuantity` double,
  `DrugTimes` varchar(100),
  `DrugAtTime` datetime,
  `Note` varchar(100)
);

--the procedure table, which records the procedures performed for each visit
    
CREATE TABLE `VisitProc` (
  `VisitId` bigint(20) NOT NULL,
  `ProcId` varchar(50),
  `ProcStatus` ENUM ('Ordered', 'In progress', 'Completed', 'Result') DEFAULT 'Ordered' COMMENT 'Trạng thái của thủ thuật',
  `ProcStaffId` smallint(6) DEFAULT NULL COMMENT 'Nhân viên thực hiện thủ thuật',
  `ProcTime` datetime DEFAULT NULL COMMENT 'Thời gian thực hiện'
);

--the test table, which records the tests indicated for each visit
CREATE TABLE `VisitTest` (
  `VisitId` bigint(20) NOT NULL,
  `TestId` varchar(50),
  `TestStatus` ENUM ('Ordered', 'In progress', 'Completed', 'Result') DEFAULT 'Ordered' COMMENT 'Trạng thái của xét nghiệm',
  `TestStaffId` smallint(6) DEFAULT NULL COMMENT 'Nhân viên thực hiện xét nghiệm',
  `TestTime` datetime DEFAULT NULL COMMENT 'Thời gian thực hiện',
  `TestResult` varchar(255) DEFAULT NULL COMMENT 'Kết quả',
  `TestConclusion` varchar(20)   
);

--the visit staff table, which records the staff involved in each visit
-- A visit can have multiple staff members associated with it
CREATE TABLE `VisitStaff` (
  `VisitId` bigint(20) NOT NULL,
  `StaffId` smallint(6) NOT NULL
);

ALTER TABLE `Staff`
  ADD FOREIGN KEY (DepartmentId) REFERENCES Department(DepartmentId);

ALTER TABLE `Sign`
  ADD FOREIGN KEY (SystemId)  REFERENCES BodySystem(SystemId);
--The constraints for the template tables

ALTER table `Template`
  ADD FOREIGN KEY (DepartmentId) REFERENCES Department(DepartmentId);

ALTER table `SignTemplate`
  ADD UNIQUE `SignTemplate_Sign`(`SignId`, `TemplateId`),
  ADD FOREIGN KEY (SignId) REFERENCES Sign(SignId),
  ADD FOREIGN KEY (TemplateId) REFERENCES Template(TemplateId);
ALTER TABLE `ProcTemplate`
  ADD UNIQUE `ProcTemplate_Proc`(`ProcId`, `TemplateId`),
  ADD FOREIGN KEY (ProcId) REFERENCES Proc(ProcId),
  ADD FOREIGN KEY (TemplateId) REFERENCES Template(TemplateId);
ALTER TABLE `DrugTemplate`
  ADD UNIQUE `DrugTemplate_Drug`(`DrugId`, `TemplateId`),
  ADD FOREIGN KEY (DrugId) REFERENCES Drug(DrugId),
  ADD FOREIGN KEY (TemplateId) REFERENCES Template(TemplateId);
ALTER TABLE `TestTemplate`
  ADD UNIQUE `TestTemplate_Test`(`TestId`, `TemplateId`),
  ADD FOREIGN KEY (TestId) REFERENCES Test(TestId),
  ADD FOREIGN KEY (TemplateId) REFERENCES Template(TemplateId);


--The constraints for patient department
ALTER TABLE `PatientDepartment`
  ADD UNIQUE `PatientDepartment_Patient`(`PatientId`, `DepartmentId`);
ALTER TABLE `PatientDepartment`
  ADD FOREIGN KEY (DepartmentId) REFERENCES Department(DepartmentId),
  ADD FOREIGN KEY (PatientId) REFERENCES Patient(PatientId);


-- The constraints for the visit tables
ALTER TABLE `VisitDrug` ADD UNIQUE `Visit_VisitDrug`(`DrugId`, `VisitId`);
ALTER TABLE `VisitProc` ADD UNIQUE `Visit_VisitProc`(`ProcId`, `VisitId`);
ALTER TABLE `VisitTest` ADD UNIQUE `Visit_VisitTest`(`TestId`, `VisitId`);
ALTER TABLE  `VisitSign` ADD UNIQUE `Visit_VisitSign`(`SignId`, `VisitId`);
ALTER TABLE  `VisitStaff` ADD UNIQUE `Visit_VisitStaff`(`StaffId`, `VisitId`); 

ALTER TABLE `Visit`
  ADD FOREIGN KEY (PatientId) REFERENCES Patient(PatientId),
  ADD FOREIGN KEY (DepartmentId) REFERENCES Department(DepartmentId),
  ADD FOREIGN KEY (StaffId) REFERENCES Staff(StaffId),
  ADD FOREIGN KEY (TestTemplateId) REFERENCES Template(TemplateId),
  ADD FOREIGN KEY (SignTemplateId) REFERENCES Template(TemplateId),
  ADD FOREIGN KEY (DrugTemplateId) REFERENCES Template(TemplateId),
  ADD FOREIGN KEY (ProcTemplateId) REFERENCES Template(TemplateId);

ALTER table `VisitImage`
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId);


 ALTER TABLE `VisitSign`
  ADD FOREIGN KEY (SignId) REFERENCES Sign(SignId),
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId);

ALTER TABLE `VisitDrug`
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId),
  ADD FOREIGN KEY (DrugId) REFERENCES Drug(DrugId); 
  

ALTER TABLE `VisitProc`
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId),
  ADD FOREIGN KEY (ProcId) REFERENCES Proc(ProcId),
  ADD FOREIGN KEY (ProcStaffId) REFERENCES Staff(StaffId);

ALTER TABLE `VisitTest`
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId),
  ADD FOREIGN KEY (TestId) REFERENCES Test(TestId),
  ADD FOREIGN KEY (TestStaffId) REFERENCES Staff(StaffId);

ALTER TABLE `VisitStaff`
  ADD FOREIGN KEY (VisitId) REFERENCES Visit(VisitId),
  ADD FOREIGN KEY (StaffId) REFERENCES Staff(StaffId);





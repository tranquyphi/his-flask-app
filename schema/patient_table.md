# TABLE `Patient` 
# COLUMNS:
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
# CONSTRAINT `PK_Patient` PRIMARY KEY (`PatientId`),
   
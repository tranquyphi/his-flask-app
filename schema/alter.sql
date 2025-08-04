--  ALTER TABLE `VisitSign` (
  --`VisitId` bigint(20) NOT NULL,
  --`SignId` smallint(6),
--   `BodySiteId` int(5) COMMENT 'Vùng cơ thể có dấu hiệu',
--   `LeftRight` ENUM ('trái', 'phải', 'cả hai bên') COMMENT 'Vị trí của dấu hiệu',
--  MODIFY COLUMN `Section` ENUM ('toàn bộ','1/2','1/3', '1/4', '1/5','I','II','III','IV','V') COMMENT 'Vị trí của dấu hiệu'
--   `UpperLower` ENUM ('trên', 'dưới','giữa','bên') COMMENT 'Vị trí của dấu hiệu',
--   `FrontBack` ENUM ('mặt trước', 'mặt sau', 'mặt trong','mặt ngoài') COMMENT 'Vị trí của dấu hiệu',
--   `SignValue` ENUM (' ','BT', 'Có DHBL','Có','Không', 'Ít', 'Vừa', 'Nhiều','Nhẹ','Tăng','Giảm','Như cũ') COMMENT 'Giá trị của dấu hiệu',
--   `FollowUp` tinyint(1) DEFAULT 0,
--   `ForEmr` tinyint(1) DEFAULT 0,
--   `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)'
-- );

-- CREATE TABLE `VisitImage` (
--   `VisitId` bigint(20) NOT NULL,
--   `ImageId` bigint(20) NOT NULL AUTO_INCREMENT,
--   `ImageType` varchar(50) DEFAULT NULL COMMENT 'Type of image (e.g. wound, burn, scan, etc.)',
--   `ImageData` longblob COMMENT 'Binary image data',
--   `ImageUrl` varchar(255) DEFAULT NULL COMMENT 'Optional: URL if stored externally',
--   `Description` varchar(255) DEFAULT NULL COMMENT 'Description or notes about the image',
--   `CreatedAt` datetime DEFAULT CURRENT_TIMESTAMP,
--   PRIMARY KEY (`ImageId`),
--   KEY `VisitId` (`VisitId`),
--   CONSTRAINT `VisitImage_Visit_FK` FOREIGN KEY (`VisitId`) REFERENCES `Visit` (`VisitId`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `VisitTest` 
  MODIFY COLUMN `TestStatus` ENUM ('CD', 'TH', 'XONG') DEFAULT 'CD';
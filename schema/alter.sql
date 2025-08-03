 ALTER TABLE `VisitSign` (
  --`VisitId` bigint(20) NOT NULL,
  --`SignId` smallint(6),
--   `BodySiteId` int(5) COMMENT 'Vùng cơ thể có dấu hiệu',
--   `LeftRight` ENUM ('trái', 'phải', 'cả hai bên') COMMENT 'Vị trí của dấu hiệu',
 MODIFY COLUMN `Section` ENUM ('toàn bộ','1/2','1/3', '1/4', '1/5','I','II','III','IV','V') COMMENT 'Vị trí của dấu hiệu'
--   `UpperLower` ENUM ('trên', 'dưới','giữa','bên') COMMENT 'Vị trí của dấu hiệu',
--   `FrontBack` ENUM ('mặt trước', 'mặt sau', 'mặt trong','mặt ngoài') COMMENT 'Vị trí của dấu hiệu',
--   `SignValue` ENUM (' ','BT', 'Có DHBL','Có','Không', 'Ít', 'Vừa', 'Nhiều','Nhẹ','Tăng','Giảm','Như cũ') COMMENT 'Giá trị của dấu hiệu',
--   `FollowUp` tinyint(1) DEFAULT 0,
--   `ForEmr` tinyint(1) DEFAULT 0,
--   `IsCustom` tinyint(1) DEFAULT 0 COMMENT '1 nếu bác sĩ tự thêm (không từ template)'
);
---
mode: agent
---
Define the task to achieve, including specific requirements, constraints, and success criteria.
# Sign 
The sign is clinical ones.
The sign is used to identify and document specific clinical findings or symptoms observed in a patient.
The signs are predefined indicators in the table Sign that help healthcare professionals assess a patient's condition and make informed decisions about their care.
# Template
One template consists of a set of signs that are commonly used together to evaluate a specific clinical scenario or condition.
The template consists of many signs that are relevant to the particular situation being assessed.
One sign should belongs to many template.
The list of templates stored in table SignTemplate.
The list of signs of a specific template is stored in the table TemplateSignDetail.
# The schema of the tables related to sign and its templates
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
# The backend
The API endpoints for sign and template management
CRUD operations for Sign and SignTemplate, SignTemplateDetail
## Sign
## SignTemplate
## SignTemplateDetail
### SignTemplateDetailSpecific
SignTemplateDetail with TemplateId parameter.
# The frontend
## General required:
UI for creating, updating, and deleting record.
Responsive.
Use icon instead of text if possible (the buttons)
The filter is performed using dropdown list using ENUM values or FK
## Sign UI: 
Display: List of signs with their details
Search signs by description, type, and specialty
Filter signs by system and specialty.
## SignTemplate UI: 
Display: List of templates with their details (not including their signs)
The button to jump to SignTemplateDetailSpecific UI which displays the details of the selected template (including their signs).
Search template by description
Filter by Department
## SignTemplateDetailSpecific UI: 
Display: List details of signs of template.
CRUD for signs of specific this template.


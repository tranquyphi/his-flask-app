-- examdb.BodyPart definition

CREATE TABLE `BodyPart` (
  `BodyPartId` smallint(5) unsigned NOT NULL,
  `BodyPartName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`BodyPartId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- examdb.BodySite definition

CREATE TABLE `BodySite` (
  `SiteId` int(5) NOT NULL AUTO_INCREMENT,
  `SiteName` varchar(100) NOT NULL,
  `BodyPartId` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`SiteId`),
  KEY `BodySite_BodyPart_FK` (`BodyPartId`),
  CONSTRAINT `BodySite_BodyPart_FK` FOREIGN KEY (`BodyPartId`) REFERENCES `BodyPart` (`BodyPartId`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
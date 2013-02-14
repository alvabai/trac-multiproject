-- MySQL dump 10.13  Distrib 5.1.41, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: home
-- ------------------------------------------------------
-- Server version	5.1.41-3ubuntu12.10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `home`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `home` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;

USE `home`;

--
-- Table structure for table `attachment`
--

DROP TABLE IF EXISTS `attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attachment` (
  `type` text COLLATE utf8_bin NOT NULL,
  `id` text COLLATE utf8_bin NOT NULL,
  `filename` text COLLATE utf8_bin NOT NULL,
  `size` int(11) DEFAULT NULL,
  `time` bigint(20) DEFAULT NULL,
  `description` text COLLATE utf8_bin,
  `author` text COLLATE utf8_bin,
  `ipnr` text COLLATE utf8_bin,
  PRIMARY KEY (`type`(111),`id`(111),`filename`(111))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachment`
--
-- ORDER BY:  `type`,`id`,`filename`

LOCK TABLES `attachment` WRITE;
/*!40000 ALTER TABLE `attachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_cookie`
--

DROP TABLE IF EXISTS `auth_cookie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_cookie` (
  `cookie` text COLLATE utf8_bin NOT NULL,
  `name` text COLLATE utf8_bin NOT NULL,
  `ipnr` text COLLATE utf8_bin NOT NULL,
  `time` int(11) DEFAULT NULL,
  PRIMARY KEY (`cookie`(111),`ipnr`(111),`name`(111))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_cookie`
--
-- ORDER BY:  `cookie`,`ipnr`,`name`

LOCK TABLES `auth_cookie` WRITE;
/*!40000 ALTER TABLE `auth_cookie` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_cookie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cache`
--

DROP TABLE IF EXISTS `cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cache` (
  `id` text COLLATE utf8_bin NOT NULL,
  `generation` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`(255))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cache`
--
-- ORDER BY:  `id`

LOCK TABLES `cache` WRITE;
/*!40000 ALTER TABLE `cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enum`
--

DROP TABLE IF EXISTS `enum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enum` (
  `type` text COLLATE utf8_bin NOT NULL,
  `name` text COLLATE utf8_bin NOT NULL,
  `value` text COLLATE utf8_bin,
  PRIMARY KEY (`type`(166),`name`(166))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enum`
--
-- ORDER BY:  `type`,`name`

LOCK TABLES `enum` WRITE;
/*!40000 ALTER TABLE `enum` DISABLE KEYS */;
INSERT INTO `enum` VALUES ('priority','blocker','1');
INSERT INTO `enum` VALUES ('priority','critical','2');
INSERT INTO `enum` VALUES ('priority','major','3');
INSERT INTO `enum` VALUES ('priority','minor','4');
INSERT INTO `enum` VALUES ('priority','trivial','5');
INSERT INTO `enum` VALUES ('resolution','duplicate','4');
INSERT INTO `enum` VALUES ('resolution','fixed','1');
INSERT INTO `enum` VALUES ('resolution','invalid','2');
INSERT INTO `enum` VALUES ('resolution','wontfix','3');
INSERT INTO `enum` VALUES ('resolution','worksforme','5');
INSERT INTO `enum` VALUES ('ticket_type','defect','1');
INSERT INTO `enum` VALUES ('ticket_type','enhancement','2');
INSERT INTO `enum` VALUES ('ticket_type','task','3');
/*!40000 ALTER TABLE `enum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `milestone`
--

DROP TABLE IF EXISTS `milestone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `milestone` (
  `name` text COLLATE utf8_bin NOT NULL,
  `due` bigint(20) DEFAULT NULL,
  `completed` bigint(20) DEFAULT NULL,
  `description` text COLLATE utf8_bin,
  PRIMARY KEY (`name`(255))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `milestone`
--
-- ORDER BY:  `name`

LOCK TABLES `milestone` WRITE;
/*!40000 ALTER TABLE `milestone` DISABLE KEYS */;
/*!40000 ALTER TABLE `milestone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `node_change`
--

DROP TABLE IF EXISTS `node_change`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `node_change` (
  `repos` int(11) NOT NULL DEFAULT '0',
  `rev` text COLLATE utf8_bin NOT NULL,
  `path` text COLLATE utf8_bin NOT NULL,
  `node_type` text COLLATE utf8_bin,
  `change_type` text COLLATE utf8_bin NOT NULL,
  `base_path` text COLLATE utf8_bin,
  `base_rev` text COLLATE utf8_bin,
  PRIMARY KEY (`repos`,`rev`(20),`path`(255),`change_type`(2)),
  KEY `node_change_repos_rev_idx` (`repos`,`rev`(20))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `node_change`
--
-- ORDER BY:  `repos`,`rev`,`path`,`change_type`

LOCK TABLES `node_change` WRITE;
/*!40000 ALTER TABLE `node_change` DISABLE KEYS */;
/*!40000 ALTER TABLE `node_change` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission`
--

DROP TABLE IF EXISTS `permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission` (
  `username` text COLLATE utf8_bin NOT NULL,
  `action` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`username`(166),`action`(166))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission`
--
-- ORDER BY:  `username`,`action`

LOCK TABLES `permission` WRITE;
/*!40000 ALTER TABLE `permission` DISABLE KEYS */;
INSERT INTO `permission` VALUES ('anonymous','BROWSER_VIEW');
INSERT INTO `permission` VALUES ('anonymous','CHANGESET_VIEW');
INSERT INTO `permission` VALUES ('anonymous','FILE_VIEW');
INSERT INTO `permission` VALUES ('anonymous','LOG_VIEW');
INSERT INTO `permission` VALUES ('anonymous','MILESTONE_VIEW');
INSERT INTO `permission` VALUES ('anonymous','REPORT_SQL_VIEW');
INSERT INTO `permission` VALUES ('anonymous','REPORT_VIEW');
INSERT INTO `permission` VALUES ('anonymous','ROADMAP_VIEW');
INSERT INTO `permission` VALUES ('anonymous','SEARCH_VIEW');
INSERT INTO `permission` VALUES ('anonymous','TICKET_VIEW');
INSERT INTO `permission` VALUES ('anonymous','TIMELINE_VIEW');
INSERT INTO `permission` VALUES ('anonymous','WELCOME_VIEW');
INSERT INTO `permission` VALUES ('anonymous','WIKI_VIEW');
INSERT INTO `permission` VALUES ('authenticated','TICKET_CREATE');
INSERT INTO `permission` VALUES ('authenticated','TICKET_MODIFY');
INSERT INTO `permission` VALUES ('authenticated','WIKI_CREATE');
INSERT INTO `permission` VALUES ('authenticated','WIKI_MODIFY');
INSERT INTO `permission` VALUES ('tracadmin','WELCOME_VIEW');
/*!40000 ALTER TABLE `permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `report` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `author` text COLLATE utf8_bin,
  `title` text COLLATE utf8_bin,
  `query` text COLLATE utf8_bin,
  `description` text COLLATE utf8_bin,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report`
--
-- ORDER BY:  `id`

LOCK TABLES `report` WRITE;
/*!40000 ALTER TABLE `report` DISABLE KEYS */;
INSERT INTO `report` VALUES (1,NULL,'Active Tickets','\nSELECT p.value AS __color__,\n   id AS ticket, summary, component, version, milestone, t.type AS type, \n   owner, status,\n   time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status <> \'closed\'\n  ORDER BY CAST(p.value AS signed), milestone, t.type, time\n','\n * List all active tickets by priority.\n * Color each row based on priority.\n');
INSERT INTO `report` VALUES (2,NULL,'Active Tickets by Version','\nSELECT p.value AS __color__,\n   version AS __group__,\n   id AS ticket, summary, component, version, t.type AS type, \n   owner, status,\n   time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status <> \'closed\'\n  ORDER BY (version IS NULL),version, CAST(p.value AS signed), t.type, time\n','\nThis report shows how to color results by priority,\nwhile grouping results by version.\n\nLast modification time, description and reporter are included as hidden fields\nfor useful RSS export.\n');
INSERT INTO `report` VALUES (3,NULL,'Active Tickets by Milestone','\nSELECT p.value AS __color__,\n   concat(\'Milestone \', milestone) AS __group__,\n   id AS ticket, summary, component, version, t.type AS type, \n   owner, status,\n   time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status <> \'closed\' \n  ORDER BY (milestone IS NULL),milestone, CAST(p.value AS signed), t.type, time\n','\nThis report shows how to color results by priority,\nwhile grouping results by milestone.\n\nLast modification time, description and reporter are included as hidden fields\nfor useful RSS export.\n');
INSERT INTO `report` VALUES (4,NULL,'Accepted, Active Tickets by Owner','\n\nSELECT p.value AS __color__,\n   owner AS __group__,\n   id AS ticket, summary, component, milestone, t.type AS type, time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status = \'accepted\'\n  ORDER BY owner, CAST(p.value AS signed), t.type, time\n','\nList accepted tickets, group by ticket owner, sorted by priority.\n');
INSERT INTO `report` VALUES (5,NULL,'Accepted, Active Tickets by Owner (Full Description)','\nSELECT p.value AS __color__,\n   owner AS __group__,\n   id AS ticket, summary, component, milestone, t.type AS type, time AS created,\n   description AS _description_,\n   changetime AS _changetime, reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status = \'accepted\'\n  ORDER BY owner, CAST(p.value AS signed), t.type, time\n','\nList tickets accepted, group by ticket owner.\nThis report demonstrates the use of full-row display.\n');
INSERT INTO `report` VALUES (6,NULL,'All Tickets By Milestone  (Including closed)','\nSELECT p.value AS __color__,\n   t.milestone AS __group__,\n   (CASE status \n      WHEN \'closed\' THEN \'color: #777; background: #ddd; border-color: #ccc;\'\n      ELSE \n        (CASE owner WHEN $USER THEN \'font-weight: bold\' END)\n    END) AS __style__,\n   id AS ticket, summary, component, status, \n   resolution,version, t.type AS type, priority, owner,\n   changetime AS modified,\n   time AS _time,reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  ORDER BY (milestone IS NULL), milestone DESC, (status = \'closed\'), \n        (CASE status WHEN \'closed\' THEN changetime ELSE (-1) * CAST(p.value AS signed) END) DESC\n','\nA more complex example to show how to make advanced reports.\n');
INSERT INTO `report` VALUES (7,NULL,'My Tickets','\nSELECT p.value AS __color__,\n   (CASE status WHEN \'accepted\' THEN \'Accepted\' ELSE \'Owned\' END) AS __group__,\n   id AS ticket, summary, component, version, milestone,\n   t.type AS type, priority, time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE t.status <> \'closed\' AND owner = $USER\n  ORDER BY (status = \'accepted\') DESC, CAST(p.value AS signed), milestone, t.type, time\n','\nThis report demonstrates the use of the automatically set \nUSER dynamic variable, replaced with the username of the\nlogged in user when executed.\n');
INSERT INTO `report` VALUES (8,NULL,'Active Tickets, Mine first','\nSELECT p.value AS __color__,\n   (CASE owner \n     WHEN $USER THEN \'My Tickets\' \n     ELSE \'Active Tickets\' \n    END) AS __group__,\n   id AS ticket, summary, component, version, milestone, t.type AS type, \n   owner, status,\n   time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter\n  FROM ticket t\n  LEFT JOIN enum p ON p.name = t.priority AND p.type = \'priority\'\n  WHERE status <> \'closed\' \n  ORDER BY (COALESCE(owner, \'\') = $USER) DESC, CAST(p.value AS signed), milestone, t.type, time\n','\n * List all active tickets by priority.\n * Show all tickets owned by the logged in user in a group first.\n');
/*!40000 ALTER TABLE `report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repository`
--

DROP TABLE IF EXISTS `repository`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repository` (
  `id` int(11) NOT NULL DEFAULT '0',
  `name` text COLLATE utf8_bin NOT NULL,
  `value` text COLLATE utf8_bin,
  PRIMARY KEY (`id`,`name`(166))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repository`
--
-- ORDER BY:  `id`,`name`

LOCK TABLES `repository` WRITE;
/*!40000 ALTER TABLE `repository` DISABLE KEYS */;
/*!40000 ALTER TABLE `repository` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `revision`
--

DROP TABLE IF EXISTS `revision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revision` (
  `repos` int(11) NOT NULL DEFAULT '0',
  `rev` text COLLATE utf8_bin NOT NULL,
  `time` bigint(20) DEFAULT NULL,
  `author` text COLLATE utf8_bin,
  `message` text COLLATE utf8_bin,
  PRIMARY KEY (`repos`,`rev`(20)),
  KEY `revision_repos_time_idx` (`repos`,`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `revision`
--
-- ORDER BY:  `repos`,`rev`

LOCK TABLES `revision` WRITE;
/*!40000 ALTER TABLE `revision` DISABLE KEYS */;
/*!40000 ALTER TABLE `revision` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session` (
  `sid` text COLLATE utf8_bin NOT NULL,
  `authenticated` int(11) NOT NULL DEFAULT '0',
  `last_visit` int(11) DEFAULT NULL,
  PRIMARY KEY (`sid`(166),`authenticated`),
  KEY `session_last_visit_idx` (`last_visit`),
  KEY `session_authenticated_idx` (`authenticated`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session`
--
-- ORDER BY:  `sid`,`authenticated`

LOCK TABLES `session` WRITE;
/*!40000 ALTER TABLE `session` DISABLE KEYS */;
/*!40000 ALTER TABLE `session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_attribute`
--

DROP TABLE IF EXISTS `session_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_attribute` (
  `sid` text COLLATE utf8_bin NOT NULL,
  `authenticated` int(11) NOT NULL DEFAULT '0',
  `name` text COLLATE utf8_bin NOT NULL,
  `value` text COLLATE utf8_bin,
  PRIMARY KEY (`sid`(111),`authenticated`,`name`(111))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_attribute`
--
-- ORDER BY:  `sid`,`authenticated`,`name`

LOCK TABLES `session_attribute` WRITE;
/*!40000 ALTER TABLE `session_attribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system`
--

DROP TABLE IF EXISTS `system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `system` (
  `name` text COLLATE utf8_bin NOT NULL,
  `value` text COLLATE utf8_bin,
  PRIMARY KEY (`name`(255))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system`
--
-- ORDER BY:  `name`

LOCK TABLES `system` WRITE;
/*!40000 ALTER TABLE `system` DISABLE KEYS */;
INSERT INTO `system` VALUES ('database_version','26');
INSERT INTO `system` VALUES ('initial_database_version','26');
/*!40000 ALTER TABLE `system` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ticket` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` text COLLATE utf8_bin,
  `time` bigint(20) DEFAULT NULL,
  `changetime` bigint(20) DEFAULT NULL,
  `component` text COLLATE utf8_bin,
  `severity` text COLLATE utf8_bin,
  `priority` text COLLATE utf8_bin,
  `owner` text COLLATE utf8_bin,
  `reporter` text COLLATE utf8_bin,
  `cc` text COLLATE utf8_bin,
  `version` text COLLATE utf8_bin,
  `milestone` text COLLATE utf8_bin,
  `status` text COLLATE utf8_bin,
  `resolution` text COLLATE utf8_bin,
  `summary` text COLLATE utf8_bin,
  `description` text COLLATE utf8_bin,
  `keywords` text COLLATE utf8_bin,
  PRIMARY KEY (`id`),
  KEY `ticket_time_idx` (`time`),
  KEY `ticket_status_idx` (`status`(255))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--
-- ORDER BY:  `id`

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket_change`
--

DROP TABLE IF EXISTS `ticket_change`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ticket_change` (
  `ticket` int(11) NOT NULL DEFAULT '0',
  `time` bigint(20) NOT NULL DEFAULT '0',
  `author` text COLLATE utf8_bin,
  `field` text COLLATE utf8_bin NOT NULL,
  `oldvalue` text COLLATE utf8_bin,
  `newvalue` text COLLATE utf8_bin,
  PRIMARY KEY (`ticket`,`time`,`field`(111)),
  KEY `ticket_change_ticket_idx` (`ticket`),
  KEY `ticket_change_time_idx` (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket_change`
--
-- ORDER BY:  `ticket`,`time`,`field`

LOCK TABLES `ticket_change` WRITE;
/*!40000 ALTER TABLE `ticket_change` DISABLE KEYS */;
/*!40000 ALTER TABLE `ticket_change` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket_custom`
--

DROP TABLE IF EXISTS `ticket_custom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ticket_custom` (
  `ticket` int(11) NOT NULL DEFAULT '0',
  `name` text COLLATE utf8_bin NOT NULL,
  `value` text COLLATE utf8_bin,
  PRIMARY KEY (`ticket`,`name`(166))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket_custom`
--
-- ORDER BY:  `ticket`,`name`

LOCK TABLES `ticket_custom` WRITE;
/*!40000 ALTER TABLE `ticket_custom` DISABLE KEYS */;
/*!40000 ALTER TABLE `ticket_custom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `version` (
  `name` text COLLATE utf8_bin NOT NULL,
  `time` bigint(20) DEFAULT NULL,
  `description` text COLLATE utf8_bin,
  PRIMARY KEY (`name`(255))
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `version`
--
-- ORDER BY:  `name`

LOCK TABLES `version` WRITE;
/*!40000 ALTER TABLE `version` DISABLE KEYS */;
INSERT INTO `version` VALUES ('1.0',0,NULL);
INSERT INTO `version` VALUES ('2.0',0,NULL);
/*!40000 ALTER TABLE `version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wiki`
--

DROP TABLE IF EXISTS `wiki`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wiki` (
  `name` text COLLATE utf8_bin NOT NULL,
  `version` int(11) NOT NULL DEFAULT '0',
  `time` bigint(20) DEFAULT NULL,
  `author` text COLLATE utf8_bin,
  `ipnr` text COLLATE utf8_bin,
  `text` text COLLATE utf8_bin,
  `comment` text COLLATE utf8_bin,
  `readonly` int(11) DEFAULT NULL,
  PRIMARY KEY (`name`(166),`version`),
  KEY `wiki_time_idx` (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wiki`
--
-- ORDER BY:  `name`,`version`

LOCK TABLES `wiki` WRITE;
/*!40000 ALTER TABLE `wiki` DISABLE KEYS */;
INSERT INTO `wiki` VALUES ('CamelCase',1,1327389819647871,'trac','127.0.0.1','= !CamelCase =\nNew words created by smashing together capitalized words.\n\nCamelCase is the original wiki convention for creating hyperlinks, with the additional requirement that the capitals are followed by a lower-case letter; hence â€œAlabamAâ€ and â€œABcâ€ will not be links.\n\n== Customizing the Wiki behavior ==\n\nSome people dislike linking by CamelCase.  While Trac remains faithful to the original Wiki style, it provides a number of ways to accomodate users with different preferences:\n * There\'s an option (`ignore_missing_pages` in the [wiki:TracIni#wiki-section \"[wiki]\"] section of TracIni) to simply ignore links to missing pages when the link is written using the CamelCase style, instead of that word being replaced by a gray link followed by a question mark.[[BR]]\n   That can be useful when CamelCase style is used to name code artifacts like class names and there\'s no corresponding page for them.\n * There\'s an option (`split_page_names` in the  [wiki:TracIni#wiki-section \"[wiki]\"] section of TracIni) to automatically insert space characters between the words of a CamelCase link when rendering the link.\n * Creation of explicit Wiki links is also easy, see WikiPageNames for details.\n * In addition, Wiki formatting can be disabled completely in some places (e.g. when rendering commit log messages). See `wiki_format_messages` in the [wiki:TracIni#changeset-section \"[changeset]\"] section of TracIni.\n\nSee TracIni for more information on the available options.\n\n== More information on !CamelCase ==\n\n * http://c2.com/cgi/wiki?WikiCase\n * http://en.wikipedia.org/wiki/CamelCase\n\n----\nSee also: WikiPageNames, WikiNewPage, WikiFormatting, TracWiki',NULL,NULL);
INSERT INTO `wiki` VALUES ('InterMapTxt',1,1327389819647871,'trac','127.0.0.1','= InterMapTxt =\n\n== This is the place for defining InterWiki prefixes ==\n\nThis page was modelled after the MeatBall:InterMapTxt page.\nIn addition, an optional comment is allowed after the mapping.\n\n\nThis page is interpreted in a special way by Trac, in order to support\n!InterWiki links in a flexible and dynamic way.\n\nThe code block after the first line separator in this page\nwill be interpreted as a list of !InterWiki specifications:\n{{{\nprefix <space> URL [<space> # comment]\n}}}\n\nBy using `$1`, `$2`, etc. within the URL, it is possible to create \nInterWiki links which support multiple arguments, e.g. Trac:ticket:40.\nThe URL itself can be optionally followed by a comment, \nwhich will subsequently be used for decorating the links \nusing that prefix.\n\nNew !InterWiki links can be created by adding to that list, in real time.\nNote however that \'\'deletions\'\' are also taken into account immediately,\nso it may be better to use comments for disabling prefixes.\n\nAlso note that !InterWiki prefixes are case insensitive.\n\n\n== List of Active Prefixes ==\n\n[[InterWiki]]\n\n\n----\n\n== Prefix Definitions ==\n\n{{{\nPEP     http://www.python.org/peps/pep-$1.html    # Python Enhancement Proposal \nPythonBug    http://bugs.python.org/issue$1       # Python Issue #$1\nPython-issue http://bugs.python.org/issue$1       # Python Issue #$1\n\nTrac-ML  http://thread.gmane.org/gmane.comp.version-control.subversion.trac.general/ # Message $1 in Trac Mailing List\ntrac-dev http://thread.gmane.org/gmane.comp.version-control.subversion.trac.devel/   # Message $1 in Trac Development Mailing List\n\nMercurial http://www.selenic.com/mercurial/wiki/index.cgi/ # the wiki for the Mercurial distributed SCM\n\nRFC       http://tools.ietf.org/html/rfc$1          # IETF\'s RFC $1\nISO       http://en.wikipedia.org/wiki/ISO_         # ISO Standard $1 in Wikipedia\nkb        http://support.microsoft.com/kb/$1/en-us/ # Article $1 in Microsoft\'s Knowledge Base\n\nchromium-issue  http://code.google.com/p/chromium/issues/detail?id=\n\nDjango      http://code.djangoproject.com/intertrac/ # Django\'s Trac\n\nCreoleWiki   http://wikicreole.org/wiki/\nCreole1Wiki  http://wikicreole.org/wiki/\nCreole2Wiki  http://wiki.wikicreole.org/\n\nMediaWiki    http://www.mediawiki.org/wiki/\n\n#\n# A arbitrary pick of InterWiki prefixes...\n#\nAcronym          http://www.acronymfinder.com/af-query.asp?String=exact&Acronym=\nC2find           http://c2.com/cgi/wiki?FindPage&value=\nCache            http://www.google.com/search?q=cache:\nCPAN             http://search.cpan.org/perldoc?\nDebianBug        http://bugs.debian.org/\nDebianPackage    http://packages.debian.org/\nDictionary       http://www.dict.org/bin/Dict?Database=*&Form=Dict1&Strategy=*&Query=\nGoogle           http://www.google.com/search?q=\nGoogleGroups     http://groups.google.com/group/$1/msg/$2        # Message $2 in $1 Google Group\nJargonFile       http://downlode.org/perl/jargon-redirect.cgi?term=\nMeatBall         http://www.usemod.com/cgi-bin/mb.pl?\nMetaWiki         http://sunir.org/apps/meta.pl?\nMetaWikiPedia    http://meta.wikipedia.org/wiki/\nMoinMoin         http://moinmo.in/\nWhoIs            http://www.whois.sc/\nWhy              http://clublet.com/c/c/why?\nc2Wiki           http://c2.com/cgi/wiki?\nWikiPedia        http://en.wikipedia.org/wiki/\n}}}\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('InterTrac',1,1327389819647871,'trac','127.0.0.1','= InterTrac Links  =\n\nTrac supports a convenient way to refer to resources of other Trac servers, from within the Wiki markup, since version 0.10.\n\n== Definitions ==\n\nAn InterTrac link can be seen as a scoped TracLinks.\nIt is used for referring to a Trac resource \n(Wiki page, changeset, ticket, ...) located in another\nTrac environment.\n\n== List of Active InterTrac Prefixes ==\n\n[[InterTrac]]\n\n== Link Syntax ==\n\nSimply use the name of the other Trac environment as a prefix, \nfollowed by a colon, ending with the resource located in the other environment.\n\n{{{\n<target_environment>:<TracLinks>\n}}}\n\nThe other resource is specified using a regular TracLinks, of any flavor.\n\nThat target environment name is either the real name of the \nenvironment, or an alias for it. \nThe aliases are defined in `trac.ini` (see below).\nThe prefix is case insensitive.\n\nIf the InterTrac link is enclosed in square brackets (like `[th:WikiGoodiesPlugin]`), the InterTrac prefix is removed in the displayed link, like a normal link resolver would be (i.e. the above would be displayed as `WikiGoodiesPlugin`).\n\nFor convenience, there\'s also some alternative short-hand form, \nwhere one can use an alias as an immediate prefix \nfor the identifier of a ticket, changeset or report:\n(e.g. `#T234`, `[T1508]`, `[trac 1508]`, ...)\n\n== Examples ==\n\nIt is necessary to setup a configuration for the InterTrac facility.\nThis configuration has to be done in the TracIni file, `[intertrac]` section.\n\nExample configuration:\n{{{\n...\n[intertrac]\n# -- Example of setting up an alias:\nt = trac\n\n# -- Link to an external Trac:\ntrac.title = Edgewall\'s Trac for Trac\ntrac.url = http://trac.edgewall.org\n}}}\n\nThe `.url` is mandatory and is used for locating the other Trac.\nThis can be a relative URL in case that Trac environment is located \non the same server.\n\nThe `.title` information will be used for providing an useful tooltip\nwhen moving the cursor over an InterTrac links.\n\nFinally, the `.compat` option can be used to activate or disable\na \'\'compatibility\'\' mode:\n * If the targeted Trac is running a version below [trac:milestone:0.10 0.10] \n   ([trac:r3526 r3526] to be precise), then it doesn\'t know how to dispatch an InterTrac \n   link, and it\'s up to the local Trac to prepare the correct link. \n   Not all links will work that way, but the most common do. \n   This is called the compatibility mode, and is `true` by default. \n * If you know that the remote Trac knows how to dispatch InterTrac links, \n   you can explicitly disable this compatibility mode and then \'\'any\'\' \n   TracLinks can become an InterTrac link.\n\nNow, given the above configuration, one could create the following links:\n * to this InterTrac page:\n   * `trac:wiki:InterTrac` trac:wiki:InterTrac\n   * `t:wiki:InterTrac` t:wiki:InterTrac\n   * Keys are case insensitive: `T:wiki:InterTrac` T:wiki:InterTrac\n * to the ticket #234:\n   * `trac:ticket:234` trac:ticket:234\n   * `trac:#234` trac:#234 \n   * `#T234` #T234\n * to the changeset [1912]:\n   * `trac:changeset:1912` trac:changeset:1912\n   * `[T1912]` [T1912]\n * to the log range [3300:3330]: \'\'\'(Note: the following ones need `trac.compat=false`)\'\'\'\n   * `trac:log:@3300:3330` trac:log:@3300:3330  \n   * `[trac 3300:3330]` [trac 3300:3330] \n * finally, to link to the start page of a remote trac, simply use its prefix followed by \':\', inside an explicit link. Example: `[th: Trac Hacks]` (\'\'since 0.11; note that the \'\'remote\'\' Trac has to run 0.11 for this to work\'\')\n\nThe generic form `intertrac_prefix:module:id` is translated\nto the corresponding URL `<remote>/module/id`, shorthand links\nare specific to some modules (e.g. !#T234 is processed by the\nticket module) and for the rest (`intertrac_prefix:something`),\nwe rely on the TracSearch#quickjump facility of the remote Trac.\n\n----\nSee also: TracLinks, InterWiki\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('InterWiki',1,1327389819647871,'trac','127.0.0.1','= Support for InterWiki links =\n\n\'\'(since [trac:milestone:0.10 0.10])\'\'\n\n== Definition ==\n\nAn InterWiki link can be used for referring to a Wiki page\nlocated in another Wiki system, and by extension, to any object\nlocated in any other Web application, provided a simple URL \nmapping can be done.\n\nAt the extreme, InterWiki prefixes can even be used to simply introduce\nlinks to new protocols, such as `tsvn:` used by [trac:TortoiseSvn TortoiseSvn].\n\n== Link Syntax ==\n\n{{{\n<target_wiki>(:<identifier>)+\n}}}\n\nThe link is composed by the targeted Wiki (or system) name,\nfollowed by a colon (e.g. `MeatBall:`),\nfollowed by a page specification in the target.\nNote that, as for InterTrac prefixes, \'\'\'InterWiki prefixes are case insensitive\'\'\'.\n\nThe target Wiki URL is looked up in the InterMapTxt wiki page, \nmodelled after MeatBall:InterMapTxt.\n\nIn addition to traditional InterWiki links, where the target\nis simply \'\'appended\'\' to the URL, \nTrac supports parametric InterWiki URLs:\nidentifiers `$1`, `$2`, ... in the URL\nwill be replaced by corresponding arguments.\nThe argument list is formed by splitting the page identifier\nusing the \":\" separator.\n\n== Examples ==\n\nIf the following is an excerpt of the InterMapTxt page:\n\n{{{\n= InterMapTxt =\n== This is the place for defining InterWiki prefixes ==\n\nCurrently active prefixes: [[InterWiki]]\n\nThis page is modelled after the MeatBall:InterMapTxt page.\nIn addition, an optional comment is allowed after the mapping.\n----\n{{{\nPEP      http://www.python.org/peps/pep-$1.html           # Python Enhancement Proposal $1 \nTrac-ML  http://thread.gmane.org/gmane.comp.version-control.subversion.trac.general/$1  # Message $1 in Trac Mailing List\n\ntsvn     tsvn:                                            # Interact with TortoiseSvn\n...\nMeatBall http://www.usemod.com/cgi-bin/mb.pl?\nMetaWiki http://sunir.org/apps/meta.pl?\nMetaWikiPedia http://meta.wikipedia.org/wiki/\nMoinMoin http://moinmoin.wikiwikiweb.de/\n...\n}}}\n}}}\n\nThen, \n * `MoinMoin:InterWikiMap` should be rendered as MoinMoin:InterWikiMap\n   and the \'\'title\'\' for that link would be \"!InterWikiMap in !MoinMoin\"\n * `Trac-ML:4346` should be rendered as Trac-ML:4346\n   and the \'\'title\'\' for that link would be \"Message 4346 in Trac Mailing List\"\n\n----\nSee also: InterTrac, InterMapTxt',NULL,NULL);
INSERT INTO `wiki` VALUES ('PageTemplates',1,1327389819647871,'trac','127.0.0.1','= Wiki Page Templates = \n\n  \'\'(since [http://trac.edgewall.org/milestone/0.11 0.11])\'\'\n\nThe default content for a new wiki page can be chosen from a list of page templates. \n\nThat list is made up from all the existing wiki pages having a name starting with \'\'PageTemplates/\'\'.\nThe initial content of a new page will simply be the content of the chosen template page, or a blank page if the special \'\'(blank page)\'\' entry is selected. When there\'s actually no wiki pages matching that prefix, the initial content will always be the blank page and the list selector will not be shown (i.e. this matches the behavior we had up to now).\n\nTo create a new template, simply create a new page having a name starting with \'\'PageTemplates/\'\'.\n\n(Hint: one could even create a \'\'!PageTemplates/Template\'\' for facilitating the creation of new templates!)\n\nAfter you have created your new template, a drop-down selection box will automatically appear on any new wiki pages that are created.  By default it is located on the right side of the \'Create this page\' button.\n\nAvailable templates: \n[[TitleIndex(PageTemplates/)]]\n----\nSee also: TracWiki',NULL,NULL);
INSERT INTO `wiki` VALUES ('RecentChanges',1,1327389819647871,'trac','127.0.0.1','\'\'\' [TitleIndex Index by Title] \'\'\' | \'\'\' Index by Date \'\'\'\n\n[[RecentChanges]]',NULL,NULL);
INSERT INTO `wiki` VALUES ('SandBox',1,1327389819647871,'trac','127.0.0.1','= The Sandbox =\n\nThis is just a page to practice and learn WikiFormatting. \n\nGo ahead, edit it freely.',NULL,NULL);
INSERT INTO `wiki` VALUES ('TitleIndex',1,1327389819647871,'trac','127.0.0.1','\'\'\' Index by Title \'\'\' | \'\'\' [RecentChanges Index by Date] \'\'\'\n\n[[TitleIndex(format=group,min=4)]]',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracAccessibility',1,1327389819647871,'trac','127.0.0.1','= Accessibility Support in Trac =\n\nNot every user has a graphic environment with a mouse or other pointing device. Some users rely on keyboard, alternative keyboard or voice input to navigate links, activate form controls, etc. In Trac, we work to assure users may interact with devices other than a pointing device.\n\nTrac supports accessibility keys for the most common operations. On Windows and Linux platforms, press any of the keys listed below in combination with the `<Alt>` key; on a Mac, use the `<ctrl>` key instead.\n\n\'\'Note that when using Internet Explorer on Windows, you need to hit `<Enter>` after having used the access key.\'\'[[BR]]\n\'\'Note that when using Firefox 2.0 on Windows, you need to hit `<Shift> + <Alt> + <Key>`.\'\'\n\n== Global Access Keys ==\n\n * `1` - WikiStart\n * `2` - [wiki:TracTimeline Timeline]\n * `3` - [wiki:TracRoadmap Roadmap]\n * `4` - [wiki:TracSearch Search]\n * `6` - [wiki:TracGuide Trac Guide / Documentation]\n * `7` - [wiki:TracTickets New Ticket]\n * `9` - [/about About Trac]\n * `0` - This page\n * `e` - Edit this page\n * `f` - Search\n\n\n----\nSee also: TracGuide',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracAdmin',1,1327389819647871,'trac','127.0.0.1','= TracAdmin =\n[[TracGuideToc]]\n\nTrac is distributed with a powerful command-line configuration tool. This tool can be used  to configure and customize your Trac-installation to better fit your needs.\n\nSome of those operations can also be performed via the \'\'Admin\'\' web interface, an updated version of the [trac:WebAdmin] plugin now integrated within Trac (since version 0.11).\n\n== Usage ==\n\nFor nearly every `trac-admin` command, you\'ll need to specify the path to the TracEnvironment that you want to administer as the first argument, for example:\n{{{\ntrac-admin /path/to/projenv wiki list\n}}}\n\nThe only exception is for the `help` command, but even in this case if you omit the environment, you\'ll only get a very succinct list of commands (`help` and `initenv`), the same list you\'d get when invoking `trac-admin` alone.\nAlso, `trac-admin --version` will tell you about the Trac version (e.g. 0.12) corresponding to the program.\n\nIf you want to get a comprehensive list of the available commands and sub-commands, you need to specify an existing environment:\n{{{\ntrac-admin /path/to/projenv help\n}}}\n\nSome commands have a more detailed help, which you can access by specifying the command\'s name as a subcommand for `help`:\n\n{{{\ntrac-admin /path/to/projenv help <command>\n}}}\n\n=== `trac-admin <targetdir> initenv` === #initenv\n\nThis subcommand is very important as it\'s the one used to create a TracEnvironment in the specified `<targetdir>`. That directory must not exists prior to the call.\n\n[[TracAdminHelp(initenv)]]\n\nIt supports an extra `--inherit` option, which can be used to specify a global configuration file which can be used share settings between several environments. You can also inherit from a shared configuration afterwards, by setting the `[inherit] file` option in the `conf/trac.ini` file in your newly created environment, but the advantage of specifying the inherited configuration file at environment creation time is that only the options \'\'not\'\' already specified in the global configuration file will be written in the created environment\'s `conf/trac.ini` file.\nSee TracIni#GlobalConfiguration.\n\nNote that in version 0.11 of Trac, `initenv` lost an extra last argument `<templatepath>`, which was used in previous versions to point to the `templates` folder. If you are using the one-liner \'`trac-admin /path/to/trac/ initenv <projectname> <db> <repostype> <repospath>`\' in the above and getting an error that reads \'\'\'\'`Wrong number of arguments to initenv: 4`\'\'\'\', then this is because you\'re using a `trac-admin` script from an \'\'\'older\'\'\' version of Trac.\n\n== Interactive Mode ==\n\nWhen passing the environment path as the only argument, `trac-admin` starts in interactive mode.\nCommands can then be executed on the selected environment using the prompt, which offers tab-completion\n(on non-Windows environments, and when the Python `readline` module is available) and automatic repetition of the last command issued.\n\nOnce you\'re in interactive mode, you can also get help on specific commands or subsets of commands:\n\nFor example, to get an explanation of the `resync` command, run:\n{{{\n> help resync\n}}}\n\nTo get help on all the Wiki-related commands, run:\n{{{\n> help wiki\n}}}\n\n== Full Command Reference ==\n\nYou\'ll find below the detailed help for all the commands available by default in `trac-admin`. Note that this may not match the list given by `trac-admin <yourenv> help`, as the commands  pertaining to components disabled in that environment won\'t be available and conversely some plugins activated in the environment can add their own commands.\n\n[[TracAdminHelp()]]\n\n----\nSee also: TracGuide, TracBackup, TracPermissions, TracEnvironment, TracIni, [trac:TracMigrate TracMigrate]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracBackup',1,1327389819647871,'trac','127.0.0.1','= Trac Backup =\n[[TracGuideToc]]\n\nSince Trac uses a database backend, some extra care is required to safely create a backup of a [wiki:TracEnvironment project environment]. Luckily, [wiki:TracAdmin trac-admin] has a command to make backups easier: `hotcopy`.\n\n  \'\'Note: Trac uses the `hotcopy` nomenclature to match that of [http://subversion.tigris.org/ Subversion], to make it easier to remember when managing both Trac and Subversion servers.\'\'\n\n== Creating a Backup ==\n\nTo create a backup of a live TracEnvironment, simply run:\n{{{\n\n  $ trac-admin /path/to/projenv hotcopy /path/to/backupdir\n\n}}}\n\n[wiki:TracAdmin trac-admin] will lock the database while copying.\'\'\n\nThe resulting backup directory is safe to handle using standard file-based backup tools like `tar` or `dump`/`restore`.\n\nPlease, note, that hotcopy command does not overwrite target directory and when such exists, hotcopy ends with error: `Command failed: [Errno 17] File exists:` This is discussed in [trac:ticket:3198 #3198].\n\n=== Restoring a Backup ===\n\nBackups are simply a copied snapshot of the entire [wiki:TracEnvironment project environment] directory, including the SQLite database. \n\nTo restore an environment from a backup, stop the process running Trac (i.e. the Web server or [wiki:TracStandalone tracd]), restore the contents of your backup (path/to/backupdir) to your [wiki:TracEnvironment project environment] directory and restart the service.\n\n  \'\'Note: Automatic backup of environments that don\'t use SQLite as database backend is not supported at this time. As a workaround, we recommend that you stop the server, copy the environment directory, and make a backup of the database using whatever mechanism is provided by the database system.\'\'\n\n----\nSee also: TracAdmin, TracEnvironment, TracGuide, [trac:TracMigrate TracMigrate]',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracBrowser',1,1327389819647871,'trac','127.0.0.1','= The Trac Repository Browser =\n[[TracGuideToc]]\n\nThe Trac repository browser can be used to browse specific revisions of directories \nand files stored in the repositories associated with the Trac environment.\n\n\'\'(since 0.12)\'\': \nAt the top-level of the repository browser is the \'\'\'Repository Index\'\'\', \nlisting all the configured repositories. \nEach repository has a name which is used as a path prefix in a \n\"virtual\" file hierarchy encompassing all the available repositories.\nIf a default repository has been configured, its top-level files and directories \nare also listed, in a \'\'\'Default Repository\'\'\' section placed before the \nrepository index. If the default repository is the only repository associated \nwith the Trac environment the \'\'\'Repository Index\'\'\' will be omitted ^[#note-multirepos (1)]^.\n\nDirectory entries are displayed in a list with sortable columns. The list \nentries can be sorted by \'\'Name\'\', \'\'Size\'\', \'\'Age\'\' or \'\'Author\'\' by clicking on the column\nheaders. The sort order can be reversed by clicking on a given column\nheader again.\n\nThe browser can be used to navigate through the directory structure \nby clicking on the directory names. \nClicking on a file name will show the contents of the file. \nClicking on the revision number of a file or directory will take \nyou to the TracRevisionLog for that file.\nNote that there\'s also a \'\'Revision Log\'\' navigation link that will do the \nsame for the path currently being examined.\nClicking on the \'\'diff\'\' icon after revision number will display the changes made \nto the files modified in that revision.\nClicking on the \'\'Age\'\' of the file - will take you to that changeset in the timeline.\n\nIt\'s also possible to browse directories or files as they were in history,\nat any given repository revision. The default behavior is to display the\nlatest revision but another revision number can easily be selected using\nthe \'\'View revision\'\' input field at the top of the page.\n\nThe color bar next to the \'\'Age\'\' column gives a visual indication of the age\nof the last change to a file or directory, following the convention that\n\'\'\'[[span(style=color:#88f,blue)]]\'\'\' is oldest and \'\'\'[[span(style=color:#f88,red)]]\'\'\'\nis newest, but this can be [TracIni#browser-section configured].\n\nAt the top of the browser page, there\'s a \'\'Visit\'\' drop-down menu which you can use \nto select some interesting places in the repository, for example branches or tags. \nThis is sometimes referred to as the \'\'browser quickjump\'\' facility.\nThe precise meaning and content of this menu depends on your repository backend.\nFor Subversion, this list contains by default the top-level trunk directory \nand sub-directories of the top-level branches and tags directories \n(`/trunk`, `/branches/*`, and `/tags/*`).  This can be [TracIni#svn-section configured] \nfor more advanced cases.\n\nIf you\'re using a Javascript enabled browser, you\'ll be able to expand and \ncollapse directories in-place by clicking on the arrow head at the right side of a \ndirectory. Alternatively, the [trac:TracKeys keyboard] can also be used for this: \n - use `\'j\'` and `\'k\'` to select the next or previous entry, starting with the first\n - `\'o\'` (open) to toggle between expanded and collapsed state of the selected \n   directory or for visiting the selected file \n - `\'v\'` (view, visit) and `\'<Enter>\'`, same as above\n - `\'r\'` can be used to force the reload of an already expanded directory\n - `\'A\'` can be used to directly visit a file in annotate (blame) mode\n - `\'L\'` to view the log for the selected entry\nIf no row has been selected using `\'j\'` or `\'k\'` these keys will operate on the entry under the mouse .\n\n{{{#!comment\nMMM: I guess that some keys are upper case and some lower to avoid conflicts with browser defined keys.\nI find for example in Firefox and IE on windows that \'a\' works as well as \'A\' but \'l\' does not work for \'L\'.\n cboos: \'l\' is reserved for Vim like behavior, see #7867\n}}}\n\nFor the Subversion backend, some advanced additional features are available:\n - The `svn:needs-lock` property will be displayed\n - Support for the `svn:mergeinfo` property showing the merged and eligible information\n - Support for browsing the `svn:externals` property \n   (which can be [TracIni#svn:externals-section configured])\n - The `svn:mime-type` property is used to select the syntax highlighter for rendering \n   the file. For example, setting `svn:mime-type` to `text/html` will ensure the file is \n   highlighted as HTML, regardless of the file extension. It also allows selecting the character \n   encoding used in the file content. For example, if the file content is encoded in UTF-8, \n   set `svn:mime-type` to `text/html;charset=utf-8`. The `charset=` specification overrides the \n   default encoding defined in the `default_charset` option of the `[trac]` section \n   of [TracIni#trac-section trac.ini].\n{{{#!comment\nMMM: I found this section a bit hard to understand. I changed the first item as I understood that well.\nbut I think the other items could be changed also\n cboos: in the meantime, I\'ve added the \'\'advanced\'\' word as a hint this can be a bit complex...\n}}}\n\n\n----\n{{{#!div style=\"font-size:85%\"\n[=#note-multirepos (1)] -  This means that after upgrading a single-repository Trac of version \n0.11 (or below) to a multi-repository Trac (0.12), the repository browser will look and feel \nthe same, that single repository becoming automatically the \"default\" repository.\n}}}\n\nSee also: TracGuide, TracChangeset, TracFineGrainedPermissions\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracCgi',1,1327389819647871,'trac','127.0.0.1','= Installing Trac as CGI =\n\n{{{\n#!div class=important\n  \'\'Please note that using Trac via CGI is the slowest deployment method available. It is slower than [TracModPython mod_python], [TracFastCgi FastCGI] and even [trac:TracOnWindowsIisAjp IIS/AJP] on Windows.\'\'\n}}}\n\nCGI script is the entrypoint that web-server calls when a web-request to an application is made. To generate the `trac.cgi` script run:\n{{{\ntrac-admin /path/to/env deploy /path/to/www/trac\n}}}\n`trac.cgi` will be in the `cgi-bin` folder inside the given path. Make sure it is executable by your web server. This command also copies `static resource` files to a `htdocs` directory of a given destination.\n\n== Apache web-server configuration ==\n\nIn [http://httpd.apache.org/ Apache] there are two ways to run Trac as CGI:\n\n 1. Use a `ScriptAlias` directive that maps an URL to the `trac.cgi` script (recommended)\n 2. Copy the `trac.cgi` file into the directory for CGI executables used by your web server (commonly named `cgi-bin`). You can also create a symbolic link, but in that case make sure that the `FollowSymLinks` option is enabled for the `cgi-bin` directory.\n\nTo make Trac available at `http://yourhost.example.org/trac` add `ScriptAlias` directive to Apache configuration file, changing `trac.cgi` path to match your installation:\n{{{\nScriptAlias /trac /path/to/www/trac/cgi-bin/trac.cgi\n}}}\n\n \'\'Note that this directive requires enabled `mod_alias` module.\'\'\n\nIf you\'re using Trac with a single project you need to set its location using the `TRAC_ENV` environment variable:\n{{{\n<Location \"/trac\">\n  SetEnv TRAC_ENV \"/path/to/projectenv\"\n</Location>\n}}}\n\nOr to use multiple projects you can specify their common parent directory using the `TRAC_ENV_PARENT_DIR` variable:\n{{{\n<Location \"/trac\">\n  SetEnv TRAC_ENV_PARENT_DIR \"/path/to/project/parent/dir\"\n</Location>\n}}}\n\n \'\'Note that the `SetEnv` directive requires enabled `mod_env` module. It is also possible to set TRAC_ENV in trac.cgi. Just add the following code between \"try:\" and \"from trac.web ...\":\'\'\n\n{{{\n    import os\n    os.environ[\'TRAC_ENV\'] = \"/path/to/projectenv\"\n}}}\n\n \'\' Or for TRAC_ENV_PARENT_DIR: \'\'\n\n{{{\n    import os\n    os.environ[\'TRAC_ENV_PARENT_DIR\'] = \"/path/to/project/parent/dir\"\n}}}\n\nIf you are using the [http://httpd.apache.org/docs/suexec.html Apache suEXEC] feature please see [http://trac.edgewall.org/wiki/ApacheSuexec].\n\nOn some systems, you \'\'may\'\' need to edit the shebang line in the `trac.cgi` file to point to your real Python installation path. On a Windows system you may need to configure Windows to know how to execute a .cgi file (Explorer -> Tools -> Folder Options -> File Types -> CGI).\n\n== Mapping Static Resources ==\n\nOut of the box, Trac will pass static resources such as style sheets or images through itself. For a CGI setup this is \'\'\'highly undesirable\'\'\', because this way CGI script is invoked for documents that could be much more efficiently served directly by web server.\n\nWeb servers such as [http://httpd.apache.org/ Apache] allow you to create â€œAliasesâ€ to resources, giving them a virtual URL that doesn\'t necessarily reflect the layout of the servers file system. We already used this capability by defining a `ScriptAlias` for the CGI script. We also can map requests for static resources directly to the directory on the file system, avoiding processing these requests by CGI script.\n\nThere are two primary URL paths for static resources - `/chrome/common` and `/chrome/site`. Plugins can add their own resources usually accessible by `/chrome/plugin` path, so its important to override only known paths and not try to make universal `/chrome` alias for everything.\n\nAdd the following snippet to Apache configuration \'\'\'before\'\'\' the `ScriptAlias` for the CGI script, changing paths to match your deployment:\n{{{\nAlias /trac/chrome/common /path/to/trac/htdocs/common\nAlias /trac/chrome/site /path/to/trac/htdocs/site\n<Directory \"/path/to/www/trac/htdocs\">\n  Order allow,deny\n  Allow from all\n</Directory>\n}}}\n\nIf using mod_python, you might want to add this too (otherwise, the alias will be ignored):\n{{{\n<Location \"/trac/chrome/common/\">\n  SetHandler None\n</Location>\n}}}\n\nNote that we mapped `/trac` part of the URL to the `trac.cgi` script, and the path `/chrome/common` is the path you have to append to that location to intercept requests to the static resources. \n\nFor example, if Trac is mapped to `/cgi-bin/trac.cgi` on your server, the URL of the Alias should be `/cgi-bin/trac.cgi/chrome/common`.\n\nSimilarly, if you have static resources in a project\'s htdocs directory (which is referenced by /chrome/site URL in themes), you can configure Apache to serve those resources (again, put this \'\'\'before\'\'\' the `ScriptAlias` for the CGI script, and adjust names and locations to match your installation):\n\n{{{\nAlias /trac/chrome/site /path/to/projectenv/htdocs\n<Directory \"/path/to/projectenv/htdocs\">\n  Order allow,deny\n  Allow from all\n</Directory>\n}}}\n\nAlternatively to hacking `/trac/chrome/site`, you can directly specify path to static resources using `htdocs_location` configuration option in [wiki:TracIni trac.ini]:\n{{{\n[trac]\nhtdocs_location = http://yourhost.example.org/trac-htdocs\n}}}\n\nTrac will then use this URL when embedding static resources into HTML pages. Of course, you still need to make the Trac `htdocs` directory available through the web server at the specified URL, for example by copying (or linking) the directory into the document root of the web server:\n{{{\n$ ln -s /path/to/www/trac/htdocs /var/www/yourhost.example.org/trac-htdocs\n}}}\n\nNote that in order to get this `htdocs` directory, you need first to extract the relevant Trac resources using the `deploy` command of TracAdmin:\n[[TracAdminHelp(deploy)]]\n\n\n== Adding Authentication ==\n\nThe simplest way to enable authentication with Apache is to create a password file. Use the `htpasswd` program to create the password file:\n{{{\n$ htpasswd -c /somewhere/trac.htpasswd admin\nNew password: <type password>\nRe-type new password: <type password again>\nAdding password for user admin\n}}}\n\nAfter the first user, you dont need the \"-c\" option anymore:\n{{{\n$ htpasswd /somewhere/trac.htpasswd john\nNew password: <type password>\nRe-type new password: <type password again>\nAdding password for user john\n}}}\n\n  \'\'See the man page for `htpasswd` for full documentation.\'\'\n\nAfter you\'ve created the users, you can set their permissions using TracPermissions.\n\nNow, you\'ll need to enable authentication against the password file in the Apache configuration:\n{{{\n<Location \"/trac/login\">\n  AuthType Basic\n  AuthName \"Trac\"\n  AuthUserFile /somewhere/trac.htpasswd\n  Require valid-user\n</Location>\n}}}\n\nIf you\'re hosting multiple projects you can use the same password file for all of them:\n{{{\n<LocationMatch \"/trac/[^/]+/login\">\n  AuthType Basic\n  AuthName \"Trac\"\n  AuthUserFile /somewhere/trac.htpasswd\n  Require valid-user\n</LocationMatch>\n}}}\n\nFor better security, it is recommended that you either enable SSL or at least use the â€œdigestâ€ authentication scheme instead of â€œBasicâ€. Please read the [http://httpd.apache.org/docs/2.0/ Apache HTTPD documentation] to find out more. For example, on a Debian 4.0r1 (etch) system the relevant section  in apache configuration can look like this:\n{{{\n<Location \"/trac/login\">\n    LoadModule auth_digest_module /usr/lib/apache2/modules/mod_auth_digest.so\n    AuthType Digest\n    AuthName \"trac\"\n    AuthDigestDomain /trac\n    AuthUserFile /somewhere/trac.htpasswd\n    Require valid-user\n</Location>\n}}}\nand you\'ll have to create your .htpasswd file with htdigest instead of htpasswd as follows:\n{{{\n# htdigest /somewhere/trac.htpasswd trac admin\n}}}\nwhere the \"trac\" parameter above is the same as !AuthName above  (\"Realm\" in apache-docs). \n\n----\nSee also:  TracGuide, TracInstall, [wiki:TracModWSGI], TracFastCgi, TracModPython',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracChangeset',1,1327389819647871,'trac','127.0.0.1','= Trac Changeset Module =\n[[TracGuideToc]]\n\nTrac has a built-in functionality for visualizing â€œdiffsâ€ - changes to files.\n\nThere are different kinds of \'\'change sets\'\'. \nSome can correspond to revisions made in the repositories,\nothers can aggregate changes made in several revisions, \nbut in the end, any kind of differences can be shown.\n\nThe changeset view consists of two parts, the \'\'header\'\' \nand the \'\'diff views\'\'.\n\n== Changeset Header ==\n\nThe header shows an overview of the whole changeset.\nHere you will find information such as:\n\n * Timestamp â€” When the changeset was commited\n * Author â€” Who commited the changeset\n * Message â€” A brief description from the author (the commit log message)\n * Location â€” Parent directory of all files affected by this changeset\n * Files â€” A list of files affected by this changeset\n\nIf more than one revision is involved in the set of changes being\ndisplayed, the \'\'Timestamp\'\', \'\'Author\'\' and \'\'Message\'\' fields \nwon\'t be shown.\n\nIn front of each listed file, you\'ll find  a colored rectangle. The color\nindicates how the file is affected by the changeset.\n \n * Green: Added\n * Red: Removed\n * Yellow: Modified\n * Blue: Copied\n * Gray: Moved\n\nThe color legend is located below the header as a reminder.\n\n== Diff Views ==\n\nBelow the header is the main part of the changeset, the diff view. Each file is shown in a separate section, each of which will contain only the regions of the file that are affected by the changeset. There are two different styles of displaying the diffs: \'\'inline\'\' or \'\'side-by-side\'\' (you can switch between those styles using the preferences form):\n\n * The \'\'inline\'\' style shows the changed regions of a file underneath each other. A region removed from the file will be colored red, an added region will be colored green. If a region was modified, the old version is displayed above the new version. Line numbers on the left side indicate the exact position of the change in both the old and the new version of the file.\n * The \'\'side-by-side\'\' style shows the old version on the left and the new version on the right (this will typically require more screen width than the inline style.) Added and removed regions will be colored in the same way as with the inline style (green and red, respectively), but modified regions will have a yellow background.\n\nIn addition, various advanced options are available in the preferences form for adjusting the display of the diffs:\n * You can set how many lines are displayed before and after every change\n   (if the value \'\'all\'\' is used, then the full file will be shown)\n * You can toggle whether blank lines, case changes and white space changes are ignored, thereby letting you find the functional changes more quickly\n\n\n== The Different Ways to Get a Diff ==\n\n=== Examining a Changeset ===\n\nWhen viewing a repository check-in, such as when following a\nchangeset [wiki:TracLinks link] or a changeset event in the \n[wiki:TracTimeline timeline], Trac will display the exact changes\nmade by the check-in.\n\nThere will be also navigation links to the \'\'Previous Changeset\'\'\nto and \'\'Next Changeset\'\'.\n\n=== Examining Differences Between Revisions ===\n\nOften you\'ll want to look at changes made on a file \nor on a directory spanning multiple revisions. The easiest way\nto get there is from the TracRevisionLog, where you can select\nthe \'\'old\'\' and the \'\'new\'\' revisions of the file or directory, and\nthen click the \'\'View changes\'\' button.\n\n=== Examining Differences Between Branches ===\n\nOne of the core features of version control systems is the possibility\nto work simultaneously on different \'\'Lines of Developments\'\', commonly\ncalled â€œbranchesâ€. Trac enables you to examine the exact differences\nbetween such branches.\n\nUsing the \'\'\'View changes ...\'\'\' button in the TracBrowser allows you to enter\n\'\'From:\'\' and \'\'To:\'\' path/revision pairs. The resulting set of differences consist\nof the changes that should be applied to the \'\'From:\'\' content in order\nto get to the \'\'To:\'\' content.\n\nFor convenience, it is possible to invert the roles of the \'\'old\'\' and the \'\'new\'\'\npath/revision pairs by clicking the \'\'Reverse Diff\'\' link on the changeset page.\n\n=== Checking the Last Change ===\n\nThe last possibility for examining changes is to use the \'\'Last Change\'\'\nlink provided by the TracBrowser.\n\nThis link will take you to the last change that was made on that path.\nFrom there, you can use the \'\'Previous Change\'\' and \'\'Next Change\'\' links\nto traverse the change history of the file or directory.\n\n----\nSee also: TracGuide, TracBrowser\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracEnvironment',1,1327389819647871,'trac','127.0.0.1','= The Trac Environment =\n\nTrac uses a directory structure and a database for storing project data. The directory is referred to as the â€œenvironmentâ€.\n\n== Creating an Environment ==\n\nA new Trac environment is created using  [TracAdmin#initenv trac-admin\'s initenv]:\n{{{\n$ trac-admin /path/to/myproject initenv\n}}}\n\n`trac-admin` will ask you for the name of the project and the\ndatabase connection string (explained below).\n\n=== Some Useful Tips\n - The user under which the web server runs will require file system write permission to \n the environment directory and all the files inside. Please remember to set\n the appropriate permissions. The same applies to the source code repository, \n although the user under which Trac runs will only require write access to a Subversion repository created with the BDB file system; for other repository types, check the corresponding plugin\'s documentation. \n \n - `initenv`, when using an svn repository, does not imply that trac-admin will perform `svnadmin create` for the specified repository path. You need to perform the `svnadmin create` prior to `trac-admin initenv` if you\'re creating a new svn repository altogether with a new trac environment, otherwise you will see a message \"Warning: couldn\'t index the repository\" when initializing the environment.\n\n - Non-ascii environment paths are not supported\n \n - Also, it seems that project names with spaces can be problematic for authentication (see [trac:#7163]).\n\n - TracPlugins located in a [TracIni#inherit-section shared plugins folder] that is defined in an [TracIni#GlobalConfiguration inherited configuration] are currently not loaded during creation, and hence, if they need to create extra tables for example, you\'ll need to [TracUpgrade#UpgradetheTracEnvironment upgrade the environment] before being able to use it.\n\n== Database Connection Strings ==\n\nSince version 0.9, Trac supports both [http://sqlite.org/ SQLite] and\n[http://www.postgresql.org/ PostgreSQL] database backends.  Preliminary\nsupport for [http://mysql.com/ MySQL] was added in 0.10.  The default is\nto use SQLite, which is probably sufficient for most projects. The database\nfile is then stored in the environment directory, and can easily be \n[wiki:TracBackup backed up] together with the rest of the environment.\n\n=== SQLite Connection String ===\nThe connection string for an SQLite database is:\n{{{\nsqlite:db/trac.db\n}}}\nwhere `db/trac.db` is the path to the database file within the Trac environment.\n\n=== PostgreSQL Connection String ===\nIf you want to use PostgreSQL or MySQL instead, you\'ll have to use a\ndifferent connection string. For example, to connect to a PostgreSQL\ndatabase on the same machine called `trac`, that allows access to the\nuser `johndoe` with the password `letmein`, use:\n{{{\npostgres://johndoe:letmein@localhost/trac\n}}}\n\'\'Note that due to the way the above string is parsed, the \"/\" and \"@\" characters cannot be part of the password.\'\'\n\nIf PostgreSQL is running on a non-standard port (for example 9342), use:\n{{{\npostgres://johndoe:letmein@localhost:9342/trac\n}}}\n\nOn UNIX, you might want to select a UNIX socket for the transport,\neither the default socket as defined by the PGHOST environment variable:\n{{{\npostgres://user:password@/database\n}}}\nor a specific one:\n{{{\npostgres://user:password@/database?host=/path/to/socket/dir\n}}}\n\nNote that with PostgreSQL you will have to create the database before running\n`trac-admin initenv`.\n\nSee the [http://www.postgresql.org/docs/ PostgreSQL documentation] for detailed instructions on how to administer [http://postgresql.org PostgreSQL].\nGenerally, the following is sufficient to create a database user named `tracuser`, and a database named `trac`.\n{{{\ncreateuser -U postgres -E -P tracuser\ncreatedb -U postgres -O tracuser -E UTF8 trac\n}}}\nWhen running `createuser` you will be prompted for the password for the user \'tracuser\'. This new user will not be a superuser, will not be allowed to create other databases and will not be allowed to create other roles. These privileges are not needed to run a trac instance. If no password is desired for the user, simply remove the `-P` and `-E` options from the `createuser` command.  Also note that the database should be created as UTF8. LATIN1 encoding causes errors trac\'s use of unicode in trac.  SQL_ASCII also seems to work.\n\nUnder some default configurations (debian) one will have run the `createuser` and `createdb` scripts as the `postgres` user.  For example:\n{{{\nsudo su - postgres -c \'createuser -U postgres -S -D -R -E -P tracuser\'\nsudo su - postgres -c \'createdb -U postgres -O tracuser -E UTF8 trac\'\n}}}\n\nTrac uses the `public` schema by default but you can specify a different schema in the connection string:\n{{{\npostgres://user:pass@server/database?schema=yourschemaname\n}}}\n\n=== MySQL Connection String ===\n\nIf you want to use MySQL instead, you\'ll have to use a\ndifferent connection string. For example, to connect to a MySQL\ndatabase on the same machine called `trac`, that allows access to the\nuser `johndoe` with the password `letmein`, the mysql connection string is:\n{{{\nmysql://johndoe:letmein@localhost:3306/trac\n}}}\n\n== Source Code Repository ==\n\nSince version 0.12, a single Trac environment can be connected to more than one repository. There are many different ways to connect repositories to an environment, see TracRepositoryAdmin. This page also details the various attributes that can be set for a repository (like `type`, `url`, `description`).\n\nIn Trac 0.12 `trac-admin` no longer asks questions related to repositories. Therefore, by default Trac is not connected to any source code repository, and the \'\'Browse Source\'\' toolbar item will not be displayed.\nYou can also explicitly disable the `trac.versioncontrol.*` components (which are otherwise still loaded)\n{{{\n[components]\ntrac.versioncontrol.* = disabled\n}}}\n\nFor some version control systems, it is possible to specify not only the path to the repository,\nbut also a \'\'scope\'\' within the repository. Trac will then only show information\nrelated to the files and changesets below that scope. The Subversion backend for\nTrac supports this; for other types, check the corresponding plugin\'s documentation.\n\nExample of a configuration for a Subversion repository used as the default repository:\n{{{\n[trac]\nrepository_type = svn\nrepository_dir = /path/to/your/repository\n}}}\n\nThe configuration for a scoped Subversion repository would be:\n{{{\n[trac]\nrepository_type = svn\nrepository_dir = /path/to/your/repository/scope/within/repos\n}}}\n\n== Directory Structure ==\n\nAn environment directory will usually consist of the following files and directories:\n\n * `README` - Brief description of the environment.\n * `VERSION` - Contains the environment version identifier.\n * `attachments` - Attachments to wiki pages and tickets are stored here.\n * `conf`\n   * `trac.ini` - Main configuration file. See TracIni.\n * `db`\n   * `trac.db` - The SQLite database (if you\'re using SQLite).\n * `htdocs` - directory containing web resources, which can be referenced in Genshi templates using `/htdocs/site/...` URLs. \'\'(since 0.11)\'\'\n * `log` - default directory for log files, if logging is turned on and a relative path is given.\n * `plugins` - Environment-specific [wiki:TracPlugins plugins] (Python eggs or single file plugins, since [trac:milestone:0.10 0.10])\n * `templates` - Custom Genshi environment-specific templates. \'\'(since 0.11)\'\'\n   * `site.html` - method to customize header, footer, and style, described in TracInterfaceCustomization#SiteAppearance\n\n\'\'\'Caveat:\'\'\' \'\'don\'t confuse a Trac environment directory with the source code repository directory.\'\' \n\nThis is a common beginners\' mistake.\nIt happens that the structure for a Trac environment is loosely modelled after the Subversion repository directory \nstructure, but those are two disjoint entities and they are not and \'\'must not\'\' be located at the same place.\n\n----\nSee also: TracAdmin, TracBackup, TracIni, TracGuide\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracFastCgi',1,1327389819647871,'trac','127.0.0.1','= Trac with FastCGI =\n\n[http://www.fastcgi.com/ FastCGI] interface allows Trac to remain resident much like with [wiki:TracModPython mod_python]. It is faster than external CGI interfaces which must start a new process for each request. However, unlike mod_python, FastCGI supports [http://httpd.apache.org/docs/suexec.html Apache SuEXEC], i.e. run with different permissions than web server. Additionally, it is supported by much wider variety of web servers.\n\n\'\'\'Note for Windows:\'\'\' Trac\'s FastCGI does not run under Windows, as Windows does not implement `Socket.fromfd`, which is used by `_fcgi.py`. If you want to connect to IIS, you may want to try [trac:TracOnWindowsIisAjp AJP].\n\n== Simple Apache configuration ==\n\nThere are two FastCGI modules commonly available for Apache: `mod_fastcgi` and\n`mod_fcgid` (preferred). The latter is more up-to-date.\n\n==== setup with `mod_fastcgi` ====\n`mod_fastcgi` uses `FastCgiIpcDir` and `FastCgiConfig` directives that should be added to an appropriate Apache configuration file:\n{{{\n# Enable fastcgi for .fcgi files\n# (If you\'re using a distro package for mod_fcgi, something like\n# this is probably already present)\n<IfModule mod_fastcgi.c>\n   AddHandler fastcgi-script .fcgi\n   FastCgiIpcDir /var/lib/apache2/fastcgi \n</IfModule>\nLoadModule fastcgi_module /usr/lib/apache2/modules/mod_fastcgi.so\n}}}\nSetting `FastCgiIpcDir` is optional if the default is suitable. Note that the `LoadModule` line must be after the `IfModule` group.\n\nConfigure `ScriptAlias` or similar options as described in TracCgi, but\ncalling `trac.fcgi` instead of `trac.cgi`.\n\nYou can set up the `TRAC_ENV` as an overall default:\n{{{\nFastCgiConfig -initial-env TRAC_ENV=/path/to/env/trac\n}}}\n\nOr you can serve multiple Trac projects in a directory like:\n{{{\nFastCgiConfig -initial-env TRAC_ENV_PARENT_DIR=/parent/dir/of/projects\n}}}\n\n==== setup with `mod_fcgid` ====\nConfigure `ScriptAlias` (see TracCgi for details), but call `trac.fcgi`\ninstead of `trac.cgi`. Note that slash at the end - it is important.\n{{{\nScriptAlias /trac /path/to/www/trac/cgi-bin/trac.fcgi/\n}}}\n\nTo setup Trac environment for `mod_fcgid` it is necessary to use\n`DefaultInitEnv` directive. It cannot be used in `Directory` or\n`Location` context, so if you need to support multiple projects, try\nalternative environment setup below.\n\n{{{\nDefaultInitEnv TRAC_ENV /path/to/env/trac/\n}}}\n\n==== alternative environment setup ====\nA better method to specify path to Trac environment it to embed the path\ninto `trac.fcgi` script itself. That doesn\'t require configuration of server\nenvironment variables, works for both FastCgi modules\n(and for [http://www.lighttpd.net/ lighttpd] and CGI as well):\n{{{\nimport os\nos.environ[\'TRAC_ENV\'] = \"/path/to/projectenv\"\n}}}\nor\n{{{\nimport os\nos.environ[\'TRAC_ENV_PARENT_DIR\'] = \"/path/to/project/parent/dir\"\n}}}\n\nWith this method different projects can be supported by using different\n`.fcgi` scripts with different `ScriptAliases`.\n\nSee [https://coderanger.net/~coderanger/httpd/fcgi_example.conf this fcgid example config] which uses a !ScriptAlias directive with trac.fcgi with a trailing / like this:\n{{{\nScriptAlias / /srv/tracsite/cgi-bin/trac.fcgi/\n}}}\n\n== Simple Cherokee Configuration ==\n\nThe configuration on Cherokee\'s side is quite simple. You will only need to know that you can spawn Trac as an SCGI process.\nYou can either start it manually, or better yet, automatically by letting Cherokee spawn the server whenever it is down.\nFirst set up an information source in cherokee-admin with a local interpreter.\n\n{{{\nHost:\nlocalhost:4433\n\nInterpreter:\n/usr/bin/tracd â€”single-env â€”daemonize â€”protocol=scgi â€”hostname=localhost â€”port=4433 /path/to/project/\n}}}\n\nIf the port was not reachable, the interpreter command would be launched. Note that, in the definition of the information source, you will have to manually launch the spawner if you use a \'\'Remote host\'\' as \'\'Information source\'\' instead of a \'\'Local interpreter\'\'.\n\nAfter doing this, we will just have to create a new rule managed by the SCGI handler to access Trac. It can be created in a new virtual server, trac.example.net for instance, and will only need two rules. The \'\'\'default\'\'\' one will use the SCGI handler associated to the previously created information source.\nThe second rule will be there to serve the few static files needed to correctly display the Trac interface. Create it as \'\'Directory rule\'\' for \'\'/chrome/common\'\' and just set it to the \'\'Static files\'\' handler and with a \'\'Document root\'\' that points to the appropriate files: \'\'/usr/share/trac/htdocs/\'\'\n\n== Simple Lighttpd Configuration ==\n\nThe FastCGI front-end was developed primarily for use with alternative webservers, such as [http://www.lighttpd.net/ lighttpd].\n\nlighttpd is a secure, fast, compliant and very flexible web-server that has been optimized for high-performance\nenvironments.  It has a very low memory footprint compared to other web servers and takes care of CPU load.\n\nFor using `trac.fcgi`(prior to 0.11) / fcgi_frontend.py (0.11) with lighttpd add the following to your lighttpd.conf:\n{{{\n#var.fcgi_binary=\"/usr/bin/python /path/to/fcgi_frontend.py\" # 0.11 if installed with easy_setup, it is inside the egg directory\nvar.fcgi_binary=\"/path/to/cgi-bin/trac.fcgi\" # 0.10 name of prior fcgi executable\nfastcgi.server = (\"/trac\" =>\n   \n                   (\"trac\" =>\n                     (\"socket\" => \"/tmp/trac-fastcgi.sock\",\n                      \"bin-path\" => fcgi_binary,\n                      \"check-local\" => \"disable\",\n                      \"bin-environment\" =>\n                        (\"TRAC_ENV\" => \"/path/to/projenv\")\n                     )\n                   )\n                 )\n}}}\n\nNote that you will need to add a new entry to `fastcgi.server` for each separate Trac instance that you wish to run. Alternatively, you may use the `TRAC_ENV_PARENT_DIR` variable instead of `TRAC_ENV` as described above,\nand you may set one of the two in `trac.fcgi` instead of in `lighttpd.conf`\nusing `bin-environment` (as in the section above on Apache configuration).\n\nNote that lighttpd has a bug related to \'SCRIPT_NAME\' and \'PATH_INFO\' when the uri of fastcgi.server is \'/\' instead of \'/trac\' in this example, see #Trac2418. This should be fixed since lighttpd 1.4.23, and you may need to add `\"fix-root-scriptname\" => \"enable\"` as parameter of fastcgi.server.\n\nFor using two projects with lighttpd add the following to your `lighttpd.conf`:\n{{{\nfastcgi.server = (\"/first\" =>\n                   (\"first\" =>\n                    (\"socket\" => \"/tmp/trac-fastcgi-first.sock\",\n                     \"bin-path\" => fcgi_binary,\n                     \"check-local\" => \"disable\",\n                     \"bin-environment\" =>\n                       (\"TRAC_ENV\" => \"/path/to/projenv-first\")\n                    )\n                  ),\n                  \"/second\" =>\n                    (\"second\" =>\n                    (\"socket\" => \"/tmp/trac-fastcgi-second.sock\",\n                     \"bin-path\" => fcgi_binary,\n                     \"check-local\" => \"disable\",\n                     \"bin-environment\" =>\n                       (\"TRAC_ENV\" => \"/path/to/projenv-second\")\n                    )\n                  )\n                )\n}}}\nNote that field values are different.  If you prefer setting the environment\nvariables in the `.fcgi` scripts, then copy/rename `trac.fcgi`, e.g., to\n`first.fcgi` and `second.fcgi`, and reference them in the above settings.\nNote that the above will result in different processes in any event, even\nif both are running from the same `trac.fcgi` script.\n{{{\n#!div class=important\n\'\'\'Note\'\'\' It\'s very important the order on which server.modules are loaded, if mod_auth is not loaded \'\'\'BEFORE\'\'\' mod_fastcgi, then the server will fail to authenticate the user.\n}}}\nFor authentication you should enable mod_auth in lighttpd.conf \'server.modules\', select auth.backend and auth rules:\n{{{\nserver.modules              = (\n...\n  \"mod_auth\",\n...\n)\n\nauth.backend               = \"htpasswd\"\n\n# Separated password files for each project\n# See \"Conditional Configuration\" in\n# http://trac.lighttpd.net/trac/file/branches/lighttpd-merge-1.4.x/doc/configuration.txt\n\n$HTTP[\"url\"] =~ \"^/first/\" {\n  auth.backend.htpasswd.userfile = \"/path/to/projenv-first/htpasswd.htaccess\"\n}\n$HTTP[\"url\"] =~ \"^/second/\" {\n  auth.backend.htpasswd.userfile = \"/path/to/projenv-second/htpasswd.htaccess\"\n}\n\n# Enable auth on trac URLs, see\n# http://trac.lighttpd.net/trac/file/branches/lighttpd-merge-1.4.x/doc/authentication.txt\n\nauth.require = (\"/first/login\" =>\n                (\"method\"  => \"basic\",\n                 \"realm\"   => \"First project\",\n                 \"require\" => \"valid-user\"\n                ),\n                \"/second/login\" =>\n                (\"method\"  => \"basic\",\n                 \"realm\"   => \"Second project\",\n                 \"require\" => \"valid-user\"\n                )\n               )\n\n\n}}}\nNote that lighttpd (I use version 1.4.3) stopped if password file doesn\'t exist.\n\nNote that lighttpd doesn\'t support \'valid-user\' in versions prior to 1.3.16.\n\nConditional configuration is also useful for mapping static resources, i.e. serving out images and CSS directly instead of through FastCGI:\n{{{\n# Aliasing functionality is needed\nserver.modules += (\"mod_alias\")\n\n# Setup an alias for the static resources\nalias.url = (\"/trac/chrome/common\" => \"/usr/share/trac/htdocs\")\n\n# Use negative lookahead, matching all requests that ask for any resource under /trac, EXCEPT in\n# /trac/chrome/common, and use FastCGI for those\n$HTTP[\"url\"] =~ \"^/trac(?!/chrome/common)\" {\n# Even if you have other fastcgi.server declarations for applications other than Trac, do NOT use += here\nfastcgi.server = (\"/trac\" =>\n                   (\"trac\" =>\n                     (\"socket\" => \"/tmp/trac-fastcgi.sock\",\n                      \"bin-path\" => fcgi_binary,\n                      \"check-local\" => \"disable\",\n                      \"bin-environment\" =>\n                        (\"TRAC_ENV\" => \"/path/to/projenv\")\n                     )\n                   )\n                 )\n}\n}}}\nThe technique can be easily adapted for use with multiple projects by creating aliases for each of them, and wrapping the fastcgi.server declarations inside conditional configuration blocks.\nAlso there is another way to handle multiple projects and it\'s to use TRAC_ENV_PARENT_DIR instead of TRAC_ENV and use global auth, let\'s see an example:\n{{{\n#  This is for handling multiple projects\n  alias.url       = ( \"/trac/\" => \"/path/to/trac/htdocs/\" )\n\n  fastcgi.server += (\"/projects\"  =>\n                      (\"trac\" =>\n                        (\n                          \"socket\" => \"/tmp/trac.sock\",\n                          \"bin-path\" => fcgi_binary,\n                          \"check-local\" => \"disable\",\n                          \"bin-environment\" =>\n                            (\"TRAC_ENV_PARENT_DIR\" => \"/path/to/parent/dir/of/projects/\" )\n                        )\n                      )\n                    )\n#And here starts the global auth configuration\n  auth.backend = \"htpasswd\"\n  auth.backend.htpasswd.userfile = \"/path/to/unique/htpassword/file/trac.htpasswd\"\n  $HTTP[\"url\"] =~ \"^/projects/.*/login$\" {\n    auth.require = (\"/\" =>\n                     (\n                       \"method\"  => \"basic\",\n                       \"realm\"   => \"trac\",\n                       \"require\" => \"valid-user\"\n                     )\n                   )\n  }\n}}}\n\nChanging date/time format also supported by lighttpd over environment variable LC_TIME\n{{{\nfastcgi.server = (\"/trac\" =>\n                   (\"trac\" =>\n                     (\"socket\" => \"/tmp/trac-fastcgi.sock\",\n                      \"bin-path\" => fcgi_binary,\n                      \"check-local\" => \"disable\",\n                      \"bin-environment\" =>\n                        (\"TRAC_ENV\" => \"/path/to/projenv\",\n                        \"LC_TIME\" => \"ru_RU\")\n                     )\n                   )\n                 )\n}}}\nFor details about languages specification see [trac:TracFaq TracFaq] question 2.13.\n\nOther important information like [http://trac.lighttpd.net/trac/wiki/TracInstall this updated TracInstall page], [wiki:TracCgi#MappingStaticResources and this] are useful for non-fastcgi specific installation aspects.\n\nIf you use trac-0.9, read [http://lists.edgewall.com/archive/trac/2005-November/005311.html about small bug]\n\nRelaunch lighttpd, and browse to `http://yourhost.example.org/trac` to access Trac.\n\nNote about running lighttpd with reduced permissions:\n\n  If nothing else helps and trac.fcgi doesn\'t start with lighttpd settings `server.username = \"www-data\"`, `server.groupname = \"www-data\"`, then in the `bin-environment` section set `PYTHON_EGG_CACHE` to the home directory of `www-data` or some other directory accessible to this account for writing.\n\n\n== Simple !LiteSpeed Configuration ==\n\nThe FastCGI front-end was developed primarily for use with alternative webservers, such as [http://www.litespeedtech.com/ LiteSpeed].\n\n!LiteSpeed web server is an event-driven asynchronous Apache replacement designed from the ground-up to be secure, scalable, and operate with minimal resources. !LiteSpeed can operate directly from an Apache config file and is targeted for business-critical environments.\n\n=== Setup ===\n\n 1. Please make sure you have first have a working install of a Trac project. Test install with â€œtracdâ€ first.\n\n 2. Create a Virtual Host for this setup. From now on we will refer to this vhost as !TracVhost. For this tutorial we will be assuming that your trac project will be accessible via:\n\n{{{\nhttp://yourdomain.com/trac/\n}}}\n\n 3. Go â€œ!TracVhost â†’ External Appsâ€ tab and create a new â€œExternal Applicationâ€.\n\n{{{\nName: MyTracFCGI	\nAddress: uds://tmp/lshttpd/mytracfcgi.sock\nMax Connections: 10\nEnvironment: TRAC_ENV=/fullpathto/mytracproject/ <--- path to root folder of trac project\nInitial Request Timeout (secs): 30\nRetry Timeout (secs): 0\nPersistent Connection	Yes\nConnection Keepalive Timeout: 30\nResponse Bufferring: No	\nAuto Start: Yes\nCommand: /usr/share/trac/cgi-bin/trac.fcgi  <--- path to trac.fcgi\nBack Log: 50\nInstances: 10\n}}}\n\n 4. Optional. If you need to use htpasswd based authentication. Go to â€œ!TracVhost â†’ Securityâ€ tab and create a new security â€œRealmâ€.\n\n{{{\nDB Type: Password File\nRealm Name: MyTracUserDB               <--- any name you wish and referenced later\nUser DB Location: /fullpathto/htpasswd <--- path to your htpasswd file\n}}}\n\nIf you donâ€™t have a htpasswd file or donâ€™t know how to create the entries within one, go to http://sherylcanter.com/encrypt.php, to generate the user:password combos.\n\n 5. Go to â€œ!PythonVhost â†’ Contextsâ€ and create a new â€œFCGI Contextâ€.\n\n{{{\nURI: /trac/                              <--- URI path to bind to python fcgi app we created	\nFast CGI App: [VHost Level] MyTractFCGI  <--- select the trac fcgi extapp we just created\nRealm: TracUserDB                        <--- only if (4) is set. select realm created in (4)\n}}}\n\n 6. Modify `/fullpathto/mytracproject/conf/trac.ini`\n\n{{{\n#find/set base_rul, url, and link variables\nbase_url = http://yourdomain.com/trac/ <--- base url to generate correct links to\nurl = http://yourdomain.com/trac/      <--- link of project\nlink = http://yourdomain.com/trac/     <--- link of graphic logo\n}}}\n\n 7. Restart !LiteSpeed, â€œlswsctrl restartâ€, and access your new Trac project at: \n\n{{{\nhttp://yourdomain.com/trac/\n}}}\n\n== Simple Nginx Configuration ==\n\n 1. Nginx configuration snippet - confirmed to work on 0.6.32\n{{{\n    server {\n        listen       10.9.8.7:443;\n        server_name  trac.example;\n\n        ssl                  on;\n        ssl_certificate      /etc/ssl/trac.example.crt;\n        ssl_certificate_key  /etc/ssl/trac.example.key;\n\n        ssl_session_timeout  5m;\n\n        ssl_protocols  SSLv2 SSLv3 TLSv1;\n        ssl_ciphers  ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;\n        ssl_prefer_server_ciphers   on;\n\n        # (Or ``^/some/prefix/(.*)``.\n        if ($uri ~ ^/(.*)) {\n             set $path_info /$1;\n        }\n\n        # You can copy this whole location to ``location [/some/prefix]/login``\n        # and remove the auth entries below if you want Trac to enforce\n        # authorization where appropriate instead of needing to authenticate\n        # for accessing the whole site.\n        # (Or ``location /some/prefix``.)\n        location / {\n            auth_basic            \"trac realm\";\n            auth_basic_user_file /home/trac/htpasswd;\n\n            # socket address\n            fastcgi_pass   unix:/home/trac/run/instance.sock;\n\n            # python - wsgi specific\n            fastcgi_param HTTPS on;\n\n            ## WSGI REQUIRED VARIABLES\n            # WSGI application name - trac instance prefix.\n	    # (Or ``fastcgi_param  SCRIPT_NAME  /some/prefix``.)\n            fastcgi_param  SCRIPT_NAME        \"\";\n            fastcgi_param  PATH_INFO          $path_info;\n\n            ## WSGI NEEDED VARIABLES - trac warns about them\n            fastcgi_param  REQUEST_METHOD     $request_method;\n            fastcgi_param  SERVER_NAME        $server_name;\n            fastcgi_param  SERVER_PORT        $server_port;\n            fastcgi_param  SERVER_PROTOCOL    $server_protocol;\n            fastcgi_param  QUERY_STRING     $query_string;\n\n            # for authentication to work\n            fastcgi_param  AUTH_USER          $remote_user;\n            fastcgi_param  REMOTE_USER        $remote_user;\n        }\n    }\n}}}\n\n 2. Modified trac.fcgi:\n\n{{{\n#!/usr/bin/env python\nimport os\nsockaddr = \'/home/trac/run/instance.sock\'\nos.environ[\'TRAC_ENV\'] = \'/home/trac/instance\'\n\ntry:\n     from trac.web.main import dispatch_request\n     import trac.web._fcgi\n\n     fcgiserv = trac.web._fcgi.WSGIServer(dispatch_request, \n          bindAddress = sockaddr, umask = 7)\n     fcgiserv.run()\n\nexcept SystemExit:\n    raise\nexcept Exception, e:\n    print \'Content-Type: text/plain\\r\\n\\r\\n\',\n    print \'Oops...\'\n    print\n    print \'Trac detected an internal error:\'\n    print\n    print e\n    print\n    import traceback\n    import StringIO\n    tb = StringIO.StringIO()\n    traceback.print_exc(file=tb)\n    print tb.getvalue()\n\n}}}\n\n 3. reload nginx and launch trac.fcgi like that:\n\n{{{\ntrac@trac.example ~ $ ./trac-standalone-fcgi.py \n}}}\n\nThe above assumes that:\n * There is a user named \'trac\' for running trac instances and keeping trac environments in its home directory.\n * `/home/trac/instance` contains a trac environment\n * `/home/trac/htpasswd` contains authentication information\n * `/home/trac/run` is owned by the same group the nginx runs under\n  * and if your system is Linux the `/home/trac/run` has setgid bit set (`chmod g+s run`)\n  * and patch from ticket #T7239 is applied, or you\'ll have to fix the socket file permissions every time\n\nUnfortunately nginx does not support variable expansion in fastcgi_pass directive. \nThus it is not possible to serve multiple trac instances from one server block. \n\nIf you worry enough about security, run trac instances under separate users. \n\nAnother way to run trac as a FCGI external application is offered in ticket #T6224\n\n----\nSee also:  TracGuide, TracInstall, [wiki:TracModWSGI ModWSGI], [wiki:TracCgi CGI], [wiki:TracModPython ModPython], [trac:TracNginxRecipe TracNginxRecipe]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracFineGrainedPermissions',1,1327389819647871,'trac','127.0.0.1','= Fine grained permissions =\n\nBefore Trac 0.11, it was only possible to define fine-grained permissions checks on the repository browser sub-system.\n\nSince 0.11, there\'s a general mechanism in place that allows custom **permission policy plugins** to grant or deny any action on any kind of Trac resources, even at the level of specific versions of such resources.\n\nNote that for Trac 0.12, `authz_policy` has been integrated as an optional module (in `tracopt.perm.authz_policy.*`), so it\'s installed by default and can simply be activated via the //Plugins// panel in the Trac administration module.\n\n\n== Permission Policies ==\n\nA great diversity of permission policies can be implemented, and Trac comes with a few examples. \n\nWhich policies are currently active is determined by a configuration setting in TracIni:\ne.g.\n{{{\n[trac]\npermission_policies = AuthzSourcePolicy, DefaultPermissionPolicy, LegacyAttachmentPolicy\n}}}\nThis lists the [#AuthzSourcePolicy] described below as the first policy, followed by the !DefaultPermissionPolicy which checks for the traditional coarse grained style permissions described in TracPermissions, and the !LegacyAttachmentPolicy which knows how to use the coarse grained permissions for checking the permissions available on attachments.\n\nAmong the possible optional choices, there is [#AuthzPolicy], a very generic permission policy, based on an Authz-style system. See\n[trac:source:branches/0.12-stable/tracopt/perm/authz_policy.py authz_policy.py] for details. \n\nAnother popular permission policy [#AuthzSourcePolicy], re-implements the pre-0.12 support for checking fine-grained permissions limited to Subversion repositories in terms of the new system.\n\nSee also [trac:source:branches/0.12-stable/sample-plugins/permissions sample-plugins/permissions] for more examples.\n\n\n=== !AuthzPolicy === \n\n - Install [http://www.voidspace.org.uk/python/configobj.html ConfigObj] (required).\n - Copy authz_policy.py into your plugins directory.\n - Put a [http://swapoff.org/files/authzpolicy.conf authzpolicy.conf] file somewhere, preferably on a secured location on the server, not readable for others than the webuser. If the  file contains non-ASCII characters, the UTF-8 encoding should be used.\n - Update your `trac.ini`:\n   1. modify the [TracIni#trac-section permission_policies] entry in the `[trac]` section\n{{{\n[trac]\n...\npermission_policies = AuthzPolicy, DefaultPermissionPolicy, LegacyAttachmentPolicy\n}}}\n   2. add a new `[authz_policy]` section\n{{{\n[authz_policy]\nauthz_file = /some/trac/env/conf/authzpolicy.conf\n}}}\n   3. enable the single file plugin\n{{{\n[components]\n...\n# Trac 0.12\ntracopt.perm.authz_policy.* = enabled\n# for Trac 0.11 use this\n#authz_policy.* = enabled \n}}}\n\nNote that the order in which permission policies are specified is quite critical, \nas policies will be examined in the sequence provided.\n\nA policy will return either `True`, `False` or `None` for a given permission check.\nOnly if the return value is `None` will the \'\'next\'\' permission policy be consulted.\nIf no policy explicitly grants the permission, the final result will be `False` \n(i.e. no permission).\n\nFor example, if the `authz_file` contains:\n{{{\n[wiki:WikiStart@*]\n* = WIKI_VIEW\n\n[wiki:PrivatePage@*]\njohn = WIKI_VIEW\n* =\n}}}\nand the default permissions are set like this:\n{{{\njohn           WIKI_VIEW\njack           WIKI_VIEW\n# anonymous has no WIKI_VIEW\n}}}\n\nThen: \n - All versions of WikiStart will be viewable by everybody (including anonymous)\n - !PrivatePage will be viewable only by john\n - other pages will be viewable only by john and jack\n\n\n=== !AuthzSourcePolicy  (mod_authz_svn-like permission policy) === #AuthzSourcePolicy\n\nAt the time of this writing, the old fine grained permissions system from Trac 0.11 and before used for restricting access to the repository has  been converted to a permission policy component, but from the user point of view, this makes little if no difference.\n\nThat kind of fine-grained permission control needs a definition file, which is the one used by Subversion\'s mod_authz_svn. \nMore information about this file format and about its usage in Subversion is available in the  [http://svnbook.red-bean.com/en/1.5/svn.serverconfig.pathbasedauthz.html Path-Based Authorization] section in the Server Configuration chapter of the svn book.\n\nExample:\n{{{\n[/]\n* = r\n\n[/branches/calc/bug-142]\nharry = rw\nsally = r\n\n[/branches/calc/bug-142/secret]\nharry =\n}}}\n\n * \'\'\'/\'\'\' = \'\'Everyone has read access by default\'\'\n * \'\'\'/branches/calc/bug-142\'\'\' = \'\'harry has read/write access, sally read only\'\'\n * \'\'\'/branches/calc/bug-142/secret\'\'\' = \'\'harry has no access, sally has read access (inherited as a sub folder permission)\'\'\n\n==== Trac Configuration ====\n\nTo activate fine grained permissions you __must__ specify the {{{authz_file}}} option in the {{{[trac]}}} section of trac.ini. If this option is set to null or not specified the permissions will not be used.\n\n{{{\n[trac]\nauthz_file = /path/to/svnaccessfile\n}}}\n\nIf you want to support the use of the `[`\'\'modulename\'\'`:/`\'\'some\'\'`/`\'\'path\'\'`]` syntax within the `authz_file`, add \n\n{{{\nauthz_module_name = modulename\n}}}\n\nwhere \'\'modulename\'\' refers to the same repository indicated by the `repository_dir` entry in the `[trac]` section. As an example, if the `repository_dir` entry in the `[trac]` section is {{{/srv/active/svn/blahblah}}}, that would yield the following:\n\n{{{ \n[trac]\nauthz_file = /path/to/svnaccessfile\nauthz_module_name = blahblah\n...\nrepository_dir = /srv/active/svn/blahblah \n}}}\n\nwhere the svn access file, {{{/path/to/svnaccessfile}}}, contains entries such as {{{[blahblah:/some/path]}}}.\n\n\'\'\'Note:\'\'\' Usernames inside the Authz file __must__ be the same as those used inside trac. \n\nAs of version 0.12, make sure you have \'\'!AuthzSourcePolicy\'\' included in the permission_policies list in trac.ini, otherwise the authz permissions file will be ignored.\n\n{{{ \n[trac]\npermission_policies = AuthzSourcePolicy, DefaultPermissionPolicy, LegacyAttachmentPolicy\n}}}\n\n==== Subversion Configuration ====\n\nThe same access file is typically applied to the corresponding Subversion repository using an Apache directive like this:\n{{{\n<Location /repos>\n  DAV svn\n  SVNParentPath /usr/local/svn\n\n  # our access control policy\n  AuthzSVNAccessFile /path/to/svnaccessfile\n</Location>\n}}}\n\nFor information about how to restrict access to entire projects in a multiple project environment see [trac:wiki:TracMultipleProjectsSVNAccess]\n\n== Debugging permissions\nIn trac.ini set:\n{{{\n[logging]\nlog_file = trac.log\nlog_level = DEBUG\nlog_type = file\n}}}\n\nAnd watch:\n{{{\ntail -n 0 -f log/trac.log | egrep \'\\[perm\\]|\\[authz_policy\\]\'\n}}}\n\nto understand what checks are being performed. See the sourced documentation of the plugin for more info.\n\n\n----\nSee also: TracPermissions,\n[http://trac-hacks.org/wiki/FineGrainedPageAuthzEditorPlugin TracHacks:FineGrainedPageAuthzEditorPlugin] for a simple editor plugin.',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracGuide',1,1327389819647871,'trac','127.0.0.1','= The Trac User and Administration Guide =\n[[TracGuideToc]]\n\nThe TracGuide is meant to serve as a starting point for all documentation regarding Trac usage and development. The guide is a free document, a collaborative effort, and a part of the [http://trac.edgewall.org Trac Project] itself.\n\n== Table of Contents ==\n\nCurrently available documentation:\n * \'\'\'User Guide\'\'\'\n   * TracWiki â€” How to use the built-in Wiki.\n   * TracTimeline â€” The timeline provides a historic perspective on a project.\n   * TracRss â€” RSS content syndication in Trac.\n   * \'\'The Version Control Subsystem\'\'\n     * TracBrowser â€” Browsing source code with Trac.\n     * TracChangeset â€” Viewing changes to source code.\n     * TracRevisionLog â€” Viewing change history.\n   * \'\'The Ticket Subsystem\'\'\n     * TracTickets â€” Using the issue tracker.\n     * TracReports â€” Writing and using reports.\n     * TracQuery â€” Executing custom ticket queries.\n     * TracRoadmap â€” The roadmap helps tracking project progress.\n * \'\'\'Administrator Guide\'\'\'\n   * TracInstall â€” How to install and run Trac.\n   * TracUpgrade â€” How to upgrade existing installations.\n   * TracAdmin â€” Administering a Trac project.\n   * TracImport â€” Importing tickets from other bug databases.\n   * TracIni â€” Trac configuration file reference. \n   * TracPermissions â€” Access control and permissions.\n   * TracInterfaceCustomization â€” Customizing the Trac interface.\n   * TracPlugins â€” Installing and managing Trac extensions.\n   * TracLogging â€” The Trac logging facility.\n   * TracNotification â€” Email notification.\n   * TracWorkflow â€” Configurable Ticket Workflow.\n   * TracRepositoryAdmin â€” Management of Source Code Repositories.\n * [trac:TracFaq Trac FAQ] â€” A collection of Frequently Asked Questions (on the project website).\n\n== Support and Other Sources of Information ==\nIf you are looking for a good place to ask a question about Trac, look no further than the [http://trac.edgewall.org/wiki/MailingList MailingList]. It provides a friendly environment to discuss openly among Trac users and developers.\n\nSee also the TracSupport page for more information resources.\n\nFinally, developer documentation can be found in [trac:TracDev TracDev] and its sub-pages.\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracImport',1,1327389819647871,'trac','127.0.0.1','= Importing ticket data =\n\n== Bugzilla ==\n\nTicket data can be imported from Bugzilla using the [http://trac.edgewall.org/browser/trunk/contrib/bugzilla2trac.py bugzilla2trac.py] script, available in the contrib/ directory of the Trac distribution.\n\n{{{\n$ bugzilla2trac.py\nbugzilla2trac - Imports a bug database from Bugzilla into Trac.\n\nUsage: bugzilla2trac.py [options]\n\nAvailable Options:\n  --db <MySQL dbname>              - Bugzilla\'s database\n  --tracenv /path/to/trac/env      - full path to Trac db environment\n  -h | --host <MySQL hostname>     - Bugzilla\'s DNS host name\n  -u | --user <MySQL username>     - effective Bugzilla\'s database user\n  -p | --passwd <MySQL password>   - Bugzilla\'s user password\n  -c | --clean                     - remove current Trac tickets before importing\n  --help | help                    - this help info\n\nAdditional configuration options can be defined directly in the script.\n}}}\n\nCurrently, the following data is imported from Bugzilla:\n\n  * bugs\n  * bug activity (field changes)\n  * bug attachments\n  * user names and passwords (put into a htpasswd file)\n\nThe script provides a number of features to ease the conversion, such as:\n\n  * PRODUCT_KEYWORDS:  Trac doesn\'t have the concept of products, so the script provides the ability to attach a ticket keyword instead.\n\n  * IGNORE_COMMENTS:  Don\'t import Bugzilla comments that match a certain regexp.\n\n  * STATUS_KEYWORDS:  Attach ticket keywords for the Bugzilla statuses not available in Trac.  By default, the \'VERIFIED\' and \'RELEASED\' Bugzilla statuses are translated into Trac keywords.\n\nFor more details on the available options, see the configuration section at the top of the script.\n\n== Sourceforge ==\n\nTicket data can be imported from Sourceforge using the [http://trac.edgewall.org/browser/trunk/contrib/sourceforge2trac.py sourceforge2trac.py] script, available in the contrib/ directory of the Trac distribution.\n\nSee #Trac3521 for an updated sourceforge2trac script.\n\n== Mantis ==\n\nThe mantis2trac script now lives at http://trac-hacks.org/wiki/MantisImportScript. You can always get the latest version from http://trac-hacks.org/changeset/latest/mantisimportscript?old_path=/&filename=mantisimportscript&format=zip\n\nMantis bugs can be imported using the attached script.\n\nCurrently, the following data is imported from Mantis:\n  * bugs\n  * bug comments\n  * bug activity (field changes)\n  * attachments (as long as the files live in the mantis db, not on the filesystem) \n\nIf you use the script, please read the NOTES section (at the top of the file) and make sure you adjust the config parameters for your environment.\n\nmantis2trac.py has the same parameters as the bugzilla2trac.py script:\n{{{\nmantis2trac - Imports a bug database from Mantis into Trac.\n\nUsage: mantis2trac.py [options] \n\nAvailable Options:\n  --db <MySQL dbname>              - Mantis database\n  --tracenv /path/to/trac/env      - Full path to Trac db environment\n  -h | --host <MySQL hostname>     - Mantis DNS host name\n  -u | --user <MySQL username>     - Effective Mantis database user\n  -p | --passwd <MySQL password>   - Mantis database user password\n  -c | --clean                     - Remove current Trac tickets before importing\n  --help | help                    - This help info\n\nAdditional configuration options can be defined directly in the script.\n}}} \n\n== Jira ==\n\nThe [http://trac-hacks.org/wiki/JiraToTracIntegration Jira2Trac plugin] provides you with tools to import Atlassian Jira backup files into Trac.\n\nThe plugin consists of a Python 3.1 commandline tool that:\n\n - Parses the Jira backup XML file\n - Sends the imported Jira data and attachments to Trac using the [http://trac-hacks.org/wiki/XmlRpcPlugin XmlRpcPlugin]\n - Generates a htpasswd file containing the imported Jira users and their SHA-512 base64 encoded passwords\n\n== Other ==\n\nSince trac uses a SQL database to store the data, you can import from other systems by examining the database tables. Just go into [http://www.sqlite.org/sqlite.html sqlite] command line to look at the tables and import into them from your application.\n\n=== Using a comma delimited file - CSV ===\nSee [http://trac.edgewall.org/attachment/wiki/TracSynchronize/csv2trac.2.py] for details.  This approach is particularly useful if one needs to enter a large number of tickets by hand. (note that the ticket type type field, (task etc...) is also needed for this script to work with more recent Trac releases)\nComments on script: The script has an error on line 168, (\'Ticket\' needs to be \'ticket\').  Also, the listed values for severity and priority are swapped. \n\n=== Using an Excel (.xls) or comma delimited file (.csv) ===\nThis plugin http://trac-hacks.org/wiki/TicketImportPlugin lets you import into Trac a series of tickets from a CSV file or (if the xlrd library is installed) from an Excel file.\n\nYou can also use it to modify tickets in batch, by saving a report as CSV, editing the CSV file, and re-importing the tickets.\n\nThis plugin is very useful when starting a new project: you can import a list of requirements that may have come from meeting notes, list of features, other ticketing systems... It\'s also great to review the tickets off-line, or to do massive changes to tickets.\n\nBased on the ticket id (or, if no id exists, on the summary) in the imported file, tickets are either created or updated. \n\n\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracIni',1,1327389819647871,'trac','127.0.0.1','= The Trac Configuration File =\n\n[[TracGuideToc]]\n\nTrac configuration is done by editing the \'\'\'`trac.ini`\'\'\' config file, located in `<projectenv>/conf/trac.ini`.  Changes to the configuration are usually reflected immediately, though changes to the `[components]` or `[logging]` sections will require restarting the web server. You may also need to restart the web server after creating a global configuration file when none was previously present.\n\nThe `trac.ini` configuration file should be writable by the web server, as Trac currently relies on the possibility to trigger a complete environment reload to flush its caches.\n\n== Global Configuration ==\n\nIn versions prior to 0.11, the global configuration was by default located in `$prefix/share/trac/conf/trac.ini` or /etc/trac/trac.ini, depending on the distribution. If you\'re upgrading, you may want to specify that file to inherit from.  Literally, when you\'re upgrading to 0.11, you have to add an `[inherit]` section to your project\'s `trac.ini` file. Additionally, you have to move your customized templates and common images from `$prefix/share/trac/...` to the new location.\n\nGlobal options will be merged with the environment-specific options, where local options override global options. The options file is specified as follows:\n{{{\n[inherit]\nfile = /path/to/global/trac.ini\n}}}\nMultiple files can be specified using a comma-separated list.\n\nNote that you can also specify a global option file when creating a new project,  by adding the option `--inherit=/path/to/global/trac.ini` to [TracAdmin#initenv trac-admin]\'s `initenv` command.  If you do not do this but nevertheless intend to use a global option file with your new environment, you will have to go through the newly generated `conf/trac.ini` file and delete the entries that will otherwise override those set in the global file.\n\nThere are two more entries in the [[#inherit-section| [inherit] ]] section, `templates_dir` for sharing global templates and `plugins_dir`, for sharing plugins. Those entries can themselves be specified in the shared configuration file, and in fact, configuration files can even be chained if you specify another `[inherit] file` there.\n\n== Reference for settings\n\nThis is a brief reference of available configuration options.\n\n \'\'Note that the [bitten], [spam-filter] and [vote] sections below are added by plugins enabled on this Trac, and therefore won\'t be part of a default installation.\'\'\n\n[[TracIni]]\n\n== Reference for special sections\n[[PageOutline(3,,inline)]]\n\n=== [components] === #components-section\nThis section is used to enable or disable components provided by plugins, as well as by Trac itself. The component to enable/disable is specified via the name of the option. Whether its enabled is determined by the option value; setting the value to `enabled` or `on` will enable the component, any other value (typically `disabled` or `off`) will disable the component.\n\nThe option name is either the fully qualified name of the components or the module/package prefix of the component. The former enables/disables a specific component, while the latter enables/disables any component in the specified package/module.\n\nConsider the following configuration snippet:\n{{{\n[components]\ntrac.ticket.report.ReportModule = disabled\nwebadmin.* = enabled\n}}}\n\nThe first option tells Trac to disable the [wiki:TracReports report module]. The second option instructs Trac to enable all components in the `webadmin` package. Note that the trailing wildcard is required for module/package matching.\n\nSee the \'\'Plugins\'\' page on \'\'About Trac\'\' to get the list of active components (requires `CONFIG_VIEW` [wiki:TracPermissions permissions].)\n\nSee also: TracPlugins\n\n=== [milestone-groups] === #milestone-groups-section\n\'\'(since 0.11)\'\'\n\nAs the workflow for tickets is now configurable, there can be many ticket states,\nand simply displaying closed tickets vs. all the others is maybe not appropriate \nin all cases. This section enables one to easily create \'\'groups\'\' of states \nthat will be shown in different colors in the milestone progress bar.\n\nExample configuration (the default only has closed and active):\n{{{\nclosed = closed\n# sequence number in the progress bar\nclosed.order = 0\n# optional extra param for the query (two additional columns: created and modified and sort on created)\nclosed.query_args = group=resolution,order=time,col=id,col=summary,col=owner,col=type,col=priority,col=component,col=severity,col=time,col=changetime\n# indicates groups that count for overall completion \nclosed.overall_completion = truepercentage\n\nnew = new\nnew.order = 1\nnew.css_class = new\nnew.label = new\n\n# one catch-all group is allowed\nactive = *\nactive.order = 2\n# CSS class for this interval\nactive.css_class = open\n# Displayed label for this group\nactive.label = in progress\n}}}\n\nThe definition consists in a comma-separated list of accepted status.\nAlso, \'*\' means any status and could be used to associate all remaining\nstates to one catch-all group.\n\nThe CSS class can be one of: new (yellow), open (no color) or\nclosed (green). New styles can easily be added using the following\nselector:  `table.progress td.<class>`\n\n=== [repositories] === #repositories-section\n\n(\'\'since 0.12\'\' multirepos)\n\nOne of the alternatives for registering new repositories is to populate the `[repositories]` section of the trac.ini.\n\nThis is especially suited for setting up convenience aliases, short-lived repositories, or during the initial phases of an installation.\n\nSee [TracRepositoryAdmin#Intrac.ini TracRepositoryAdmin] for details about the format adopted for this section and the rest of that page for the other alternatives.\n\n=== [svn:externals] === #svn:externals-section\n\'\'(since 0.11)\'\'\n\nThe TracBrowser for Subversion can interpret the `svn:externals` property of folders.\nBy default, it only turns the URLs into links as Trac can\'t browse remote repositories.\n\nHowever, if you have another Trac instance (or an other repository browser like [http://www.viewvc.org/ ViewVC]) configured to browse the target repository, then you can instruct Trac which other repository browser to use for which external URL.\n\nThis mapping is done in the `[svn:externals]` section of the TracIni\n\nExample:\n{{{\n[svn:externals]\n1 = svn://server/repos1                       http://trac/proj1/browser/$path?rev=$rev\n2 = svn://server/repos2                       http://trac/proj2/browser/$path?rev=$rev\n3 = http://theirserver.org/svn/eng-soft       http://ourserver/viewvc/svn/$path/?pathrev=25914\n4 = svn://anotherserver.com/tools_repository  http://ourserver/tracs/tools/browser/$path?rev=$rev\n}}}\nWith the above, the `svn://anotherserver.com/tools_repository/tags/1.1/tools` external will be mapped to `http://ourserver/tracs/tools/browser/tags/1.1/tools?rev=` (and `rev` will be set to the appropriate revision number if the external additionally specifies a revision, see the [http://svnbook.red-bean.com/en/1.4/svn.advanced.externals.html SVN Book on externals] for more details).\n\nNote that the number used as a key in the above section is purely used as a place holder, as the URLs themselves can\'t be used as a key due to various limitations in the configuration file parser.\n\nFinally, the relative URLs introduced in [http://subversion.tigris.org/svn_1.5_releasenotes.html#externals Subversion 1.5] are not yet supported.\n\n=== [ticket-custom] === #ticket-custom-section\n\nIn this section, you can define additional fields for tickets. See TracTicketsCustomFields for more details.\n\n=== [ticket-workflow] === #ticket-workflow-section\n\'\'(since 0.11)\'\'\n\nThe workflow for tickets is controlled by plugins. \nBy default, there\'s only a `ConfigurableTicketWorkflow` component in charge. \nThat component allows the workflow to be configured via this section in the trac.ini file.\nSee TracWorkflow for more details.\n\n----\nSee also: TracGuide, TracAdmin, TracEnvironment\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracInstall',1,1327389819647871,'trac','127.0.0.1','= Trac Installation Guide for 0.12 = \n[[TracGuideToc]]\n\nTrac is written in the Python programming language and needs a database, [http://sqlite.org/ SQLite], [http://www.postgresql.org/ PostgreSQL], or [http://mysql.com/ MySQL]. For HTML rendering, Trac uses the [http://genshi.edgewall.org Genshi] templating system.\n\nSince version 0.12, Trac can also be localized, and there\'s probably a translation available for your language. If you want to be able to use the Trac interface in other languages, then make sure you **first** have installed the optional package [#OtherPythonPackages Babel]. Lacking Babel, you will only get the default english version, as usual. If you install Babel later on, you will need to re-install Trac.\n\nIf you\'re interested in contributing new translations for other languages or enhance the existing translations, then please have a look at [trac:wiki:TracL10N TracL10N].\n\nWhat follows are generic instructions for installing and setting up Trac and its requirements. While you may find instructions for installing Trac on specific systems at TracInstallPlatforms on the main Trac site, please be sure to \'\'\'first read through these general instructions\'\'\' to get a good understanding of the tasks involved.\n\n[[PageOutline(2-3,Installation Steps,inline)]]\n\n== Dependencies ==\n=== Mandatory Dependencies\nTo install Trac, the following software packages must be installed:\n\n * [http://www.python.org/ Python], version >= 2.4 and < 3.0\n   (note that we dropped the support for Python 2.3 in this release)\n * [http://peak.telecommunity.com/DevCenter/setuptools setuptools], version >= 0.6\n * [http://genshi.edgewall.org/wiki/Download Genshi], version >= 0.6\n\nYou also need a database system and the corresponding python bindings.\nThe database can be either SQLite, PostgreSQL or MySQL.\n\n==== For the SQLite database #ForSQLite\n\nIf you\'re using Python 2.5 or 2.6, you already have everything you need.\n\nIf you\'re using Python 2.4 and need pysqlite, you can download from \n[http://code.google.com/p/pysqlite/downloads/list google code] the Windows installers or the tar.gz archive for building from source: \n{{{\n$ tar xvfz <version>.tar.gz \n$ cd <version> \n$ python setup.py build_static install \n}}}\n \nThis will extract the SQLite code and build the bindings. \n\nTo install SQLite, your system may require the development headers. Without these you will get various GCC related errors when attempting to build:\n\n{{{\n$ apt-get install libsqlite3-dev\n}}}\n\nSQLite 2.x is no longer supported, and neither is !PySqlite 1.1.x.\n\nA known bug !PySqlite versions 2.5.2-4 prohibits upgrade of trac databases\nfrom 0.11.x to 0.12. Please use versions 2.5.5 and newer or 2.5.1 and\nolder. See [trac:#9434] for more detail.\n\nSee additional information in [trac:PySqlite].\n\n==== For the PostgreSQL database #ForPostgreSQL\n\nYou need to install the database and its Python bindings:\n * [http://www.postgresql.org/ PostgreSQL]\n * [http://pypi.python.org/pypi/psycopg2 psycopg2]\n\nSee [trac:DatabaseBackend#Postgresql DatabaseBackend] for details.\n\n\n==== For the MySQL database #ForMySQL\n\nTrac can now work quite well with MySQL, provided you follow the guidelines.\n\n * [http://mysql.com/ MySQL], version 5.0 or later\n * [http://sf.net/projects/mysql-python MySQLdb], version 1.2.2 or later\n\nIt is \'\'\'very\'\'\' important to read carefully the  [trac:MySqlDb] page before creating the database.\n\n=== Optional Dependencies\n\n==== Version Control System ====\n\n===== Subversion =====\n * [http://subversion.apache.org/ Subversion], 1.5.x or 1.6.x and the \'\'\'\'\'corresponding\'\'\'\'\' Python bindings. Older versions starting from 1.0, like 1.2.4, 1.3.2 or 1.4.2, etc. should still work. For troubleshooting information, check the [trac:TracSubversion#Troubleshooting TracSubversion] page.\n\nThere are [http://subversion.apache.org/packages.html pre-compiled SWIG bindings] available for various platforms. (Good luck finding precompiled SWIG bindings for any Windows package at that listing. TracSubversion points you to [http://alagazam.net Algazam], which works for me under Python 2.6.)\n\nNote that Trac \'\'\'doesn\'t\'\'\' use [http://pysvn.tigris.org/ PySVN], neither does it work yet with the newer `ctype`-style bindings. [Is there a ticket for implementing ctype bindings?]\n\n\n\'\'\'Please note:\'\'\' if using Subversion, Trac must be installed on the \'\'\'same machine\'\'\'. Remote repositories are currently [trac:ticket:493 not supported].\n\n\n===== Others =====\n\nSupport for other version control systems is provided via third-parties. See [trac:PluginList] and [trac:VersioningSystemBackend].\n\n==== Web Server ====\nA web server is optional because Trac is shipped with a server included, see the [#RunningtheStandaloneServer Running the Standalone Server ] section below.\n\nAlternatively you configure Trac to run in any of the following environments.\n * [http://httpd.apache.org/ Apache] with \n   - [http://code.google.com/p/modwsgi/ mod_wsgi], see [wiki:TracModWSGI] and \n     http://code.google.com/p/modwsgi/wiki/IntegrationWithTrac\n   - [http://modpython.org/ mod_python 3.3.1], deprecated: see TracModPython)\n * a [http://www.fastcgi.com/ FastCGI]-capable web server (see TracFastCgi)\n * an [http://tomcat.apache.org/connectors-doc/ajp/ajpv13a.html AJP]-capable web\n   server (see [trac:TracOnWindowsIisAjp])\n * a CGI-capable web server (see TracCgi), \'\'\'but usage of Trac as a cgi script \n   is highly discouraged\'\'\', better use one of the previous options. \n   \n\n==== Other Python Packages ====\n\n * [http://babel.edgewall.org Babel], version >= 0.9.5, \n   needed for localization support[[BR]]\n   \'\'Note: \'\' If you want to be able to use the Trac interface in other languages, then make sure you first have installed the optional package Babel. Lacking Babel, you will only get the default english version, as usual. If you install Babel later on, you will need to re-install Trac. \n * [http://docutils.sourceforge.net/ docutils], version >= 0.3.9 \n   for WikiRestructuredText.\n * [http://pygments.pocoo.org Pygments] for \n   [wiki:TracSyntaxColoring syntax highlighting].\n   [http://silvercity.sourceforge.net/ SilverCity] and/or \n   [http://gnu.org/software/enscript/enscript.html Enscript] may still be used\n   but are deprecated and you really should be using Pygments.\n * [http://pytz.sf.net pytz] to get a complete list of time zones,\n   otherwise Trac will fall back on a shorter list from \n   an internal time zone implementation.\n\n\'\'\'Attention\'\'\': The various available versions of these dependencies are not necessarily interchangable, so please pay attention to the version numbers above. If you are having trouble getting Trac to work please double-check all the dependencies before asking for help on the [trac:MailingList] or [trac:IrcChannel].\n\nPlease refer to the documentation of these packages to find out how they are best installed. In addition, most of the [trac:TracInstallPlatforms platform-specific instructions] also describe the installation of the dependencies. Keep in mind however that the information there \'\'probably concern older versions of Trac than the one you\'re installing\'\' (there are even some pages that are still talking about Trac 0.8!).\n\n\n== Installing Trac ==\n=== Using `easy_install`\nOne way to install Trac is using [http://pypi.python.org/pypi/setuptools setuptools].\nWith setuptools you can install Trac from the subversion repository; \n\nA few examples:\n\n - install Trac 0.12:\n   {{{\n   easy_install Trac==0.12\n   }}}\n\n - install latest development version 0.12dev:\n   {{{\n   easy_install Trac==dev\n   }}}\n   Note that in this case you won\'t have the possibility to run a localized version of Trac;\n   either use a released version or install from source \n\n=== Using `pip`\n\'pip\' is an easy_install replacement that is very useful to quickly install python packages.\nTo get a trac installation up and running in less than 5 minutes:\n\nAssuming you want to have your entire pip installation in /opt/user/trac\n\n - \n{{{\npip -E /opt/user/trac install trac psycopg2 \n}}}\nor\n - \n{{{\npip -E /opt/user/trac install trac mysql-python \n}}}\n\nMake sure your OS specific headers are available for pip to automatically build PostgreSQL (libpq-dev) or MySQL (libmysqlclient-dev) bindings.\n\npip will automatically resolve all dependencies (like Genshi, pygments, etc.) and download the latest packages on pypi.python.org and create a self contained installation in /opt/user/trac \n\nAll commands (tracd, trac-admin) are available in /opt/user/trac/bin . This can also be leveraged for mod_python (using PythonHandler directive) and mod_wsgi (using WSGIDaemonProcess directive)\n\nAdditionally, you can install several trac plugins (listed [http://pypi.python.org/pypi?:action=search&term=trac&submit=search here]) through pip.\n\n\n\n=== From source\nOf course, using the python-typical setup at the top of the source directory also works.\n\nYou can obtain the source for a .tar.gz or .zip file corresponding to a release (e.g. Trac-0.12.tar.gz), or you can get the source directly from the repository (see [trac:SubversionRepository] for details).\n\n{{{\n$ python ./setup.py install\n}}}\n\n\'\'You\'ll need root permissions or equivalent for this step.\'\'\n\nThis will byte-compile the python source code and install it as an .egg file or folder in the `site-packages` directory\nof your Python installation. The .egg will also contain all other resources needed by standard Trac, such as htdocs and templates.\n\nThe script will also install the [wiki:TracAdmin trac-admin] command-line tool, used to create and maintain [wiki:TracEnvironment project environments], as well as the [wiki:TracStandalone tracd] standalone server.\n\nIf you install from source and want to make Trac available in other languages, make sure  Babel is installed. Only then, perform the `install` (or simply redo the `install` once again afterwards if you realize Babel was not yet installed):\n{{{\n$ python ./setup.py install\n}}}\nAlternatively, you can do a `bdist_egg` and copy the .egg from dist/ to the place of your choice, or you can create a Windows installer (`bdist_wininst`).\n\n=== Advanced Options ===\n\nTo install Trac to a custom location, or find out about other advanced installation options, run:\n{{{\neasy_install --help\n}}}\n\nAlso see [http://docs.python.org/inst/inst.html Installing Python Modules] for detailed information.\n\nSpecifically, you might be interested in:\n{{{\neasy_install --prefix=/path/to/installdir\n}}}\nor, if installing Trac to a Mac OS X system:\n{{{\neasy_install --prefix=/usr/local --install-dir=/Library/Python/2.5/site-packages\n}}}\nNote: If installing on Mac OS X 10.6 running {{{ easy_install http://svn.edgewall.org/repos/trac/trunk }}} will install into {{{ /usr/local }}} and {{{ /Library/Python/2.6/site-packages }}} by default\n\nThe above will place your `tracd` and `trac-admin` commands into `/usr/local/bin` and will install the Trac libraries and dependencies into `/Library/Python/2.5/site-packages`, which is Apple\'s preferred location for third-party Python application installations.\n\n\n== Creating a Project Environment ==\n\nA [TracEnvironment Trac environment] is the backend storage where Trac stores information like wiki pages, tickets, reports, settings, etc. An environment is basically a directory that contains a human-readable [TracIni configuration file], and various other files and directories.\n\nA new environment is created using [wiki:TracAdmin trac-admin]:\n{{{\n$ trac-admin /path/to/myproject initenv\n}}}\n\n[TracAdmin trac-admin] will prompt you for the information it needs to create the environment, such as the name of the project and the [TracEnvironment#DatabaseConnectionStrings database connection string]. If you\'re not sure what to specify for one of these options, just press `<Enter>` to use the default value. \n\nUsing the default database connection string in particular will always work as long as you have SQLite installed.\nFor the other [DatabaseBackend database backends] you should plan ahead and already have a database ready to use at this point.\n\nSince 0.12, Trac doesn\'t ask for a [TracEnvironment#SourceCodeRepository source code repository] anymore when creating an environment. Repositories can be [TracRepositoryAdmin added] afterward, or the version control support can be disabled completely if you don\'t need it.\n\nAlso note that the values you specify here can be changed later by directly editing the [TracIni conf/trac.ini] configuration file.\n\nFinally, make sure the user account under which the web front-end runs will have \'\'\'write permissions\'\'\' to the environment directory and all the files inside. This will be the case if you run `trac-admin ... initenv` as this user. If not, you should set the correct user afterwards. For example on Linux, with the web server running as user `apache` and group `apache`, enter:\n{{{\n# chown -R apache.apache /path/to/myproject\n}}}\n\n== Running the Standalone Server ==\n\nAfter having created a Trac environment, you can easily try the web interface by running the standalone server [wiki:TracStandalone tracd]:\n{{{\n$ tracd --port 8000 /path/to/myproject\n}}}\n\nThen, fire up a browser and visit `http://localhost:8000/`. You should get a simple listing of all environments that `tracd` knows about. Follow the link to the environment you just created, and you should see Trac in action. If you only plan on managing a single project with Trac you can have the standalone server skip the environment list by starting it like this:\n{{{\n$ tracd -s --port 8000 /path/to/myproject\n}}}\n\n== Running Trac on a Web Server ==\n\nTrac provides various options for connecting to a \"real\" web server: [wiki:TracCgi CGI], [wiki:TracFastCgi FastCGI], [wiki:TracModWSGI mod_wsgi] and [wiki:TracModPython mod_python]. For decent performance, it is recommended that you use either FastCGI or mod_wsgi.\n\nTrac also supports [trac:TracOnWindowsIisAjp AJP] which may be your choice if you want to connect to IIS.\n\n==== Generating the Trac cgi-bin directory ====\n\nIn order for Trac to function properly with FastCGI you need to have a `trac.fcgi` file and for mod_wsgi a `trac.wsgi` file. These are Python scripts which load the appropriate Python code. They can be generated using the `deploy` option of [wiki:TracAdmin trac-admin].\n\nThere is, however, a bit of a chicken-and-egg problem. The [wiki:TracAdmin trac-admin] command requires an existing environment to function, but complains if the deploy directory already exists. This is a problem, because environments are often stored in a subdirectory of the deploy. The solution is to do something like this:\n{{{\nmkdir -p /usr/share/trac/projects/my-project\ntrac-admin /usr/share/trac/projects/my-project initenv\ntrac-admin /usr/share/trac/projects/my-project deploy /tmp/deploy\nmv /tmp/deploy/* /usr/share/trac\n}}}\n\n==== Setting up the Plugin Cache ====\n\nSome Python plugins need to be extracted to a cache directory. By default the cache resides in the home directory of the current user. When running Trac on a Web Server as a dedicated user (which is highly recommended) who has no home directory, this might prevent the plugins from starting. To override the cache location you can set the PYTHON_EGG_CACHE environment variable. Refer to your server documentation for detailed instructions on how to set environment variables.\n\n== Configuring Authentication ==\n\nThe process of adding, removing, and configuring user accounts for authentication depends on the specific way you run Trac. The basic procedure is described in the [wiki:TracCgi#AddingAuthentication \"Adding Authentication\"] section on the TracCgi page. To learn how to setup authentication for the frontend you\'re using, please refer to one of the following pages:\n\n * TracStandalone if you use the standalone server, `tracd`.\n * TracCgi if you use the CGI or FastCGI web front ends.\n * [wiki:TracModWSGI] if you use the Apache mod_wsgi web front end.\n * TracModPython if you use the Apache mod_python web front end.\n\n\n== Automatic reference to the SVN changesets in Trac tickets ==\n\nYou can configure SVN to automatically add a reference to the changeset into the ticket comments, whenever changes are committed to the repository. The description of the commit needs to contain one of the following formulas:\n * \'\'\'`Refs #123`\'\'\' - to reference this changeset in `#123` ticket\n * \'\'\'`Fixes #123`\'\'\' - to reference this changeset and close `#123` ticket with the default status \'\'fixed\'\'\n\nThis functionality requires a post-commit hook to be installed as described in [wiki:TracRepositoryAdmin#ExplicitSync TracRepositoryAdmin], and enabling the optional commit updater components by adding the following line to the `[components]` section of your [wiki:TracIni#components-section trac.ini], or enabling the components in the \"Plugins\" admin panel.\n{{{\ntracopt.ticket.commit_updater.* = enabled\n}}}\nFor more information, see the documentation of the `CommitTicketUpdater` component in the \"Plugins\" admin panel.\n\n== Using Trac ==\n\nOnce you have your Trac site up and running, you should be able to create tickets, view the timeline, browse your version control repository if configured, etc.\n\nKeep in mind that anonymous (not logged in) users can by default access most but not all of the features. You will need to configure authentication and grant additional [wiki:TracPermissions permissions] to authenticated users to see the full set of features.\n\n\'\' Enjoy! \'\'\n\n[trac:TracTeam The Trac Team]\n\n----\nSee also: [trac:TracInstallPlatforms TracInstallPlatforms], TracGuide, TracCgi, TracFastCgi, TracModPython, [wiki:TracModWSGI], TracUpgrade, TracPermissions\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracInterfaceCustomization',1,1327389819647871,'trac','127.0.0.1','= Customizing the Trac Interface =\n[[TracGuideToc]]\n\n== Introduction ==\nThis page is meant to give users suggestions on how they can customize the look of Trac.  Topics on this page cover editing the HTML templates and CSS files, but not the program code itself.  The topics are intended to show users how they can modify the look of Trac to meet their specific needs.  Suggestions for changes to Trac\'s interface applicable to all users should be filed as tickets, not listed on this page.\n\n== Project Logo and Icon ==\nThe easiest parts of the Trac interface to customize are the logo and the site icon.  Both of these can be configured with settings in [wiki:TracIni trac.ini].\n\nThe logo or icon image should be put in a folder named \"htdocs\" in your project\'s environment folder.  (\'\'Note: in projects created with a Trac version prior to 0.9 you will need to create this folder\'\')\n\n \'\'Note: you can actually put the logo and icon anywhere on your server (as long as it\'s accessible through the web server), and use their absolute or server-relative URLs in the configuration.\'\'\n\nNow configure the appropriate section of your [wiki:TracIni trac.ini]:\n\n=== Logo ===\nChange the `src` setting to `site/` followed by the name of your image file.  The `width` and `height` settings should be modified to match your image\'s dimensions (the Trac chrome handler uses \"`site/`\" for files within the project directory `htdocs` and \"`common/`\" for the common ones).\n\n{{{\n[header_logo]\nsrc = site/my_logo.gif\nalt = My Project\nwidth = 300\nheight = 100\n}}}\n\n=== Icon ===\nIcons should be a 16x16 image in `.gif` or `.ico` format.  Change the `icon` setting to `site/` followed by the name of your icon file.  Icons will typically be displayed by your web browser next to the site\'s URL and in the `Bookmarks` menu.\n\n{{{\n[project]\nicon = site/my_icon.ico\n}}}\n\nNote though that this icon is ignored by Internet Explorer, which only accepts a file named ``favicon.ico`` at the root of the host. To make the project icon work in both IE and other browsers, you can store the icon in the document root of the host, and reference it from ``trac.ini`` as follows:\n\n{{{\n[project]\nicon = /favicon.ico\n}}}\n\nShould your browser have issues with your favicon showing up in the address bar, you may put a \"?\" (less the quotation marks) after your favicon file extension. \n\n{{{\n[project]\nicon = /favicon.ico?\n}}}\n\n== Custom Navigation Entries ==\nThe new [mainnav] and [metanav] can now be used to customize the text and link used for the navigation items, or even to disable them (but not for adding new ones).\n\nIn the following example, we rename the link to the Wiki start \"Home\", and hide the \"Help/Guide\". We also make the \"View Tickets\" entry link to a specific report .\n{{{\n[mainnav]\nwiki.label = Home\ntickets.href = /report/24\n\n[metanav]\nhelp = disabled\n}}}\n\nSee also TracNavigation for a more detailed explanation of the mainnav and metanav terms.\n\n== Site Appearance == #SiteAppearance\n\nTrac is using [http://genshi.edgewall.org Genshi] as the templating engine. Documentation is yet to be written, in the meantime the following tip should work.\n\nSay you want to add a link to a custom stylesheet, and then your own\nheader and footer. Save the following content as \'site.html\' inside your projects templates directory (each Trac project can have their own site.html), e.g. {{{/path/to/env/templates/site.html}}}:\n\n{{{\n#!xml\n<html xmlns=\"http://www.w3.org/1999/xhtml\"\n      xmlns:py=\"http://genshi.edgewall.org/\"\n      py:strip=\"\">\n\n  <!--! Add site-specific style sheet -->\n  <head py:match=\"head\" py:attrs=\"select(\'@*\')\">\n    ${select(\'*|comment()|text()\')}\n    <link rel=\"stylesheet\" type=\"text/css\"\n          href=\"${href.chrome(\'site/style.css\')}\" />\n  </head>\n\n  <body py:match=\"body\" py:attrs=\"select(\'@*\')\">\n    <!--! Add site-specific header -->\n    <div id=\"siteheader\">\n      <!--! Place your header content here... -->\n    </div>\n\n    ${select(\'*|text()\')}\n\n    <!--! Add site-specific footer -->\n    <div id=\"sitefooter\">\n      <!--! Place your footer content here... -->\n    </div>\n  </body>\n</html>\n}}}\n\nThose who are familiar with XSLT may notice that Genshi templates bear some similarities. However, there are some Trac specific features - for example \'\'\'${href.chrome(\'site/style.css\')}\'\'\' attribute references template placed into environment\'s \'\'htdocs/\'\'  In a similar fashion \'\'\'${chrome.htdocs_location}\'\'\' is used to specify common \'\'htdocs/\'\' directory from Trac installation.\n\n`site.html` is one file to contain all your modifications. It usually works by the py:match (element or attribute), and it allows you to modify the page as it renders - the matches hook onto specific sections depending on what it tries to find\nand modify them.\nSee [http://groups.google.com/group/trac-users/browse_thread/thread/70487fb2c406c937/ this thread] for a detailed explanation of the above example `site.html`.\nA site.html can contain any number of such py:match sections for whatever you need to modify. This is all [http://genshi.edgewall.org/ Genshi], so the docs on the exact syntax can be found there.\n\n\nExample snippet of adding introduction text to the new ticket form (hide when preview):\n\n{{{\n#!xml\n<form py:match=\"div[@id=\'content\' and @class=\'ticket\']/form\" py:attrs=\"select(\'@*\')\">\n  <py:if test=\"req.environ[\'PATH_INFO\'] == \'/newticket\' and (not \'preview\' in req.args)\">\n    <p>Please make sure to search for existing tickets before reporting a new one!</p>\n  </py:if>\n  ${select(\'*\')} \n</form>\n}}}\n\nThis example illustrates a technique of using \'\'\'`req.environ[\'PATH_INFO\']`\'\'\' to limit scope of changes to one view only. For instance, to make changes in site.html only for timeline and avoid modifying other sections - use  \'\'`req.environ[\'PATH_INFO\'] == \'/timeline\'`\'\' condition in <py:if> test.\n\nMore examples snippets for `site.html` can be found at [trac:wiki:CookBook/SiteHtml CookBook/SiteHtml].\n\nExample snippets for `style.css` can be found at [trac:wiki:CookBook/SiteStyleCss CookBook/SiteStyleCss].\n\nIf the environment is upgraded from 0.10 and a `site_newticket.cs` file already exists, it can actually be loaded by using a workaround - providing it contains no ClearSilver processing. In addition, as only one element can be imported, the content needs some sort of wrapper such as a `<div>` block or other similar parent container. The XInclude namespace must be specified to allow includes, but that can be moved to document root along with the others:\n{{{\n#!xml\n<form py:match=\"div[@id=\'content\' and @class=\'ticket\']/form\" py:attrs=\"select(\'@*\')\"\n        xmlns:xi=\"http://www.w3.org/2001/XInclude\">\n  <py:if test=\"req.environ[\'PATH_INFO\'] == \'/newticket\' and (not \'preview\' in req.args)\"> \n    <xi:include href=\"site_newticket.cs\"><xi:fallback /></xi:include>\n  </py:if>\n  ${select(\'*\')} \n</form>\n}}}\n\nAlso note that the `site.html` (despite its name) can be put in a common templates directory - see the `[inherit] templates_dir` option. This could provide easier maintainence (and a migration path from 0.10 for larger installations) as one new global `site.html` file can be made to include any existing header, footer and newticket snippets.\n\n== Project List == #ProjectList\n\nYou can use a custom Genshi template to display the list of projects if you are using Trac with multiple projects.  \n\nThe following is the basic template used by Trac to display a list of links to the projects.  For projects that could not be loaded it displays an error message. You can use this as a starting point for your own index template.\n\n{{{\n#!text/html\n<!DOCTYPE html\n    PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"\n    \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\"\n      xmlns:py=\"http://genshi.edgewall.org/\"\n      xmlns:xi=\"http://www.w3.org/2001/XInclude\">\n  <head>\n    <title>Available Projects</title>\n  </head>\n  <body>\n    <h1>Available Projects</h1>\n    <ul>\n      <li py:for=\"project in projects\" py:choose=\"\">\n        <a py:when=\"project.href\" href=\"$project.href\"\n           title=\"$project.description\">$project.name</a>\n        <py:otherwise>\n          <small>$project.name: <em>Error</em> <br /> ($project.description)</small>\n        </py:otherwise>\n      </li>\n    </ul>\n  </body>\n</html>\n}}}\n\nOnce you\'ve created your custom template you will need to configure the webserver to tell Trac where the template is located (pls verify ... not yet changed to 0.11):\n\nFor [wiki:TracModWSGI mod_wsgi]:\n{{{\nos.environ[\'TRAC_ENV_INDEX_TEMPLATE\'] = \'/path/to/template\'\n}}}\n\nFor [wiki:TracFastCgi FastCGI]:\n{{{\nFastCgiConfig -initial-env TRAC_ENV_PARENT_DIR=/parent/dir/of/projects \\\n              -initial-env TRAC_ENV_INDEX_TEMPLATE=/path/to/template\n}}}\n\nFor [wiki:TracModPython mod_python]:\n{{{\nPythonOption TracEnvParentDir /parent/dir/of/projects\nPythonOption TracEnvIndexTemplate /path/to/template\n}}}\n\nFor [wiki:TracCgi CGI]:\n{{{\nSetEnv TRAC_ENV_INDEX_TEMPLATE /path/to/template\n}}}\n\nFor [wiki:TracStandalone], you\'ll need to set up the `TRAC_ENV_INDEX_TEMPLATE` environment variable in the shell used to launch tracd:\n - Unix\n   {{{\n#!sh\n$ export TRAC_ENV_INDEX_TEMPLATE=/path/to/template\n   }}}\n - Windows\n   {{{\n#!sh\n$ set TRAC_ENV_INDEX_TEMPLATE=/path/to/template\n   }}}\n\n== Project Templates ==\n\nThe appearance of each individual Trac environment (that is, instance of a project) can be customized independently of other projects, even those hosted by the same server. The recommended way is to use a `site.html` template (see [#SiteAppearance]) whenever possible. Using `site.html` means changes are made to the original templates as they are rendered, and you should not normally need to redo modifications whenever Trac is upgraded. If you do make a copy of `theme.html` or any other Trac template, you need to migrate your modifiations to the newer version - if not, new Trac features or bug fixes may not work as expected.\n\nWith that word of caution, any Trac template may be copied and customized. The default Trac templates are located inside the installed Trac egg (`/usr/lib/pythonVERSION/site-packages/Trac-VERSION.egg/trac/templates, .../trac/ticket/templates, .../trac/wiki/templates, ++`). The [#ProjectList] template file is called `index.html`, while the template responsible for main layout is called `theme.html`. Page assets such as images and CSS style sheets are located in the egg\'s `trac/htdocs` directory.\n\nHowever, do not edit templates or site resources inside the Trac egg - installing Trac again can completely delete your modifications. Instead use one of two alternatives:\n * For a modification to one project only, copy the template to project `templates` directory.\n * For a modification shared by several projects, copy the template to a shared location and have each project point to this location using the `[inherit] templates_dir =` trac.ini option.\n\nTrac resolves requests for a template by first looking inside the project, then in any inherited templates location, and finally inside the Trac egg.\n\nTrac caches templates in memory by default to improve performance. To apply a template you need to restart the server.\n----\nSee also TracGuide, TracIni\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracLinks',1,1327389819647871,'trac','127.0.0.1','= Trac Links =\n[[TracGuideToc]]\n\nTracLinks are a fundamental feature of Trac, because they allow easy hyperlinking between the various entities in the systemâ€”such as tickets, reports, changesets, Wiki pages, milestones, and source filesâ€”from anywhere WikiFormatting is used.\n\nTracLinks are generally of the form \'\'\'type:id\'\'\' (where \'\'id\'\' represents the\nnumber, name or path of the item) though some frequently used kinds of items\nalso have short-hand notations.\n\n== Where to use TracLinks ==\nYou can use TracLinks in:\n\n * Source code (Subversion) commit messages\n * Wiki pages\n * Full descriptions for tickets, reports and milestones\n\nand any other text fields explicitly marked as supporting WikiFormatting.\n\n== Overview ==\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n Wiki pages :: `CamelCase` or `wiki:CamelCase`\n Parent page :: `[..]`\n Tickets :: `#1` or `ticket:1`\n Ticket comments :: `comment:1:ticket:2`\n Reports :: `{1}` or `report:1`\n Milestones :: `milestone:1.0`\n Attachment :: `attachment:example.tgz` (for current page attachment), `attachment:attachment.1073.diff:ticket:944` (absolute path)\n Changesets :: `r1`, `[1]`, `changeset:1` or (restricted) `[1/trunk]`, `changeset:1/trunk`\n Revision log :: `r1:3`, `[1:3]` or `log:@1:3`, `log:trunk@1:3`, `[2:5/trunk]`\n Diffs :: `diff:@1:3`, `diff:tags/trac-0.9.2/wiki-default//tags/trac-0.9.3/wiki-default` \n          or `diff:trunk/trac@3538//sandbox/vc-refactoring@3539`\n Files :: `source:trunk/COPYING`, `source:/trunk/COPYING@200` (at version 200), `source:/trunk/COPYING@200#L25` (at version 200, line 25)\n}}}\n{{{#!td\n Wiki pages :: CamelCase or wiki:CamelCase\n Parent page :: [..]\n Tickets :: #1 or ticket:1\n Ticket comments :: comment:1:ticket:2 \n Reports :: {1} or report:1\n Milestones :: milestone:1.0\n Attachment :: attachment:example.tgz (for current page attachment), attachment:attachment.1073.diff:ticket:944 (absolute path)\n Changesets :: r1, [1], changeset:1 or (restricted) [1/trunk], changeset:1/trunk\n Revision log :: r1:3, [1:3] or log:@1:3, log:trunk@1:3, [2:5/trunk]\n Diffs :: diff:@1:3, diff:tags/trac-0.9.2/wiki-default//tags/trac-0.9.3/wiki-default \n          or diff:trunk/trac@3538//sandbox/vc-refactoring@3539\n Files :: source:trunk/COPYING, source:/trunk/COPYING@200 (at version 200), source:/trunk/COPYING@200#L25 (at version 200, line 25)\n}}}\n\n\'\'\'Note:\'\'\' The wiki:CamelCase form is rarely used, but it can be convenient to refer to\npages whose names do not follow WikiPageNames rules, i.e., single words,\nnon-alphabetic characters, etc. See WikiPageNames for more about features specific\nto links to Wiki page names.\n\n\n{{{#!table class=\"\"\n|||| Trac links using the full (non-shorthand) notation can also be given a custom link title like this: ||\n{{{#!td\n{{{\n[ticket:1 This is a link to ticket number one] or\n[[ticket:1|This is another link to ticket number one]].\n}}}\n}}}\n{{{#!td\n[ticket:1 This is a link to ticket number one] or\n[[ticket:1|This is another link to ticket number one]].\n}}}\n|--------------------------------------------------------------------------------------\n|||| If the title is omitted, only the id (the part after the colon) is displayed:  ||\n{{{#!td\n{{{\n[ticket:1] or [[ticket:2]]\n}}}\n}}}\n{{{#!td\n[ticket:1] or [[ticket:2]]\n}}}\n|--------------------------------------------------------------------------------------\n|||| `wiki` is the default if the namespace part of a full link is omitted:  || \n{{{#!td\n{{{\n[SandBox the sandbox] or\n[[SandBox|the sandbox]]\n}}}\n}}}\n{{{#!td\n[SandBox the sandbox] or\n[[SandBox|the sandbox]]\n}}}\n|--------------------------------------------------------------------------------------\n|||| The short form \'\'realm:target\'\' can also be wrapped within a <...> pair, [[br]] which allow for arbitrary characters (i.e. anything but >)  ||\n{{{#!td\n{{{\n<wiki:Strange(page@!)>\n}}}\n}}}\n{{{#!td\n<wiki:Strange(page@!)>\n}}}\n}}}\n\nTracLinks are a very simple idea, but actually allow quite a complex network of information. In practice, it\'s very intuitive and simple to use, and we\'ve found the \"link trail\" extremely helpful to better understand what\'s happening in a project or why a particular change was made.\n\n\n== Advanced use of TracLinks ==\n\n=== Relative links ===\n\nTo create a link to a specific anchor in a page, use \'#\':\n{{{\n [#Relativelinks relative links] or [[#Relativelinks|relative links]]\n}}}\nDisplays:\n  [#Relativelinks relative links] or [[#Relativelinks|relative links]]\n\nHint: when you move your mouse over the title of a section, a \'Â¶\' character will be displayed. This is a link to that specific section and you can use this to copy the `#...` part inside a relative link to an anchor.\n\nTo create a link to a [trac:SubWiki SubWiki]-page just use a \'/\':\n{{{\n WikiPage/SubWikiPage or ./SubWikiPage\n}}}\n\nTo link from a [trac:SubWiki SubWiki] page to a parent, simply use a \'..\':\n{{{\n  [..] or [[..]]\n}}}\n  [..] or [[..]]\n\nTo link from a [trac:SubWiki SubWiki] page to a [=#sibling sibling] page, use a \'../\':\n{{{\n  [../Sibling see next sibling] or [[../Sibling|see next sibling]]\n}}}\n  [../Sibling see next sibling] or [[../Sibling|see next sibling]]\n\nBut in practice you often won\'t need to add the `../` prefix to link to a sibling page.\nFor resolving the location of a wiki link, it\'s the target page closest in the hierarchy\nto the page where the link is written which will be selected. So for example, within \na sub-hierarchy, a sibling page will be targeted in preference to a toplevel page.\nThis makes it easy to copy or move pages to a sub-hierarchy by [[WikiNewPage#renaming|renaming]] without having to adapt the links.\n\nIn order to link explicitly to a [=#toplevel toplevel] Wiki page,\nuse the `wiki:/` prefix.\nBe careful **not** to use the `/` prefix alone, as this corresponds to the\n[#Server-relativelinks] syntax and with such a link you will lack the `/wiki/` \npart in the resulting URL.\n\n\'\'(Changed in 0.11)\'\' Note that in Trac 0.10, using e.g. `[../newticket]`  may have worked for linking to the `/newticket` top-level URL, but since 0.11, such a link will stay in the wiki namespace and therefore link to a sibling page. \nSee [#Server-relativelinks] for the new syntax.\n\n=== InterWiki links ===\n\nOther prefixes can be defined freely and made to point to resources in other Web applications. The definition of those prefixes as well as the URLs of the corresponding Web applications is defined in a special Wiki page, the InterMapTxt page. Note that while this could be used to create links to other Trac environments, there\'s a more specialized way to register other Trac environments which offers greater flexibility.\n\n=== InterTrac links ===\n\nThis can be seen as a kind of InterWiki link specialized for targeting other Trac projects.\n\nAny type of Trac link can be written in one Trac environment and actually refer to resources in another Trac environment. All that is required is to prefix the Trac link with the name of the other Trac environment followed by a colon. The other Trac environment must be registered on the InterTrac page. \n\nA distinctive advantage of InterTrac links over InterWiki links is that the shorthand form of Trac links (e.g. `{}`, `r`, `#`) can also be used. For example if T was set as an alias for Trac, links to Trac tickets can be written #T234, links to Trac changesets can be written [trac 1508].\nSee InterTrac for the complete details. \n\n=== Server-relative links ===\n\nIt is often useful to be able to link to objects in your project that\nhave no built-in Trac linking mechanism, such as static resources, `newticket`,\na shared `/register` page on the server, etc.\n\nTo link to resources inside the project, use either an absolute path from the project root, \nor a relative link from the URL of the current page (\'\'Changed in 0.11\'\'):\n\n{{{\n[/newticket Create a new ticket] or [[//newticket|Create a new ticket]]\n[/ home] or [[/|home]]\n}}}\n\nDisplay: [/newticket Create a new ticket] or [[//newticket|Create a new ticket]]\n[/ home] or [[/|home]]\n\nTo link to another location on the server (possibly outside the project but on the same host), use the `//` prefix (\'\'Changed in 0.11\'\'):\n\n{{{\n[//register Register Here] or [[//register|Register Here]]\n}}}\n\nDisplay: [//register Register Here] or [[//register|Register Here]]\n\n=== Quoting space in TracLinks ===\n\nImmediately after a TracLinks prefix, targets containing space characters should\nbe enclosed in a pair of quotes or double quotes.\nExamples:\n * !wiki:\"The whitespace convention\"\n * !attachment:\'the file.txt\' or\n * !attachment:\"the file.txt\" \n * !attachment:\"the file.txt:ticket:123\" \n\nNote that by using [trac:WikiCreole] style links, it\'s quite natural to write links containing spaces:\n * ![[The whitespace convention]]\n * ![[attachment:the file.txt]]\n\n=== Escaping Links ===\n\nTo prevent parsing of a !TracLink, you can escape it by preceding it with a \'!\' (exclamation mark).\n{{{\n !NoLinkHere.\n ![42] is not a link either.\n}}}\n\nDisplay:\n !NoLinkHere.\n ![42] is not a link either.\n\n\n=== Parameterized Trac links ===\n\nMany Trac resources have more than one way to be rendered, depending on some extra parameters. For example, a Wiki page can accept a `version` or a `format` parameter, a report can make use of dynamic variables, etc.\n\nTrac links can support an arbitrary set of parameters, written in the same way as they would be for the corresponding URL. Some examples:\n - `wiki:WikiStart?format=txt`\n - `ticket:1?version=1`\n - `[/newticket?component=module1 create a ticket for module1]`\n - `[/newticket?summary=Add+short+description+here create a ticket with URL with spaces]`\n\n\n== TracLinks Reference ==\nThe following sections describe the individual link types in detail, as well as notes on advanced usage of links.\n\n=== attachment: links ===\n\nThe link syntax for attachments is as follows:\n * !attachment:the_file.txt creates a link to the attachment the_file.txt of the current object\n * !attachment:the_file.txt:wiki:MyPage creates a link to the attachment the_file.txt of the !MyPage wiki page\n * !attachment:the_file.txt:ticket:753 creates a link to the attachment the_file.txt of the ticket 753\n\nNote that the older way, putting the filename at the end, is still supported: !attachment:ticket:753:the_file.txt.\n\nIf you\'d like to create a direct link to the content of the attached file instead of a link to the attachment page, simply use `raw-attachment:` instead of `attachment:`.\n\nThis can be useful for pointing directly to an HTML document, for example. Note that for this use case, you\'d have to allow the web browser to render the content by setting `[attachment] render_unsafe_content = yes` (see TracIni#attachment-section). Caveat: only do that in environments for which you\'re 100% confident you can trust the people who are able to attach files, as otherwise this would open up your site to [wikipedia:Cross-site_scripting cross-site scripting] attacks.\n\nSee also [#export:links].\n\n=== comment: links ===\n\nWhen you\'re inside a given ticket, you can simply write e.g. !comment:3 to link to the third change comment.\nIt is possible to link to a comment of a specific ticket from anywhere using one of the following syntax:\n - `comment:3:ticket:123` \n - `ticket:123#comment:3` (note that you can\'t write `#123#!comment:3`!)\nIt is also possible to link to the ticket\'s description using one of the following syntax:\n - `comment:description` (within the ticket)\n - `comment:description:ticket:123`\n - `ticket:123#comment:description`\n\n=== query: links ===\n\nSee TracQuery#UsingTracLinks and [#ticket:links].\n\n=== search: links ===\n\nSee TracSearch#SearchLinks \n\n=== ticket: links ===\n \'\'alias:\'\' `bug:`\n\nBesides the obvious `ticket:id` form, it is also possible to specify a list of tickets or even a range of tickets instead of the `id`. This generates a link to a custom query view containing this fixed set of tickets.\n\nExample: \n - `ticket:5000-6000`\n - `ticket:1,150`\n\n\'\'(since Trac 0.11)\'\'\n\n=== timeline: links ===\n\nLinks to the timeline can be created by specifying a date in the ISO:8601 format. The date can be optionally followed by a time specification. The time is interpreted as being UTC time, but alternatively you can specify your local time, followed by your timezone if you don\'t want to compute the UTC time.\n\nExamples:\n - `timeline:2008-01-29`\n - `timeline:2008-01-29T15:48`\n - `timeline:2008-01-29T15:48Z`\n - `timeline:2008-01-29T16:48+01`\n\n\'\'(since Trac 0.11)\'\'\n\n=== wiki: links ===\n\nSee WikiPageNames and [#QuotingspaceinTracLinks quoting space in TracLinks] above.\n\n=== Version Control related links ===\n\nIt should be noted that multiple repository support works by creating a kind of virtual namespace for versioned files in which the toplevel folders correspond to the repository names. Therefore, in presence of multiple repositories, a \'\'/path\'\' specification in the syntax of links detailed below should start with the name of the repository. If omitted, the default repository is used. In case a toplevel folder of the default repository has the same name as a repository, the latter \"wins\". One can always access such folder by fully qualifying it (the default repository can be an alias of a named repository, or conversely, it is always possible to create an alias for the default repository, ask your Trac administrator).\n\nFor example, `source:/trunk/COPYING` targets the path `/trunk/COPYING` in the default repository, whereas `source:/projectA/trunk/COPYING` targets the path `/trunk/COPYING` in the repository named `projectA`. This can be the same file if `\'projectA\'` is an alias to the default repository or if `\'\'` (the default repository) is an alias to `\'projectA\'`.\n\n==== source: links ====\n \'\'aliases:\'\' `browser:`, `repos:`\n\nThe default behavior for a source:/some/path link is to open the browser in that directory directory \nif the path points to a directory or to show the latest content of the file.\n\nIt\'s also possible to link directly to a specific revision of a file like this:\n - `source:/some/file@123` - link to the file\'s revision 123\n - `source:/some/file@head` - link explicitly to the latest revision of the file\n\nIf the revision is specified, one can even link to a specific line number:\n - `source:/some/file@123#L10`\n - `source:/tag/0.10@head#L10`\n\nFinally, one can also highlight an arbitrary set of lines:\n - `source:/some/file@123:10-20,100,103#L99` - highlight lines 10 to 20, and lines 100 and 103.\n   \'\'(since 0.11)\'\'\n\nNote that in presence of multiple repositories, the name of the repository is simply integrated in the path you specify for `source:` (e.g. `source:reponame/trunk/README`). \'\'(since 0.12)\'\'\n\n==== export: links ====\n\nTo force the download of a file in the repository, as opposed to displaying it in the browser, use the `export` link.  Several forms are available:\n * `export:/some/file` - get the HEAD revision of the specified file\n * `export:123:/some/file` - get revision 123 of the specified file\n * `export:/some/file@123` - get revision 123 of the specified file\n\nThis can be very useful for displaying XML or HTML documentation with correct stylesheets and images, in case that has been checked in into the repository. Note that for this use case, you\'d have to allow the web browser to render the content by setting `[browser] render_unsafe_content = yes` (see TracIni#browser-section), otherwise Trac will force the files to be downloaded as attachments for security concerns. \n\nIf the path is to a directory in the repository instead of a specific file, the source browser will be used to display the directory (identical to the result of `source:/some/dir`).\n\n==== log: links ====\n\nThe `log:` links are used to display revision ranges. In its simplest form, it can link to the latest revisions of the specified path, but it can also support displaying an arbitrary set of revisions.\n - `log:/` - the latest revisions starting at the root of the repository\n - `log:/trunk/tools` - the latest revisions in `trunk/tools`\n - `log:/trunk/tools@10000` - the revisions in `trunk/tools` starting from  revision 10000\n - `log:@20788,20791:20795` - list revision 20788 and the revisions from 20791 to 20795 \n - `log:/trunk/tools@20788,20791:20795` - list revision 20788 and the revisions from 20791 to 20795 which affect the given path\n\nThere are short forms for revision ranges as well:\n - `[20788,20791:20795]`\n - `[20788,20791:20795/trunk/tools]`\n - `r20791:20795` (but not `r20788,20791:20795` nor `r20791:20795/trunk`)\n\nFinally, note that in all of the above, a revision range can be written either as `x:y` or `x-y`.\n\nIn the presence of multiple repositories, the name of the repository should be specified as the first part of the path, e.g. `log:repos/branches` or `[20-40/repos]`.\n\n----\nSee also: WikiFormatting, TracWiki, WikiPageNames, InterTrac, InterWiki\n \n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracLogging',1,1327389819647871,'trac','127.0.0.1','= Trac Logging =\n[[TracGuideToc]]\n\nTrac supports logging of system messages using the standard [http://docs.python.org/lib/module-logging.html logging module] that comes with Python.\n\nLogging is configured in the `[logging]` section in [wiki:TracIni#logging-section trac.ini].\n\n== Supported Logging Methods ==\n\nThe log method is set using the `log_type` option in [wiki:TracIni#logging-section trac.ini], which takes any of the following values:\n\n \'\'\'none\'\':: Suppress all log messages.\n \'\'\'file\'\'\':: Log messages to a file, specified with the `log_file` option in [wiki:TracIni#logging-section trac.ini]. Relative paths in `log_file` are resolved relative to the `log` directory of the environment.\n \'\'\'stderr\'\'\':: Output all log entries to console ([wiki:TracStandalone tracd] only).\n \'\'\'syslog\'\'\':: (UNIX) Send all log messages to the local syslogd via named pipe `/dev/log`. By default, syslog will write them to the file /var/log/messages.\n \'\'\'eventlog\'\'\':: (Windows) Use the system\'s NT Event Log for Trac logging.\n\n== Log Levels ==\n\nThe verbosity level of logged messages can be set using the `log_level` option in [wiki:TracIni#logging-section trac.ini]. The log level defines the minimum level of urgency required for a message to be logged, and those levels are:\n\n \'\'\'CRITICAL\'\'\':: Log only the most critical (typically fatal) errors.\n \'\'\'ERROR\'\'\':: Log failures, bugs and errors. \n \'\'\'WARN\'\'\':: Log warnings, non-interrupting events.\n \'\'\'INFO\'\'\':: Diagnostic information, log information about all processing.\n \'\'\'DEBUG\'\'\':: Trace messages, profiling, etc.\n\nNote that starting with Trac 0.11.5 you can in addition enable logging of SQL statements, at debug level. This is turned off by default, as it\'s very verbose (set `[trac] debug_sql = yes` in TracIni to activate).\n\n== Log Format ==\n\nStarting with Trac 0.10.4 (see [trac:#2844 #2844]), it is possible to set the output format for log entries. This can be done through the `log_format` option in [wiki:TracIni#logging-section trac.ini]. The format is a string which can contain any of the [http://docs.python.org/lib/node422.html Python logging Formatter variables]. Additonally, the following Trac-specific variables can be used:\n \'\'\'$(basename)s\'\'\':: The last path component of the current environment.\n \'\'\'$(path)s\'\'\':: The absolute path for the current environment.\n \'\'\'$(project)s\'\'\':: The originating project\'s name.\n\nNote that variables are identified using a dollar sign (`$(...)s`) instead of percent sign (`%(...)s`).\n\nThe default format is:\n{{{\nlog_format = Trac[$(module)s] $(levelname)s: $(message)s\n}}}\n\nIn a multi-project environment where all logs are sent to the same place (e.g. `syslog`), it makes sense to add the project name. In this example we use `basename` since that can generally be used to identify a project:\n{{{\nlog_format = Trac[$(basename)s:$(module)s] $(levelname)s: $(message)s\n}}}\n\n----\nSee also: TracIni, TracGuide, TracEnvironment\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracModPython',1,1327389819647871,'trac','127.0.0.1','= Trac and mod_python =\n[[TracGuideToc]]\n\nTrac supports [http://www.modpython.org/ mod_python], which speeds up Trac\'s response times considerably, especially compared to [TracCgi CGI], and permits use of many Apache features not possible with [wiki:TracStandalone tracd]/mod_proxy.\n\nThese instructions are for Apache 2; if you are still using Apache 1.3, you may have some luck with [trac:wiki:TracModPython2.7 TracModPython2.7].\n\n== A Word of Warning ==\n\nAs of 16^th^ June 2010, the mod_python project is officially dead.  If you are considering using mod_python for a new installation, \'\'\'please don\'t\'\'\'!  There are known issues which will not be fixed and there are now better alternatives.  Check out the main TracInstall pages for your target version for more information.\n\n== Simple configuration ==\n\nIf you just installed mod_python, you may have to add a line to load the module in the Apache configuration:\n{{{\nLoadModule python_module modules/mod_python.so\n}}}\n\n\'\'Note: The exact path to the module depends on how the HTTPD installation is laid out.\'\'\n\nOn Debian using apt-get\n{{{\napt-get install libapache2-mod-python libapache2-mod-python-doc\n}}}\n(Still on Debian) after you have installed mod_python, you must enable the modules in apache2 (equivalent of the above Load Module directive):\n{{{\na2enmod python\n}}}\nOn Fedora use, using yum:\n{{{\nyum install mod_python\n}}}\nYou can test your mod_python installation by adding the following to your httpd.conf.  You should remove this when you are done testing for security reasons. Note: mod_python.testhandler is only available in mod_python 3.2+.\n{{{\n#!xml\n<Location /mpinfo>\n   SetHandler mod_python\n   PythonInterpreter main_interpreter\n   PythonHandler mod_python.testhandler\n</Location>\n}}}\n\nA simple setup of Trac on mod_python looks like this:\n{{{\n#!xml\n<Location /projects/myproject>\n   SetHandler mod_python\n   PythonInterpreter main_interpreter\n   PythonHandler trac.web.modpython_frontend \n   PythonOption TracEnv /var/trac/myproject\n   PythonOption TracUriRoot /projects/myproject\n</Location>\n}}}\n\nThe option \'\'\'`TracUriRoot`\'\'\' may or may not be necessary in your setup. Try your configuration without it; if the URLs produced by Trac look wrong, if Trac does not seem to recognize URLs correctly, or you get an odd \"No handler matched request to...\" error, add the \'\'\'`TracUriRoot`\'\'\' option.  You will notice that the `Location` and \'\'\'`TracUriRoot`\'\'\' have the same path.\n\nThe options available are\n{{{\n    # For a single project\n    PythonOption TracEnv /var/trac/myproject\n    # For multiple projects\n    PythonOption TracEnvParentDir /var/trac/myprojects\n    # For the index of multiple projects\n    PythonOption TracEnvIndexTemplate /srv/www/htdocs/trac/project_list_template.html\n    # A space delimitted list, with a \",\" between key and value pairs.\n    PythonOption TracTemplateVars key1,val1 key2,val2\n    # Useful to get the date in the wanted order\n    PythonOption TracLocale en_GB.UTF8\n    # See description above        \n    PythonOption TracUriRoot /projects/myproject\n}}}\n\n=== Python Egg Cache ===\n\nCompressed python eggs like Genshi are normally extracted into a directory named `.python-eggs` in the users home directory. Since apache\'s home usually is not writable an alternate egg cache directory can be specified like this:\n{{{\nPythonOption PYTHON_EGG_CACHE /var/trac/myprojects/egg-cache\n}}}\n\nor you can uncompress the Genshi egg to resolve problems extracting from it.\n=== Configuring Authentication ===\n\nCreating password files and configuring authentication works similar to the process for [wiki:TracCgi#AddingAuthentication CGI]:\n{{{\n#!xml\n<Location /projects/myproject/login>\n  AuthType Basic\n  AuthName \"myproject\"\n  AuthUserFile /var/trac/myproject/.htpasswd\n  Require valid-user\n</Location>\n}}}\n\nConfiguration for mod_ldap authentication in Apache is a bit tricky (httpd 2.2.x and OpenLDAP: slapd 2.3.19)\n\n1. You need to load the following modules in Apache httpd.conf\n{{{\nLoadModule ldap_module modules/mod_ldap.so\nLoadModule authnz_ldap_module modules/mod_authnz_ldap.so\n}}}\n\n2. Your httpd.conf also needs to look something like:\n\n{{{\n#!xml\n<Location /trac/>\n  SetHandler mod_python\n  PythonInterpreter main_interpreter\n  PythonHandler trac.web.modpython_frontend\n  PythonOption TracEnv /home/trac/\n  PythonOption TracUriRoot /trac/\n  Order deny,allow\n  Deny from all\n  Allow from 192.168.11.0/24\n  AuthType Basic\n  AuthName \"Trac\"\n  AuthBasicProvider \"ldap\"\n  AuthLDAPURL \"ldap://127.0.0.1/dc=example,dc=co,dc=ke?uid?sub?(objectClass=inetOrgPerson)\"\n  authzldapauthoritative Off\n  require valid-user\n</Location>\n}}}\n\nOr the LDAP interface to a Microsoft Active Directory:\n\n{{{\n#!xml\n<Location /trac/>\n  SetHandler mod_python\n  PythonInterpreter main_interpreter\n  PythonHandler trac.web.modpython_frontend\n  PythonOption TracEnv /home/trac/\n  PythonOption TracUriRoot /trac/\n  Order deny,allow\n  Deny from all\n  Allow from 192.168.11.0/24\n  AuthType Basic\n  AuthName \"Trac\"\n  AuthBasicProvider \"ldap\"\n  AuthLDAPURL \"ldap://adserver.company.com:3268/DC=company,DC=com?sAMAccountName?sub?(objectClass=user)\"\n  AuthLDAPBindDN       ldap-auth-user@company.com\n  AuthLDAPBindPassword \"the_password\"\n  authzldapauthoritative Off\n  # require valid-user\n  require ldap-group CN=Trac Users,CN=Users,DC=company,DC=com\n</Location>\n}}}\n\nNote 1: This is the case where the LDAP search will get around the multiple OUs, conecting to Global Catalog Server portion of AD (Notice the port is 3268, not the normal LDAP 389). The GCS is basically a \"flattened\" tree which allows searching for a user without knowing to which OU they belong.\n\nNote 2: Active Directory requires an authenticating user/password to access records (AuthLDAPBindDN and AuthLDAPBindPassword).\n\nNote 3: The directive \"require ldap-group ...\"  specifies an AD group whose members are allowed access.\n\n\n=== Setting the Python Egg Cache ===\n\nIf the Egg Cache isn\'t writeable by your Web server, you\'ll either have to change the permissions, or point Python to a location where Apache can write. This can manifest itself as a \'\'500 internal server error\'\' and/or a complaint in the syslog. \n\n{{{\n#!xml\n<Location /projects/myproject>\n  ...\n  PythonOption PYTHON_EGG_CACHE /tmp \n  ...\n</Location>\n}}}\n\n\n=== Setting the !PythonPath ===\n\nIf the Trac installation isn\'t installed in your Python path, you\'ll have to tell Apache where to find the Trac mod_python handler  using the `PythonPath` directive:\n{{{\n#!xml\n<Location /projects/myproject>\n  ...\n  PythonPath \"sys.path + [\'/path/to/trac\']\"\n  ...\n</Location>\n}}}\n\nBe careful about using the !PythonPath directive, and \'\'not\'\' `SetEnv PYTHONPATH`, as the latter won\'t work.\n\n== Setting up multiple projects ==\n\nThe Trac mod_python handler supports a configuration option similar to Subversion\'s `SvnParentPath`, called `TracEnvParentDir`:\n{{{\n#!xml\n<Location /projects>\n  SetHandler mod_python\n  PythonInterpreter main_interpreter\n  PythonHandler trac.web.modpython_frontend \n  PythonOption TracEnvParentDir /var/trac\n  PythonOption TracUriRoot /projects\n</Location>\n}}}\n\nWhen you request the `/projects` URL, you will get a listing of all subdirectories of the directory you set as `TracEnvParentDir` that look like Trac environment directories. Selecting any project in the list will bring you to the corresponding Trac environment.\n\nIf you don\'t want to have the subdirectory listing as your projects home page you can use a\n{{{\n#!xml\n<LocationMatch \"/.+/\">\n}}}\n\nThis will instruct Apache to use mod_python for all locations different from root while having the possibility of placing a custom home page for root in your !DocumentRoot folder.\n\nYou can also use the same authentication realm for all of the projects using a `<LocationMatch>` directive:\n{{{\n#!xml\n<LocationMatch \"/projects/[^/]+/login\">\n  AuthType Basic\n  AuthName \"Trac\"\n  AuthUserFile /var/trac/.htpasswd\n  Require valid-user\n</LocationMatch>\n}}}\n\n== Virtual Host Configuration ==\n\nBelow is the sample configuration required to set up your trac as a virtual server (i.e. when you access it at the URLs like\n!http://trac.mycompany.com):\n\n{{{\n#!xml\n<VirtualHost * >\n    DocumentRoot /var/www/myproject\n    ServerName trac.mycompany.com\n    <Location />\n        SetHandler mod_python\n        PythonInterpreter main_interpreter\n        PythonHandler trac.web.modpython_frontend\n        PythonOption TracEnv /var/trac/myproject\n        PythonOption TracUriRoot /\n    </Location>\n    <Location /login>\n        AuthType Basic\n        AuthName \"MyCompany Trac Server\"\n        AuthUserFile /var/trac/myproject/.htpasswd\n        Require valid-user\n    </Location>\n</VirtualHost>\n}}}\n\nThis does not seem to work in all cases. What you can do if it does not:\n * Try using `<LocationMatch>` instead of `<Location>`\n * <Location /> may, in your server setup, refer to the complete host instead of simple the root of the server. This means that everything (including the login directory referenced below) will be sent to python and authentication does not work (i.e. you get the infamous Authentication information missing error). If this applies to you, try using a sub-directory for trac instead of the root (i.e. /web/ and /web/login instead of / and /login).\n * Depending on apache\'s `NameVirtualHost` configuration, you may need to use `<VirtualHost *:80>` instead of `<VirtualHost *>`.\n\nFor a virtual host that supports multiple projects replace \"`TracEnv`\" /var/trac/myproject with \"`TracEnvParentDir`\" /var/trac/\n\nNote: !DocumentRoot should not point to your Trac project env. As Asmodai wrote on #trac: \"suppose there\'s a webserver bug that allows disclosure of !DocumentRoot they could then leech the entire Trac environment\".\n\n== Troubleshooting ==\n\nIn general, if you get server error pages, you can either check the Apache error log, or enable the `PythonDebug` option:\n{{{\n#!xml\n<Location /projects/myproject>\n  ...\n  PythonDebug on\n</Location>\n}}}\n\nFor multiple projects, try restarting the server as well.\n\n=== Expat-related segmentation faults === #expat\n\nThis problem will most certainly hit you on Unix when using Python 2.4.\nIn Python 2.4, some version of Expat (an XML parser library written in C) is used, \nand if Apache is using another version, this results in segmentation faults.\nAs Trac 0.11 is using Genshi, which will indirectly use Expat, that problem\ncan now hit you even if everything was working fine before with Trac 0.10.\n\nSee Graham Dumpleton\'s detailed [http://www.dscpl.com.au/wiki/ModPython/Articles/ExpatCausingApacheCrash explanation and workarounds] for the issue.\n\n=== Form submission problems ===\n\nIf you\'re experiencing problems submitting some of the forms in Trac (a common problem is that you get redirected to the start page after submission), check whether your {{{DocumentRoot}}} contains a folder or file with the same path that you mapped the mod_python handler to. For some reason, mod_python gets confused when it is mapped to a location that also matches a static resource.\n\n=== Problem with virtual host configuration ===\n\nIf the <Location /> directive is used, setting the `DocumentRoot` may result in a \'\'403 (Forbidden)\'\' error. Either remove the `DocumentRoot` directive, or make sure that accessing the directory it points is allowed (in a corresponding `<Directory>` block).\n\nUsing <Location /> together with `SetHandler` resulted in having everything handled by mod_python, which leads to not being able download any CSS or images/icons. I used <Location /trac> `SetHandler None` </Location> to circumvent the problem, though I do not know if this is the most elegant solution.\n\n=== Problem with zipped egg ===\n\nIt\'s possible that your version of mod_python will not import modules from zipped eggs. If you encounter an `ImportError: No module named trac` in your Apache logs but you think everything is where it should be, this might be your problem. Look in your site-packages directory; if the Trac module appears as a \'\'file\'\' rather than a \'\'directory\'\', then this might be your problem. To rectify, try installing Trac using the `--always-unzip` option, like this:\n\n{{{\neasy_install --always-unzip Trac-0.12b1.zip\n}}}\n\n=== Using .htaccess ===\n\nAlthough it may seem trivial to rewrite the above configuration as a directory in your document root with a `.htaccess` file, this does not work. Apache will append a \"/\" to any Trac URLs, which interferes with its correct operation.\n\nIt may be possible to work around this with mod_rewrite, but I failed to get this working. In all, it is more hassle than it is worth. Stick to the provided instructions. :)\n\nA success story: For me it worked out-of-box, with following trivial config:\n{{{\nSetHandler mod_python\nPythonInterpreter main_interpreter\nPythonHandler trac.web.modpython_frontend \nPythonOption TracEnv /system/path/to/this/directory\nPythonOption TracUriRoot /path/on/apache\n\nAuthType Basic\nAuthName \"ProjectName\"\nAuthUserFile /path/to/.htpasswd\nRequire valid-user\n}}}\n\nThe `TracUriRoot` is obviously the path you need to enter to the browser to get to the trac (e.g. domain.tld/projects/trac)\n\n=== Additional .htaccess help ===\n\nIf you are using the .htaccess method you may have additional problems if your trac directory is inheriting .htaccess directives from another.  This may also help to add to your .htaccess file:\n\n{{{\n<IfModule mod_rewrite.c>\n  RewriteEngine Off\n</IfModule>\n}}}\n\n\n=== Win32 Issues ===\nIf you run trac with mod_python < 3.2 on Windows, uploading attachments will \'\'\'not\'\'\' work. This problem is resolved in mod_python 3.1.4 or later, so please upgrade mod_python to fix this.\n\n\n=== OS X issues ===\n\nWhen using mod_python on OS X you will not be able to restart Apache using `apachectl restart`. This is apparently fixed in mod_python 3.2, but there\'s also a patch available for earlier versions [http://www.dscpl.com.au/projects/vampire/patches.html here].\n\n=== SELinux issues ===\n\nIf Trac reports something like: \'\'Cannot get shared lock on db.lock\'\'\nThe security context on the repository may need to be set:\n\n{{{\nchcon -R -h -t httpd_sys_content_t PATH_TO_REPOSITORY\n}}}\n\nSee also [http://subversion.tigris.org/faq.html#reposperms]\n\n=== FreeBSD issues ===\nPay attention to the version of the installed mod_python and sqlite packages. Ports have both the new and old ones, but earlier versions of pysqlite and mod_python won\'t integrate as the former requires threaded support in python, and the latter requires a threadless install.\n\nIf you compiled and installed apache2, apache wouldnÂ´t support threads (cause it doesnÂ´t work very well on FreeBSD). You could force thread support when running ./configure for apache, using --enable-threads, but this isnÂ´t recommendable.\nThe best option [http://modpython.org/pipermail/mod_python/2006-September/021983.html seems to be] adding to /usr/local/apache2/bin/ennvars the line \n\n{{{\nexport LD_PRELOAD=/usr/lib/libc_r.so\n}}}\n\n=== Subversion issues ===\n\nIf you get the following Trac Error `Unsupported version control system \"svn\"` only under mod_python, though it works well on the command-line and even with TracStandalone, chances are that you forgot to add the path to the Python bindings with the [TracModPython#ConfiguringPythonPath PythonPath] directive. (The better way is to add a link to the bindings in the Python `site-packages` directory, or create a `.pth` file in that directory.)\n\nIf this is not the case, it\'s possible that you\'re using Subversion libraries that are binary incompatible with the apache ones (an incompatibility of the `apr` libraries is usually the cause). In that case, you also won\'t be able to use the svn modules for Apache (`mod_dav_svn`).\n\nYou also need a recent version of `mod_python` in order to avoid a runtime error ({{{argument number 2: a \'apr_pool_t *\' is expected}}}) due to the default usage of multiple sub-interpreters. 3.2.8 \'\'should\'\' work, though it\'s probably better to use the workaround described in [trac:#3371 #3371], in order to force the use of the main interpreter:\n{{{\nPythonInterpreter main_interpreter\n}}}\nThis is anyway the recommended workaround for other well-known issues seen when using the Python bindings for Subversion within mod_python ([trac:#2611 #2611], [trac:#3455 #3455]). See in particular Graham Dumpleton\'s comment in [trac:comment:9:ticket:3455 #3455] explaining the issue.\n\n=== Page layout issues ===\n\nIf the formatting of the Trac pages look weird chances are that the style sheets governing the page layout are not handled properly by the web server. Try adding the following lines to your apache configuration:\n{{{\n#!xml\nAlias /myproject/css \"/usr/share/trac/htdocs/css\"\n<Location /myproject/css>\n    SetHandler None\n</Location>\n}}}\n\nNote: For the above configuration to have any effect it must be put after the configuration of your project root location, i.e. {{{<Location /myproject />}}}.\n\nAlso, setting `PythonOptimize On` seems to mess up the page headers and footers, in addition to hiding the documentation for macros and plugins (see #Trac8956). Considering how little effect the option has, it is probably a good idea to leave it `Off`.\n\n=== HTTPS issues ===\n\nIf you want to run Trac fully under https you might find that it tries to redirect to plain http. In this case just add the following line to your apache configuration:\n{{{\n#!xml\n<VirtualHost * >\n    DocumentRoot /var/www/myproject\n    ServerName trac.mycompany.com\n    SetEnv HTTPS 1\n    ....\n</VirtualHost>\n}}}\n\n=== Fedora 7 Issues ===\nMake sure you install the \'python-sqlite2\' package as it seems to be required for TracModPython but not for tracd\n\n\n=== Segmentation fault with php5-mhash or other php5 modules ===\nYou may encounter segfaults (reported on debian etch) if php5-mhash module is installed. Try to remove it to see if this solves the problem. See debian bug report [http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=411487]\n\nSome people also have troubles when using php5 compiled with its own 3rd party libraries instead of system libraries. Check here [http://www.djangoproject.com/documentation/modpython/#if-you-get-a-segmentation-fault]\n\n----\nSee also:  TracGuide, TracInstall, [wiki:TracModWSGI ModWSGI], [wiki:TracFastCgi FastCGI],  [trac:TracNginxRecipe TracNginxRecipe]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracModWSGI',1,1327389819647871,'trac','127.0.0.1','= Trac and mod_wsgi =\n\n\'\'\'Important note:\'\'\' \'\'Please use either version 1.6, 2.4 or later of `mod_wsgi`. Versions prior to 2.4 in the 2.X branch have problems with some Apache configurations that use WSGI file wrapper extension. This extension is used in Trac to serve up attachments and static media files such as style sheets. If you are affected by this problem attachments will appear to be empty and formatting of HTML pages will appear not to work due to style sheet files not loading properly. See mod_wsgi tickets [http://code.google.com/p/modwsgi/issues/detail?id=100 #100] and [http://code.google.com/p/modwsgi/issues/detail?id=132 #132].\'\'\n\n[http://code.google.com/p/modwsgi/ mod_wsgi] is an Apache module for running WSGI-compatible Python applications directly on top of Apache. The mod_wsgi adapter is written completely in C and provides significantly better performance than using existing WSGI adapters for mod_python or CGI.\n\nTrac can be run on top of mod_wsgi with the help of the following application script, which is just a Python file, though usually saved with a .wsgi extension). This file can be created using \'\'\'trac-admin <env> deploy <dir>\'\'\' command which automatically substitutes required paths.\n\n{{{\n#!python\nimport os\n\nos.environ[\'TRAC_ENV\'] = \'/usr/local/trac/mysite\'\nos.environ[\'PYTHON_EGG_CACHE\'] = \'/usr/local/trac/mysite/eggs\'\n\nimport trac.web.main\napplication = trac.web.main.dispatch_request\n}}}\n\nThe `TRAC_ENV` variable should naturally be the directory for your Trac environment (if you have several Trac environments in a directory, you can also use `TRAC_ENV_PARENT_DIR` instead), while the `PYTHON_EGG_CACHE` should be a directory where Python can temporarily extract Python eggs.\n\n\'\'\'Important note:\'\'\' If you\'re using multiple `.wsgi` files (for example one per Trac environment) you must \'\'not\'\' use `os.environ[\'TRAC_ENV\']` to set the path to the Trac environment. Using this method may lead to Trac delivering the content of another Trac environment. (The variable may be filled with the path of a previously viewed Trac environment.) To solve this problem, use the following `.wsgi` file instead:\n\n{{{\n#!python\nimport os\n\nos.environ[\'PYTHON_EGG_CACHE\'] = \'/usr/local/trac/mysite/eggs\'\n\nimport trac.web.main\ndef application(environ, start_response):\n  environ[\'trac.env_path\'] = \'/usr/local/trac/mysite\' \n  return trac.web.main.dispatch_request(environ, start_response)\n}}}\n\nFor clarity, you should give this file a `.wsgi` extension. You should probably put the file in it\'s own directory, since you will open up its directory to Apache. You can create a .wsgi files which handles all this for you by running the TracAdmin command `deploy`.\n\nIf you have installed trac and eggs in a path different from the standard one you should add that path by adding the following code on top of the wsgi script:\n\n{{{\n#!python\nimport site\nsite.addsitedir(\'/usr/local/trac/lib/python2.4/site-packages\')\n}}}\n\nChange it according to the path you installed the trac libs at.\n\nAfter you\'ve done preparing your wsgi-script, add the following to your httpd.conf.\n\n{{{\nWSGIScriptAlias /trac /usr/local/trac/mysite/apache/mysite.wsgi\n\n<Directory /usr/local/trac/mysite/apache>\n    WSGIApplicationGroup %{GLOBAL}\n    Order deny,allow\n    Allow from all\n</Directory>\n}}}\n\nHere, the script is in a subdirectory of the Trac environment. In order to let Apache run the script, access to the directory in which the script resides is opened up to all of Apache. Additionally, the {{{WSGIApplicationGroup}}} directive ensures that Trac is always run in the first Python interpreter created by mod_wsgi; this is necessary because the Subversion Python bindings, which are used by Trac, don\'t always work in other subinterpreters and may cause requests to hang or cause Apache to crash as a result. After adding this configuration, restart Apache, and then it should work.\n\nTo test the setup of Apache, mod_wsgi and Python itself (ie. without involving Trac and dependencies), this simple wsgi application can be used to make sure that requests gets served (use as only content in your .wsgi script):\n\n{{{\ndef application(environ, start_response):\n        start_response(\'200 OK\',[(\'Content-type\',\'text/html\')])\n        return [\'<html><body>Hello World!</body></html>\']\n}}}\n\nSee also the mod_wsgi [http://code.google.com/p/modwsgi/wiki/IntegrationWithTrac installation instructions] for Trac.\n\nFor troubleshooting tips, see the [TracModPython#Troubleshooting mod_python troubleshooting] section, as most Apache-related issues are quite similar, plus discussion of potential [http://code.google.com/p/modwsgi/wiki/ApplicationIssues application issues] when using mod_wsgi.\n\n\'\'Note: using mod_wsgi 2.5 and Python 2.6.1 gave an Internal Server Error on my system (Apache 2.2.11 and Trac 0.11.2.1). Upgrading to Python 2.6.2 (as suggested [http://www.mail-archive.com/modwsgi@googlegroups.com/msg01917.html here]) solved this for me[[BR]]-- Graham Shanks\'\'\n\n== Apache Basic Authentication for Trac thru mod_wsgi ==\n\nPer the mod_wsgi documentation linked to above, here is an example Apache configuration that a) serves the trac from a virtualhost subdomain and b) uses Apache basic authentication for Trac authentication.\n\n\nIf you want your trac to be served from e.g. !http://trac.my-proj.my-site.org, then from the folder e.g. {{{/home/trac-for-my-proj}}}, if you used the command {{{trac-admin the-env initenv}}} to create a folder {{{the-env}}}, and you used {{{trac-admin the-env deploy the-deploy}}} to create a folder {{{the-deploy}}}, then:\n\ncreate the htpasswd file:\n{{{\ncd /home/trac-for-my-proj/the-env\nhtpasswd -c htpasswd firstuser\n### and add more users to it as needed:\nhtpasswd htpasswd seconduser\n}}}\n(for security keep the file above your document root)\n\ncreate this file e.g. (ubuntu) {{{/etc/apache2/sites-enabled/trac.my-proj.my-site.org.conf}}} with these contents:\n\n{{{\n<Directory /home/trac-for-my-proj/the-deploy/cgi-bin/trac.wsgi>\n  WSGIApplicationGroup %{GLOBAL}\n  Order deny,allow\n  Allow from all\n</Directory>\n\n<VirtualHost *:80>\n  ServerName trac.my-proj.my-site.org\n  DocumentRoot /home/trac-for-my-proj/the-env/htdocs/\n  WSGIScriptAlias / /home/trac-for-my-proj/the-deploy/cgi-bin/trac.wsgi\n  <Location \'/\'>\n    AuthType Basic\n    AuthName \"Trac\"\n    AuthUserFile /home/trac-for-my-proj/the-env/htpasswd\n    Require valid-user\n  </Location>\n</VirtualHost>\n\n}}}\n\n\n(for subdomains to work you would probably also need to alter /etc/hosts and add A-Records to your host\'s DNS.)\n\n== Trac with PostgreSQL ==\n\nWhen using the mod_wsgi adapter with multiple Trac instances and PostgreSQL (or MySQL?) as a database back-end the server can get a lot of open database connections. (and thus PostgreSQL processes)\n\nA workable solution is to disabled connection pooling in Trac. This is done by setting poolable = False in trac.db.postgres_backend on the PostgreSQLConnection class.\n\nBut it\'s not necessary to edit the source of trac, the following lines in trac.wsgi will also work:\n\n{{{\nimport trac.db.postgres_backend\ntrac.db.postgres_backend.PostgreSQLConnection.poolable = False\n}}}\n\nNow Trac drops the connection after serving a page and the connection count on the database will be kept minimal.\n\n== Getting Trac to work nicely with SSPI and \'Require Group\' ==\nIf like me you\'ve set Trac up on Apache, Win32 and configured SSPI, but added a \'Require group\' option to your apache configuration, then the SSPIOmitDomain option is probably not working.  If its not working your usernames in trac are probably looking like \'DOMAIN\\user\' rather than \'user\'.\n\nThis WSGI script \'fixes\' things, hope it helps:\n{{{\nimport os\nimport trac.web.main\n\nos.environ[\'TRAC_ENV\'] = \'/usr/local/trac/mysite\'\nos.environ[\'PYTHON_EGG_CACHE\'] = \'/usr/local/trac/mysite/eggs\'\n\ndef application(environ, start_response):\n    if \"\\\\\" in environ[\'REMOTE_USER\']:\n        environ[\'REMOTE_USER\'] = environ[\'REMOTE_USER\'].split(\"\\\\\", 1)[1]\n    return trac.web.main.dispatch_request(environ, start_response)\n}}}\n----\nSee also:  TracGuide, TracInstall, [wiki:TracFastCgi FastCGI], [wiki:TracModPython ModPython], [trac:TracNginxRecipe TracNginxRecipe]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracNavigation',1,1327389819647871,'trac','127.0.0.1','= Trac Navigation =\n\nStarting with Trac 0.11, it is now possible to customize the main and meta navigation entries in some basic ways.\n\nThe new `[mainnav]` and `[metanav]` configuration sections can now be used to customize the text and link used for the navigation items, or even to disable them.\n\n`[mainnav]` corresponds to the \'\'\'main navigation bar\'\'\', the one containing entries such as \'\'Wiki\'\', \'\'Timeline\'\', \'\'Roadmap\'\', \'\'Browse Source\'\' and so on. This navigation bar is meant to access the default page of the main modules enabled in Trac and accessible for the current user.\n\n`[metanav]` corresponds to the \'\'\'meta navigation bar\'\'\', by default positioned above the main navigation bar and below the \'\'Search\'\' box. It contains the \'\'Log in\'\', \'\'Logout\'\', \'\'!Help/Guide\'\' etc. entries. This navigation bar is meant to access some global information about the Trac project and the current user.\n\nThere is one special entry in the  `[metanav]` section: `logout.redirect` is the page the user sees after hitting the logout button. \n\nPossible URL formats:\n|| \'\'\'config\'\'\' || \'\'\'redirect to\'\'\' ||\n|| `wiki/Logout` || `/projects/env/wiki/Logout` ||\n|| `http://hostname/` || `http://hostname/` ||\n|| `/projects` || `/projects` ||\n[[comment(see also #Trac3808)]]\n\nNote that it is still not possible to customize the \'\'\'contextual navigation bar\'\'\', i.e. the one usually placed below the main navigation bar.\n\n=== Example ===\n\nIn the following example, we rename the link to the Wiki start \"Home\", and hide the \"!Help/Guide\" link. \nWe also make the \"View Tickets\" entry link to a specific report.\n\nRelevant excerpt from the TracIni:\n{{{\n[mainnav]\nwiki.label = Home\ntickets.href = /report/24\n\n[metanav]\nhelp = disabled\nlogout.redirect = wiki/Logout\n}}}\n\n----\nSee also: TracInterfaceCustomization, and the [http://trac-hacks.org/wiki/NavAddPlugin TracHacks:NavAddPlugin] or [http://trac-hacks.org/wiki/MenusPlugin TracHacks:MenusPlugin] (still needed for adding entries)\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracNotification',1,1327389819647871,'trac','127.0.0.1','= Email Notification of Ticket Changes =\n[[TracGuideToc]]\n\nTrac supports notification of ticket changes via email. \n\nEmail notification is useful to keep users up-to-date on tickets/issues of interest, and also provides a convenient way to post all ticket changes to a dedicated mailing list. For example, this is how the [http://lists.edgewall.com/archive/trac-tickets/ Trac-tickets] mailing list is set up.\n\nDisabled by default, notification can be activated and configured in [wiki:TracIni trac.ini].\n\n== Receiving Notification Mails ==\nWhen reporting a new ticket or adding a comment, enter a valid email address or your username in the \'\'reporter\'\', \'\'assigned to/owner\'\' or \'\'cc\'\' field. Trac will automatically send you an email when changes are made to the ticket (depending on how notification is configured).\n\nThis is useful to keep up-to-date on an issue or enhancement request that interests you.\n\n=== How to use your username to receive notification mails ===\n\nTo receive notification mails, you can either enter a full email address or your username. To get notified with a simple username or login, you need to specify a valid email address in the \'\'Preferences\'\' page. \n\nAlternatively, a default domain name (\'\'\'`smtp_default_domain`\'\'\') can be set in the TracIni file (see [#ConfigurationOptions Configuration Options] below). In this case, the default domain will be appended to the username, which can be useful for an \"Intranet\" kind of installation.\n\n== Configuring SMTP Notification ==\n\n\'\'\'Important:\'\'\' For TracNotification to work correctly, the `[trac] base_url` option must be set in [wiki:TracIni trac.ini]. \n\n=== Configuration Options ===\nThese are the available options for the `[notification]` section in trac.ini.\n\n * \'\'\'`smtp_enabled`\'\'\': Enable email notification.\n * \'\'\'`smtp_from`\'\'\': Email address to use for \'\'Sender\'\'-headers in notification emails.\n * \'\'\'`smtp_from_name`\'\'\': Sender name to use for \'\'Sender\'\'-headers in notification emails.\n * \'\'\'`smtp_replyto`\'\'\': Email address to use for \'\'Reply-To\'\'-headers in notification emails.\n * \'\'\'`smtp_default_domain`\'\'\': (\'\'since 0.10\'\') Append the specified domain to addresses that do not contain one. Fully qualified addresses are not modified. The default domain is appended to all username/login for which an email address cannot be found from the user settings.\n * \'\'\'`smtp_always_cc`\'\'\': List of email addresses to always send notifications to. \'\'Typically used to post ticket changes to a dedicated mailing list.\'\'\n * \'\'\'`smtp_always_bcc`\'\'\': (\'\'since 0.10\'\') List of email addresses to always send notifications to, but keeps addresses not visible from other recipients of the notification email \n * \'\'\'`smtp_subject_prefix`\'\'\': (\'\'since 0.10.1\'\') Text that is inserted before the subject of the email. Set to \"!__default!__\" by default.\n * \'\'\'`always_notify_reporter`\'\'\':  Always send notifications to any address in the reporter field (default: false).\n * \'\'\'`always_notify_owner`\'\'\': (\'\'since 0.9\'\') Always send notifications to the address in the owner field (default: false).\n * \'\'\'`always_notify_updater`\'\'\': (\'\'since 0.10\'\') Always send a notification to the updater of a ticket (default: true).\n * \'\'\'`use_public_cc`\'\'\': (\'\'since 0.10\'\') Addresses in To: (owner, reporter) and Cc: lists are visible by all recipients (default is \'\'Bcc:\'\' - hidden copy).\n * \'\'\'`use_short_addr`\'\'\': (\'\'since 0.10\'\') Enable delivery of notifications to addresses that do not contain a domain (i.e. do not end with \'\'@<domain.com>\'\').This option is useful for intranets, where the SMTP server can handle local addresses and map the username/login to a local mailbox. See also `smtp_default_domain`. Do not use this option with a public SMTP server. \n * \'\'\'`mime_encoding`\'\'\': (\'\'since 0.10\'\') This option allows selecting the MIME encoding scheme. Supported values:\n   * `none`: default value, uses 7bit encoding if the text is plain ASCII, or 8bit otherwise. \n   * `base64`: works with any kind of content. May cause some issues with touchy anti-spam/anti-virus engines.\n   * `qp` or `quoted-printable`: best for european languages (more compact than base64) if 8bit encoding cannot be used.\n * \'\'\'`ticket_subject_template`\'\'\': (\'\'since 0.11\'\') A [http://genshi.edgewall.org/wiki/Documentation/text-templates.html Genshi text template] snippet used to get the notification subject.\n * \'\'\'`email_sender`\'\'\': (\'\'since 0.12\'\') Name of the component implementing `IEmailSender`. This component is used by the notification system to send emails. Trac currently provides the following components:\n   * `SmtpEmailSender`: connects to an SMTP server (default).\n   * `SendmailEmailSender`: runs a `sendmail`-compatible executable.\n\nEither \'\'\'`smtp_from`\'\'\' or \'\'\'`smtp_replyto`\'\'\' (or both) \'\'must\'\' be set, otherwise Trac refuses to send notification mails.\n\nThe following options are specific to email delivery through SMTP.\n * \'\'\'`smtp_server`\'\'\': SMTP server used for notification messages.\n * \'\'\'`smtp_port`\'\'\': (\'\'since 0.9\'\') Port used to contact the SMTP server.\n * \'\'\'`smtp_user`\'\'\': (\'\'since 0.9\'\') User name for authentication SMTP account.\n * \'\'\'`smtp_password`\'\'\': (\'\'since 0.9\'\') Password for authentication SMTP account.\n * \'\'\'`use_tls`\'\'\': (\'\'since 0.10\'\') Toggle to send notifications via a SMTP server using [http://en.wikipedia.org/wiki/Transport_Layer_Security TLS], such as GMail.\n\nThe following option is specific to email delivery through a `sendmail`-compatible executable.\n * \'\'\'`sendmail_path`\'\'\': (\'\'since 0.12\'\') Path to the sendmail executable. The sendmail program must accept the `-i` and `-f` options.\n\n=== Example Configuration (SMTP) ===\n{{{\n[notification]\nsmtp_enabled = true\nsmtp_server = mail.example.com\nsmtp_from = notifier@example.com\nsmtp_replyto = myproj@projects.example.com\nsmtp_always_cc = ticketmaster@example.com, theboss+myproj@example.com\n}}}\n\n=== Example Configuration (`sendmail`) ===\n{{{\n[notification]\nsmtp_enabled = true\nemail_sender = SendmailEmailSender\nsendmail_path = /usr/sbin/sendmail\nsmtp_from = notifier@example.com\nsmtp_replyto = myproj@projects.example.com\nsmtp_always_cc = ticketmaster@example.com, theboss+myproj@example.com\n}}}\n\n=== Customizing the e-mail subject ===\nThe e-mail subject can be customized with the `ticket_subject_template` option, which contains a [http://genshi.edgewall.org/wiki/Documentation/text-templates.html Genshi text template] snippet. The default value is:\n{{{\n$prefix #$ticket.id: $summary\n}}}\nThe following variables are available in the template:\n\n * `env`: The project environment (see [trac:source:/trunk/trac/env.py env.py]).\n * `prefix`: The prefix defined in `smtp_subject_prefix`.\n * `summary`: The ticket summary, with the old value if the summary was edited.\n * `ticket`: The ticket model object (see [trac:source:/trunk/trac/ticket/model.py model.py]). Individual ticket fields can be addressed by appending the field name separated by a dot, e.g. `$ticket.milestone`.\n\n=== Customizing the e-mail content ===\n\nThe notification e-mail content is generated based on `ticket_notify_email.txt` in `trac/ticket/templates`.  You can add your own version of this template by adding a `ticket_notify_email.txt` to the templates directory of your environment. The default looks like this:\n\n{{{\n$ticket_body_hdr\n$ticket_props\n#choose ticket.new\n  #when True\n$ticket.description\n  #end\n  #otherwise\n    #if changes_body\nChanges (by $change.author):\n\n$changes_body\n    #end\n    #if changes_descr\n      #if not changes_body and not change.comment and change.author\nDescription changed by $change.author:\n      #end\n$changes_descr\n--\n    #end\n    #if change.comment\n\nComment${not changes_body and \'(by %s)\' % change.author or \'\'}:\n\n$change.comment\n    #end\n  #end\n#end\n\n-- \nTicket URL: <$ticket.link>\n$project.name <${project.url or abs_href()}>\n$project.descr\n}}}\n== Sample Email ==\n{{{\n#42: testing\n---------------------------+------------------------------------------------\n       Id:  42             |      Status:  assigned                \nComponent:  report system  |    Modified:  Fri Apr  9 00:04:31 2004\n Severity:  major          |   Milestone:  0.9                     \n Priority:  lowest         |     Version:  0.6                     \n    Owner:  anonymous      |    Reporter:  jonas@example.com               \n---------------------------+------------------------------------------------\nChanges:\n  * component:  changset view => search system\n  * priority:  low => highest\n  * owner:  jonas => anonymous\n  * cc:  daniel@example.com =>\n         daniel@example.com, jonas@example.com\n  * status:  new => assigned\n\nComment:\nI\'m interested too!\n\n--\nTicket URL: <http://example.com/trac/ticket/42>\nMy Project <http://myproj.example.com/>\n}}}\n\n== Using GMail as the SMTP relay host ==\n\nUse the following configuration snippet\n{{{\n[notification]\nsmtp_enabled = true\nuse_tls = true\nmime_encoding = base64\nsmtp_server = smtp.gmail.com\nsmtp_port = 587\nsmtp_user = user\nsmtp_password = password\n}}}\n\nwhere \'\'user\'\' and \'\'password\'\' match an existing GMail account, \'\'i.e.\'\' the ones you use to log in on [http://gmail.com]\n\nAlternatively, you can use `smtp_port = 25`.[[br]]\nYou should not use `smtp_port = 465`. It will not work and your ticket submission may deadlock. Port 465 is reserved for the SMTPS protocol, which is not supported by Trac. See [comment:ticket:7107:2 #7107] for details.\n \n== Filtering notifications for one\'s own changes ==\nIn Gmail, use the filter:\n\n{{{\nfrom:(<smtp_from>) ((\"Reporter: <username>\" -Changes) OR \"Changes (by <username>)\")\n}}}\n\nFor Trac .10, use the filter:\n{{{\nfrom:(<smtp_from>) ((\"Reporter: <username>\" -Changes -Comment) OR \"Changes (by <username>)\" OR \"Comment (by <username>)\")\n}}}\n\nto delete these notifications.\n\nIn Thunderbird, there is no such solution if you use IMAP\n(see http://kb.mozillazine.org/Filters_(Thunderbird)#Filtering_the_message_body).\n\nThe best you can do is to set \"always_notify_updater\" in conf/trac.ini to false.\nYou will however still get an email if you comment a ticket that you own or have reported.\n\nYou can also add this plugin:\nhttp://trac-hacks.org/wiki/NeverNotifyUpdaterPlugin\n\n== Troubleshooting ==\n\nIf you cannot get the notification working, first make sure the log is activated and have a look at the log to find if an error message has been logged. See TracLogging for help about the log feature.\n\nNotification errors are not reported through the web interface, so the user who submit a change or a new ticket never gets notified about a notification failure. The Trac administrator needs to look at the log to find the error trace.\n\n=== \'\'Permission denied\'\' error ===\n\nTypical error message:\n{{{\n  ...\n  File \".../smtplib.py\", line 303, in connect\n    raise socket.error, msg\n  error: (13, \'Permission denied\')\n}}}\n\nThis error usually comes from a security settings on the server: many Linux distributions do not let the web server (Apache, ...) to post email message to the local SMTP server.\n\nMany users get confused when their manual attempts to contact the SMTP server succeed:\n{{{\ntelnet localhost 25\n}}}\nThe trouble is that a regular user may connect to the SMTP server, but the web server cannot:\n{{{\nsudo -u www-data telnet localhost 25\n}}}\n\nIn such a case, you need to configure your server so that the web server is authorized to post to the SMTP server. The actual settings depend on your Linux distribution and current security policy. You may find help browsing the Trac [trac:MailingList MailingList] archive.\n\nRelevant ML threads:\n * SELinux: http://article.gmane.org/gmane.comp.version-control.subversion.trac.general/7518\n\nFor SELinux in Fedora 10:\n{{{\n$ setsebool -P httpd_can_sendmail 1\n}}}\n=== \'\'Suspected spam\'\' error ===\n\nSome SMTP servers may reject the notification email sent by Trac.\n\nThe default Trac configuration uses Base64 encoding to send emails to the recipients. The whole body of the email is encoded, which sometimes trigger \'\'false positive\'\' SPAM detection on sensitive email servers. In such an event, it is recommended to change the default encoding to \"quoted-printable\" using the `mime_encoding` option.\n\nQuoted printable encoding works better with languages that use one of the Latin charsets. For Asian charsets, it is recommended to stick with the Base64 encoding.\n\n=== \'\'501, 5.5.4 Invalid Address\'\' error ===\n\nOn IIS 6.0 you could get a \n{{{\nFailure sending notification on change to ticket #1: SMTPHeloError: (501, \'5.5.4 Invalid Address\')\n}}}\nin the trac log. Have a look [http://support.microsoft.com/kb/291828 here] for instructions on resolving it.\n\n\n----\nSee also: TracTickets, TracIni, TracGuide\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracPermissions',1,1327389819647871,'trac','127.0.0.1','= Trac Permissions =\n[[TracGuideToc]]\n\nTrac uses a simple, case sensitive, permission system to control what users can and can\'t access.\n\nPermission privileges are managed using the [TracAdmin trac-admin] tool or (new in version 0.11) the \'\'General / Permissions\'\' panel in the \'\'Admin\'\' tab of the web interface.\n\nIn addition to the default permission policy described in this page, it is possible to activate additional permission policies by enabling plugins and listing them in the `[trac] permission_policies` configuration entry in the TracIni. See TracFineGrainedPermissions for more details.\n\nNon-authenticated users accessing the system are assigned the name \"anonymous\". Assign permissions to the \"anonymous\" user to set privileges for anonymous/guest users. The parts of Trac that a user does not have the privileges for will not be displayed in the navigation.\nIn addition to these privileges, users can be granted additional individual rights in effect when authenticated and logged into the system. All logged in users belong to the virtual group \"authenticated\", which inherits permissions from \"anonymous\".\n\n== Graphical Admin Tab ==\n\'\'This feature is new in version 0.11.\'\'\n\nTo access this tab, a user must have `TRAC_ADMIN privileges`. This can be performed as follows (more on the trac-admin script below):\n{{{\n  $ trac-admin /path/to/projenv permission add bob TRAC_ADMIN\n}}}\n\nThen, the user `bob` will be able to see the Admin tab, and can then access the permissions menu. This menu will allow you to perform all the following actions, but from the browser without requiring root access to the server (just the correct permissions for your user account).\n\n 1. [[Image(htdocs:../common/guide/admin.png)]]\n 1. [[Image(htdocs:../common/guide/admin-permissions.png)]]\n 1. [[Image(htdocs:../common/guide/admin-permissions-TICKET_ADMIN.png)]]\n\nAn easy way to quickly secure a new Trac install is to run the above command on the anonymous user, install the [http://trac-hacks.org/wiki/AccountManagerPlugin AccountManagerPlugin], create a new admin account graphically and then remove the TRAC_ADMIN permission from the anonymous user.\n\n== Available Privileges ==\n\nTo enable all privileges for a user, use the `TRAC_ADMIN` permission. Having `TRAC_ADMIN` is like being `root` on a *NIX system: it will allow you to perform any operation.\n\nOtherwise, individual privileges can be assigned to users for the various different functional areas of Trac (\'\'\'note that the privilege names are case-sensitive\'\'\'):\n\n=== Repository Browser ===\n\n|| `BROWSER_VIEW` || View directory listings in the [wiki:TracBrowser repository browser] ||\n|| `LOG_VIEW` || View revision logs of files and directories in the [wiki:TracBrowser repository browser] ||\n|| `FILE_VIEW` || View files in the [wiki:TracBrowser repository browser] ||\n|| `CHANGESET_VIEW` || View [wiki:TracChangeset repository check-ins] ||\n\n=== Ticket System ===\n\n|| `TICKET_VIEW` || View existing [wiki:TracTickets tickets] and perform [wiki:TracQuery ticket queries] ||\n|| `TICKET_CREATE` || Create new [wiki:TracTickets tickets] ||\n|| `TICKET_APPEND` || Add comments or attachments to [wiki:TracTickets tickets] ||\n|| `TICKET_CHGPROP` || Modify [wiki:TracTickets ticket] properties (priority, assignment, keywords, etc.) with the following exceptions: edit description field, add/remove other users from cc field when logged in, and set email to pref ||\n|| `TICKET_MODIFY` || Includes both `TICKET_APPEND` and `TICKET_CHGPROP`, and in addition allows resolving [wiki:TracTickets tickets]. Tickets can be assigned to users through a [TracTickets#Assign-toasDrop-DownList drop-down list] when the list of possible owners has been restricted. ||\n|| `TICKET_EDIT_CC` || Full modify cc field ||\n|| `TICKET_EDIT_DESCRIPTION` || Modify description field ||\n|| `TICKET_EDIT_COMMENT` || Modify comments ||\n|| `TICKET_ADMIN` || All `TICKET_*` permissions, plus the deletion of ticket attachments and modification of the reporter and description fields. It also allows managing ticket properties in the WebAdmin panel. ||\n\nAttention: the \"view tickets\" button appears with the `REPORT_VIEW` permission.\n\n=== Roadmap ===\n\n|| `MILESTONE_VIEW` || View milestones and assign tickets to milestones. ||\n|| `MILESTONE_CREATE` || Create a new milestone ||\n|| `MILESTONE_MODIFY` || Modify existing milestones ||\n|| `MILESTONE_DELETE` || Delete milestones ||\n|| `MILESTONE_ADMIN` || All `MILESTONE_*` permissions ||\n|| `ROADMAP_VIEW` || View the [wiki:TracRoadmap roadmap] page, is not (yet) the same as MILESTONE_VIEW, see [trac:#4292 #4292] ||\n|| `ROADMAP_ADMIN` || to be removed with [trac:#3022 #3022], replaced by MILESTONE_ADMIN ||\n\n=== Reports ===\n\n|| `REPORT_VIEW` || View [wiki:TracReports reports], i.e. the \"view tickets\" link. ||\n|| `REPORT_SQL_VIEW` || View the underlying SQL query of a [wiki:TracReports report] ||\n|| `REPORT_CREATE` || Create new [wiki:TracReports reports] ||\n|| `REPORT_MODIFY` || Modify existing [wiki:TracReports reports] ||\n|| `REPORT_DELETE` || Delete [wiki:TracReports reports] ||\n|| `REPORT_ADMIN` || All `REPORT_*` permissions ||\n\n=== Wiki System ===\n\n|| `WIKI_VIEW` || View existing [wiki:TracWiki wiki] pages ||\n|| `WIKI_CREATE` || Create new [wiki:TracWiki wiki] pages ||\n|| `WIKI_MODIFY` || Change [wiki:TracWiki wiki] pages ||\n|| `WIKI_RENAME` || Rename [wiki:TracWiki wiki] pages ||\n|| `WIKI_DELETE` || Delete [wiki:TracWiki wiki] pages and attachments ||\n|| `WIKI_ADMIN` || All `WIKI_*` permissions, plus the management of \'\'readonly\'\' pages. ||\n\n=== Permissions ===\n\n|| `PERMISSION_GRANT` || add/grant a permission ||\n|| `PERMISSION_REVOKE` || remove/revoke a permission ||\n|| `PERMISSION_ADMIN` || All `PERMISSION_*` permissions ||\n\n\n=== Others ===\n\n|| `TIMELINE_VIEW` || View the [wiki:TracTimeline timeline] page ||\n|| `SEARCH_VIEW` || View and execute [wiki:TracSearch search] queries ||\n|| `CONFIG_VIEW` || Enables additional pages on \'\'About Trac\'\' that show the current configuration or the list of installed plugins ||\n|| `EMAIL_VIEW` || Shows email addresses even if [trac:wiki:0.11/TracIni trac show_email_addresses configuration option is false] ||\n\n== Granting Privileges ==\n\nYou grant privileges to users using [wiki:TracAdmin trac-admin]. The current set of privileges can be listed with the following command:\n{{{\n  $ trac-admin /path/to/projenv permission list\n}}}\n\nThis command will allow the user \'\'bob\'\' to delete reports:\n{{{\n  $ trac-admin /path/to/projenv permission add bob REPORT_DELETE\n}}}\n\nThe `permission add` command also accepts multiple privilege names:\n{{{\n  $ trac-admin /path/to/projenv permission add bob REPORT_DELETE WIKI_CREATE\n}}}\n\nOr add all privileges:\n{{{\n  $ trac-admin /path/to/projenv permission add bob TRAC_ADMIN\n}}}\n\n== Permission Groups ==\n\nThere are two built-in groups, \"authenticated\" and \"anonymous\".\nAny user who has not logged in is automatically in the \"anonymous\" group.\nAny user who has logged in is also in the \"authenticated\" group.\nThe \"authenticated\" group inherits permissions from the \"anonymous\" group.\nFor example, if the \"anonymous\" group has permission WIKI_MODIFY, \nit is not necessary to add the WIKI_MODIFY permission to the \"authenticated\" group as well.\n\nCustom groups may be defined that inherit permissions from the two built-in groups.\n\nPermissions can be grouped together to form roles such as \'\'developer\'\', \'\'admin\'\', etc.\n{{{\n  $ trac-admin /path/to/projenv permission add developer WIKI_ADMIN\n  $ trac-admin /path/to/projenv permission add developer REPORT_ADMIN\n  $ trac-admin /path/to/projenv permission add developer TICKET_MODIFY\n  $ trac-admin /path/to/projenv permission add bob developer\n  $ trac-admin /path/to/projenv permission add john developer\n}}}\n\nGroup membership can be checked by doing a {{{permission list}}} with no further arguments; the resulting output will include group memberships. \'\'\'Use at least one lowercase character in group names, as all-uppercase names are reserved for permissions\'\'\'.\n\n== Adding a New Group and Permissions ==\nPermission groups can be created by assigning a user to a group you wish to create, then assign permissions to that group.\n\nThe following will add \'\'bob\'\' to the new group called \'\'beta_testers\'\' and then will assign WIKI_ADMIN permissions to that group. (Thus, \'\'bob\'\' will inherit the WIKI_ADMIN permission)\n{{{ \n   $ trac-admin /path/to/projenv permission add bob beta_testers\n   $ trac-admin /path/to/projenv permission add beta_testers WIKI_ADMIN\n\n}}}\n\n== Removing Permissions ==\n\nPermissions can be removed using the \'remove\' command. For example:\n\nThis command will prevent the user \'\'bob\'\' from deleting reports:\n{{{\n  $ trac-admin /path/to/projenv permission remove bob REPORT_DELETE\n}}}\n\nJust like `permission add`, this command accepts multiple privilege names.\n\nYou can also remove all privileges for a specific user:\n{{{\n  $ trac-admin /path/to/projenv permission remove bob \'*\'\n}}}\n\nOr one privilege for all users:\n{{{\n  $ trac-admin /path/to/projenv permission remove \'*\' REPORT_ADMIN\n}}}\n\n== Default Permissions ==\n\nBy default on a new Trac installation, the `anonymous` user will have \'\'view\'\' access to everything in Trac, but will not be able to create or modify anything.\nOn the other hand, the `authenticated` users will have the permissions to \'\'create and modify tickets and wiki pages\'\'.\n\n\'\'\'anonymous\'\'\'\n{{{\n BROWSER_VIEW \n CHANGESET_VIEW \n FILE_VIEW \n LOG_VIEW \n MILESTONE_VIEW \n REPORT_SQL_VIEW \n REPORT_VIEW \n ROADMAP_VIEW \n SEARCH_VIEW \n TICKET_VIEW \n TIMELINE_VIEW\n WIKI_VIEW\n}}}\n\n\'\'\'authenticated\'\'\'\n{{{\n TICKET_CREATE \n TICKET_MODIFY \n WIKI_CREATE \n WIKI_MODIFY  \n}}}\n----\nSee also: TracAdmin, TracGuide and TracFineGrainedPermissions\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracPlugins',1,1327389819647871,'trac','127.0.0.1','= Trac Plugins =\n[[TracGuideToc]]\n\nTrac is extensible with [trac:PluginList plugins] since version 0.9. The plugin functionality is based on the [trac:TracDev/ComponentArchitecture component architecture] with peculiarities described at [TracDev/PluginDevelopment plugin development] page.\n\n== Plugin discovery ==\n\nFrom the user point of view a Plugin is either standalone .py file or an .egg package. Trac looks for Plugins in a global shared plugins directory (see [TracIni#GlobalConfiguration Global Configuration]), or in a local TracEnvironment, in its `plugins` directory.\nExcept for the later case, the components defined in a plugin should be explicitly enabled in the [[TracIni#components-section| [components] ]] section of the trac.ini file.\n\n== Requirements for Trac eggs  ==\n\nTo use egg based plugins in Trac, you need to have [http://peak.telecommunity.com/DevCenter/setuptools setuptools] (version 0.6) installed.\n\nTo install `setuptools`, download the bootstrap module [http://peak.telecommunity.com/dist/ez_setup.py ez_setup.py] and execute it as follows:\n{{{\n$ python ez_setup.py\n}}}\n\nIf the `ez_setup.py` script fails to install the setuptools release, you can download it from [http://www.python.org/pypi/setuptools PyPI] and install it manually.\n\nPlugins can also consist of a single `.py` file dropped into either the environment or the shared plugins directory.\n\n== Installing a Trac Plugin ==\n\n=== For a Single Project ===\n\nPlugins are packaged as [http://peak.telecommunity.com/DevCenter/PythonEggs Python eggs]. That means they are ZIP archives with the file extension `.egg`. \n\nIf you have downloaded a source distribution of a plugin, and want to build the `.egg` file, follow this instruction:\n * Unpack the source. It should provide a setup.py. \n * Run:\n{{{\n$ python setup.py bdist_egg\n}}}\n\nThen you will have a *.egg file. Examine the output of running python to find where this was created.\n\nOnce you have the plugin archive, you need to copy it into the `plugins` directory of the [wiki:TracEnvironment project environment]. Also, make sure that the web server has sufficient permissions to read the plugin egg. Then, restart the web server (this requirement was not previously mentioned in this document, but in my tests it began working only after I did so).\n\nTo uninstall a plugin installed this way, remove the egg from `plugins` directory and restart web server.\n\nNote that the Python version that the egg is built with must\nmatch the Python version with which Trac is run.  If for\ninstance you are running Trac under Python 2.5, but have\nupgraded your standalone Python to 2.6, the eggs won\'t be\nrecognized.\n\nNote also that in a multi-project setup, a pool of Python interpreter instances will be dynamically allocated to projects based on need, and since plugins occupy a place in Python\'s module system, the first version of any given plugin to be loaded will be used for all the projects. In other words, you cannot use different versions of a single plugin in two projects of a multi-project setup. It may be safer to install plugins for all projects (see below) and then enable them selectively on a project-by-project basis.\n\n=== For All Projects ===\n\n==== With an .egg file ====\n\nSome plugins (such as [trac:SpamFilter SpamFilter]) are downloadable as a `.egg` file which can be installed with the `easy_install` program:\n{{{\neasy_install TracSpamFilter\n}}}\n\nIf `easy_install` is not on your system see the Requirements section above to install it.  Windows users will need to add the `Scripts` directory of their Python installation (for example, `C:\\Python24\\Scripts`) to their `PATH` environment variable (see [http://peak.telecommunity.com/DevCenter/EasyInstall#windows-notes easy_install Windows notes] for more information).\n\nIf Trac reports permission errors after installing a zipped egg and you would rather not bother providing a egg cache directory writable by the web server, you can get around it by simply unzipping the egg. Just pass `--always-unzip` to `easy_install`:\n{{{\neasy_install --always-unzip TracSpamFilter-0.4.1_r10106-py2.6.egg\n}}}\nYou should end up with a directory having the same name as the zipped egg (complete with `.egg` extension) and containing its uncompressed contents.\n\nTrac also searches for plugins installed in the shared plugins directory \'\'(since 0.10)\'\', see TracIni#GlobalConfiguration. This is a convenient way to share the installation of plugins across several but not all environments.\n\n==== From source ====\n\n`easy_install` makes installing from source a snap. Just give it the URL to either a Subversion repository or a tarball/zip of the source:\n{{{\neasy_install http://svn.edgewall.com/repos/trac/plugins/0.12/spam-filter-captcha\n}}}\n\n==== Enabling the plugin ====\nUnlike plugins installed per-environment, you\'ll have to explicitly enable globally installed plugins via [wiki:TracIni trac.ini]. This also applies to plugins installed in shared plugins directory, i.e. the path specified in the `[inherit] plugins_dir` configuration option. \n\nThis is done in the `[components]` section of the configuration file, for example:\n{{{\n[components]\ntracspamfilter.* = enabled\n}}}\n\nThe name of the option is the Python package of the plugin. This should be specified in the documentation of the plugin, but can also be easily discovered by looking at the source (look for a top-level directory that contains a file named `__init__.py`.)\n\nNote: After installing the plugin, you need to restart your web server.\n\n==== Uninstalling ====\n\n`easy_install` or `python setup.py` does not have an uninstall feature. Hower, it is usually quite trivial to remove a globally installed egg and reference:\n 1. Do `easy_install -m [plugin name]` to remove references from `$PYTHONLIB/site-packages/easy-install.pth` when the plugin installed by setuptools.\n 1. Delete executables from `/usr/bin`, `/usr/local/bin` or `C:\\\\Python*\\Scripts`. For search what executables are there, you may refer to `[console-script]` section of `setup.py`.\n 1. Delete the .egg file or folder from where it is installed, usually inside `$PYTHONLIB/site-packages/`.\n 1. Restart web server.\n\nIf you are uncertain about the location of the egg, here is a small tip to help locate an egg (or any package) - replace `myplugin` with whatever namespace the plugin uses (as used when enabling the plugin):\n{{{\n>>> import myplugin\n>>> print myplugin.__file__\n/opt/local/python24/lib/site-packages/myplugin-0.4.2-py2.4.egg/myplugin/__init__.pyc\n}}}\n\n== Setting up the Plugin Cache ==\n\nSome plugins will need to be extracted by the Python eggs runtime (`pkg_resources`), so that their contents are actual files on the file system. The directory in which they are extracted defaults to \'.python-eggs\' in the home directory of the current user, which may or may not be a problem. You can however override the default location using the `PYTHON_EGG_CACHE` environment variable.\n\nTo do this from the Apache configuration, use the `SetEnv` directive as follows:\n{{{\nSetEnv PYTHON_EGG_CACHE /path/to/dir\n}}}\n\nThis works whether you are using the [wiki:TracCgi CGI] or the [wiki:TracModPython mod_python] front-end. Put this directive next to where you set the path to the [wiki:TracEnvironment Trac environment], i.e. in the same `<Location>` block.\n\nFor example (for CGI):\n{{{\n <Location /trac>\n   SetEnv TRAC_ENV /path/to/projenv\n   SetEnv PYTHON_EGG_CACHE /path/to/dir\n </Location>\n}}}\n\nor (for mod_python):\n{{{\n <Location /trac>\n   SetHandler mod_python\n   ...\n   SetEnv PYTHON_EGG_CACHE /path/to/dir\n </Location>\n}}}\n\n \'\'Note: !SetEnv requires the `mod_env` module which needs to be activated for Apache. In this case the !SetEnv directive can also be used in the `mod_python` Location block.\'\'\n\nFor [wiki:TracFastCgi FastCGI], you\'ll need to `-initial-env` option, or whatever is provided by your web server for setting environment variables. \n\n \'\'Note: that if you already use -initial-env to set the project directory for either a single project or parent you will need to add an additional -initial-env directive to the !FastCgiConfig directive. I.e.\n\n{{{\nFastCgiConfig -initial-env TRAC_ENV=/var/lib/trac -initial-env PYTHON_EGG_CACHE=/var/lib/trac/plugin-cache\n}}}\n\n=== About hook scripts ===\n\nIf you have set up some subversion hook scripts that call the Trac engine - such as the post-commit hook script provided in the `/contrib` directory - make sure you define the `PYTHON_EGG_CACHE` environment variable within these scripts as well.\n\n== Troubleshooting ==\n\n=== Is setuptools properly installed? ===\n\nTry this from the command line:\n{{{\n$ python -c \"import pkg_resources\"\n}}}\n\nIf you get \'\'\'no output\'\'\', setuptools \'\'\'is\'\'\' installed. Otherwise, you\'ll need to install it before plugins will work in Trac.\n\n=== Did you get the correct version of the Python egg? ===\n\nPython eggs have the Python version encoded in their filename. For example, `MyPlugin-1.0-py2.5.egg` is an egg for Python 2.5, and will \'\'\'not\'\'\' be loaded if you\'re running a different Python version (such as 2.4 or 2.6).\n\nAlso, verify that the egg file you downloaded is indeed a ZIP archive. If you downloaded it from a Trac site, chances are you downloaded the HTML preview page instead.\n\n=== Is the plugin enabled? ===\n\n\nIf you install a plugin globally (i.e. \'\'not\'\' inside the `plugins` directory of the Trac project environment) you will have to explicitly enable it in [TracIni trac.ini]. Make sure that:\n * you actually added the necessary line(s) to the `[components]` section\n * the package/module names are correct\n * the value is â€œenabled\", not e.g. â€œenableâ€\n\n=== Check the permissions on the egg file ===\n\nTrac must be able to read the file. \n\n=== Check the log files ===\n\nEnable [wiki:TracLogging logging] and set the log level to `DEBUG`, then watch the log file for messages about loading plugins.\n\n=== Verify you have proper permissions ===\n\nSome plugins require you have special permissions in order to use them. [trac:WebAdmin WebAdmin], for example, requires the user to have TRAC_ADMIN permissions for it to show up on the navigation bar.\n\n=== Is the wrong version of the plugin loading? ===\n\nIf you put your plugins inside plugins directories, and certainly if you have more than one project, you need to make sure that the correct version of the plugin is loading. Here are some basic rules:\n * Only one version of the plugin can be loaded for each running Trac server (ie. each Python process). The Python namespaces and module list will be shared, and it cannot handle duplicates. Whether a plugin is `enabled` or `disabled` makes no difference.\n * A globally installed plugin (typically `setup.py install`) will override any version in global or project plugins directories. A plugin from the global plugins directory will be located before any project plugins directory.\n * If your Trac server hosts more than one project (as with `TRAC_ENV_PARENT_DIR` setups), then having two versions of a plugin in two different projects will give uncertain results. Only one of them will load, and the one loaded will be shared by both projects. Trac will load the first found - basically from the project that receives the first request.\n * Having more than one version listed inside Python site-packages is fine (ie. installed with `setup.py install`) - setuptools will make sure you get the version installed most recently. However, don\'t store more than one version inside a global or project plugins directory - neither version number nor installed date will matter at all. There is no way to determine which one will be located first when Trac searches the directory for plugins.\n\n=== If all of the above failed ===\n\nOK, so the logs don\'t mention plugins, the egg is readable, the python version is correct \'\'and\'\' the egg has been installed globally (and is enabled in the trac.ini) and it still doesn\'t work or give any error messages or any other indication as to why? Hop on the [trac:IrcChannel IrcChannel] and ask away.\n\n----\nSee also TracGuide, [trac:PluginList plugin list], [trac:TracDev/ComponentArchitecture component architecture]',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracQuery',1,1327389819647871,'trac','127.0.0.1','= Trac Ticket Queries =\n[[TracGuideToc]]\n\nIn addition to [wiki:TracReports reports], Trac provides support for \'\'custom ticket queries\'\', used to display lists of tickets meeting a specified set of criteria. \n\nTo configure and execute a custom query, switch to the \'\'View Tickets\'\' module from the navigation bar, and select the \'\'Custom Query\'\' link.\n\n== Filters ==\n\nWhen you first go to the query page the default filter will display tickets relevant to you:\n * If logged in then all open tickets it will display open tickets assigned to you.\n * If not logged in but you have specified a name or email address in the preferences then it will display all open tickets where your email (or name if email not defined) is in the CC list.\n * If not logged and no name/email defined in the preferences then all open issues are displayed.\n\nCurrent filters can be removed by clicking the button to the right with the minus sign on the label.  New filters are added from the pulldown lists at the bottom corners of the filters box (\'And\' conditions on the left, \'Or\' conditions on the right).  Filters with either a text box or a pulldown menu of options can be added multiple times to perform an \'\'or\'\' of the criteria.\n\nYou can use the fields just below the filters box to group the results based on a field, or display the full description for each ticket.\n\nOnce you\'ve edited your filters click the \'\'Update\'\' button to refresh your results.\n\n== Navigating Tickets ==\nClicking on one of the query results will take you to that ticket.  You can navigate through the results by clicking the \'\'Next Ticket\'\' or \'\'Previous Ticket\'\' links just below the main menu bar, or click the \'\'Back to Query\'\' link to return to the query page.  \n\nYou can safely edit any of the tickets and continue to navigate through the results using the \'\'!Next/Previous/Back to Query\'\' links after saving your results.  When you return to the query \'\'any tickets which were edited\'\' will be displayed with italicized text.  If one of the tickets was edited such that [[html(<span style=\"color: grey\">it no longer matches the query criteria </span>)]] the text will also be greyed. Lastly, if \'\'\'a new ticket matching the query criteria has been created\'\'\', it will be shown in bold. \n\nThe query results can be refreshed and cleared of these status indicators by clicking the \'\'Update\'\' button again.\n\n== Saving Queries ==\n\nTrac allows you to save the query as a named query accessible from the reports module. To save a query ensure that you have \'\'Updated\'\' the view and then click the \'\'Save query\'\' button displayed beneath the results.\nYou can also save references to queries in Wiki content, as described below.\n\n\'\'Note:\'\' one way to easily build queries like the ones below, you can build and test the queries in the Custom report module and when ready - click \'\'Save query\'\'. This will build the query string for you. All you need to do is remove the extra line breaks.\n\n=== Using TracLinks ===\n\nYou may want to save some queries so that you can come back to them later.  You can do this by making a link to the query from any Wiki page.\n{{{\n[query:status=new|assigned|reopened&version=1.0 Active tickets against 1.0]\n}}}\n\nWhich is displayed as:\n  [query:status=new|assigned|reopened&version=1.0 Active tickets against 1.0]\n\nThis uses a very simple query language to specify the criteria (see [wiki:TracQuery#QueryLanguage Query Language]).\n\nAlternatively, you can copy the query string of a query and paste that into the Wiki link, including the leading `?` character:\n{{{\n[query:?status=new&status=assigned&status=reopened&group=owner Assigned tickets by owner]\n}}}\n\nWhich is displayed as:\n  [query:?status=new&status=assigned&status=reopened&group=owner Assigned tickets by owner]\n\n=== Using the `[[TicketQuery]]` Macro ===\n\nThe [trac:TicketQuery TicketQuery] macro lets you display lists of tickets matching certain criteria anywhere you can use WikiFormatting.\n\nExample:\n{{{\n[[TicketQuery(version=0.6|0.7&resolution=duplicate)]]\n}}}\n\nThis is displayed as:\n  [[TicketQuery(version=0.6|0.7&resolution=duplicate)]]\n\nJust like the [wiki:TracQuery#UsingTracLinks query: wiki links], the parameter of this macro expects a query string formatted according to the rules of the simple [wiki:TracQuery#QueryLanguage ticket query language].\n\nA more compact representation without the ticket summaries is also available:\n{{{\n[[TicketQuery(version=0.6|0.7&resolution=duplicate, compact)]]\n}}}\n\nThis is displayed as:\n  [[TicketQuery(version=0.6|0.7&resolution=duplicate, compact)]]\n\nFinally if you wish to receive only the number of defects that match the query using the ``count`` parameter.\n\n{{{\n[[TicketQuery(version=0.6|0.7&resolution=duplicate, count)]]\n}}}\n\nThis is displayed as:\n  [[TicketQuery(version=0.6|0.7&resolution=duplicate, count)]]\n\n=== Customizing the \'\'table\'\' format ===\nYou can also customize the columns displayed in the table format (\'\'format=table\'\') by using \'\'col=<field>\'\' - you can specify multiple fields and what order they are displayed by placing pipes (`|`) between the columns like below:\n\n{{{\n[[TicketQuery(max=3,status=closed,order=id,desc=1,format=table,col=resolution|summary|owner|reporter)]]\n}}}\n\nThis is displayed as:\n[[TicketQuery(max=3,status=closed,order=id,desc=1,format=table,col=resolution|summary|owner|reporter)]]\n\n==== Full rows ====\nIn \'\'table\'\' format you can also have full rows by using \'\'rows=<field>\'\' like below:\n\n{{{\n[[TicketQuery(max=3,status=closed,order=id,desc=1,format=table,col=resolution|summary|owner|reporter,rows=description)]]\n}}}\n\nThis is displayed as:\n[[TicketQuery(max=3,status=closed,order=id,desc=1,format=table,col=resolution|summary|owner|reporter,rows=description)]]\n\n\n=== Query Language ===\n\n`query:` TracLinks and the `[[TicketQuery]]` macro both use a mini â€œquery languageâ€ for specifying query filters. Basically, the filters are separated by ampersands (`&`). Each filter then consists of the ticket field name, an operator, and one or more values. More than one value are separated by a pipe (`|`), meaning that the filter matches any of the values. To include a litteral `&` or `|` in a value, escape the character with a backslash (`\\`).\n\nThe available operators are:\n|| \'\'\'`=`\'\'\' || the field content exactly matches the one of the values ||\n|| \'\'\'`~=`\'\'\' || the field content contains one or more of the values ||\n|| \'\'\'`^=`\'\'\' || the field content starts with one of the values ||\n|| \'\'\'`$=`\'\'\' || the field content ends with one of the values ||\n\nAll of these operators can also be negated:\n|| \'\'\'`!=`\'\'\' || the field content matches none of the values ||\n|| \'\'\'`!~=`\'\'\' || the field content does not contain any of the values ||\n|| \'\'\'`!^=`\'\'\' || the field content does not start with any of the values ||\n|| \'\'\'`!$=`\'\'\' || the field content does not end with any of the values ||\n\nThe date fields `created` and `modified` can be constrained by using the `=` operator and specifying a value containing two dates separated by two dots (`..`). Either end of the date range can be left empty, meaning that the corresponding end of the range is open. The date parser understands a few natural date specifications like \"3 weeks ago\", \"last month\" and \"now\", as well as Bugzilla-style date specifications like \"1d\", \"2w\", \"3m\" or \"4y\" for 1 day, 2 weeks, 3 months and 4 years, respectively. Spaces in date specifications can be left out to avoid having to quote the query string. \n|| \'\'\'`created=2007-01-01..2008-01-01`\'\'\' || query tickets created in 2007 ||\n|| \'\'\'`created=lastmonth..thismonth`\'\'\' || query tickets created during the previous month ||\n|| \'\'\'`modified=1weekago..`\'\'\' || query tickets that have been modified in the last week ||\n|| \'\'\'`modified=..30daysago`\'\'\' || query tickets that have been inactive for the last 30 days ||\n\n----\nSee also: TracTickets, TracReports, TracGuide\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracReports',1,1327389819647871,'trac','127.0.0.1','= Trac Reports =\n[[TracGuideToc]]\n\nThe Trac reports module provides a simple, yet powerful reporting facility\nto present information about tickets in the Trac database.\n\nRather than have its own report definition format, TracReports relies on standard SQL\n`SELECT` statements for custom report definition. \n\n  \'\'\'Note:\'\'\' \'\'The report module is being phased out in its current form because it seriously limits the ability of the Trac team to make adjustments to the underlying database schema. We believe that the [wiki:TracQuery query module] is a good replacement that provides more flexibility and better usability. While there are certain reports that cannot yet be handled by the query module, we intend to further enhance it so that at some point the reports module can be completely removed. This also means that there will be no major enhancements to the report module anymore.\'\'\n\n  \'\'You can already completely replace the reports module by the query module simply by disabling the former in [wiki:TracIni trac.ini]:\'\'\n  {{{\n  [components]\n  trac.ticket.report.* = disabled\n  }}}\n  \'\'This will make the query module the default handler for the â€œView Ticketsâ€ navigation item. We encourage you to try this configuration and report back what kind of features of reports you are missing, if any.\'\'\n\n\nA report consists of these basic parts:\n * \'\'\'ID\'\'\' â€” Unique (sequential) identifier \n * \'\'\'Title\'\'\' â€” Descriptive title\n * \'\'\'Description\'\'\' â€” A brief description of the report, in WikiFormatting text.\n * \'\'\'Report Body\'\'\' â€” List of results from report query, formatted according to the methods described below.\n * \'\'\'Footer\'\'\' â€” Links to alternative download formats for this report.\n\n== Changing Sort Order ==\nSimple reports - ungrouped reports to be specific - can be changed to be sorted by any column simply by clicking the column header. \n\nIf a column header is a hyperlink (red), click the column you would like to sort by. Clicking the same header again reverses the order.\n\n== Changing Report Numbering ==\nThere may be instances where you need to change the ID of the report, perhaps to organize the reports better. At present this requires changes to the trac database. The \'\'report\'\' table has the following schema \'\'(since 0.10)\'\':\n * id integer PRIMARY KEY\n * author text\n * title text\n * query text\n * description text\nChanging the ID changes the shown order and number in the \'\'Available Reports\'\' list and the report\'s perma-link. This is done by running something like:\n{{{\nupdate report set id=5 where id=3;\n}}}\nKeep in mind that the integrity has to be maintained (i.e., ID has to be unique, and you don\'t want to exceed the max, since that\'s managed by SQLite someplace).\n\nYou may also need to update or remove the report number stored in the report or query.\n\n== Navigating Tickets ==\nClicking on one of the report results will take you to that ticket. You can navigate through the results by clicking the \'\'Next Ticket\'\' or \'\'Previous Ticket\'\' links just below the main menu bar, or click the \'\'Back to Report\'\' link to return to the report page.\n\nYou can safely edit any of the tickets and continue to navigate through the results using the \'\'!Next/Previous/Back to Report\'\' links after saving your results, but when you return to the report, there will be no hint about what has changed, as would happen if you were navigating a list of tickets obtained from a query (see TracQuery#NavigatingTickets). \'\'(since 0.11)\'\'\n\n== Alternative Download Formats ==\nAside from the default HTML view, reports can also be exported in a number of alternative formats.\nAt the bottom of the report page, you will find a list of available data formats. Click the desired link to \ndownload the alternative report format.\n\n=== Comma-delimited - CSV (Comma Separated Values) ===\nExport the report as plain text, each row on its own line, columns separated by a single comma (\',\').\n\'\'\'Note:\'\'\' The output is fully escaped so carriage returns, line feeds, and commas will be preserved in the output.\n\n=== Tab-delimited ===\nLike above, but uses tabs (\\t) instead of comma.\n\n=== RSS - XML Content Syndication ===\nAll reports support syndication using XML/RSS 2.0. To subscribe to an RSS feed, click the orange \'XML\' icon at the bottom of the page. See TracRss for general information on RSS support in Trac.\n\n----\n\n== Creating Custom Reports ==\n\n\'\'Creating a custom report requires a comfortable knowledge of SQL.\'\'\n\nA report is basically a single named SQL query, executed and presented by\nTrac.  Reports can be viewed and created from a custom SQL expression directly\nin the web interface.\n\nTypically, a report consists of a SELECT-expression from the \'ticket\' table,\nusing the available columns and sorting the way you want it.\n\n== Ticket columns ==\nThe \'\'ticket\'\' table has the following columns:\n * id\n * type\n * time\n * changetime\n * component\n * severity  \n * priority \n * owner\n * reporter\n * cc\n * version\n * milestone\n * status\n * resolution\n * summary\n * description\n * keywords\n\nSee TracTickets for a detailed description of the column fields.\n\nExample: \'\'\'All active tickets, sorted by priority and time\'\'\'\n{{{\nSELECT id AS ticket, status, severity, priority, owner, \n       time AS created, summary FROM ticket \n  WHERE status IN (\'new\', \'assigned\', \'reopened\')\n  ORDER BY priority, time\n}}}\n\n---\n\n== Advanced Reports: Dynamic Variables ==\nFor more flexible reports, Trac supports the use of \'\'dynamic variables\'\' in report SQL statements. \nIn short, dynamic variables are \'\'special\'\' strings that are replaced by custom data before query execution.\n\n=== Using Variables in a Query ===\nThe syntax for dynamic variables is simple, any upper case word beginning with \'$\' is considered a variable.\n\nExample:\n{{{\nSELECT id AS ticket,summary FROM ticket WHERE priority=$PRIORITY\n}}}\n\nTo assign a value to $PRIORITY when viewing the report, you must define it as an argument in the report URL, leaving out the leading \'$\'.\n\nExample:\n{{{\n http://trac.edgewall.org/reports/14?PRIORITY=high\n}}}\n\nTo use multiple variables, separate them with an \'&\'.\n\nExample:\n{{{\n http://trac.edgewall.org/reports/14?PRIORITY=high&SEVERITY=critical\n}}}\n\n\n=== !Special/Constant Variables ===\nThere is one dynamic variable whose value is set automatically (the URL does not have to be changed) to allow practical reports. \n\n * $USER â€” Username of logged in user.\n\nExample (\'\'List all tickets assigned to me\'\'):\n{{{\nSELECT id AS ticket,summary FROM ticket WHERE owner=$USER\n}}}\n\n\n----\n\n\n== Advanced Reports: Custom Formatting ==\nTrac is also capable of more advanced reports, including custom layouts,\nresult grouping and user-defined CSS styles. To create such reports, we\'ll use\nspecialized SQL statements to control the output of the Trac report engine.\n\n== Special Columns ==\nTo format reports, TracReports looks for \'magic\' column names in the query\nresult. These \'magic\' names are processed and affect the layout and style of the \nfinal report.\n\n=== Automatically formatted columns ===\n * \'\'\'ticket\'\'\' â€” Ticket ID number. Becomes a hyperlink to that ticket. \n * \'\'\'id\'\'\' â€” same as \'\'\'ticket\'\'\' above when \'\'\'realm\'\'\' is not set\n * \'\'\'realm\'\'\' â€” together with \'\'\'id\'\'\', can be used to create links to other resources than tickets (e.g. a realm of \'\'wiki\'\' and an \'\'id\'\' to a page name will create a link to that wiki page)\n * \'\'\'created, modified, date, time\'\'\' â€” Format cell as a date and/or time.\n * \'\'\'description\'\'\' â€” Ticket description field, parsed through the wiki engine.\n\n\'\'\'Example:\'\'\'\n{{{\nSELECT id AS ticket, created, status, summary FROM ticket \n}}}\n\nThose columns can also be defined but marked as hidden, see [#column-syntax below].\n\nSee trac:wiki/CookBook/Configuration/Reports for some example of creating reports for realms other than \'\'ticket\'\'.\n\n=== Custom formatting columns ===\nColumns whose names begin and end with 2 underscores (Example: \'\'\'`__color__`\'\'\') are\nassumed to be \'\'formatting hints\'\', affecting the appearance of the row.\n \n * \'\'\'`__group__`\'\'\' â€” Group results based on values in this column. Each group will have its own header and table.\n * \'\'\'`__grouplink__`\'\'\' â€” Make the header of each group a link to the specified URL. The URL is taken from the first row of each group.\n * \'\'\'`__color__`\'\'\' â€” Should be a numeric value ranging from 1 to 5 to select a pre-defined row color. Typically used to color rows by issue priority.\n{{{\n#!html\n<div style=\"margin-left:7.5em\">Defaults: \n<span style=\"border: none; color: #333; background: transparent;  font-size: 85%; background: #fdc; border-color: #e88; color: #a22\">Color 1</span>\n<span style=\"border: none; color: #333; background: transparent;  font-size: 85%; background: #ffb; border-color: #eea; color: #880\">Color 2</span>\n<span style=\"border: none; color: #333; background: transparent;  font-size: 85%; background: #fbfbfb; border-color: #ddd; color: #444\">Color 3</span>\n<span style=\"border: none; color: #333; background: transparent; font-size: 85%; background: #e7ffff; border-color: #cee; color: #099\">Color 4</span>\n<span style=\"border: none; color: #333; background: transparent;  font-size: 85%; background: #e7eeff; border-color: #cde; color: #469\">Color 5</span>\n</div>\n}}}\n * \'\'\'`__style__`\'\'\' â€” A custom CSS style expression to use for the current row. \n\n\'\'\'Example:\'\'\' \'\'List active tickets, grouped by milestone, group header linked to milestone page, colored by priority\'\'\n{{{\nSELECT p.value AS __color__,\n     t.milestone AS __group__,\n     \'../milestone/\' || t.milestone AS __grouplink__,\n     (CASE owner WHEN \'daniel\' THEN \'font-weight: bold; background: red;\' ELSE \'\' END) AS __style__,\n       t.id AS ticket, summary\n  FROM ticket t,enum p\n  WHERE t.status IN (\'new\', \'assigned\', \'reopened\') \n    AND p.name=t.priority AND p.type=\'priority\'\n  ORDER BY t.milestone, p.value, t.severity, t.time\n}}}\n\n\'\'\'Note:\'\'\' A table join is used to match \'\'ticket\'\' priorities with their\nnumeric representation from the \'\'enum\'\' table.\n\n=== Changing layout of report rows === #column-syntax\nBy default, all columns on each row are display on a single row in the HTML\nreport, possibly formatted according to the descriptions above. However, it\'s\nalso possible to create multi-line report entries.\n\n * \'\'\'`column_`\'\'\' â€” \'\'Break row after this\'\'. By appending an underscore (\'_\') to the column name, the remaining columns will be be continued on a second line.\n\n * \'\'\'`_column_`\'\'\' â€” \'\'Full row\'\'. By adding an underscore (\'_\') both at the beginning and the end of a column name, the data will be shown on a separate row.\n\n * \'\'\'`_column`\'\'\' â€” \'\'Hide data\'\'. Prepending an underscore (\'_\') to a column name instructs Trac to hide the contents from the HTML output. This is useful for information to be visible only if downloaded in other formats (like CSV or RSS/XML).\n   This can be used to hide any kind of column, even important ones required for identifying the resource, e.g. `id as _id` will hide the \'\'\'Id\'\'\' column but the link to the ticket will be present.\n\n\'\'\'Example:\'\'\' \'\'List active tickets, grouped by milestone, colored by priority, with  description and multi-line layout\'\'\n\n{{{\nSELECT p.value AS __color__,\n       t.milestone AS __group__,\n       (CASE owner \n          WHEN \'daniel\' THEN \'font-weight: bold; background: red;\' \n          ELSE \'\' END) AS __style__,\n       t.id AS ticket, summary AS summary_,             -- ## Break line here\n       component,version, severity, milestone, status, owner,\n       time AS created, changetime AS modified,         -- ## Dates are formatted\n       description AS _description_,                    -- ## Uses a full row\n       changetime AS _changetime, reporter AS _reporter -- ## Hidden from HTML output\n  FROM ticket t,enum p\n  WHERE t.status IN (\'new\', \'assigned\', \'reopened\') \n    AND p.name=t.priority AND p.type=\'priority\'\n  ORDER BY t.milestone, p.value, t.severity, t.time\n}}}\n\n=== Reporting on custom fields ===\n\nIf you have added custom fields to your tickets (a feature since v0.8, see TracTicketsCustomFields), you can write a SQL query to cover them. You\'ll need to make a join on the ticket_custom table, but this isn\'t especially easy.\n\nIf you have tickets in the database \'\'before\'\' you declare the extra fields in trac.ini, there will be no associated data in the ticket_custom table. To get around this, use SQL\'s \"LEFT OUTER JOIN\" clauses. See [trac:TracIniReportCustomFieldSample TracIniReportCustomFieldSample] for some examples.\n\n\'\'\'Note that you need to set up permissions in order to see the buttons for adding or editing reports.\'\'\'\n\n----\nSee also: TracTickets, TracQuery, TracGuide, [http://www.sqlite.org/lang_expr.html Query Language Understood by SQLite]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracRepositoryAdmin',1,1327389819647871,'trac','127.0.0.1','= Repository Administration =\n[[PageOutline(2-3)]]\n\n== Quick start == #QuickStart\n\n * Manage repositories in the \"Repository\" admin panel, with `trac-admin` or in the `[repositories]` section of [wiki:TracIni#repositories-section trac.ini].\n * Set up a call to `trac-admin $ENV changeset added $REPO $REV` in the post-commit hook of each repository. Additionally, add a call to `trac-admin $ENV changeset modified $REPO $REV` in the post-revprop-change hook of repositories allowing revision property changes.\n * Set the `[trac] repository_sync_per_request` option to an empty value to disable per-request syncing.\n\n\n== Specifying repositories == #Repositories\nStarting with 0.12, Trac can handle more than one repository per environment. The pre-0.12 way of specifying the repository with the `repository_dir` and `repository_type` options in the `[trac]` section of [wiki:TracIni trac.ini] is still supported, but two new mechanisms allow including additional repositories into an environment.\n\nIt is also possible to define aliases of repositories, that act as \"pointers\" to real repositories. This can be useful when renaming a repository, to avoid breaking all the links to the old name.\n\nA number of attributes can be associated with each repository, which define the repository\'s location, type, name and how it is displayed in the source browser. The following attributes are supported:\n\n||=\'\'\'Attribute\'\'\' =||=\'\'\'Description\'\'\' =||\n||`alias` ||\\\n||A repository having an `alias` attribute is an alias to a real repository. All TracLinks referencing the alias resolve to the aliased repository. Note that multiple indirection is not supported, so an alias must always point to a real repository. The `alias` and `dir` attributes are mutually exclusive. ||\n||`description` ||\\\n||The text specified in the `description` attribute is displayed below the top-level entry for the repository in the source browser. It supports WikiFormatting. ||\n||`dir` ||\\\n||The `dir` attribute specifies the location of the repository in the filesystem. It corresponds to the value previously specified in the option `[trac] repository_dir`. The `alias` and `dir` attributes are mutually exclusive. ||\n||`hidden` ||When set to `true`, the repository is hidden from the repository index page in the source browser. Browsing the repository is still possible, and links referencing the repository remain valid. ||\n||`name` ||The `name` attribute specifies the leading path element to the repository. ||\n||`type` ||The `type` attribute sets the type of version control system used by the repository. Trac supports Subversion out-of-the-box, and plugins add support for many other systems. If `type` is not specified, it defaults to the value of the `[trac] repository_type` option. ||\n||`url` ||The `url` attribute specifies the root URL to be used for checking out from the repository. When specified, a \"Repository URL\" link is added to the context navigation links in the source browser, that can be copied into the tool used for creating the working copy. ||\n\nThe `name` attribute and one of `alias` or `dir` are mandatory. All others are optional.\n\nAfter adding a repository, the cache for that repository must be re-synchronized once with the `trac-admin $ENV repository resync` command.\n\n `repository resync <repos>`::\n   Re-synchronize Trac with a repository.\n\n\n=== In `trac.ini` === #ReposTracIni\nRepositories and repository attributes can be specified in the `[repositories]` section of [wiki:TracIni#repositories-section trac.ini]. Every attribute consists of a key structured as `{name}.{attribute}` and the corresponding value separated with an equal sign (`=`). The name of the default repository is empty.\n\nThe main advantage of specifying repositories in `trac.ini` is that they can be inherited from a global configuration (see the [wiki:TracIni#GlobalConfiguration global configuration] section of TracIni). One drawback is that, due to limitations in the `ConfigParser` class used to parse `trac.ini`, the repository name is always all-lowercase.\n\nThe following example defines two Subversion repositories named `project` and `lib`, and a hidden alias to `project` as the default repository. This is a typical use case where a Trac environment previously had a single repository (the `project` repository), and was converted to multiple repositories. The alias ensures that links predating the change continue to resolve to the `project` repository.\n{{{\n#!ini\n[repositories]\nproject.dir = /var/repos/project\nproject.description = This is the \'\'main\'\' project repository.\nproject.type = svn\nproject.url = http://example.com/svn/project\nlib.dir = /var/repos/lib\nlib.description = This is the secondary library code.\nlib.type = svn\nlib.url = http://example.com/svn/lib\n.alias = project\n.hidden = true\n}}}\nNote that `name.alias = target` makes `name` an alias for the `target` repo, not the other way around.\n\n=== In the database === #ReposDatabase\nRepositories can also be specified in the database, using either the \"Repositories\" admin panel under \"Version Control\", or the `trac-admin $ENV repository` commands.\n\nThe admin panel shows the list of all repositories defined in the Trac environment. It allows adding repositories and aliases, editing repository attributes and removing repositories. Note that repositories defined in `trac.ini` are displayed but cannot be edited.\n\nThe following [wiki:TracAdmin trac-admin] commands can be used to perform repository operations from the command line.\n\n `repository add <repos> <dir> [type]`::\n   Add a repository `<repos>` located at `<dir>`, and optionally specify its type.\n\n `repository alias <name> <target>`::\n   Create an alias `<name>` for the repository `<target>`.\n\n `repository remove <repos>`::\n   Remove the repository `<repos>`.\n\n `repository set <repos> <key> <value>`::\n   Set the attribute `<key>` to `<value>` for the repository `<repos>`. \n\nNote that the default repository has an empty name, so it will likely need to be quoted when running `trac-admin` from a shell. Alternatively, the name \"`(default)`\" can be used instead, for example when running `trac-admin` in interactive mode.\n\n\n== Repository synchronization == #Synchronization\nPrior to 0.12, Trac synchronized its cache with the repository on every HTTP request. This approach is not very efficient and not practical anymore with multiple repositories. For this reason, explicit synchronization through post-commit hooks was added. \n\nThere is also new functionality in the form of a repository listener extension point \'\'(IRepositoryChangeListener)\'\' that is triggered by the post-commit hook when a changeset is added or modified, and can be used by plugins to perform actions on commit.\n\n=== Mercurial Repositories ===\nPlease note that at the time of writing, no initial resynchronization or any hooks are necessary for Mercurial repositories - see [trac:#9485] for more information. \n\n=== Explicit synchronization === #ExplicitSync\nThis is the preferred method of repository synchronization. It requires setting the `[trac]  repository_sync_per_request` option in [wiki:TracIni#trac-section trac.ini] to an empty value, and adding a call to `trac-admin` in the post-commit hook of each repository. Additionally, if a repository allows changing revision metadata, a call to `trac-admin` must be added to the post-revprop-change hook as well.\n\n `changeset added <repos> <rev> [...]`::\n   Notify Trac that one or more changesets have been added to a repository.\n\n `changeset modified <repos> <rev> [...]`::\n   Notify Trac that metadata on one or more changesets in a repository has been modified.\n\nThe `<repos>` argument can be either a repository name (use \"`(default)`\" for the default repository) or the path to the repository.\n\nNote that you may have to set the environment variable PYTHON_EGG_CACHE to the same value as was used for the web server configuration before calling trac-admin, if you changed it from its default location. See [wiki:TracPlugins Trac Plugins] for more information.\n\nThe following examples are complete post-commit and post-revprop-change scripts for Subversion. They should be edited for the specific environment, marked executable (where applicable) and placed in the `hooks` directory of each repository. On Unix (`post-commit`):\n{{{#!sh\n#!/bin/sh\nexport PYTHON_EGG_CACHE=\"/path/to/dir\"\n/usr/bin/trac-admin /path/to/env changeset added \"$1\" \"$2\"\n}}}\nOn Windows (`post-commit.cmd`):\n{{{#!application/x-dos-batch\n@C:\\Python26\\Scripts\\trac-admin.exe C:\\path\\to\\env changeset added \"%1\" \"%2\"\n}}}\n\nThe post-revprop-change hook for Subversion is very similar. On Unix (`post-revprop-change`):\n{{{#!sh\n#!/bin/sh\nexport PYTHON_EGG_CACHE=\"/path/to/dir\"\n/usr/bin/trac-admin /path/to/env changeset modified \"$1\" \"$2\"\n}}}\nOn Windows (`post-revprop-change.cmd`):\n{{{#!application/x-dos-batch\n@C:\\Python26\\Scripts\\trac-admin.exe C:\\path\\to\\env changeset modified \"%1\" \"%2\"\n}}}\n\nThe Unix variants above assume that the user running the Subversion commit has write access to the Trac environment, which is the case in the standard configuration where both the repository and Trac are served by the web server. If you access the repository through another means, for example `svn+ssh://`, you may have to run `trac-admin` with different privileges, for example by using `sudo`.\n\nNote that calling `trac-admin` in your Subversion hooks can slow down the commit and log editing operations on the client side. You might want to use the [trac:source:trunk/contrib/trac-svn-hook contrib/trac-svn-hook] script which starts `trac-admin` in an asynchronous way. The script also comes with a number of safety checks and usage advices which should make it easier to set up and test your hooks. There\'s no equivalent `trac-svn-hook.bat` for Windows yet, but the script can be run by Cygwin\'s bash.\n\nSee the [http://svnbook.red-bean.com/en/1.5/svn.reposadmin.create.html#svn.reposadmin.create.hooks section about hooks] in the Subversion book for more information. Other repository types will require different hook setups. Please see the plugin documentation for specific instructions.\n\n=== Per-request synchronization === #PerRequestSync\nIf the post-commit hooks are not available, the environment can be set up for per-request synchronization. In that case, the `[trac] repository_sync_per_request` option in [wiki:TracIni#trac-section trac.ini] must be set to a comma-separated list of repository names to be synchronized.\n\nNote that in this case, the changeset listener extension point is not called, and therefore plugins using it will not work correctly.\n\n\n== Migration from a single-repository setup (Subversion) == #Migration\nThe following procedure illustrates a typical migration from a Subversion single-repository setup to multiple repositories.\n\n 1. Remove the default repository specification from the `[trac] repository_dir` option.\n 1. Add the \"main\" repository as a named repository.\n 1. Re-synchronize the main repository.\n 1. Set up post-commit and post-revprop-change hooks on the main repository, and set `[trac] repository_sync_per_request` to an empty value.\n 1. Add a hidden alias to the main repository as the default repository. This ensures that all links predating the migration still resolve to the main repository.\n 1. Repeat steps 2, 3 and 4 to add other (named) repositories as needed.\n\n== Migration from a single-repository setup (Mercurial) == #MigrationMercurial\nThe following procedure illustrates a typical migration from a Mercurial single-repository setup to multiple repositories. Please note that at the time of writing, no initial resynchronization or any hooks are necessary for Mercurial repositories - see #9485 for more information.\n\n 1. Upgrade to the latest version of the TracMercurial plugin.\n 1. Remove the default repository specification from the `[trac] repository_dir` option.\n 1. Add the \"main\" repository as a named repository.\n 1. Add a hidden alias to the main repository as the default repository. This ensures that all links predating the migration still resolve to the main repository.\n 1. Repeat step 3 to add other (named) repositories as needed.\n\n== Troubleshooting ==\n\n=== My trac-post-commit-hook doesn\'t work anymore === #trac-post-commit-hook\n\nYou must now use the optional components from `tracopt.ticket.commit_updater.*`, which you can activate through the Plugins panel in the Administrative part of the web interface, or by directly modifying the [TracIni#components-section \"[components]\"] section in the trac.ini. Be sure to use [#ExplicitSync explicit synchronization] as explained above.\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracRevisionLog',1,1327389819647871,'trac','127.0.0.1','= Viewing Revision Logs =\n[[TracGuideToc]]\n\nWhen you browse the repository, it\'s always possible to query the \n\'\'Revision Log\'\' view corresponding to the path you\'re currently seeing.\nThis will display a list of the most recent changesets in which the \ncurrent path or any other path below it has been modified.\n\n== The Revision Log Form ==\n\nIt\'s possible to set the revision at which the revision log should\nstart, using the \'\'View log starting at\'\' field. An empty value\nor a value of \'\'head\'\' is taken to be the newest changeset. \n\nIt\'s also possible to specify the revision at which the log should\nstop, using the \'\'back to\'\' field. By default, it\'s left empty, \nwhich means the revision log will stop as soon as 100 revisions have \nbeen listed.\n\nAlso, there are three modes of operation of the revision log.\n\nBy default, the revision log \'\'stops on copy\'\', which means that \nwhenever an \'\'Add\'\', \'\'Copy\'\' or \'\'Rename\'\' operation is detected, \nno older revision will be shown. That\'s very convenient when working\nwith branches, as one only sees the history corresponding to what\nhas been done on the branch.\n\nIt\'s also possible to indicate that one wants to see what happened\nbefore a \'\'Copy\'\' or \'\'Rename\'\' change, by selecting the \n\'\'Follow copies\'\' mode. This will cross all copies or renames changes.\nEach time the name of the path changes, there will be an additional\nindentation level. That way, the changes on the different paths\nare easily grouped together visually.\n\nIt\'s even possible to go past an \'\'Add\'\' change, in order to see \nif there has been a \'\'Delete\'\' change on that path, before \nthat \'\'Add\'\'. This mode corresponds to the mode called \n\'\'Show only adds, moves and deletes\'\'. \nWhile quite useful at times, be aware that this operation is quite \nresource intensive.\n\nFinally, there\'s also a checkbox \'\'Show full log messages\'\',\nwhich controls whether the full content of the commit log message\nshould be displayed for each change, or only a shortened version of it.\n\n== The Revision Log Information ==\n\nFor each revision log entry, there are 7 columns:\n 1. The first column contains a pair of radio buttons and should be used \n    for selecting the \'\'old\'\' and the \'\'new\'\' revisions that will be \n    used for [wiki:TracRevisionLog#viewingtheactualchanges viewing the actual changes].\n 1. A color code (similar to the one used for the\n    [wiki:TracChangeset#ChangesetHeader changesets]) indicating kind of change.\n    Clicking on this column refreshes the revision log so that it restarts\n    with this change.\n 1. The \'\'\'Revision\'\'\' number, displayed as `@xyz`.\n    This is a link to the TracBrowser, using the displayed revision as the base line.\n 1. The \'\'\'Changeset\'\'\' number, displayed as `[xyz]`.\n    This is a link to the TracChangeset view.\n 1. The \'\'\'Date\'\'\' at which the change was made.\n    The date is displayed as the time elapsed from the date of the revision. The time\n    elapsed is displayed as the number of hours, days, weeks, months, or years.\n 1. The \'\'\'Author\'\'\' of the change.\n 1. The \'\'\'Log Message\'\'\', which contains either the truncated or full commit \n    log message, depending on the value of the \'\'Show full log messages\'\' \n    checkbox in the form above.\n    \n\n== Inspecting Changes Between Revisions ==\n\nThe \'\'View changes...\'\' buttons (placed above and below the list\nof changes, on the left side) will show the set of differences\ncorresponding to the aggregated changes starting from the \'\'old\'\'\nrevision (first radio-button) to the \'\'new\'\' revision (second\nradio-button), in the TracChangeset view.\n\nNote that the \'\'old\'\' revision doesn\'t need to be actually \n\'\'older\'\' than the \'\'new\'\' revision: it simply gives a base\nfor the diff. It\'s therefore entirely possible to easily \ngenerate a \'\'reverse diff\'\', for reverting what has been done\nin the given range of revisions.\n\nFinally, if the two revisions are identical, the corresponding\nchangeset will be shown (same effect as clicking on the !ChangeSet number).\n\n== Alternative Formats ==\n\n=== The !ChangeLog Text ===\n\nAt the bottom of the page, there\'s a \'\'!ChangeLog\'\' link\nthat will show the range of revisions as currently shown,\nbut as a simple text, matching the usual conventions for\n!ChangeLog files.\n\n=== RSS Support ===\n\nThe revision log also provides a RSS feed to monitor the changes.\nTo subscribe to a RSS feed for a file or directory, open its\nrevision log in the browser and click the orange \'XML\' icon at the bottom\nof the page. For more information on RSS support in Trac, see TracRss.\n\n----\nSee also: TracBrowser, TracChangeset, TracGuide',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracRoadmap',1,1327389819647871,'trac','127.0.0.1','= The Trac Roadmap =\n[[TracGuideToc]]\n\nThe roadmap provides a view on the [wiki:TracTickets ticket system] that helps planning and managing the future development of a project.\n\n== The Roadmap View ==\n\nBasically, the roadmap is just a list of future milestones. You can add a description to milestones (using WikiFormatting) describing main objectives, for example. In addition, tickets targeted for a milestone are aggregated, and the ratio between active and resolved tickets is displayed as a milestone progress bar.  It is possible to further [trac:TracRoadmapCustomGroups customise the ticket grouping] and have multiple ticket statuses shown on the progress bar.\n\nThe roadmap can be filtered to show or hide \'\'completed milestones\'\' and \'\'milestones with no due date\'\'. In the case that both \'\'show completed milestones\'\' and \'\'hide milestones with no due date\'\' are selected, \'\'completed\'\' milestones with no due date __will__ be shown.\n\n== The Milestone View ==\n\nYou can add a description for each milestone (using WikiFormatting) describing main objectives, for example. In addition, tickets targeted for a milestone are aggregated, and the ratio between active and resolved tickets is displayed as a milestone progress bar.  It is possible to further [trac:TracRoadmapCustomGroups customise the ticket grouping] and have multiple ticket statuses shown on the progress bar.\n\nIt is possible to drill down into this simple statistic by viewing the individual milestone pages. By default, the active/resolved ratio will be grouped and displayed by component. You can also regroup the status by other criteria, such as ticket owner or severity. Ticket numbers are linked to [wiki:TracQuery custom queries] listing corresponding tickets.\n\n== Roadmap Administration ==\n\nWith appropriate permissions it is possible to add, modify and remove milestones using either the web interface (roadmap and milestone pages), web administration interface or by using `trac-admin`. \n\n\'\'\'Note:\'\'\' Milestone descriptions can not currently be edited using \'trac-admin\'.\n\n== iCalendar Support ==\n\nThe Roadmap supports the [http://www.ietf.org/rfc/rfc2445.txt iCalendar] format to keep track of planned milestones and related tickets from your favorite calendar software. Many calendar applications support the iCalendar specification including\n * [http://www.apple.com/ical/ Apple iCal] for Mac OS X\n * the cross-platform [http://www.mozilla.org/projects/calendar/ Mozilla Calendar]\n * [http://chandlerproject.org Chandler]\n * [http://kontact.kde.org/korganizer/ Korganizer] (the calendar application of the [http://www.kde.org/ KDE] project)\n * [http://www.novell.com/de-de/products/desktop/features/evolution.html Evolution] also support iCalendar\n * [http://office.microsoft.com/en-us/outlook/ Microsoft Outlook] can also read iCalendar files (it appears as a new static calendar in Outlook)\n\nTo subscribe to the roadmap, copy the iCalendar link from the roadmap (found at the bottom of the page) and choose the \"Subscribe to remote calendar\" action (or similar) of your calendar application, and insert the URL just copied.\n\n\'\'\'Note:\'\'\' For tickets to be included in the calendar as tasks, you need to be logged in when copying the link. You will only see tickets assigned to yourself, and associated with a milestone.\n\nMore information about iCalendar can be found at [http://en.wikipedia.org/wiki/ICalendar Wikipedia].\n----\nSee also: TracTickets, TracReports, TracQuery, [trac:TracRoadmapCustomGroups TracRoadmapCustomGroups]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracRss',1,1327389819647871,'trac','127.0.0.1','= Using RSS with Trac =\n[[TracGuideToc]]\n\nSeveral of the Trac modules support content syndication using the RSS (Really Simple Syndication) XML format.\nUsing the RSS subscription feature in Trac, you can easily monitor progress of the project, a set of issues or even changes to a single file.\n\nTrac supports RSS feeds in:\n\n * TracTimeline â€”  Use the RSS feed to \'\'\'subscribe to project events\'\'\'.[[br]]Monitor overall project progress in your favorite RSS reader.\n * TracTickets, TracReports, and TracQuery â€” Allows syndication of report and ticket query results.[[br]]Be notified about important and relevant issue tickets.\n * TracBrowser and TracRevisionLog â€” Syndication of file changes.[[br]]Stay up to date with changes to a specific file or directory.\n\n== How to access RSS data ==\nAnywhere in Trac where RSS is available, you should find a small orange \'\'\'XML\'\'\' icon, typically placed at the bottom of the page. Clicking the icon will access the RSS feed for that specific resource.\n\n\'\'\'Note:\'\'\' Different modules provide different data in their RSS feeds. Usually, the syndicated information corresponds to the current view. For example, if you click the RSS link on a report page, the feed will be based on that report. It might be explained by thinking of the RSS feeds as an \'\'alternate view of the data currently displayed\'\'.\n\n== Links ==\n * \'\'Specifications:\'\'\n   * http://blogs.law.harvard.edu/tech/rss â€” RSS 2.0 Specification\n\n * \'\'Multi-platform RSS readers:\'\'\n   * http://www.rssowl.org/ â€” Open source, Eclipse-based, RSS reader for Linux, Mac and Windows systems that supports https and authenticated feeds.\n\n * \'\'Linux/BSD/*n*x systems:\'\'\n   * http://pim.kde.org/users.php â€” [http://kde.org KDE] RSS Reader for Linux/BSD/*n*x systems\n   * http://liferea.sourceforge.net/ â€” Open source GTK2 RSS Reader for Linux\n   * http://akregator.sourceforge.net/ â€” Open source KDE RSS Reader (part of KDE-PIM)\n\n * \'\'Mac OS X systems:\'\'\n   * http://ranchero.com/netnewswire/ â€” An excellent RSS reader for Mac OS X (has both free and pay versions)\n   * http://www.utsire.com/shrook/ â€” An RSS reader for Max OS X that supports https (even with self signed certificates) and authenticated feeds.\n   * http://vienna-rss.sourceforge.net/ â€” Open source Feed Reader for Mac OS X with smart folders support\n   * http://www.mesadynamics.com/Tickershock.html â€” Non-intrusive \"news ticker\" style RSS reader for Mac OS X\n\n * \'\'Windows systems:\'\'\n   * http://www.rssreader.com/ â€” Free and powerful RSS Reader for Windows\n   * http://www.sharpreader.net/ â€” A free RSS Reader written in .NET for Windows\n\n * \'\'Firefox:\'\'\n   * http://www.mozilla.org/products/firefox/ â€” Mozilla Firefox supports [http://www.mozilla.org/products/firefox/live-bookmarks.html live bookmarks] using RSS\n   * http://sage.mozdev.org â€” Sage RSS and Atom feed aggregator for Mozilla Firefox\n   * http://www.wizzrss.com/Welcome.php â€” WizzRSS Feed Reader for Firefox\n\n----\nSee also: TracGuide, TracTimeline, TracReports, TracBrowser\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracSearch',1,1327389819647871,'trac','127.0.0.1','= Using Search =\n\nTrac has a built-in search engine to allow finding occurrences of keywords and substrings in wiki pages, tickets and changeset properties (author, revision and log message).\n\nUsing the Trac search facility is straightforward and its interface should be familiar to most users.\n\nApart from the [search: Search module], you will also find a small search field above the navigation bar at all time. It provides convenient access to the search module from all pages.\n\n== \"Quickjump\" searches ==\nFor quick access to various project resources, the quick-search field at the top of every page can be used to enter a [TracLinks wiki link], which will take you directly to the resource identified by that link.\n\nFor example:\n\n * ![42] -- Opens change set 42\n * !#42 -- Opens ticket number 42\n * !{1} -- Opens report 1\n * /trunk -- Opens the browser for the `trunk` directory\n\n== Advanced ==\n\n=== Disabling Quickjumps ===\nTo disable the quickjump feature for a search keyword - for example when searching for occurences of the literal word !TracGuide - begin the query with an exclamation mark (!).\n\n=== Search Links ===\nFrom the Wiki, it is possible to link to a specific search, using\n`search:` links:\n * `search:?q=crash` will search for the string \"crash\" \n * `search:?q=trac+link&wiki=on` will search for \"trac\" and \"link\" \n   in wiki pages only\n\n----\nSee also: TracGuide, TracLinks, TracQuery',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracStandalone',1,1327389819647871,'trac','127.0.0.1','= Tracd =\n\nTracd is a lightweight standalone Trac web server.\nIt can be used in a variety of situations, from a test or development server to a multiprocess setup behind another web server used as a load balancer.\n\n== Pros ==\n\n * Fewer dependencies: You don\'t need to install apache or any other web-server.\n * Fast: Should be almost as fast as the [wiki:TracModPython mod_python] version (and much faster than the [wiki:TracCgi CGI]), even more so since version 0.12 where the HTTP/1.1 version of the protocol is enabled by default\n * Automatic reloading: For development, Tracd can be used in \'\'auto_reload\'\' mode, which will automatically restart the server whenever you make a change to the code (in Trac itself or in a plugin).\n\n== Cons ==\n\n * Fewer features: Tracd implements a very simple web-server and is not as configurable or as scalable as Apache httpd.\n * No native HTTPS support: [http://www.rickk.com/sslwrap/ sslwrap] can be used instead,\n   or [http://trac.edgewall.org/wiki/STunnelTracd stunnel -- a tutorial on how to use stunnel with tracd] or Apache with mod_proxy.\n\n== Usage examples ==\n\nA single project on port 8080. (http://localhost:8080/)\n{{{\n $ tracd -p 8080 /path/to/project\n}}}\nStricly speaking this will make your Trac accessible to everybody from your network rather than \'\'localhost only\'\'. To truly limit it use \'\'--hostname\'\' option.\n{{{\n $ tracd --hostname=localhost -p 8080 /path/to/project\n}}}\nWith more than one project. (http://localhost:8080/project1/ and http://localhost:8080/project2/)\n{{{\n $ tracd -p 8080 /path/to/project1 /path/to/project2\n}}}\n\nYou can\'t have the last portion of the path identical between the projects since Trac uses that name to keep the URLs of the\ndifferent projects unique. So if you use `/project1/path/to` and `/project2/path/to`, you will only see the second project.\n\nAn alternative way to serve multiple projects is to specify a parent directory in which each subdirectory is a Trac project, using the `-e` option. The example above could be rewritten:\n{{{\n $ tracd -p 8080 -e /path/to\n}}}\n\nTo exit the server on Windows, be sure to use {{{CTRL-BREAK}}} -- using {{{CTRL-C}}} will leave a Python process running in the background.\n\n== Installing as a Windows Service ==\n\n=== Option 1 ===\nTo install as a Windows service, get the [http://www.google.com/search?q=srvany.exe SRVANY] utility and run:\n{{{\n C:\\path\\to\\instsrv.exe tracd C:\\path\\to\\srvany.exe\n reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\tracd\\Parameters /v Application /d \"\\\"C:\\path\\to\\python.exe\\\" \\\"C:\\path\\to\\python\\scripts\\tracd-script.py\\\" <your tracd parameters>\"\n net start tracd\n}}}\n\n\'\'\'DO NOT\'\'\' use {{{tracd.exe}}}.  Instead register {{{python.exe}}} directly with {{{tracd-script.py}}} as a parameter.  If you use {{{tracd.exe}}}, it will spawn the python process without SRVANY\'s knowledge.  This python process will survive a {{{net stop tracd}}}.\n\nIf you want tracd to start automatically when you boot Windows, do:\n{{{\n sc config tracd start= auto\n}}}\n\nThe spacing here is important.\n\n{{{#!div\nOnce the service is installed, it might be simpler to run the Registry Editor rather than use the `reg add` command documented above.  Navigate to:[[BR]]\n`HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\tracd\\Parameters`\n\nThree (string) parameters are provided:\n||!AppDirectory ||C:\\Python26\\ ||\n||Application ||python.exe ||\n||!AppParameters ||scripts\\tracd-script.py -p 8080 ... ||\n\nNote that, if the !AppDirectory is set as above, the paths of the executable \'\'and\'\' of the script name and parameter values are relative to the directory.  This makes updating Python a little simpler because the change can be limited, here, to a single point.\n(This is true for the path to the .htpasswd file, as well, despite the documentation calling out the /full/path/to/htpasswd; however, you may not wish to store that file under the Python directory.)\n}}}\n\nFor Windows 7 User, srvany.exe may not be an option, so you can use [http://www.google.com/search?q=winserv.exe WINSERV] utility and run:\n{{{\n\"C:\\path\\to\\winserv.exe\" install tracd -displayname \"tracd\" -start auto \"C:\\path\\to\\python.exe\" c:\\path\\to\\python\\scripts\\tracd-script.py <your tracd parameters>\"\n\nnet start tracd\n}}}\n\n=== Option 2 ===\n\nUse [http://trac-hacks.org/wiki/WindowsServiceScript WindowsServiceScript], available at [http://trac-hacks.org/ Trac Hacks]. Installs, removes, starts, stops, etc. your Trac service.\n\n== Using Authentication ==\n\nTracd provides support for both Basic and Digest authentication. The default is to use Digest; to use Basic authentication, replace `--auth` with `--basic-auth` in the examples below. (You must still specify a dialogic \"realm\", which can be an empty string by trailing the BASICAUTH with a comma.)\n\n\nThe general format for using authentication is:\n{{{\n $ tracd -p port --auth=\"base_project_dir,password_file_path,realm\" project_path\n}}}\n\nwhere:\n\n * \'\'\'base_project_dir\'\'\': the base directory of the project specified as follows:\n   * when serving multiple projects: \'\'relative\'\' to the `project_path`\n   * when serving only a single project (`-s`): the name of the project directory\n Don\'t use an absolute path here as this won\'t work. \'\'Note:\'\' This parameter is case-sensitive even for environments on Windows.\n * \'\'\'password_file_path\'\'\': path to the password file\n * \'\'\'realm\'\'\': the realm name (can be anything)\n * \'\'\'project_path\'\'\': path of the project\n * **`--auth`** in the above means use Digest authentication, replace `--auth` with `--basic-auth` if you want to use Basic auth\n\nExamples:\n\n{{{\n $ tracd -p 8080 \\\n   --auth=\"project1,/path/to/passwordfile,mycompany.com\" /path/to/project1\n}}}\n\nOf course, the password file can be be shared so that it is used for more than one project:\n{{{\n $ tracd -p 8080 \\\n   --auth=\"project1,/path/to/passwordfile,mycompany.com\" \\\n   --auth=\"project2,/path/to/passwordfile,mycompany.com\" \\\n   /path/to/project1 /path/to/project2\n}}}\n\nAnother way to share the password file is to specify \"*\" for the project name:\n{{{\n $ tracd -p 8080 \\\n   --auth=\"*,/path/to/users.htdigest,mycompany.com\" \\\n   /path/to/project1 /path/to/project2\n}}}\n\n=== Using a htpasswd password file ===\nThis section describes how to use `tracd` with Apache .htpasswd files.\n\nTo create a .htpasswd file use Apache\'s `htpasswd` command (see [#GeneratingPasswordsWithoutApache below] for a method to create these files without using Apache):\n\n{{{\n $ sudo htpasswd -c /path/to/env/.htpasswd username\n}}}\nthen for additional users:\n{{{\n $ sudo htpasswd /path/to/env/.htpasswd username2\n}}}\n\nThen to start `tracd` run something like this:\n\n{{{\n $ tracd -p 8080 --basic-auth=\"projectdirname,/fullpath/environmentname/.htpasswd,realmname\" /fullpath/environmentname\n}}}\n\nFor example:\n\n{{{\n $ tracd -p 8080 --basic-auth=\"testenv,/srv/tracenv/testenv/.htpasswd,My Test Env\" /srv/tracenv/testenv\n}}}\n\n\'\'Note:\'\' You might need to pass \"-m\" as a parameter to htpasswd on some platforms (OpenBSD).\n\n=== Using a htdigest password file ===\n\nIf you have Apache available, you can use the htdigest command to generate the password file. Type \'htdigest\' to get some usage instructions, or read [http://httpd.apache.org/docs/2.0/programs/htdigest.html this page] from the Apache manual to get precise instructions.  You\'ll be prompted for a password to enter for each user that you create.  For the name of the password file, you can use whatever you like, but if you use something like `users.htdigest` it will remind you what the file contains. As a suggestion, put it in your <projectname>/conf folder along with the [TracIni trac.ini] file.\n\nNote that you can start tracd without the --auth argument, but if you click on the \'\'Login\'\' link you will get an error.\n\n=== Generating Passwords Without Apache ===\n\nIf you don\'t have Apache available, you can use this simple Python script to generate your passwords:\n\n{{{\n#!python\nfrom optparse import OptionParser\n# The md5 module is deprecated in Python 2.5\ntry:\n    from hashlib import md5\nexcept ImportError:\n    from md5 import md5\nrealm = \'trac\'\n\n# build the options\nusage = \"usage: %prog [options]\"\nparser = OptionParser(usage=usage)\nparser.add_option(\"-u\", \"--username\",action=\"store\", dest=\"username\", type = \"string\",\n                  help=\"the username for whom to generate a password\")\nparser.add_option(\"-p\", \"--password\",action=\"store\", dest=\"password\", type = \"string\",\n                  help=\"the password to use\")\nparser.add_option(\"-r\", \"--realm\",action=\"store\", dest=\"realm\", type = \"string\",\n                  help=\"the realm in which to create the digest\")\n(options, args) = parser.parse_args()\n\n# check options\nif (options.username is None) or (options.password is None):\n   parser.error(\"You must supply both the username and password\")\nif (options.realm is not None):\n   realm = options.realm\n   \n# Generate the string to enter into the htdigest file\nkd = lambda x: md5(\':\'.join(x)).hexdigest()\nprint \':\'.join((options.username, realm, kd([options.username, realm, options.password])))\n}}}\n\nNote: If you use the above script you must use the --auth option to tracd, not --basic-auth, and you must set the realm in the --auth value to \'trac\' (without the quotes). Example usage (assuming you saved the script as trac-digest.py):\n\n{{{\n $ python trac-digest.py -u username -p password >> c:\\digest.txt\n $ tracd --port 8000 --auth=proj_name,c:\\digest.txt,trac c:\\path\\to\\proj_name\n}}}\n\n\nNote: If you would like to use --basic-auth you need to use htpasswd tool from apache server to generate .htpasswd file. The remaining part is similar but make sure to use empty realm (i.e. coma after path). Make sure to use -m option for it.  If you do not have Apache, [trac:source:/tags/trac-0.11/contrib/htpasswd.py htpasswd.py] may help.  (Note that it requires a `crypt` or `fcrypt` module; see the source comments for details.)\n\nIt is possible to use md5sum utility to generate digest-password file using such method:\n{{{\n $ printf \"${user}:trac:${password}\" | md5sum - >>user.htdigest\n}}}\nand manually delete \" -\" from the end and add \"${user}:trac:\" to the start of line from \'to-file\'.\n\n== Reference ==\n\nHere\'s the online help, as a reminder (`tracd --help`):\n{{{\nUsage: tracd [options] [projenv] ...\n\nOptions:\n  --version             show program\'s version number and exit\n  -h, --help            show this help message and exit\n  -a DIGESTAUTH, --auth=DIGESTAUTH\n                        [projectdir],[htdigest_file],[realm]\n  --basic-auth=BASICAUTH\n                        [projectdir],[htpasswd_file],[realm]\n  -p PORT, --port=PORT  the port number to bind to\n  -b HOSTNAME, --hostname=HOSTNAME\n                        the host name or IP address to bind to\n  --protocol=PROTOCOL   http|scgi|ajp\n  -q, --unquote         unquote PATH_INFO (may be needed when using ajp)\n  --http10              use HTTP/1.0 protocol version (default)\n  --http11              use HTTP/1.1 protocol version instead of HTTP/1.0\n  -e PARENTDIR, --env-parent-dir=PARENTDIR\n                        parent directory of the project environments\n  --base-path=BASE_PATH\n                        the initial portion of the request URL\'s \"path\"\n  -r, --auto-reload     restart automatically when sources are modified\n  -s, --single-env      only serve a single project without the project list\n}}}\n\n== Tips ==\n\n=== Serving static content ===\n\nIf `tracd` is the only web server used for the project, \nit can also be used to distribute static content \n(tarballs, Doxygen documentation, etc.)\n\nThis static content should be put in the `$TRAC_ENV/htdocs` folder,\nand is accessed by URLs like `<project_URL>/chrome/site/...`.\n\nExample: given a `$TRAC_ENV/htdocs/software-0.1.tar.gz` file,\nthe corresponding relative URL would be `/<project_name>/chrome/site/software-0.1.tar.gz`, \nwhich in turn can be written as `htdocs:software-0.1.tar.gz` (TracLinks syntax) or `[/<project_name>/chrome/site/software-0.1.tar.gz]` (relative link syntax). \n\n \'\'Support for `htdocs:` TracLinks syntax was added in version 0.10\'\'\n\n=== Using tracd behind a proxy\n\nIn some situations when you choose to use tracd behind Apache or another web server.\n\nIn this situation, you might experience issues with redirects, like being redirected to URLs with the wrong host or protocol. In this case (and only in this case), setting the `[trac] use_base_url_for_redirect` to `true` can help, as this will force Trac to use the value of `[trac] base_url` for doing the redirects.\n\nIf you\'re using the AJP protocol to connect with `tracd` (which is possible if you have flup installed), then you might experience problems with double quoting. Consider adding the `--unquote` parameter.\n\nSee also [trac:TracOnWindowsIisAjp], [trac:TracNginxRecipe].\n\n=== Serving a different base path than / ===\nTracd supports serving projects with different base urls than /<project>. The parameter name to change this is\n{{{\n $ tracd --base-path=/some/path\n}}}\n\n----\nSee also: TracInstall, TracCgi, TracModPython, TracGuide, [trac:TracOnWindowsStandalone#RunningTracdasservice Running tracd.exe as a Windows service]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracSupport',1,1327389819647871,'trac','127.0.0.1','= Trac Support =\n\nLike in most [http://www.opensource.org/ open source projects], \"free\" Trac support is available primarily through the community itself, mainly through the [trac:MailingList mailing list] and the project wiki.\n\nThere is also an [trac:IrcChannel IRC channel], where people might be able to help out. Much of the \'live\' development discussions also happen there.\n\nBefore you start a new support query, make sure you\'ve done the appropriate searching:\n * in the project\'s [trac:TracFaq FAQ]\n * in past messages to the Trac [http://blog.gmane.org/gmane.comp.version-control.subversion.trac.general?set_user_css=http%3A%2F%2Fwww.edgewall.com%2Fcss%2Fgmane.css&do_set_user_css=t Mailing List]\n * in the Trac ticket system, using either a [http://trac.edgewall.org/search?q=&ticket=on&wiki=on full search] or a [http://trac.edgewall.org/query?summary=~&keywords=~ ticket query].\n\nPlease \'\'\'don\'t\'\'\' create a ticket in this Trac for asking a support question about Trac. Only use it when you face a \'\'real\'\' and \'\'new\'\' bug in Trac, and do so only after having read the [trac:NewTicketGuidelines NewTicketGuidelines]. The more a bug report or enhancement request complies with those guidelines, the higher the chances are that it will be fixed or implemented promptly!\n\n----\nSee also: [trac:MailingList MailingList], [trac:TracTroubleshooting TracTroubleshooting], [trac:CommercialServices CommercialServices]\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracSyntaxColoring',1,1327389819647871,'trac','127.0.0.1','= Syntax Coloring of Source Code =\nTrac supports language-specific syntax highlighting of source code within wiki formatted text in [WikiProcessors#CodeHighlightingSupport wiki processors] blocks and in the [TracBrowser repository browser].\n\nTo do this, Trac uses external libraries with support for a great number of programming languages.\n\nCurrently Trac supports syntax coloring using one or more of the following packages:\n\n * [http://pygments.pocoo.org/ Pygments], by far the preferred system, as it covers a wide range of programming languages and other structured texts and is actively supported\n * [http://www.codento.com/people/mtr/genscript/ GNU Enscript], commonly available on Unix but somewhat unsupported on Windows\n * [http://silvercity.sourceforge.net/ SilverCity], legacy system, some versions can be [http://trac.edgewall.org/wiki/TracFaq#why-is-my-css-code-not-being-highlighted-even-though-i-have-silvercity-installed problematic]\n\n\nTo activate syntax coloring, simply install either one (or more) of these packages (see [#ExtraSoftware] section below).\nIf none of these packages is available, Trac will display the data as plain text. \n\n\n=== About Pygments ===\n\nStarting with trac 0.11 [http://pygments.org/ pygments] will be the new default highlighter. It\'s a highlighting library implemented in pure python, very fast, easy to extend and [http://pygments.org/docs/ well documented].\n\nThe Pygments default style can specified in the [TracIni#mimeviewer-section mime-viewer] section of trac.ini. The default style can be overridden by setting a Style preference on the [/prefs/pygments preferences page]. \n\nIt\'s very likely that the list below is outdated because the list of supported pygments lexers is growing weekly. Just have a look at the page of [http://pygments.org/docs/lexers/ supported lexers] on the pygments webpage.\n\n\n== Syntax Coloring Support ==\n\n=== Known MIME Types\n\n[[KnownMimeTypes]]\n\n\n=== List of Languages Supported, by Highlighter #language-supported\n\nThis list is only indicative.\n\n||                 ||= !SilverCity   =||= Enscript      =||= Pygments =||\n|| Ada             ||                 ||  âœ“              ||     ||\n|| Asm             ||                 ||  âœ“              ||     ||\n|| Apache Conf     ||                 ||                 ||  âœ“  ||\n|| ASP             ||  âœ“              ||  âœ“              ||     ||\n|| C               ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| C#              ||                 ||  âœ“ ^[#a1 (1)]^  ||  âœ“  ||\n|| C++             ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| Java            ||  âœ“ ^[#a2 (2)]^  ||  âœ“              ||  âœ“  ||\n|| Awk             ||                 ||  âœ“              ||     ||\n|| Boo             ||                 ||                 ||  âœ“  ||\n|| CSS             ||  âœ“              ||                 ||  âœ“  ||\n|| Python Doctests ||                 ||                 ||  âœ“  ||\n|| Diff            ||                 ||  âœ“              ||  âœ“  ||\n|| Eiffel          ||                 ||  âœ“              ||     ||\n|| Elisp           ||                 ||  âœ“              ||     ||\n|| Fortran         ||                 ||  âœ“ ^[#a1 (1)]^  ||  âœ“  ||\n|| Haskell         ||                 ||  âœ“              ||  âœ“  ||\n|| Genshi          ||                 ||                 ||  âœ“  ||\n|| HTML            ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| IDL             ||                 ||  âœ“              ||     ||\n|| INI             ||                 ||                 ||  âœ“  ||\n|| Javascript      ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| Lua             ||                 ||                 ||  âœ“  ||\n|| m4              ||                 ||  âœ“              ||     ||\n|| Makefile        ||                 ||  âœ“              ||  âœ“  ||\n|| Mako            ||                 ||                 ||  âœ“  ||\n|| Matlab ^[#a3 (3)]^  ||             ||  âœ“              ||  âœ“  ||\n|| Mygthy          ||                 ||                 ||  âœ“  ||\n|| Objective-C     ||                 ||  âœ“              ||  âœ“  ||\n|| OCaml           ||                 ||                 ||  âœ“  ||\n|| Pascal          ||                 ||  âœ“              ||  âœ“  ||\n|| Perl            ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| PHP             ||  âœ“              ||                 ||  âœ“  ||\n|| PSP             ||  âœ“              ||                 ||     ||\n|| Pyrex           ||                 ||  âœ“              ||     ||\n|| Python          ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| Ruby            ||  âœ“              ||  âœ“ ^[#a1 (1)]^  ||  âœ“  ||\n|| Scheme          ||                 ||  âœ“              ||  âœ“  ||\n|| Shell           ||                 ||  âœ“              ||  âœ“  ||\n|| Smarty          ||                 ||                 ||  âœ“  ||\n|| SQL             ||  âœ“              ||  âœ“              ||  âœ“  ||\n|| Troff           ||                 ||  âœ“              ||  âœ“  ||\n|| TCL             ||                 ||  âœ“              ||     ||\n|| Tex             ||                 ||  âœ“              ||  âœ“  ||\n|| Verilog         ||  âœ“ ^[#a2 (2)]^  ||  âœ“              ||     ||\n|| VHDL            ||                 ||  âœ“              ||     ||\n|| Visual Basic    ||                 ||  âœ“              ||  âœ“  ||\n|| VRML            ||                 ||  âœ“              ||     ||\n|| XML             ||  âœ“              ||                 ||  âœ“  ||\n\n\n\n\'\'[=#a1 (1)] Not included in the Enscript distribution.  Additional highlighting rules can be obtained for\n[http://neugierig.org/software/ruby/ Ruby],\n[http://wiki.hasno.info/index.php/Csharp.st C#],\n[http://wiki.hasno.info/index.php/F90.st Fortran 90x/2003]\n\n\'\'[=#a2 (2)] since Silvercity 0.9.7 released on 2006-11-23\n\n\'\'[=#a3 (3)] By default `.m` files are considered Objective-C files. In order to treat `.m` files as MATLAB files, add \"text/matlab:m\" to the \"mime_map\" setting in the [wiki:TracIni#mimeviewer-section \"[mimeviewer] section of trac.ini\"].\n\n== Extra Software ==\n * GNU Enscript -- http://directory.fsf.org/GNU/enscript.html\n * GNU Enscript for Windows -- http://gnuwin32.sourceforge.net/packages/enscript.htm\n * !SilverCity -- http://silvercity.sf.net/\n * Pygments -- http://pygments.org/\n\n----\nSee also: WikiProcessors, WikiFormatting, TracWiki, TracBrowser\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracTickets',1,1327389819647871,'trac','127.0.0.1','= The Trac Ticket System =\n[[TracGuideToc]]\n\nThe Trac ticket database provides simple but effective tracking of issues and bugs within a project.\n\nAs the central project management element of Trac, tickets are used for \'\'\'project tasks\'\'\', \'\'\'feature requests\'\'\', \'\'\'bug reports\'\'\' and \'\'\'software support issues\'\'\'. \n\nAs with the TracWiki, this subsystem has been designed with the goal of making user contribution and participation as simple as possible. It should be as easy as possible to report bugs, ask questions and suggest improvements.\n\nAn issue is assigned to a person who must resolve it or reassign the ticket to someone else.\nAll tickets can be edited, annotated, assigned, prioritized and discussed at any time.\n\n== Ticket Fields ==\n\nA  ticket contains the following information attributes:\n \n * \'\'\'Reporter\'\'\' â€” The author of the ticket.\n * \'\'\'Type\'\'\' â€” The nature of the ticket (for example, defect or enhancement request)\n\n * \'\'\'Component\'\'\' â€” The project module or subsystem this ticket concerns.\n * \'\'\'Version\'\'\' â€” Version of the project that this ticket pertains to.\n * \'\'\'Keywords\'\'\' â€” Keywords that a ticket is marked with.  Useful for searching and report generation.\n\n * \'\'\'Priority\'\'\' â€” The importance of this issue, ranging from \'\'trivial\'\' to \'\'blocker\'\'.\n * \'\'\'Milestone\'\'\' â€” When this issue should be resolved at the latest.\n * \'\'\'Assigned to/Owner\'\'\' â€” Principal person responsible for handling the issue.\n * \'\'\'Cc\'\'\' â€” A comma-separated list of other users or E-Mail addresses to notify. \'\'Note that this does not imply responsiblity or any other policy.\'\'\n \n * \'\'\'Resolution\'\'\' â€” Reason for why a ticket was closed. One of {{{fixed}}}, {{{invalid}}}, {{{wontfix}}}, {{{duplicate}}}, {{{worksforme}}}.\n * \'\'\'Status\'\'\' â€” What is the current status? One of {{{new}}}, {{{assigned}}}, {{{closed}}}, {{{reopened}}}.\n * \'\'\'Summary\'\'\' â€” A brief description summarizing the problem or issue.\n * \'\'\'Description\'\'\' â€” The body of the ticket. A good description should be specific, descriptive and to the point.\n\n\'\'\'Note:\'\'\' Versions of Trac prior to 0.9 did not have the \'\'type\'\' field, but instead provided a \'\'severity\'\' field and different default values for the \'\'priority\'\' field. This change was done to simplify the ticket model by removing the somewhat blurry distinction between \'\'priority\'\' and \'\'severity\'\'. However, the old model is still available if you prefer it: just add/modify the default values of the \'\'priority\'\' and \'\'severity\'\', and optionally hide the \'\'type\'\' field by removing all the possible values through [wiki:TracAdmin trac-admin].\n\n\'\'\'Note:\'\'\' the [trac:TicketTypes type], [trac:TicketComponent component], version, priority and severity fields can be managed with [wiki:TracAdmin trac-admin] or with the [trac:WebAdmin WebAdmin] plugin.\n\n\'\'\'Note:\'\'\' Description of the builtin \'\'priority\'\' values is available at [trac:TicketTypes#Whyistheseverityfieldgone TicketTypes]\n\n== Changing and Commenting Tickets ==\n\nOnce a ticket has been entered into Trac, you can at any time change the\ninformation by \'\'\'annotating\'\'\' the bug. This means changes and comments to\nthe ticket are logged as a part of the ticket itself.\n\nWhen viewing a ticket, the history of changes will appear below the main ticket area.\n\n\'\'In the Trac project, we use ticket comments to discuss issues and tasks. This makes\nunderstanding the motivation behind a design- or implementation choice easier,\nwhen returning to it later.\'\'\n\n\'\'\'Note:\'\'\' An important feature is being able to use TracLinks and\nWikiFormatting in ticket descriptions and comments. Use TracLinks to refer to\nother issues, changesets or files to make your ticket more specific and easier\nto understand.\n\n\'\'\'Note:\'\'\' See TracNotification for how to configure email notifications of ticket changes.\n\n\'\'\'Note:\'\'\' See TracWorkflow for information about the state transitions (ticket lifecycle), and how this workflow can be customized.\n\n== Default Values for Drop-Down Fields ==\n\nThe option selected by default for the various drop-down fields can be set in [wiki:TracIni trac.ini], in the `[ticket]` section:\n\n * `default_component`: Name of the component selected by default\n * `default_milestone`: Name of the default milestone\n * `default_priority`: Default priority value\n * `default_severity`: Default severity value\n * `default_type`: Default ticket type\n * `default_version`: Name of the default version\n * `default_owner`: Name of the default owner, \'\'if no owner for the component has been set\'\'\n\nIf any of these options are omitted, the default value will either be the first in the list, or an empty value, depending on whether the field in question is required to be set.  Some of these can be chosen through the [trac:WebAdmin WebAdmin] plugin in the \"Ticket System\" section (others in the \"trac.ini\" section).  The default owner for a ticket will be the component owner, if that is set, or `default_owner`, if not.\n\n\n== Hiding Fields and Adding Custom Fields ==\n\nMany of the default ticket fields can be hidden from the ticket web interface simply by removing all the possible values through [wiki:TracAdmin trac-admin]. This of course only applies to drop-down fields, such as \'\'type\'\', \'\'priority\'\', \'\'severity\'\', \'\'component\'\', \'\'version\'\' and \'\'milestone\'\'.\n\nTrac also lets you add your own custom ticket fields. See TracTicketsCustomFields for more information.\n\n\n== Assign-to as Drop-Down List ==\n\nIf the list of possible ticket owners is finite, you can change the \'\'assign-to\'\' ticket field from a text input to a drop-down list. This is done by setting the `restrict_owner` option of the `[ticket]` section in [wiki:TracIni trac.ini] to â€œtrueâ€. In that case, Trac will use the list of all users who have accessed the project to populate the drop-down field.\n\nTo appear in the dropdown list, a user needs be registered with the project, \'\'i.e.\'\' a user session should exist in the database. Such an entry is automatically created in the database the first time the user submits a change in the project, for example when editing the user\'s details in the \'\'Settings\'\' page, or simply by authenticating if the user has a login. Also, the user must have `TICKET_MODIFY` [TracPermissions permissions].\n\n\'\'\'Note:\'\'\' See [http://pacopablo.com/wiki/pacopablo/blog/set-assign-to-drop-down Populating Assign To Drop Down] on how to add user entries at database level\n\n\'\'\'Note 2:\'\'\' If you need serious flexibility and aren\'t afraid of a little plugin coding of your own, see [http://trac-hacks.org/wiki/FlexibleAssignToPlugin FlexibleAssignTo] (disclosure: I\'m the author)\n\n\'\'\'Note 3:\'\'\' Activating this option may cause some performance degradation, read more about this in the [trac:TracPerformance#Configuration Trac performance] page.\n\n== Preset Values for New Tickets ==\n\nTo create a link to the new-ticket form filled with preset values, you need to call the `/newticket?` URL with variable=value separated by &. \n\nPossible variables are :\n\n * \'\'\'type\'\'\' â€” The type droplist\n * \'\'\'reporter\'\'\' â€” Name or email of the reporter\n * \'\'\'summary\'\'\' â€” Summary line for the ticket\n * \'\'\'description\'\'\' â€” Long description of the ticket\n * \'\'\'component\'\'\' â€” The component droplist\n * \'\'\'version\'\'\' â€” The version droplist\n * \'\'\'severity\'\'\' â€” The severity droplist\n * \'\'\'keywords\'\'\' â€” The keywords \n * \'\'\'priority\'\'\' â€” The priority droplist\n * \'\'\'milestone\'\'\' â€” The milestone droplist\n * \'\'\'owner\'\'\' â€” The person responsible for the ticket\n * \'\'\'cc\'\'\' â€” The list of emails for notifying about the ticket change\n\n\'\'\'Example:\'\'\' \'\'/trac/newticket?summary=Compile%20Error&version=1.0&component=gui\'\'[[BR]]\n\n----\nSee also:  TracGuide, TracWiki, TracTicketsCustomFields, TracNotification, TracReports, TracQuery',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracTicketsCustomFields',1,1327389819647871,'trac','127.0.0.1','= Custom Ticket Fields =\nTrac supports adding custom, user-defined fields to the ticket module. Using custom fields, you can add typed, site-specific properties to tickets.\n\n== Configuration ==\nConfiguring custom ticket fields is done in the [wiki:TracIni trac.ini] file. All field definitions should be under a section named `[ticket-custom]`.\n\nThe syntax of each field definition is:\n{{{\n FIELD_NAME = TYPE\n (FIELD_NAME.OPTION = VALUE)\n ...\n}}}\nThe example below should help to explain the syntax.\n\n=== Available Field Types and Options ===\n * \'\'\'text\'\'\': A simple (one line) text field.\n   * label: Descriptive label.\n   * value: Default value.\n   * order: Sort order placement. (Determines relative placement in forms with respect to other custom fields.)\n   * format: Either `plain` for plain text or `wiki` to interpret the content as WikiFormatting. (\'\'since 0.11.3\'\')\n * \'\'\'checkbox\'\'\': A boolean value check box.\n   * label: Descriptive label.\n   * value: Default value (0 or 1).\n   * order: Sort order placement.\n * \'\'\'select\'\'\': Drop-down select box. Uses a list of values.\n   * label: Descriptive label.\n   * options: List of values, separated by \'\'\'|\'\'\' (vertical pipe).\n   * value: Default value (one of the values from options).\n   * order: Sort order placement.\n * \'\'\'radio\'\'\': Radio buttons. Essentially the same as \'\'\'select\'\'\'.\n   * label: Descriptive label.\n   * options: List of values, separated by \'\'\'|\'\'\' (vertical pipe).\n   * value: Default value (one of the values from options).\n   * order: Sort order placement.\n * \'\'\'textarea\'\'\': Multi-line text area.\n   * label: Descriptive label.\n   * value: Default text.\n   * cols: Width in columns.\n   * rows: Height in lines.\n   * order: Sort order placement.\n   * format: Either `plain` for plain text or `wiki` to interpret the content as WikiFormatting. (\'\'since 0.11.3\'\')\n\n=== Sample Config ===\n{{{\n[ticket-custom]\n\ntest_one = text\ntest_one.label = Just a text box\n\ntest_two = text\ntest_two.label = Another text-box\ntest_two.value = Default [mailto:joe@nospam.com owner]\ntest_two.format = wiki\n\ntest_three = checkbox\ntest_three.label = Some checkbox\ntest_three.value = 1\n\ntest_four = select\ntest_four.label = My selectbox\ntest_four.options = one|two|third option|four\ntest_four.value = two\n\ntest_five = radio\ntest_five.label = Radio buttons are fun\ntest_five.options = uno|dos|tres|cuatro|cinco\ntest_five.value = dos\n\ntest_six = textarea\ntest_six.label = This is a large textarea\ntest_six.value = Default text\ntest_six.cols = 60\ntest_six.rows = 30\n}}}\n\n\'\'Note: To make entering an option for a `select` type field optional, specify a leading `|` in the `fieldname.options` option.\'\'\n\n=== Reports Involving Custom Fields ===\n\nCustom ticket fields are stored in the `ticket_custom` table, not in the `ticket` table. So to display the values from custom fields in a report, you will need a join on the 2 tables. Let\'s use an example with a custom ticket field called `progress`.\n\n{{{\n#!sql\nSELECT p.value AS __color__,\n   id AS ticket, summary, owner, c.value AS progress\n  FROM ticket t, enum p, ticket_custom c\n  WHERE status IN (\'assigned\') AND t.id = c.ticket AND c.name = \'progress\'\nAND p.name = t.priority AND p.type = \'priority\'\n  ORDER BY p.value\n}}}\n\'\'\'Note\'\'\' that this will only show tickets that have progress set in them, which is \'\'\'not the same as showing all tickets\'\'\'. If you created this custom ticket field \'\'after\'\' you have already created some tickets, they will not have that field defined, and thus they will never show up on this ticket query. If you go back and modify those tickets, the field will be defined, and they will appear in the query. If that\'s all you want, you\'re set.\n\nHowever, if you want to show all ticket entries (with progress defined and without), you need to use a `JOIN` for every custom field that is in the query.\n{{{\n#!sql\nSELECT p.value AS __color__,\n   id AS ticket, summary, component, version, milestone, severity,\n   (CASE status WHEN \'assigned\' THEN owner||\' *\' ELSE owner END) AS owner,\n   time AS created,\n   changetime AS _changetime, description AS _description,\n   reporter AS _reporter,\n  (CASE WHEN c.value = \'0\' THEN \'None\' ELSE c.value END) AS progress\n  FROM ticket t\n     LEFT OUTER JOIN ticket_custom c ON (t.id = c.ticket AND c.name = \'progress\')\n     JOIN enum p ON p.name = t.priority AND p.type=\'priority\'\n  WHERE status IN (\'new\', \'assigned\', \'reopened\')\n  ORDER BY p.value, milestone, severity, time\n}}}\n\nNote in particular the `LEFT OUTER JOIN` statement here.\n\n=== Updating the database ===\n\nAs noted above, any tickets created before a custom field has been defined will not have a value for that field. Here\'s a bit of SQL (tested with SQLite) that you can run directly on the Trac database to set an initial value for custom ticket fields. Inserts the default value of \'None\' into a custom field called \'request_source\' for all tickets that have no existing value:\n\n{{{\n#!sql\nINSERT INTO ticket_custom\n   (ticket, name, value)\n   SELECT \n      id AS ticket,\n      \'request_source\' AS name,\n      \'None\' AS value\n   FROM ticket \n   WHERE id NOT IN (\n      SELECT ticket FROM ticket_custom\n   );\n}}}\n\nIf you added multiple custom fields at different points in time, you should be more specific in the subquery on table {{{ticket}}} by adding the exact custom field name to the query:\n\n{{{\n#!sql\nINSERT INTO ticket_custom\n   (ticket, name, value)\n   SELECT \n      id AS ticket,\n      \'request_source\' AS name,\n      \'None\' AS value\n   FROM ticket \n   WHERE id NOT IN (\n      SELECT ticket FROM ticket_custom WHERE name = \'request_source\'\n   );\n}}}\n\n----\nSee also: TracTickets, TracIni',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracTimeline',1,1327389819647871,'trac','127.0.0.1','= The Trac Timeline =\n[[TracGuideToc]]\n\nThe timeline provides a historic view of the project in a single report.\n\nIt lists all Trac events that have occurred in chronological order, a\nbrief description of each event and if applicable, the person responsible for\nthe change.\n\nThe timeline lists these kinds of events:\n * \'\'\'Wiki page events\'\'\' â€” Creation and changes\n * \'\'\'Ticket events\'\'\' â€” Creation and resolution/closing (and optionally other changes)\n * \'\'\'Source code changes \'\'\' â€” Repository check-ins\n * \'\'\'Milestone \'\'\' â€” Milestone completed\n\nEach event entry provides a hyperlink to the specific event in question, who authored the change as well as\na brief excerpt of the actual comment or text, if available.\n\nIt is possible to filter the displayed events with the various filters in the option panel:\n * \'\'View changes from\'\' â€” the date from which to start displaying events (current date if empty). Events that occurred after this date will not be shown, only those that occurred before that date.\n * \'\'and X days back\'\' â€” how many days backwards in time to get events.\n * \'\'done by\'\' â€” the author of an event. It accepts a space-separated list of authors for which events should be included. Alternatively, if the author names are prefixed by a \"-\" character, then the events having those authors will be excluded, and all the others included. Single or double quotes can be used for specifying author names containing space characters. \'\'(since 0.12)\'\'\n * \'\'Changesets in all repositories\'\' â€” if you have more than one repository connected to your Trac project, then you can filter the output so events from specific repositories are not shown. \'\'(since 0.12)\'\'\n * \'\'Milestones reached\'\' â€” display or hide milestones reached.\n * \'\'Opened and closed tickets\'\' â€” display or hide ticket open or close events.\n * \'\'Wiki changes\'\' â€” display or hide Wiki change events.\n\nSee !TracIni\'s [wiki:TracIni#timeline-section \"[timeline] section\"] for timeline configuration options.\n\n== RSS Support ==\n\nThe Timeline module supports subscription using RSS 2.0 syndication. To subscribe to project events, click the orange \'\'\'XML\'\'\' icon at the bottom of the page. See TracRss for more information on RSS support in Trac.\n\n----\nSee also: TracGuide, TracIni, TracWiki, WikiFormatting, TracRss, TracNotification\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracUnicode',1,1327389819647871,'trac','127.0.0.1','= Unicode Support in Trac =\n[[TracGuideToc]]\n\nTrac stores all text using UTF-8 encoding, including text in tickets and wiki pages. Internal processing of text uses true Unicode representations.\n\nAs such, it supports most (all?) commonly used character encodings.\n\nIf your encoding is not UTF-8, you can use [wiki:TracModPython mod_python] to handle it.  For example, if your local encoding is gbk, you can set \n   default_charset = gbk\nin trac.ini.\n\nYou also must make sure that your [trac:DatabaseBackend database backend] stores its data in UTF-8; otherwise strange things will happen.\n\nTo convert your database to UTF-8, the easiest way is to dump the database, convert the dump into UTF-8 and then import the converted dump back into the database.[[BR]]\nYou can use [http://www.gnu.org/software/libiconv/documentation/libiconv/iconv.1.html iconv] to convert the dump.\n\n\n== Examples ==\n\n=== Arabic ===\nØªØ±Ø§Ùƒ ÙŠÙ‚ÙˆÙ… Ø¨Ø­ÙØ¸ ÙƒÙ„ Ø§Ù„ÙƒÙ„Ù…Ø§Øª Ø¨Ø§Ø³ØªØ®Ø¯Ø§Ù… ØµÙŠØºØ© UTF-8ØŒ Ø¨Ù…Ø§ ÙÙŠ Ø°Ù„Ùƒ Ø§Ù„ÙƒÙ„Ù…Ø§Øª Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…Ø© ÙÙŠ ØµÙØ­Ø§Øª  Ø§Ù„ØªÙŠÙƒØª ÙˆØ§Ù„ÙˆÙŠÙƒÙŠ.\n\n=== Bulgarian ===\nÐ‘ÑŠÐ»Ð³Ð°Ñ€ÑÐºÐ¸ÑÑ‚ ÐµÐ·Ð¸Ðº Ñ€Ð°Ð±Ð¾Ñ‚Ð¸ Ð»Ð¸?\n\n=== ÄŒesky ===\nÄŒeÅ¡tina v kÃ³dovÃ¡nÃ­ UTF-8, Å¾Ã¡dnÃ½ problÃ©m.\n\n=== Chinese ===\nTraditional: ç¹é«”ä¸­æ–‡, æ¼¢å­—æ¸¬è©¦; Simplified: ç®€ä½“ä¸­æ–‡ï¼Œæ±‰å­—æµ‹è¯•\n\n=== Croatian ===\nAko podrÅ¾ava srpski i slovenski mora podrÅ¾avati i Hrvatski - ÄÄ‡Å¾Å¡Ä‘ ÄŒÄ†Å½Å Ä \n\n=== English ===\nYes indeed, Trac supports English. Fully.\n\n=== FranÃ§ais ===\nIl est possible d\'Ã©crire en FranÃ§ais : Ã , Ã§, Ã», ...\n\n=== German ===\nTrac-Wiki muÃŸ auch deutsche Umlaute richtig anzeigen: Ã¶, Ã¤, Ã¼, Ã„, Ã–, Ãœ; und das scharfe ÃŸ\n\n=== Greek ===\nÎ¤Î± Î•Î»Î»Î·Î½Î¹ÎºÎ¬ Ï…Ï€Î¿ÏƒÏ„Î·ÏÎ¯Î¶Î¿Î½Ï„Î±Î¹ ÎµÏ€Î±ÏÎºÏŽÏ‚ ÎµÏ€Î¯ÏƒÎ·Ï‚.\n\n=== Hebrew ===\n×× ×™ ×™×›×•×œ ×œ××›×•×œ ×–×›×•×›×™×ª ×•×–×” ×œ× ×ž×–×™×§ ×œ×™\n\n=== Hindi ===\nà¤…à¤¬ à¤¹à¤¿à¤¨à¥à¤¦à¥€ à¤®à¥‡à¤‚à¥¤\n\n=== Hungarian ===\nÃrvÃ­ztÅ±rÅ‘ tÃ¼kÃ¶rfÃºrÃ³gÃ©p\n\n=== Icelandic ===\nÃ†var sagÃ°i viÃ° Ã¶mmu sÃ­na: SjÃ¡Ã°u hvaÃ° Ã©g er stÃ³r!\n\n=== Japanese ===\næ¼¢å­— ã²ã‚‰ãŒãª ã‚«ã‚¿ã‚«ãƒŠ ï¾Šï¾ï½¶ï½¸ï½¶ï¾… æ—¥æœ¬èªžè©¦é¨“\n\n=== Korean ===\nì´ë²ˆì—ëŠ” í•œê¸€ë¡œ ì¨ë³´ê² ìŠµë‹ˆë‹¤. ìž˜ ë³´ì´ë‚˜ìš”? í•œê¸€\n\n=== Latvian ===\n\nLatvieÅ¡u valoda arÄ« strÄdÄ!\n\n=== Lithuanian ===\nSudalyvaukime ir mes. Ar veikia lietuviÅ¡kos raidÄ—s? Ä…ÄÄ™Ä—Ä¯Å¡Å³Å«Å¾ Ä„ÄŒÄ˜Ä–Ä®Å Å²ÅªÅ½ Å½inoma, kad veikia :)\nKas tie mes?\n\n=== Persian (Farsi) ===\nØ§ÛŒÙ† ÛŒÚ© Ù…ØªÙ† ÙØ§Ø±Ø³ÛŒ Ø§Ø³Øª ÙˆÙ„ÛŒ Ø§Ù…Ú©Ø§Ù† Ù†ÙˆØ´ØªÙ† Ù…Ø³ØªÙ‚ÛŒÙ… ÙØ§Ø±Ø³ÛŒ Ù†ÛŒØ³Øª Ú†ÙˆÙ† Ø­Ø§Ù„Øª Ù…ØªÙ† Ø§Ø² Ø±Ø§Ø³Øª Ø¨Ù‡ Ú†Ù¾ Ùˆ Ø¬ÙˆØ¯ Ù†Ø¯Ø§Ø±Ø¯ Ø¨Ø±Ø§ÛŒ ÙØ§Ø±Ø³ÛŒ Ù†ÙˆØ´ØªÙ† Ø¨Ø§ÛŒØ¯ Ø§Ø² HTML Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.\n{{{\n#!html\n<div dir=\"rtl\">\n}}}\nØ§ÛŒÙ† Ù†Ù…ÙˆÙ†Ù‡ ÛŒÚ© Ù…ØªÙ† Ø§Ø² Ø±Ø§Ø³Øª Ø¨Ù‡ Ú†Ù¾ ÙØ§Ø±Ø³ÛŒ Ø§Ø³Øª Ú©Ù‡ Ø¯Ø± HTML Ù†ÙˆØ´ØªÙ‡ Ø´Ø¯Ù‡ ØªØ§ Ø§Ø¹Ø¯Ø§Ø¯ 12345 Ùˆ Ø­Ø±ÙˆÙ Ù„Ø§ØªÛŒÙ† ABCDEF Ø¯Ø± Ù…Ø­Ù„ Ø®ÙˆØ¯Ø´Ø§Ù† Ù†Ù…Ø§ÛŒØ´ Ø¯Ø§Ø¯Ù‡ Ø´ÙˆÙ†Ø¯.\n{{{\n#!html\n</div>\n}}}\n\n=== Polish ===\nPchnÄ…Ä‡ w tÄ™ Å‚Ã³dÅº jeÅ¼a lub osiem skrzyÅ„ fig; Nocna gÅ¼egÅ¼Ã³Å‚ka zawsze dziennÄ… przekuka.\n\n=== Portuguese ===\nÃ‰ possÃ­vel guardar caracteres especias da lÃ­ngua portuguesa, incluindo o sÃ­mbolo da moeda europÃ©ia \'â‚¬\', trema \'Ã¼\', crase \'Ã \', agudos \'Ã¡Ã©Ã­Ã³Ãº\', circunflexos \'Ã¢ÃªÃ´\', til \'Ã£Ãµ\', cedilha \'Ã§\', ordinais \'ÂªÂº\', grau \'Â°Â¹Â²Â³\'.\n\n=== Russian ===\nÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ñ€ÑƒÑÑÐºÐ¾Ð³Ð¾ ÑÐ·Ñ‹ÐºÐ°: ÐºÐ°Ð¶ÐµÑ‚ÑÑ Ñ€Ð°Ð±Ð¾Ñ‚Ð°ÐµÑ‚... Ð˜ Ð±ÑƒÐºÐ²Ð° \"Ñ‘\" ÐµÑÑ‚ÑŒ...\n\n=== Serbian ===\nPodrÅ¾an, uprkos Äinjenici da se za njegovo pisanje koriste Ñ‡Ð°Ðº Ð´Ð²Ð° Ð°Ð»Ñ„Ð°Ð±ÐµÑ‚Ð°.\n\n=== Slovenian ===\nTa suhi Å¡kafec puÅ¡Äa vodo Å¾e od nekdaj!\n\n=== Spanish ===\nEsto es un pequeÃ±o texto en EspaÃ±ol, donde el veloz murciÃ©lago hindÃº comÃ­a cardlllo y kiwi\n\n=== Swedish ===\nRÃ¤ven raskar Ã¶ver isen med luva pÃ¥.\n\n=== Thai ===\nTrac à¹à¸ªà¸”à¸‡à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¹„à¸”à¹‰à¸­à¸¢à¹ˆà¸²à¸‡à¸–à¸¹à¸à¸•à¹‰à¸­à¸‡!\n\n=== Ukrainian ===\nÐŸÐµÑ€ÐµÐ²Ñ–Ñ€ÐºÐ° ÑƒÐºÑ€Ð°Ñ—Ð½ÑÑŒÐºÐ¾Ñ— Ð¼Ð¾Ð²Ð¸...\n\n=== Urdu ===\nÙ¹Ø±ÛŒÚ© Ø§Ø±Ø¯Ùˆ Ø¨Ú¾ÛŒ Ø³Ù¾ÙˆØ±Ù¹ Ú©Ø±ØªØ§ ÛÛ’Û”\n\n=== Vietnamese ===\nViáº¿t tiáº¿ng Viá»‡t cÅ©ng Ä‘Æ°á»£c.\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracUpgrade',1,1327389819647871,'trac','127.0.0.1','= Upgrade Instructions =\n[[TracGuideToc]]\n\n== Instructions ==\n\nTypically, there are seven steps involved in upgrading to a newer version of Trac:\n\n=== 1. Update the Trac Code === #UpdatetheTracCode\n\nGet the new version as described in TracInstall, or your operating system specific procedure.\n\nIf you already have a 0.11 version of Trac installed via `easy_install`, it might be easiest to also use `easy_install` to upgrade your Trac installation:\n\n{{{\n# easy_install --upgrade Trac==0.12\n}}}\n\nIf you do a manual (not operating system-specific) upgrade, you should also stop any running Trac servers before the installation. Doing \"hot\" upgrades is not advised, especially on Windows ([trac:#7265]).\n\nYou may also want to remove the pre-existing Trac code by deleting the `trac` directory from the Python `lib/site-packages` directory, or remove Trac `.egg` files from former versions.\nThe location of the site-packages directory depends on the operating system and the location in which Python was installed. However, the following locations are typical:\n * on Linux: `/usr/lib/python2.X/site-packages`\n * on Windows: `C:\\Python2.X\\lib\\site-packages`\n * on MacOSX: `/Library/Python/2.X/site-packages`\n\nYou may also want to remove the Trac `cgi-bin`, `htdocs`, `templates` and `wiki-default` directories that are commonly found in a directory called `share/trac`. (The exact location depends on your platform.)\n\nThis cleanup is not mandatory, but makes it easier to troubleshoot issues later on, as you won\'t waste your time looking at code or templates from a previous release that are not being used anymore... As usual, make a backup before actually deleting things.\n\n=== 2. Upgrade the Trac Environment === #UpgradetheTracEnvironment\n\nEnvironment upgrades are not necessary for minor version releases unless otherwise noted. \n\nAfter restarting, Trac should show the instances which need a manual upgrade via the automated upgrade scripts to ease the pain. These scripts are run via [TracAdmin trac-admin]:\n{{{\ntrac-admin /path/to/projenv upgrade\n}}}\n\nThis command will do nothing if the environment is already up-to-date.\n\nNote that a backup of your database will be performed automatically prior to the upgrade. \nThis feature is relatively new for the PostgreSQL or MySQL database backends, so if it fails, you will have to backup the database manually. Then, to perform the actual upgrade, run:\n{{{\ntrac-admin /path/to/projenv upgrade --no-backup\n}}}\n\n=== 3. Update the Trac Documentation === #UpdatetheTracDocumentation\n\nEvery [TracEnvironment Trac environment] includes a copy of the Trac documentation for the installed version. As you probably want to keep the included documentation in sync with the installed version of Trac, [TracAdmin trac-admin] provides a command to upgrade the documentation:\n{{{\ntrac-admin /path/to/projenv wiki upgrade\n}}}\n\nNote that this procedure will leave your `WikiStart` page intact.\n\n=== 4. Resynchronize the Trac Environment Against the Source Code Repository ===\n\nEach [TracEnvironment Trac environment] must be resynchronized against the source code repository in order to avoid errors such as \"[http://trac.edgewall.org/ticket/6120 No changeset ??? in the repository]\" while browsing the source through the Trac interface:\n\n{{{\ntrac-admin /path/to/projenv repository resync \'*\'\n}}}\n\n=== 5. Refresh static resources ===\n\nIf you have set up a web server to give out static resources directly (accessed using the `/chrome/` URL) then you will need to refresh them using the same command:\n{{{\ntrac-admin /path/to/env deploy /deploy/path\n}}}\nthis will extract static resources and CGI scripts (`trac.wsgi`, etc) from new Trac version and its plugins into `/deploy/path`.\n\nSome web browsers cache CSS and Javascript files persistently, so you may need to instruct your users to manually erase the contents of their browser\'s cache.\n\n=== 6. Steps specific to a given Trac version  ===\n==== Upgrading from Trac 0.11 to Trac 0.12 ====\n===== Python 2.3 no longer supported =====\nThe minimum supported version of python is now 2.4\n\n===== SQLite v3.x required =====\nSQLite v2.x is no longer supported. If you still use a Trac database of this format, you\'ll need to convert it to SQLite v3.x first. See [trac:PySqlite#UpgradingSQLitefrom2.xto3.x] for details.\n\n===== PySqlite 2 required =====\nPySqlite 1.1.x is no longer supported. Please install 2.5.5 or later if possible (see [#Tracdatabaseupgrade Trac database upgrade] below).\n\n===== Multiple Repository Support =====\nThe latest version includes support for multiple repositories. If you plan to add more repositories to your Trac instance, please refer to TracRepositoryAdmin#Migration.\n\nThis may be of interest to users with only one repository, since there\'s now a way to avoid the potentially costly resync check at every request.\n\n===== Improved repository synchronization =====\nIn addition to supporting multiple repositories, there is now a more efficient method for synchronizing Trac and your repositories.\n\nWhile you can keep the same synchronization as in 0.11 adding the post-commit hook as outlined in TracRepositoryAdmin#Synchronization and TracRepositoryAdmin#ExplicitSync will allow more efficient synchronization and is more or less required for multiple repositories.\n\nNote that if you were using the `trac-post-commit-hook`, \'\'you\'re strongly advised to upgrade it\'\' to the new hook documented in the above references, as the old hook will not work with anything else than the default repository and even for this case, it won\'t trigger the appropriate notifications.\n\n===== Authz permission checking =====\nThe authz permission checking has been migrated to a fine-grained permission policy. If you use authz permissions (aka `[trac] authz_file` and `authz_module_name`), you must add `AuthzSourcePolicy` in front of your permission policies in `[trac] permission_policies`. You must also remove `BROWSER_VIEW`, `CHANGESET_VIEW`, `FILE_VIEW` and `LOG_VIEW` from your global permissions (with `trac-admin $ENV permission remove` or the \"Permissions\" admin panel).\n\n==== Upgrading from Trac 0.10 to Trac 0.11 ====\n===== Site Templates and Styles =====\nThe templating engine has changed in 0.11 to Genshi, please look at TracInterfaceCustomization for more information.\n\nIf you are using custom CSS styles or modified templates in the `templates` directory of the TracEnvironment, you will need to convert them to the Genshi way of doing things. To continue to use your style sheet, follow the instructions at TracInterfaceCustomization#SiteAppearance.\n\n===== Trac Macros, Plugins =====\nThe Trac macros will need to be adapted, as the old-style wiki-macros are not supported anymore (due to the drop of [trac:ClearSilver] and the HDF); they need to be converted to the new-style macros, see WikiMacros. When they are converted to the new style, they need to be placed into the plugins directory instead and not wiki-macros, which is no longer scanned for macros or plugins.\n\n===== For FCGI/WSGI/CGI users =====\nFor those who run Trac under the CGI environment, run this command in order to obtain the trac.*gi file:\n{{{\ntrac-admin /path/to/env deploy /deploy/directory/path\n}}}\n\nThis will create a deploy directory with the following two subdirectories: `cgi-bin` and `htdocs`. Then update your Apache configuration file `httpd.conf` with this new `trac.cgi` location and `htdocs` location.\n\n===== Web Admin plugin integrated =====\nIf you had the webadmin plugin installed, you can uninstall it as it is part of the Trac code base since 0.11.\n\n=== 7. Restart the Web Server === #RestarttheWebServer\n\nIf you are not running [wiki:TracCgi CGI], reload the new Trac code by restarting your web server.\n\n== Known Issues ==\n\n=== parent dir ===\nIf you use a trac parent env configuration and one of the plugins in one child does not work, none of the children work.\n\n=== Wiki Upgrade ===\n`trac-admin` will not delete or remove default wiki pages that were present in a previous version but are no longer in the new version.\n\n=== Trac database upgrade ===\n\nA known issue in some versions of PySqlite (2.5.2-2.5.4) prevents the trac-admin upgrade script from successfully upgrading the database format. It is advised to use either a newer or older version of the sqlite python bindings to avoid this error. For more details see ticket [trac:#9434].\n\n== Upgrading Python ==\n\nUpgrading Python to a newer version will require reinstallation of Python packages: Trac of course; also [http://pypi.python.org/pypi/setuptools easy_install], if you\'ve been using that.  Assuming you\'re using Subversion, you\'ll also need to upgrade the Python bindings for svn.\n\n=== Windows and Python 2.6 ===\n\nIf you\'ve been using !CollabNet\'s Subversion package, you may need to uninstall that in favor of [http://alagazam.net/ Algazam], which has the Python bindings readily available (see TracSubversion).  The good news is, that works with no tweaking.\n\n== Changing Database Backend ==\n=== SQLite to PostgreSQL ===\n\nThe [http://trac-hacks.org/wiki/SqliteToPgScript sqlite2pg] script on [http://trac-hacks.org trac-hacks.org] has been written to assist in migrating a SQLite database to a PostgreSQL database\n\n== Older Versions ==\n\nFor upgrades from versions older than Trac 0.10, refer first to [trac:wiki:0.10/TracUpgrade#SpecificVersions].\n\n-----\nSee also: TracGuide, TracInstall\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracWiki',1,1327389819647871,'trac','127.0.0.1','= The Trac Wiki Engine =\n[[TracGuideToc]]\n\nTrac has a built-in wiki engine, used for text and documentation throughout the system. WikiFormatting is used in [wiki:TitleIndex wiki pages], [wiki:TracTickets tickets], [wiki:TracChangeset check-in log messages], [wiki:TracRoadmap milestone] and [wiki:TracReports report] descriptions.  It allows for formatted text and hyperlinks in and between all Trac modules.\n\nEditing wiki text is easy, using any web browser and a simple [WikiFormatting formatting system], rather than more complex markup languages like HTML.  The reasoning behind its design is that HTML, with its large collection of nestable tags, is too complicated to allow fast-paced editing, and distracts from the actual content of the pages. Note though that Trac also supports [WikiHtml HTML], [WikiRestructuredText reStructuredText] and [http://www.textism.com/tools/textile/ Textile] as alternative markup formats.\n\nThe main goal of the wiki is to make editing text easier and \'\'encourage\'\' people to contribute and annotate text content for a project. Trac also provides a simple toolbar to make formatting text even easier, and supports the [http://universaleditbutton.org/Universal_Edit_Button universal edit button] of your browser.\n\nThe wiki itself does not enforce any structure, but rather resembles a stack of empty sheets of paper, where you can organize information and documentation as you see fit, and later reorganize if necessary. \nAs contributing to a wiki is essentially building an hypertext, \ngeneral advice regarding HTML authoring apply here as well.\nFor example, the \'\'[http://www.w3.org/Provider/Style Style Guide for online hypertext]\'\' explains how to think about the\n[http://www.w3.org/Provider/Style/Structure.html overall structure of a work] \nand how to organize information [http://www.w3.org/Provider/Style/WithinDocument.html within each document]. One of the most important tip is â€œmake your HTML page such that you can read it even if you don\'t follow any links.â€\n\nLearn more about:\n * WikiNewPage creation, which can be configured to start from a [PageTemplates page template]\n * WikiFormatting rules, including advanced topics like WikiMacros and WikiProcessors\n * How to use WikiPageNames and other forms of TracLinks which are used to refer in a precise way to any resource within Trac\n\nIf you want to practice editing, please use the SandBox.\n\nBefore saving your changes, you can \'\'Preview\'\' the page or \'\'Review the Changes\'\' you\'ve made.\nYou can get an automatic preview of the formatting as you type when you activate the \'\'Edit Side-by-side\'\' mode. \'\' There is a [wiki:/TracIni#trac-section configurable delay] between when you make your edit and when the automatic preview will update.\'\'\n\nSome more information about wikis on the web:\n * A definition of [http://wikipedia.org/wiki/Wiki Wiki], in a famous  wiki encyclopedia\n * The [http://c2.com/cgi/wiki?WikiHistory History] of the original wiki\n * A wiki page explaining [http://www.usemod.com/cgi-bin/mb.pl?WhyWikiWorks why wiki works]\n\n----\nSee also: TracGuide\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('TracWorkflow',1,1327389819647871,'trac','127.0.0.1','= The Trac Ticket Workflow System =\n[[TracGuideToc]]\n\nThe Trac issue database provides a configurable workflow.\n\n== The Default Ticket Workflow ==\n=== Environments upgraded from 0.10 ===\nWhen you run `trac-admin <env> upgrade`, your `trac.ini` will be modified to include a `[ticket-workflow]` section.\nThe workflow configured in this case is the original workflow, so that ticket actions will behave like they did in 0.10.\n\nGraphically, that looks like this:\n\n[[Image(htdocs:../common/guide/original-workflow.png)]]\n\nThere are some significant \"warts\" in this; such as accepting a ticket sets it to \'assigned\' state, and assigning a ticket sets it to \'new\' state.  Perfectly obvious, right?\nSo you will probably want to migrate to \"basic\" workflow; [trac:source:trunk/contrib/workflow/migrate_original_to_basic.py contrib/workflow/migrate_original_to_basic.py] may be helpful.\n\n=== Environments created with 0.11 ===\nWhen a new environment is created, a default workflow is configured in your trac.ini.  This workflow is the basic workflow (described in `basic-workflow.ini`), which is somewhat different from the workflow of the 0.10 releases.\n\nGraphically, it looks like this:\n\n[[Image(htdocs:../common/guide/basic-workflow.png)]]\n\n== Additional Ticket Workflows ==\n\nThere are several example workflows provided in the Trac source tree; look in [trac:source:trunk/contrib/workflow contrib/workflow] for `.ini` config sections.  One of those may be a good match for what you want. They can be pasted into the `[ticket-workflow]` section of your `trac.ini` file. However if you have existing tickets then there may be issues if those tickets have states that are not in the new workflow. \n\nHere are some [http://trac.edgewall.org/wiki/WorkFlow/Examples diagrams] of the above examples.\n\n== Basic Ticket Workflow Customization ==\n\nNote: Ticket \"statuses\" or \"states\" are not separately defined. The states a ticket can be in are automatically generated by the transitions defined in a workflow. Therefore, creating a new ticket state simply requires defining a state transition in the workflow that starts or ends with that state.\n\nCreate a `[ticket-workflow]` section in `trac.ini`.\nWithin this section, each entry is an action that may be taken on a ticket. \nFor example, consider the `accept` action from `simple-workflow.ini`:\n{{{\naccept = new,accepted -> accepted\naccept.permissions = TICKET_MODIFY\naccept.operations = set_owner_to_self\n}}}\nThe first line in this example defines the `accept` action, along with the states the action is valid in (`new` and `accepted`), and the new state of the ticket when the action is taken (`accepted`).\nThe `accept.permissions` line specifies what permissions the user must have to use this action.\nThe `accept.operations` line specifies changes that will be made to the ticket in addition to the status change when this action is taken.  In this case, when a user clicks on `accept`, the ticket owner field is updated to the logged in user.  Multiple operations may be specified in a comma separated list.\n\nThe available operations are:\n - del_owner -- Clear the owner field.\n - set_owner -- Sets the owner to the selected or entered owner.\n   - \'\'actionname\'\'`.set_owner` may optionally be set to a comma delimited list or a single value.\n - set_owner_to_self -- Sets the owner to the logged in user.\n - del_resolution -- Clears the resolution field\n - set_resolution -- Sets the resolution to the selected value.\n   - \'\'actionname\'\'`.set_resolution` may optionally be set to a comma delimited list or a single value.\n{{{\nExample:\n\nresolve_new = new -> closed\nresolve_new.name = resolve\nresolve_new.operations = set_resolution\nresolve_new.permissions = TICKET_MODIFY\nresolve_new.set_resolution = invalid,wontfix\n}}}\n - leave_status -- Displays \"leave as <current status>\" and makes no change to the ticket.\n\'\'\'Note:\'\'\' Specifying conflicting operations (such as `set_owner` and `del_owner`) has unspecified results.\n\n{{{\nresolve_accepted = accepted -> closed\nresolve_accepted.name = resolve\nresolve_accepted.permissions = TICKET_MODIFY\nresolve_accepted.operations = set_resolution\n}}}\n\nIn this example, we see the `.name` attribute used.  The action here is `resolve_accepted`, but it will be presented to the user as `resolve`.\n\nFor actions that should be available in all states, `*` may be used in place of the state.  The obvious example is the `leave` action:\n{{{\nleave = * -> *\nleave.operations = leave_status\nleave.default = 1\n}}}\nThis also shows the use of the `.default` attribute.  This value is expected to be an integer, and the order in which the actions are displayed is determined by this value.  The action with the highest `.default` value is listed first, and is selected by default.  The rest of the actions are listed in order of decreasing `.default` values.\nIf not specified for an action, `.default` is 0.  The value may be negative.\n\nThere are a couple of hard-coded constraints to the workflow.  In particular, tickets are created with status `new`, and tickets are expected to have a `closed` state.  Further, the default reports/queries treat any state other than `closed` as an open state.\n\nWhile creating or modifying a ticket workfow, `contrib/workflow/workflow_parser.py` may be useful.  It can create `.dot` files that [http://www.graphviz.org GraphViz] understands to provide a visual description of the workflow.\n\nThis can be done as follows (your install path may be different).\n{{{\ncd /var/local/trac_devel/contrib/workflow/\nsudo ./showworkflow /srv/trac/PlannerSuite/conf/trac.ini\n}}}\nAnd then open up the resulting `trac.pdf` file created by the script (it will be in the same directory as the `trac.ini` file).\n\nAn online copy of the workflow parser is available at http://foss.wush.net/cgi-bin/visual-workflow.pl\n\nAfter you have changed a workflow, you need to restart apache for the changes to take effect. This is important, because the changes will still show up when you run your script, but all the old workflow steps will still be there until the server is restarted.\n\n== Example: Adding optional Testing with Workflow ==\n\nBy adding the following to your [ticket-workflow] section of trac.ini you get optional testing.  When the ticket is in new, accepted or needs_work status you can choose to submit it for testing.  When it\'s in the testing status the user gets the option to reject it and send it back to needs_work, or pass the testing and send it along to closed.  If they accept it then it gets automatically marked as closed and the resolution is set to fixed.  Since all the old work flow remains, a ticket can skip this entire section.\n\n{{{\ntesting = new,accepted,needs_work,assigned,reopened -> testing\ntesting.name = Submit to reporter for testing\ntesting.permissions = TICKET_MODIFY\n\nreject = testing -> needs_work\nreject.name = Failed testing, return to developer\n\npass = testing -> closed\npass.name = Passes Testing\npass.operations = set_resolution\npass.set_resolution = fixed\n}}}\n\n=== How to combine the `tracopt.ticket.commit_updater` with the testing workflow ===\n\nThe [[source:trunk/tracopt/ticket/commit_updater.py|tracopt.ticket.commit_updater]] is the optional component that [[TracRepositoryAdmin#trac-post-commit-hook|replaces the old trac-post-commit-hook]], in Trac 0.12.\n\nBy default it reacts on some keywords found in changeset message logs like \'\'close\'\', \'\'fix\'\' etc. and performs the corresponding workflow action.\n\nIf you have a more complex workflow, like the testing stage described above and you want the \'\'closes\'\' keyword to move the ticket to the \'\'testing\'\' status instead of the \'\'closed\'\' status, you need to adapt the code a bit. \n\nHave a look at the [[0.11/TracWorkflow#How-ToCombineSVNtrac-post-commit-hookWithTestWorkflow|Trac 0.11 recipe]] for the `trac-post-commit-hook`, this will give you some ideas about how to modify the component.\n\n== Example: Add simple optional generic review state ==\n\nSometimes Trac is used in situations where \"testing\" can mean different things to different people so you may want to create an optional workflow state that is between the default workflow\'s `assigned` and `closed` states, but does not impose implementation-specific details. The only new state you need to add for this is a `reviewing` state. A ticket may then be \"submitted for review\" from any state that it can be reassigned. If a review passes, you can re-use the `resolve` action to close the ticket, and if it fails you can re-use the `reassign` action to push it back into the normal workflow.\n\nThe new `reviewing` state along with its associated `review` action looks like this:\n\n{{{\nreview = new,assigned,reopened -> reviewing\nreview.operations = set_owner\nreview.permissions = TICKET_MODIFY\n}}}\n\nThen, to integrate this with the default Trac 0.11 workflow, you also need to add the `reviewing` state to the `accept` and `resolve` actions, like so:\n\n{{{\naccept = new,reviewing -> assigned\n[â€¦]\nresolve = new,assigned,reopened,reviewing -> closed\n}}}\n\nOptionally, you can also add a new action that allows you to change the ticket\'s owner without moving the ticket out of the `reviewing` state. This enables you to reassign review work without pushing the ticket back to the `new` status.\n\n{{{\nreassign_reviewing = reviewing -> *\nreassign_reviewing.name = reassign review\nreassign_reviewing.operations = set_owner\nreassign_reviewing.permissions = TICKET_MODIFY\n}}}\n\nThe full `[ticket-workflow]` configuration will thus look like this:\n\n{{{\n[ticket-workflow]\naccept = new,reviewing -> assigned\naccept.operations = set_owner_to_self\naccept.permissions = TICKET_MODIFY\nleave = * -> *\nleave.default = 1\nleave.operations = leave_status\nreassign = new,assigned,reopened -> new\nreassign.operations = set_owner\nreassign.permissions = TICKET_MODIFY\nreopen = closed -> reopened\nreopen.operations = del_resolution\nreopen.permissions = TICKET_CREATE\nresolve = new,assigned,reopened,reviewing -> closed\nresolve.operations = set_resolution\nresolve.permissions = TICKET_MODIFY\nreview = new,assigned,reopened -> reviewing\nreview.operations = set_owner\nreview.permissions = TICKET_MODIFY\nreassign_reviewing = reviewing -> *\nreassign_reviewing.operations = set_owner\nreassign_reviewing.name = reassign review\nreassign_reviewing.permissions = TICKET_MODIFY\n}}}\n\n== Example: Limit the resolution options for a new ticket ==\n\nThe above resolve_new operation allows you to set the possible resolutions for a new ticket.  By modifying the existing resolve action and removing the new status from before the `->` we then get two resolve actions.  One with limited resolutions for new tickets, and then the regular one once a ticket is accepted.\n\n{{{\nresolve_new = new -> closed\nresolve_new.name = resolve\nresolve_new.operations = set_resolution\nresolve_new.permissions = TICKET_MODIFY\nresolve_new.set_resolution = invalid,wontfix,duplicate\n\nresolve = assigned,accepted,reopened -> closed\nresolve.operations = set_resolution\nresolve.permissions = TICKET_MODIFY\n}}}\n\n== Advanced Ticket Workflow Customization ==\n\nIf the customization above is not extensive enough for your needs, you can extend the workflow using plugins.  These plugins can provide additional operations for the workflow (like code_review), or implement side-effects for an action (such as triggering a build) that may not be merely simple state changes.  Look at [trac:source:trunk/sample-plugins/workflow sample-plugins/workflow] for a few simple examples to get started.\n\nBut if even that is not enough, you can disable the !ConfigurableTicketWorkflow component and create a plugin that completely replaces it.\n\n== Adding Workflow States to Milestone Progress Bars ==\n\nIf you add additional states to your workflow, you may want to customize your milestone progress bars as well.  See [TracIni#milestone-groups-section TracIni].\n\n== some ideas for next steps ==\n\nNew enhancement ideas for the workflow system should be filed as enhancement tickets against the `ticket system` component.  If desired, add a single-line link to that ticket here.  Also look at the [th:wiki:AdvancedTicketWorkflowPlugin] as it provides experimental operations.\n\nIf you have a response to the comments below, create an enhancement ticket, and replace the description below with a link to the ticket.\n\n * the \"operation\" could be on the nodes, possible operations are:\n   * \'\'\'preops\'\'\': automatic, before entering the state/activity\n   * \'\'\'postops\'\'\': automatic, when leaving the state/activity\n   * \'\'\'actions\'\'\': can be chosen by the owner in the list at the bottom, and/or drop-down/pop-up together with the default actions of leaving the node on one of the arrows.\n\'\'This appears to add complexity without adding functionality; please provide a detailed example where these additions allow something currently impossible to implement.\'\'\n\n * operations could be anything: sum up the time used for the activity, or just write some statistical fields like \n\'\'A workflow plugin can add an arbitrary workflow operation, so this is already possible.\'\'\n\n * set_actor should be an operation allowing to set the owner, e.g. as a \"preop\":\n   * either to a role, a person\n   * entered fix at define time, or at run time, e.g. out of a field, or select.\n\'\'This is either duplicating the existing `set_owner` operation, or needs to be clarified.\'\'\n\n * Actions should be selectable based on the ticket type (different Workflows for different tickets)\n\'\'Look into the [th:wiki:AdvancedTicketWorkflowPlugin]\'s `triage` operation.\'\'\n\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiDeletePage',1,1327389819647871,'trac','127.0.0.1','= Deleting a Wiki Page =\n\nExisting wiki pages can be completely deleted using the \'\'Delete Page\'\' or the \'\'Delete this Version\'\' buttons at the bottom of the wiki page. These buttons are only visible for users with `WIKI_DELETE` permissions.\n\n\'\'\'Note:\'\'\' Deleting a wiki page is an irreversible operation.\n\nIf you want to delete a page because you actually re-created a new page with the same content but a different name, it is recommended to keep the page and use it as a redirection page instead of completely deleting it, as to not frustrate the visitor with broken links when coming to the site from a search engine. \n\nIn this situation, chances are that you actually wanted to [[WikiNewPage#renaming|rename]] the page instead of doing a copy + delete. \nThe \'\'Rename\'\' operation also offers you the possibility to create a redirection page.\nA redirection page is a short page that  contains a link such as  â€œSee !SomeOtherPageâ€. \n\nHowever, deleting specific versions or even complete pages can make sense to remove spam or other abusive submissions.\n\n----\nSee also: TracWiki, TracPermissions\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiFormatting',1,1327389819647871,'trac','127.0.0.1','= WikiFormatting =\n[[TracGuideToc]]\n\nWiki markup is a core feature in Trac, tightly integrating all the other parts of Trac into a flexible and powerful whole.\n\nTrac has a built in small and powerful wiki rendering engine. This wiki engine implements an ever growing subset of the commands from other popular Wikis,\nespecially [http://moinmo.in/ MoinMoin] and [trac:WikiCreole].\n\n\nThis page will give you an in-depth explanation of the wiki markup available anywhere WikiFormatting is allowed.\n\nThe \'\'Cheat sheet\'\' below gives you a quick overview for the most common syntax, each link in the \'\'Category\'\' column will lead you to the more detailed explanation later in this page.\n\nA few other wiki pages present the advanced features of the Trac wiki markup in more depth: \n - TracLinks covers all the possible ways to refer precisely to any Trac resource or parts thereof,\n - WikiPageNames talks about the various names a wiki page can take, CamelCase or not\n - WikiMacros lists the macros available for generating dynamic content,\n - WikiProcessors and WikiHtml details how parts of the wiki text can be processed in special ways\n\n\n== Cheat sheet ==\n\n||= \'\'\'Category\'\'\' =||= \'\'\'Wiki Markup\'\'\' =||= \'\'\'Display\'\'\' =||\n|-----------------------------------------------------------\n{{{#!th rowspan=3\n[#FontStyles Font Styles]\n}}}\n|| `\'\'\'bold\'\'\'`, `\'\'italic\'\'`, `\'\'\'\'\'Wikipedia style\'\'\'\'\'` || \\\n|| \'\'\'bold\'\'\', \'\'italic\'\', \'\'\'\'\'Wikipedia style\'\'\'\'\' ||\n|| {{{`monospaced and \'\'nowiki\'\'`}}} || \\\n|| `monospaced and \'\'nowiki\'\'` ||\n|| `**bold**`, `//italic//`, `**//!WikiCreole style//**` || \\\n|| **bold**, //italic//, **//!WikiCreole style//** ||\n|-----------------------------------------------------------\n||= [#Headings Headings] =||\\\n{{{#!td \n {{{\n == Level 2 ==\n === Level 3 ^([#hn note])^\n }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n== Level 2\n=== Level 3 ^([#hn note])^\n}}}\n|-----------------------------------------------------------\n||= [#Paragraphs Paragraphs]  =||\\\n{{{#!td\n {{{\n First paragraph\n on multiple lines.\n\n Second paragraph.\n }}}\n}}}\n{{{#!td\nFirst paragraph\non multiple lines.\n\nSecond paragraph.\n}}}\n|-----------------------------------------------------------\n||= [#Lists Lists] =||\\\n{{{#!td\n {{{\n * bullets list\n   on multiple paragraphs\n   1. nested list\n     a. different numbering \n        styles\n }}}\n}}}\n{{{#!td\n* bullets list\n  on multiple paragraphs\n  1. nested list\n    a. different numbering\n       styles\n}}}\n|-----------------------------------------------------------\n{{{#!th\n[#DefinitionLists Definition Lists]\n}}}\n{{{#!td\n {{{\n  term:: definition on\n         multiple paragraphs\n }}}\n}}}\n{{{#!td\n term:: definition on\n        multiple paragraphs\n}}}\n|-----------------------------------------------------------\n||= [#PreformattedText Preformatted Text] =||\\\n{{{#!td\n {{{\n {{{\n multiple lines, \'\'no wiki\'\'\n       white space respected\n }}}\n }}}\n}}}\n{{{#!td\n {{{\n multiple lines, \'\'no wiki\'\'\n       white space respected\n }}}\n}}}\n|-----------------------------------------------------------\n||= [#Blockquotes Blockquotes] =||\\\n{{{#!td\n {{{\n   if there\'s some leading\n   space the text is quoted\n }}}\n}}}\n{{{#!td\n if there\'s some leading\n space the text is quoted\n}}}\n|-----------------------------------------------------------\n||= [#DiscussionCitations Discussion Citations] =||\\\n{{{#!td\n {{{\n >> ... (I said)\n > (he replied)\n }}}\n}}}\n{{{#!td\n>>... (I said)\n> (he replied)\n}}}\n|-----------------------------------------------------------\n||= [#Tables Tables] =||\\\n{{{#!td\n {{{\n ||= Table Header =|| Cell ||\n ||||  (details below)  ||\n }}}\n}}}\n{{{#!td\n||= Table Header =|| Cell ||\n||||  (details below)  ||\n}}}\n|-----------------------------------------------------------\n{{{#!th rowspan=2\n[#Links Links]\n}}}\n|| `http://trac.edgewall.org` ||\\\n|| http://trac.edgewall.org ||\n|| `WikiFormatting (CamelCase)` ||\\\n|| WikiFormatting (CamelCase) ||\n|-----------------------------------------------------------\n{{{#!th rowspan=5\n[#TracLinks TracLinks]\n}}}\n|| `wiki:WikiFormatting`, `wiki:\"WikiFormatting\"` ||\\\n|| wiki:WikiFormatting, wiki:\"WikiFormatting\" ||\n|| `#1 (ticket)`, `[1] (changeset)`, `{1} (report)` ||\\\n|| #1 (ticket), [1] (changeset), {1} (report) ||\n|| `ticket:1, ticket:1#comment:1` ||\\\n|| ticket:1, ticket:1#comment:1 ||\n|| `Ticket [ticket:1]`, `[ticket:1Â ticketÂ one]` ||\\\n|| Ticket [ticket:1], [ticket:1 ticketÂ one] ||\n|| `Ticket [[ticket:1]]`, `[[ticket:1|ticketÂ one]]` ||\\\n|| Ticket [[ticket:1]], [[ticket:1|ticketÂ one]] ||\n|-----------------------------------------------------------\n{{{#!th rowspan=2 \n[#SettingAnchors Setting Anchors]\n}}}\n|| `[=#point1 (1)] First...` ||\\\n|| [=#point1 (1)] First... ||\n|| `see [#point1 (1)]` ||\\\n|| see [#point1 (1)] ||\n|-----------------------------------------------------------\n{{{#!th rowspan=2\n[#EscapingLinksandWikiPageNames Escaping Markup]\n}}}\n|| `!\'\' doubled quotes` ||\\\n|| !\'\' doubled quotes ||\n|| `!wiki:WikiFormatting`, `!WikiFormatting` ||\\\n|| !wiki:WikiFormatting, !WikiFormatting ||\n|-----------------------------------------------------------\n||= [#Images Images] =|| `[[Image(`\'\'link\'\'`)]]` || [[Image(htdocs:../common/trac_logo_mini.png)]] ||\n|-----------------------------------------------------------\n{{{#!th rowspan=2\n[#Macros Macros]\n}}}\n|| `[[MacroList(*)]]` ||  \'\'(short list of all available macros)\'\'  ||\n|| `[[Image?]]` ||  \'\'(help for the Image macro)\'\'  ||\n|-----------------------------------------------------------\n||= [#Processors Processors] =||\\\n{{{#!td\n {{{\n {{{\n #!div style=\"font-size: 80%\"\n Code highlighting:\n   {{{#!python\n   hello = lambda: \"world\"\n   }}}\n }}}\n }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n {{{\n #!div style=\"font-size: 80%\"\n Code highlighting:\n   {{{#!python \n   hello = lambda: \"world\"\n   }}}\n }}}\n}}}\n|-----------------------------------------------------------\n||= [#Comments Comments] =||\\\n{{{#!td\n {{{\n {{{#!comment\n Note to Editors: ...\n }}}\n }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n {{{#!comment\n Note to Editors: ...\n }}}\n}}}\n|-----------------------------------------------------------\n||= [#Miscellaneous Miscellaneous] =||\\\n{{{#!td\n {{{\n Line [[br]] break \n Line \\\\ break\n ----\n }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\nLine [[br]] break\nLine \\\\ break\n----\n}}}\n\n\n== Font Styles ==\n\nThe Trac wiki supports the following font styles:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   * \'\'\'bold\'\'\', \n     \'\'\' triple quotes !\'\'\' \n     can be bold too if prefixed by ! \'\'\', \n   * \'\'italic\'\'\n   * \'\'\'\'\'bold italic\'\'\'\'\' or \'\'italic and\n     \'\'\' italic bold \'\'\' \'\'\n   * __underline__\n   * {{{monospace}}} or `monospace`\n     (hence `{{{` or {{{`}}} quoting)\n   * ~~strike-through~~\n   * ^^superscript^^\n   * ,,subscript,,\n   * **also bold**, //italic as well//, \n     and **\'\' bold italic **\'\' //(since 0.12)//\n  }}}\n}}}\n{{{#!td\n * \'\'\'bold\'\'\', \n   \'\'\' triple quotes !\'\'\' \n   can be bold too if prefixed by ! \'\'\', \n * \'\'italic\'\'\n * \'\'\'\'\'bold italic\'\'\'\'\' or \'\'italic and\n   \'\'\' italic bold \'\'\' \'\'\n * __underline__\n * {{{monospace}}} or `monospace`\n   (hence `{{{` or {{{`}}} quoting)\n * ~~strike-through~~\n * ^^superscript^^\n * ,,subscript,,\n * **also bold**, //italic as well//, \n   and **\'\' bold italic **\'\' //(since 0.12)//\n}}}\n\nNotes:\n * `{{{...}}}` and {{{`...`}}} commands not only select a monospace font, but also treat their content as verbatim text, meaning that no further wiki processing is done on this text.\n * {{{ ! }}} tells wiki parser to not take the following characters as wiki format, so pay attention to put a space after !, e.g. when ending bold.\n * all the font styles marks have to be used in opening/closing pairs, \n   and they must nest properly (in particular, an `\'\'` italic can\'t be paired \n   with a `//` one, and `\'\'\'` can\'t be paired with `**`)\n\n\n== Headings ==\n\nYou can create heading by starting a line with one up to six \'\'equal\'\' characters (\"=\")\nfollowed by a single space and the headline text. \n\n[=#hn]\nThe headline text can be followed by the same number of \"=\" characters, but this is no longer mandatory.\n\nFinally, the heading might optionally be followed by an explicit id. If not, an implicit but nevertheless readable id will be generated.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  = Heading =\n  == Subheading\n  === About \'\'this\'\' ===\n  === Explicit id === #using-explicit-id-in-heading\n  == Subheading #sub2\n}}}\n}}}\n{{{#!td style=\"padding: 1em;\"\n  {{{\n  #!div\n  == Subheading\n  === About \'\'this\'\' ===\n  === Explicit id === #using-explicit-id-in-heading\n  == Subheading #sub2\n  }}}\n}}}\n\n== Paragraphs ==\n\nA new text paragraph is created whenever two blocks of text are separated by one or more empty lines.\n\nA forced line break can also be inserted, using:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  Line 1[[BR]]Line 2\n  }}}\n  {{{\n  Paragraph\n  one\n\n  Paragraph \n  two\n  }}}\n}}}\n{{{#!td\n  Line 1[[BR]]Line 2\n\n  Paragraph \n  one\n\n  Paragraph \n  two\n}}}\n\n== Lists ==\n\nThe wiki supports both ordered/numbered and unordered lists.\n\nExample:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   * Item 1\n     * Item 1.1\n        * Item 1.1.1   \n        * Item 1.1.2\n        * Item 1.1.3\n     * Item 1.2\n   * Item 2\n  - items can start at the beginning of a line\n    and they can span multiple lines\n    - be careful though to continue the line \n    with the appropriate indentation, otherwise\n  that will start a new paragraph...\n  \n   1. Item 1\n     a. Item 1.a\n     a. Item 1.b\n        i. Item 1.b.i\n        i. Item 1.b.ii\n   1. Item 2\n  And numbered lists can also be restarted\n  with an explicit number:\n   3. Item 3\n  }}}\n}}}\n{{{#!td\n * Item 1\n   * Item 1.1\n      * Item 1.1.1   \n      * Item 1.1.2\n      * Item 1.1.3\n   * Item 1.2\n * Item 2\n- items can start at the beginning of a line\n  and they can span multiple lines\n  - be careful though to continue the line \n  with the appropriate indentation, otherwise\nthat will start a new paragraph...\n\n 1. Item 1\n   a. Item 1.a\n   a. Item 1.b\n      i. Item 1.b.i\n      i. Item 1.b.ii\n 1. Item 2\nAnd numbered lists can also be restarted with an explicit number:\n 3. Item 3\n}}}\n\n\n== Definition Lists ==\n\nThe wiki also supports definition lists.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   llama::\n     some kind of mammal, with hair\n   ppython::\n     some kind of reptile, without hair\n     (can you spot the typo?)\n  }}}\n}}}\n{{{#!td\n llama::\n   some kind of mammal, with hair\n ppython::\n   some kind of reptile, without hair\n   (can you spot the typo?)\n}}}\n\nNote that you need a space in front of the defined term.\n\n\n== Preformatted Text ==\n\nBlock containing preformatted text are suitable for source code snippets, notes and examples. Use three \'\'curly braces\'\' wrapped around the text to define a block quote. The curly braces need to be on a separate line.\n  \n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  {{{\n  def HelloWorld():\n      print \'\'\'Hello World\'\'\'\n  }}}\n  }}}\n}}}\n{{{#!td\n  {{{\n  def HelloWorld():\n      print \'\'\'Hello World\'\'\'\n  }}}\n}}}\n\nNote that this kind of block is also used for selecting lines that should be processed through WikiProcessors.\n\n== Blockquotes ==\n\nIn order to mark a paragraph as blockquote, indent that paragraph with two spaces.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n{{{\nParagraph\n  This text is a quote from someone else.\n}}}\n}}}\n{{{#!td\nParagraph\n  This text is a quote from someone else.\n}}}\n\n== Discussion Citations ==\n\nTo delineate a citation in an ongoing discussion thread, such as the ticket comment area, e-mail-like citation marks (\">\", \">>\", etc.) may be used.  \n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  >> Someone\'s original text\n  > Someone else\'s reply text\n  >  - which can be any kind of Wiki markup\n  My reply text\n  }}}\n}}}\n{{{#!td\n>> Someone\'s original text\n> Someone else\'s reply text\n>  - which can be any kind of Wiki markup\nMy reply text\n}}}\n\n\n== Tables ==\n=== Simple Tables ===\nSimple tables can be created like this:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  ||Cell 1||Cell 2||Cell 3||\n  ||Cell 4||Cell 5||Cell 6||\n  }}}\n}}}\n{{{#!td style=\"padding: 2em;\"\n||Cell 1||Cell 2||Cell 3||\n||Cell 4||Cell 5||Cell 6||\n}}}\n\nCell headings can be specified by wrapping the content in a pair of \'=\' characters.\nNote that the \'=\' characters have to stick to the cell separators, like this:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  ||        ||= stable =||= latest =||\n  ||= 0.10 =||  0.10.5  || 0.10.6dev||\n  ||= 0.11 =||  0.11.6  || 0.11.7dev||\n  }}}\n}}}\n{{{#!td style=\"padding: 2em;\"\n||        ||= stable =||= latest =||\n||= 0.10 =||  0.10.5  || 0.10.6dev||\n||= 0.11 =||  0.11.6  || 0.11.7dev||\n}}}\n\nFinally, specifying an empty cell means that the next non empty cell will span the empty cells. For example:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  || 1 || 2 || 3 ||\n  |||| 1-2 || 3 ||\n  || 1 |||| 2-3 ||\n  |||||| 1-2-3 ||\n  }}}\n}}}\n{{{#!td style=\"padding: 2em;\"\n|| 1 || 2 || 3 ||\n|||| 1-2 || 3 ||\n|| 1 |||| 2-3 ||\n|||||| 1-2-3 ||\n}}}\n\nNote that if the content of a cell \"sticks\" to one side of the cell and only one, then the text will be aligned on that side. Example:\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  ||=Text =||= Numbers =||\n  ||left align    ||        1.0||\n  ||  center      ||        4.5||\n  ||      right align||     4.5||\n  || default alignment ||   2.5||\n  ||default||         2.5||\n  ||  default ||      2.5||\n  || default ||       2.5||\n  }}}\n}}}\n{{{#!td style=\"padding: 2em;\"\n||=Text =||= Numbers =||\n||left align    ||        1.0||\n||  center      ||        4.5||\n||      right align||     4.5||\n|| default alignment ||   2.5||\n||default||         2.5||\n||  default ||      2.5||\n|| default ||       2.5||\n}}}\n\nIf contrary to the example above, the cells in your table contain more text, it might be convenient to spread a table row over multiple lines of markup. The `\\` character placed at the end of a line after a cell separator tells Trac to not start a new row for the cells on the next line.\n\n||= Wiki Markup =||\n{{{#!td\n  {{{\n  || this is column 1 [http://trac.edgewall.org/newticket new ticket] || \\\n  || this is column 2 [http://trac.edgewall.org/roadmap the road ahead] || \\\n  || that\'s column 3 and last one ||\n  }}}\n}}}\n|-------------\n||= Display =||\n{{{#!td style=\"padding: 2em;\"\n|| this is column 1 [http://trac.edgewall.org/newticket new ticket] || \\\n|| this is column 2 [http://trac.edgewall.org/roadmap the road ahead] || \\\n|| that\'s column 3 and last one ||\n}}}\n\n=== Complex Tables ===\n\nIf the possibilities offered by the simple \"pipe\"-based markup for tables described above are not enough for your needs, you can create more elaborated tables by using [#Processors-example-tables WikiProcessor based tables].\n\n\n== Links ==\n\nHyperlinks are automatically created for WikiPageNames and URLs. !WikiPageLinks can be disabled by prepending an exclamation mark \"!\" character, such as {{{!WikiPageLink}}}.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  TitleIndex, http://www.edgewall.com/, !NotAlink\n  }}}\n}}}\n{{{#!td\nTitleIndex, http://www.edgewall.com/, !NotAlink\n}}}\n\nLinks can be given a more descriptive title by writing the link followed by a space and a title and all this inside square brackets. \nIf the descriptive title is omitted, then the explicit prefix is discarded, unless the link is an external link. This can be useful for wiki pages not adhering to the WikiPageNames convention.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   * [http://www.edgewall.com Edgewall Software]\n   * [wiki:TitleIndex Title Index] \n   * [wiki:TitleIndex] \n   * [wiki:ISO9000]\n  }}}\n}}}\n{{{#!td\n   * [http://www.edgewall.com Edgewall Software]\n   * [wiki:TitleIndex Title Index] \n   * [wiki:TitleIndex] \n   * [wiki:ISO9000]\n}}}\n\nFollowing the [trac:WikiCreole] trend, the descriptive title can also be specified by writing the link followed by a pipe (\'|\') and a title and all this inside //double// square brackets. \n\n{{{#!td\n  {{{\n   * [[http://www.edgewall.com|Edgewall Software]]\n   * [[wiki:TitleIndex|Title Index]]\n     or even [[TitleIndex|Title Index]]\n   * [[wiki:TitleIndex]]\n     \'\'\' but not ![[TitleIndex]]! \'\'\'\n   * [[ISO9000]]\n  }}}\n}}}\n{{{#!td\n   * [[http://www.edgewall.com|Edgewall Software]]\n   * [[wiki:TitleIndex|Title Index]]\n     or even [[TitleIndex|Title Index]]\n   * [[wiki:TitleIndex]]\n     \'\'\' but not ![[TitleIndex]]! \'\'\'\n   * [[ISO9000]]\n}}}\n\n\'\'\'Note\'\'\': the [trac:WikiCreole] style for links is quick to type and\ncertainly looks familiar as it\'s the one used on Wikipedia and in many\nother wikis. Unfortunately it conflicts with the syntax for [#Macros macros].\nSo in the rare case when you need to refer to a page which is named after\na macro (typical examples being TitleIndex, InterTrac and InterWiki), \nby writing `[[TitleIndex]]` you will actually call the macro instead of linking\nto the page.\n\n== Trac Links ==\n\nWiki pages can link directly to other parts of the Trac system. Pages can refer to tickets, reports, changesets, milestones, source files and other Wiki pages using the following notations:\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   * Tickets: #1 or ticket:1\n   * Reports: {1} or report:1\n   * Changesets: r1, [1] or changeset:1\n   * ...\n   * targeting other Trac instances, \n     so called InterTrac links:\n     - Tickets: #Trac1 or Trac:ticket:1\n     - Changesets: [Trac1] or Trac:changeset:1\n  }}}\n}}}\n{{{#!td\n * Tickets: #1 or ticket:1\n * Reports: {1} or report:1\n * Changesets: r1, [1] or changeset:1\n * ... \n * targeting other Trac instances, \n   so called InterTrac links:\n   - Tickets: #Trac1 or Trac:ticket:1\n   - Changesets: [Trac1] or Trac:changeset:1\n}}}\n\nThere are many more flavors of Trac links, see TracLinks for more in-depth information and a reference for all the default link resolvers.\n\n\n== Setting Anchors ==\n\nAn anchor, or more correctly speaking, an [http://www.w3.org/TR/REC-html40/struct/links.html#h-12.2.1 anchor name] can be added explicitly at any place in the Wiki page, in order to uniquely identify a position in the document:\n\n{{{\n[=#point1]\n}}}\n\nThis syntax was chosen to match the format for explicitly naming the header id [#Headings documented above]. For example:\n{{{\n== Long title == #title\n}}}\n\nIt\'s also very close to the syntax for the corresponding link to that anchor:\n{{{\n[#point1]\n}}}\n\nOptionally, a label can be given to the anchor:\n{{{\n[[=#point1 \'\'\'Point 1\'\'\']]\n}}}\n\n||= Wiki Markup =||= Display =||\n|----------------------------------\n{{{#!td\n  {{{\n  [#point2 jump to the second point]\n\n  ...\n\n  Point2:  [=#point2] Jump here\n  }}}\n}}}\n{{{#!td\n  [#point2 jump to the second point]\n\n  ...\n\n  Point2:  [=#point2] Jump here\n}}}\n\nFor more complex anchors (e.g. when a custom title is wanted), one can use the Span macro, e.g. `[[span(id=point2, class=wikianchor, title=Point 2, ^(2)^)]]`.\n\n\n== Escaping Links and WikiPageNames ==\n\nYou may avoid making hyperlinks out of TracLinks by preceding an expression with a single \"!\" (exclamation mark).\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n   !NoHyperLink\n   !#42 is not a link\n  }}}\n}}}\n{{{#!td\n !NoHyperLink\n !#42 is not a link\n}}}\n\n== Images ==\n\nUrls ending with `.png`, `.gif` or `.jpg` are no longer automatically interpreted as image links, and converted to `<img>` tags.\n\nYou now have to use the ![[Image]] macro. The simplest way to include an image is to upload it as attachment to the current page, and put the filename in a macro call like `[[Image(picture.gif)]]`.\n\nIn addition to the current page, it is possible to refer to other resources:\n * `[[Image(wiki:WikiFormatting:picture.gif)]]` (referring to attachment on another page)\n * `[[Image(ticket:1:picture.gif)]]` (file attached to a ticket)\n * `[[Image(htdocs:picture.gif)]]` (referring to a file inside the [TracEnvironment environment] `htdocs` directory)\n * `[[Image(source:/trunk/trac/htdocs/trac_logo_mini.png)]]` (a file in repository)\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  [[Image(htdocs:../common/trac_logo_mini.png)]]\n  }}}\n}}}\n{{{#!td\n[[Image(htdocs:../common/trac_logo_mini.png)]]\n}}}\n\nSee WikiMacros for further documentation on the `[[Image()]]` macro, which has several useful options (`title=`, `link=`, etc.)\n\n\n== Macros ==\n\nMacros are \'\'custom functions\'\' to insert dynamic content in a page.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  [[RecentChanges(Trac,3)]]\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n[[RecentChanges(Trac,3)]]\n}}}\n\nSee WikiMacros for more information, and a list of installed macros.\n\nThe detailed help for a specific macro can also be obtained more directly by appending a \"?\" to the macro name.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  [[MacroList?]]\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n[[MacroList?]]\n}}}\n\n\n== Processors ==\n\nTrac supports alternative markup formats using WikiProcessors. For example, processors are used to write pages in \n[wiki:WikiRestructuredText reStructuredText] or [wiki:WikiHtml HTML]. \n\n||= Wiki Markup =||= Display =||\n|--------------------------------------------------------\n{{{#!td align=\"center\" colspan=2 style=\"border: 0px; font-size: 90%\"\n\n   [=#Processors-example-html Example 1:] HTML\n\n}}}\n|--------------------------------------------------------\n{{{#!td style=\"border: 0px\"\n  {{{\n  {{{\n  #!html\n  <h1 style=\"text-align: right; color: blue\">\n   HTML Test\n  </h1>\n  }}}\n  }}}\n}}}\n{{{#!td valign=\"top\"  style=\"border: 0px\"\n\n{{{\n#!html\n<h1 style=\"text-align: right; color: blue\">HTML Test</h1>\n}}}\n\n}}}\n|--------------------------------------------------------\n{{{#!td align=\"center\" colspan=2 style=\"border: 0px; font-size: 90%\"\n\n   [=#Processors-example-highlight Example 2:] Code Highlighting\n\n}}}\n|--------------------------------------------------------\n{{{#!td style=\"border: 0px\"\n  {{{\n  {{{\n  #!python\n  class Test:\n  \n      def __init__(self):\n          print \"Hello World\"\n  if __name__ == \'__main__\':\n     Test()\n  }}}\n  }}}\n}}}\n{{{\n#!td valign=\"top\"  style=\"border: 0px\"\n\n{{{\n#!python\nclass Test:\n    def __init__(self):\n        print \"Hello World\"\nif __name__ == \'__main__\':\n   Test()\n}}}\n\n}}}\n|--------------------------------------------------------\n{{{#!td align=\"center\" colspan=2 style=\"border: 0px; font-size: 90%\"\n\n       [=#Processors-example-tables Example 3:] Complex Tables\n\n}}}\n|--------------------------------------------------------\n{{{#!td style=\"border: 0px\"\n  {{{\n  {{{#!th rowspan=4 align=justify\n  With the `#td` and `#th` processors,\n  table cells can contain any content:\n  }}}\n  |----------------\n  {{{#!td\n    - lists\n    - embedded tables\n    - simple multiline content\n  }}}\n  |----------------\n  {{{#!td\n  As processors can be easily nested, \n  so can be tables:\n    {{{#!th\n    Example:\n    }}}\n    {{{#!td style=\"background: #eef\"\n    || must be at the third level now... ||\n    }}}\n  }}}\n  |----------------\n  {{{#!td\n  Even when you don\'t have complex markup,\n  this form of table cells can be convenient\n  to write content on multiple lines.\n  }}}\n  }}}\n}}}\n{{{\n#!td  valign=\"top\"  style=\"border: 0px\"\n\n  {{{#!th rowspan=4 align=justify\n  With the `#td` and `#th` processors,\n  table cells can contain any content:\n  }}}\n  |----------------\n  {{{#!td\n    - lists\n    - embedded tables\n    - simple multiline content\n  }}}\n  |----------------\n  {{{#!td\n  As processors can be easily nested, \n  so can be tables:\n    {{{#!th\n    Example:\n    }}}\n    {{{#!td style=\"background: #eef\"\n    || must be at the third level now... ||\n    }}}\n  }}}\n  |----------------\n  {{{#!td\n  Even when you don\'t have complex markup,\n  this form of table cells can be convenient\n  to write content on multiple lines.\n  }}}\n\n}}}\n\nSee WikiProcessors for more information.\n\n\n== Comments ==\n\nComments can be added to the plain text. These will not be rendered and will not display in any other format than plain text.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  Nothing to\n  {{{\n  #!comment\n  Your comment for editors here\n  }}}\n  see ;-)\n  }}}\n}}}\n{{{#!td\n  Nothing to\n  {{{\n  #!comment\n  Your comment for editors here\n  }}}\n  see ;-)\n}}}\n\n== Miscellaneous ==\n\nAn horizontal line can be used to separated different parts of your page:\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  Four or more dashes will be replaced \n  by an horizontal line (<HR>)\n  ----\n  See?\n  }}}\n}}}\n{{{#!td\nFour or more dashes will be replaced\nby an horizontal line (<HR>)\n----\nSee?\n}}}\n|----------------------------------\n{{{#!td\n  {{{\n  \"macro\" style [[br]] line break\n  }}}\n}}}\n{{{#!td\n\"macro\" style [[br]] line break\n}}}\n|----------------------------------\n{{{#!td\n  {{{\n  !WikiCreole style \\\\ line\\\\break\n  }}}\n}}}\n{{{#!td\n!WikiCreole style \\\\ line\\\\break\n}}}\n\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiHtml',1,1327389819647871,'trac','127.0.0.1','= Using HTML in Wiki Text =\n\nTrac supports inserting HTML into any wiki context, accomplished using the `#!html` [wiki:WikiProcessors WikiProcessor]. \n\nHowever a constraint is that this HTML has to be well-formed.\nIn particular you can\'t insert a start tag in an `#!html` block,\nresume normal wiki text and insert the corresponding end tag in a \nsecond `#!html` block. \n\nFortunately, for creating styled <div>s, <span>s  or even complex tables\ncontaining arbitrary Wiki text, there\'s a powerful alternative: use of\ndedicated `#!div`, `#!span` and `#!table`, `#!tr`, `#!td` and `#!th` blocks.\n\nThose Wiki processors are built-in, and does not require installing any additional packages.\n\n== How to use `#!html` == #HowtoUseHTML\nTo inform the wiki engine that a block of text should be treated as HTML, use the \'\'html\'\' processor. \n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  {{{\n  #!html\n  <h1 style=\"text-align: right; color: blue\">HTML Test</h1>\n  }}}\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n  {{{\n  #!html\n  <h1 style=\"text-align: right; color: blue\">HTML Test</h1>\n  }}}\n}}}\n\nNote that Trac sanitizes your HTML code before displaying it. That means that if you try to use potentially dangerous constructs such as Javascript event handlers, those will be removed from the output. \n\nSince 0.11, the filtering is done by Genshi, and as such, the produced output will be a well-formed fragment of HTML. As noted above in the introduction, this mean that you can no longer use two HTML blocks, one for opening a <div>, the second for closing it, in order to wrap arbitrary wiki text.\nThe new way to wrap any wiki content inside a <div> is to use the `#!div` Wiki  processor.\n\n== How to use `#!div` and `#!span` == #HowtoUseDivSpan\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  {{{\n  #!div class=\"important\" style=\"border: 2pt solid; text-align: center\"\n  This is the \'\'only\'\' way to go in Trac 0.11\n  }}}\n\n  {{{\n  #!div class=\"wikipage\" style=\"border: 1pt dotted\"\n  Only `wikipage` (same as specifying no class attribute)\n  }}}\n\n  {{{\n  #!div class=\"wikipage compact \" style=\"border: 1pt solid\"\n  Use combined classes (`compact` and `wikipage`)\n  }}}\n\n  {{{\n  #!div class=\"compact\" style=\"border: 1pt dotted\"\n  Only `compact`\n  }}}\n\n  {{{\n  #!div class=\"\" style=\"border: 1pt solid\"\n  No classes (//not// the same as specifying no class attribute...)\n  }}}\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em\"\n  {{{\n  #!div class=\"important\" style=\"border: 2pt solid; text-align: center\"\n  This is the \'\'only\'\' way to go in Trac 0.11\n  }}}\n\n  {{{\n  #!div class=\"wikipage\" style=\"border: 1pt dotted\"\n  Only `wikipage` (same as specifying no class attribute)\n  }}}\n\n  {{{\n  #!div class=\"wikipage compact \" style=\"border: 1pt solid\"\n  Use combined classes (`compact` and `wikipage`)\n  }}}\n\n  {{{\n  #!div class=\"compact\" style=\"border: 1pt dotted\"\n  Only compact\n  }}}\n\n  {{{\n  #!div class=\"\" style=\"border: 1pt solid\"\n  No classes (//not// the same as specifying no class attribute...)\n  }}}\n}}}\n\nNote that the contents of a `#!div` block are contained in one or more paragraphs, which have a non-zero top and bottom margin. This leads to the top and bottom padding in the example above. To remove the top and bottom margin of the contents, add the `compact` class to the `#!div`. Another predefined class besides `wikipage` and `compact` is `important`, which can be used to make a paragraph stand out. Extra CSS classes can be defined via the `site/style.css` file for example, see TracInterfaceCustomization#SiteAppearance.\n\nFor spans, you should rather use the Macro call syntax:\n||= Wiki Markup =||\n{{{#!td\n  {{{\n  Hello \n  [[span(\'\'WORLD\'\' (click [#anchor here]), style=color: green; font-size: 120%, id=anchor)]]!\n  }}}\n}}}\n|---------------------------------------------------------------------------------\n||= Display =||\n{{{#!td style=\"padding-left: 2em\"\n  Hello\n  [[span(\'\'WORLD\'\' (click [#anchor here]), style=color: green; font-size: 120%, id=anchor)]]!\n}}}\n\n== How to use `#!td` and other table related processors == #Tables\n\n`#!td` or `#!th` processors are actually the main ones, for creating table data and header cells, respectively. The other processors `#!table` and `#!tr` are not required for introducing a table structure, as `#!td` and `#!th` will do this automatically. The `|-` row separator can be used to start a new row when needed, but some may prefer to use a `#!tr` block for that, as this introduces a more formal grouping and offers the possibility to use an extra level of indentation. The main purpose of the `#!table` and `#!tr` is to give the possibility to specify HTML attributes, like \'\'style\'\' or \'\'valign\'\' to these elements.\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n {{{\n Simple 2x2 table with rich content:\n {{{#!th align=left\n  - Left\n  - Header\n }}}\n {{{#!th align=left\n  - Right\n  - Header\n }}}\n |----------------------------------\n {{{#!td style=\"background: #ffd\"\n  - Left\n  - Content\n }}}\n {{{#!td style=\"vertical-align: top\"\n !RightContent\n }}}\n |----------------------------------\n || ... and this can be mixed||\\\n ||with pipe-based cells ||\n {{{#!td colspan=2\n Pick the style the more appropriate\n to your content\n \n See WikiFormatting#Tables for details\n on the pipe-based table syntax.\n }}}\n \n If one needs to add some \n attributes to the table itself...\n \n {{{\n #!table style=\"border:none;text-align:center;margin:auto\"\n   {{{#!tr ====================================\n     {{{#!th style=\"border: none\"\n     Left header\n     }}}\n     {{{#!th style=\"border: none\"\n     Right header\n     }}}\n   }}}\n   {{{#!tr ==== style=\"border: 1px dotted grey\"\n     {{{#!td style=\"border: none\"\n     1.1\n     }}}\n     {{{#!td style=\"border: none\"\n     1.2\n     }}}\n   }}}\n   {{{#!tr ====================================\n     {{{#!td style=\"border: none\"\n     2.1\n     }}}\n     {{{#!td\n     2.2\n     }}}\n   }}}\n }}}\n\n\n }}}\n}}}\n{{{#!td valign=top\nSimple 2x2 table with rich content:\n{{{#!th align=left\n - Left\n - Header\n}}}\n{{{#!th align=left\n - Right\n - Header\n}}}\n|----------------------------------\n{{{#!td style=\"background: #ffd\"\n - Left\n - Content\n}}}\n{{{#!td style=\"vertical-align: top\"\n!RightContent\n}}}\n|----------------------------------\n|| ... and this can be mixed||\\\n||with pipe-based cells ||\n{{{#!td colspan=2\nPick the style the more appropriate\nto your content\n\nSee WikiFormatting#Tables for details\non the pipe-based table syntax.\n}}}\n\nIf one needs to add some \nattributes to the table itself...\n\n{{{\n#!table style=\"border:none;text-align:center;margin:auto\"\n  {{{#!tr ====================================\n    {{{#!th style=\"border: none\"\n    Left header\n    }}}\n    {{{#!th style=\"border: none\"\n    Right header\n    }}}\n  }}}\n  {{{#!tr ==== style=\"border: 1px dotted grey\"\n    {{{#!td style=\"border: none\"\n    1.1\n    }}}\n    {{{#!td style=\"border: none\"\n    1.2\n    }}}\n  }}}\n  {{{#!tr ====================================\n    {{{#!td style=\"border: none\"\n    2.1\n    }}}\n    {{{#!td\n    2.2\n    }}}\n  }}}\n}}}\n}}}\n\nNote that by default tables are assigned the \"wiki\" CSS class, which gives a distinctive look to the header cells and a default border to the table and cells (as can be seen for the tables on this page). By removing this class (`#!table class=\"\"`), one regains complete control on the table presentation. In particular, neither the table, the rows nor the cells will have a border, so this is a more effective way to get such an effect than having to specify a `style=\"border: no\"` parameter everywhere. \n\n{{{#!table class=\"\"\n||= Wiki Markup =||= Display =||\n {{{#!td\n  {{{\n  {{{#!table class=\"\"\n  ||  0||  1||  2||\n  || 10|| 20|| 30||\n  || 11|| 22|| 33||\n  ||||||=  numbers  =||\n  }}}\n  }}}\n }}}\n {{{#!td\n  {{{#!table class=\"\"\n  ||  0||  1||  2||\n  || 10|| 20|| 30||\n  || 11|| 22|| 33||\n  ||||||=  numbers  =||\n  }}}\n }}}\n}}}\n\nOther classes can be specified as alternatives (remember that you can define your own in [TracInterfaceCustomization#SiteAppearance site/style.css]).\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  {{{#!table class=\"listing\"\n  ||  0||  1||  2||\n  || 10|| 20|| 30||\n  || 11|| 22|| 33||\n  ||||||=  numbers  =||\n  }}}\n  }}}\n}}}\n{{{#!td\n  {{{#!table class=\"listing\"\n  ||  0||  1||  2||\n  || 10|| 20|| 30||\n  || 11|| 22|| 33||\n  ||||||=  numbers  =||\n  }}}\n}}}\n\n\n== HTML comments ==\nHTML comments are stripped from the output of the `html` processor. To add an HTML comment to a wiki page, use the `htmlcomment` processor (available since 0.12). For example, the following code block:\n||= Wiki Markup =||\n{{{#!td\n  {{{\n  {{{\n  #!htmlcomment\n  This block is translated to an HTML comment.\n  It can contain <tags> and &entities; that will not be escaped in the output.\n  }}}\n  }}}\n}}}\n|---------------------------------------------------------------------------------\n||= Display =||\n{{{#!td\n  {{{\n  <!--\n  This block is translated to an HTML comment.\n  It can contain <tags> and &entities; that will not be escaped in the output.\n  -->\n  }}}\n}}}\n\nPlease note that the character sequence \"--\" is not allowed in HTML comments, and will generate a rendering error.\n\n\n== More Information ==\n\n * http://www.w3.org/ -- World Wide Web Consortium\n * http://www.w3.org/MarkUp/ -- HTML Markup Home Page\n\n----\nSee also:  WikiProcessors, WikiFormatting, WikiRestructuredText\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiMacros',1,1327389819647871,'trac','127.0.0.1','= Trac Macros =\n\n[[PageOutline]]\n\nTrac macros are plugins to extend the Trac engine with custom \'functions\' written in Python. A macro inserts dynamic HTML data in any context supporting WikiFormatting.\n\nAnother kind of macros are WikiProcessors. They typically deal with alternate markup formats and representation of larger blocks of information (like source code highlighting).\n\n== Using Macros ==\n\nMacro calls are enclosed in two \'\'square brackets\'\'. Like Python functions, macros can also have arguments, a comma separated list within parentheses.\n\n=== Getting Detailed Help ===\nThe list of available macros and the full help can be obtained using the !MacroList macro, as seen [#AvailableMacros below].\n\nA brief list can be obtained via ![[MacroList(*)]] or ![[?]].\n\nDetailed help on a specific macro can be obtained by passing it as an argument to !MacroList, e.g. ![[MacroList(MacroList)]], or, more conveniently, by appending a question mark (?) to the macro\'s name, like in ![[MacroList?]].\n\n\n\n=== Example ===\n\nA list of 3 most recently changed wiki pages starting with \'Trac\':\n\n||= Wiki Markup =||= Display =||\n{{{#!td\n  {{{\n  [[RecentChanges(Trac,3)]]\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em;\"\n[[RecentChanges(Trac,3)]]\n}}}\n|-----------------------------------\n{{{#!td\n  {{{\n  [[RecentChanges?(Trac,3)]]\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em;\"\n[[RecentChanges?(Trac,3)]]\n}}}\n|-----------------------------------\n{{{#!td\n  {{{\n  [[?]]\n  }}}\n}}}\n{{{#!td style=\"padding-left: 2em; font-size: 80%\"\n[[?]]\n}}}\n\n== Available Macros ==\n\n\'\'Note that the following list will only contain the macro documentation if you\'ve not enabled `-OO` optimizations, or not set the `PythonOptimize` option for [wiki:TracModPython mod_python].\'\'\n\n[[MacroList]]\n\n== Macros from around the world ==\n\nThe [http://trac-hacks.org/ Trac Hacks] site provides a wide collection of macros and other Trac [TracPlugins plugins] contributed by the Trac community. If you\'re looking for new macros, or have written one that you\'d like to share with the world, please don\'t hesitate to visit that site.\n\n== Developing Custom Macros ==\nMacros, like Trac itself, are written in the [http://python.org/ Python programming language] and are developed as part of TracPlugins.\n\nFor more information about developing macros, see the [trac:TracDev development resources] on the main project site.\n\n\nHere are 2 simple examples showing how to create a Macro with Trac 0.11. \n\nAlso, have a look at [trac:source:tags/trac-0.11/sample-plugins/Timestamp.py Timestamp.py] for an example that shows the difference between old style and new style macros and at the [trac:source:tags/trac-0.11/wiki-macros/README macros/README] which provides a little more insight about the transition.\n\n=== Macro without arguments ===\nTo test the following code, you should saved it in a `timestamp_sample.py` file located in the TracEnvironment\'s `plugins/` directory.\n{{{\n#!python\nfrom datetime import datetime\n# Note: since Trac 0.11, datetime objects are used internally\n\nfrom genshi.builder import tag\n\nfrom trac.util.datefmt import format_datetime, utc\nfrom trac.wiki.macros import WikiMacroBase\n\nclass TimeStampMacro(WikiMacroBase):\n    \"\"\"Inserts the current time (in seconds) into the wiki page.\"\"\"\n\n    revision = \"$Rev$\"\n    url = \"$URL$\"\n\n    def expand_macro(self, formatter, name, text):\n        t = datetime.now(utc)\n        return tag.b(format_datetime(t, \'%c\'))\n}}}\n\n=== Macro with arguments ===\nTo test the following code, you should saved it in a `helloworld_sample.py` file located in the TracEnvironment\'s `plugins/` directory.\n{{{\n#!python\nfrom genshi.core import Markup\n\nfrom trac.wiki.macros import WikiMacroBase\n\nclass HelloWorldMacro(WikiMacroBase):\n    \"\"\"Simple HelloWorld macro.\n\n    Note that the name of the class is meaningful:\n     - it must end with \"Macro\"\n     - what comes before \"Macro\" ends up being the macro name\n\n    The documentation of the class (i.e. what you\'re reading)\n    will become the documentation of the macro, as shown by\n    the !MacroList macro (usually used in the WikiMacros page).\n    \"\"\"\n\n    revision = \"$Rev$\"\n    url = \"$URL$\"\n\n    def expand_macro(self, formatter, name, text, args):\n        \"\"\"Return some output that will be displayed in the Wiki content.\n\n        `name` is the actual name of the macro (no surprise, here it\'ll be\n        `\'HelloWorld\'`),\n        `text` is the text enclosed in parenthesis at the call of the macro.\n          Note that if there are \'\'no\'\' parenthesis (like in, e.g.\n          [[HelloWorld]]), then `text` is `None`.\n        `args` are the arguments passed when HelloWorld is called using a\n        `#!HelloWorld` code block.\n        \"\"\"\n        return \'Hello World, text = %s, args = %s\' % \\\n            (Markup.escape(text), Markup.escape(repr(args)))\n\n}}}\n\nNote that `expand_macro` optionally takes a 4^th^ parameter \'\'`args`\'\'. When the macro is called as a [WikiProcessors WikiProcessor], it\'s also possible to pass `key=value` [WikiProcessors#UsingProcessors processor parameters]. If given, those are stored in a dictionary and passed in this extra `args` parameter. On the contrary, when called as a macro, `args` is  `None`. (\'\'since 0.12\'\').\n\nFor example, when writing:\n{{{\n{{{#!HelloWorld style=\"polite\"\n<Hello World!>\n}}}\n\n{{{#!HelloWorld\n<Hello World!>\n}}}\n\n[[HelloWorld(<Hello World!>)]]\n}}}\nOne should get:\n{{{\nHello World, text = <Hello World!> , args = {\'style\': u\'polite\'}\nHello World, text = <Hello World!> , args = {}\nHello World, text = <Hello World!> , args = None\n}}}\n\nNote that the return value of `expand_macro` is \'\'\'not\'\'\' HTML escaped. Depending on the expected result, you should escape it by yourself (using `return Markup.escape(result)`) or, if this is indeed HTML, wrap it in a Markup object (`return Markup(result)`) with `Markup` coming from Genshi, (`from genshi.core import Markup`).  \n\nYou can also recursively use a wiki Formatter (`from trac.wiki import Formatter`) to process the `text` as wiki markup, for example by doing:\n\n{{{\n#!python\nfrom genshi.core import Markup\nfrom trac.wiki.macros import WikiMacroBase\nfrom trac.wiki import Formatter\nimport StringIO\n\nclass HelloWorldMacro(WikiMacroBase):\n	def expand_macro(self, formatter, name, text, args):\n		text = \"whatever \'\'\'wiki\'\'\' markup you want, even containing other macros\"\n		# Convert Wiki markup to HTML, new style\n		out = StringIO.StringIO()\n		Formatter(self.env, formatter.context).format(text, out)\n		return Markup(out.getvalue())\n}}}\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiNewPage',1,1327389819647871,'trac','127.0.0.1','= Steps to Add a New Wiki Page =\n[[TracGuideToc]]\n\n 1. Choose a name for your new page. See WikiPageNames for naming conventions.\n 2. Edit an existing page (or any other resources that support WikiFormatting and add a [TracLinks link] to your new page. Save your changes.\n 3. Follow the link you created to take you to the new page. Trac will display a \"describe !PageName here\" message.\n 4. Click the \"Edit this page\" button to edit and add content to your new page. Save your changes.\n 5. All done. Your new page is published.\n\nYou can skip the second step by entering the CamelCase name of the page in the quick-search field at the top of the page. But note that the page will effectively be \"orphaned\" unless you link to it from somewhere else.\n\n== Rename a page #renaming\n\nWhile picking up good WikiPageNames is important, you can always change your mind\nand rename the page later.\n\nYou\'ll need to ask for the WIKI_RENAME permission in order to be allowed to do this.\nWhen renaming a page, you\'ll be offered the possibility to create a redirection page, so that links pointing to the old location will not be left dangling.\n\n----\nSee also: TracWiki, PageTemplates, WikiFormatting, TracLinks, WikiDeletePage\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiPageNames',1,1327389819647871,'trac','127.0.0.1','= Wiki Page Names =\n[[TracGuideToc]]\n\nWiki page names commonly use the CamelCase convention. Within wiki text, any word in CamelCase automatically becomes a hyperlink to the wiki page with that name.\n\nCamelCase page names must follow these rules:\n\n 1. The name must consist of \'\'\'alphabetic characters only\'\'\'. No digits, spaces, punctuation, or underscores are allowed.\n 2. A name must have at least two capital letters.\n 3. The first character must be capitalized.\n 4. Every capital letter must be followed by one or more lower-case letters. \n 5. The use of slash ( / ) is permitted in page names (possibly representing a hierarchy).\n\nIf you want to create a wiki page that doesn\'t follow CamelCase rules you can use the following syntax:\n{{{\n * [wiki:Wiki_page], [wiki:ISO9000],\n   and with a label: [wiki:ISO9000 ISO 9000 standard]\n * [wiki:\"Space Matters\"]\n   and with a label: [wiki:\"Space Matters\" all about white space]\n * or simply: [\"WikiPageName\"]s\n * even better, the new [[WikiCreole link style]]\n   and with a label: [[WikiCreole link style|WikiCreole style links]]\n}}}\n\nThis will be rendered as:\n * [wiki:Wiki_page], [wiki:ISO9000],\n   and with a label: [wiki:ISO9000 ISO 9000 standard]\n * [wiki:\"Space Matters\"] \'\'(that page name embeds space characters)\'\'\n   and with a label: [wiki:\"Space Matters\" all about white space]\n * or simply: [\"WikiPageName\"]s \'\'(old !MoinMoin\'s internal free links style)\'\'\n * even better, the new [[WikiCreole link style]]\n   and with a label: [[WikiCreole link style|WikiCreole style links]]\n   \'\'(since 0.12, also now adopted by !MoinMoin)\'\'\n\n\nStarting with Trac 0.11, it\'s also possible to link to a specific \'\'version\'\' of a Wiki page, as you would do for a specific version of a file, for example: WikiStart@1.\n\nYou can also prevent a CamelCase name to be interpreted as a TracLinks, by quoting it. See TracLinks#EscapingLinks.\n\nAs visible in the example above, one can also append an anchor to a Wiki page name, in order to link to a specific section within that page. The anchor can easily be seen by hovering the mouse over a section heading, then clicking on the [[html(&para;)]] sign that appears at its end. The anchor is usually generated automatically, but it\'s also possible to specify it explicitly: see WikiFormatting#using-explicit-id-in-heading.\n----\nSee also: WikiNewPage, WikiFormatting, TracWiki, TracLinks\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiProcessors',1,1327389819647871,'trac','127.0.0.1','= Wiki Processors =\n\nProcessors are WikiMacros designed to provide alternative markup formats for the [TracWiki Wiki engine]. Processors can be thought of as \'\'macro functions to process user-edited text\'\'. \n\nWiki processors can be used in any Wiki text throughout Trac,\nfor various different purposes, like:\n - [#CodeHighlightingSupport syntax highlighting] or for rendering text verbatim,\n - rendering [#HTMLrelated Wiki markup inside a context], \n   like inside <div> blocks or <span> or within <td> or <th> table cells,\n - using an alternative markup syntax, like [wiki:WikiHtml raw HTML] and\n   [wiki:WikiRestructuredText Restructured Text],\n   or [http://www.textism.com/tools/textile/ textile]\n\n\n== Using Processors ==\n\nTo use a processor on a block of text, first delimit the lines using\na Wiki \'\'code block\'\':\n{{{\n{{{\nThe lines\nthat should be processed...\n}}}\n}}}\n\nImmediately after the `{{{` or on the line just below, \nadd `#!` followed by the \'\'processor name\'\'.\n\n{{{\n{{{\n#!processorname\nThe lines\nthat should be processed...\n}}}\n}}}\n\nThis is the \"shebang\" notation, familiar to most UNIX users.\n\nBesides their content, some Wiki processors can also accept \'\'parameters\'\',\nwhich are then given as `key=value` pairs after the processor name, \non the same line. If `value` has to contain space, as it\'s often the case for\nthe style parameter, a quoted string can be used (`key=\"value with space\"`).\n\nAs some processors are meant to process Wiki markup, it\'s quite possible to\n\'\'nest\'\' processor blocks.\nYou may want to indent the content of nested blocks for increased clarity,\nthis extra indentation will be ignored when processing the content.\n\n\n== Examples ==\n\n||= Wiki Markup =||= Display =||\n{{{#!td colspan=2 align=center style=\"border: none\"\n\n                __Example 1__: Inserting raw HTML\n}}}\n|-----------------------------------------------------------------\n{{{#!td style=\"border: none\"\n{{{\n{{{\n<h1 style=\"color: grey\">This is raw HTML</h1>\n}}}\n}}}\n}}}\n{{{#!td valign=top style=\"border: none; padding-left: 2em\"\n{{{\n#!html\n<h1 style=\"color: grey\">This is raw HTML</h1>\n}}}\n}}}\n|-----------------------------------------------------------------\n{{{#!td colspan=2 align=center style=\"border: none\"\n\n     __Example 2__: Highlighted Python code in a <div> block with custom style\n}}}\n|-----------------------------------------------------------------\n{{{#!td style=\"border: none\"\n  {{{\n  {{{#!div style=\"background: #ffd; border: 3px ridge\"\n\n  This is an example of embedded \"code\" block:\n\n    {{{\n    #!python\n    def hello():\n        return \"world\"\n    }}}\n\n  }}}\n  }}}\n}}}\n{{{#!td valign=top style=\"border: none; padding: 1em\"\n  {{{#!div style=\"background: #ffd; border: 3px ridge\"\n\n  This is an example of embedded \"code\" block:\n\n    {{{\n    #!python\n    def hello():\n        return \"world\"\n    }}}\n\n  }}}\n}}}\n|-----------------------------------------------------------------\n{{{#!td colspan=2 align=center style=\"border: none\"\n\n     __Example 3__: Searching tickets from a wiki page, by keywords.\n}}}\n|-----------------------------------------------------------------\n{{{#!td style=\"border: none\"\n  {{{\n  {{{\n  #!html\n  <form action=\"/query\" method=\"get\">\n  <input type=\"text\" name=\"keywords\" value=\"~\" size=\"30\">\n  <input type=\"submit\" value=\"Search by Keywords\">\n  <!-- To control what fields show up use hidden fields\n  <input type=\"hidden\" name=\"col\" value=\"id\">\n  <input type=\"hidden\" name=\"col\" value=\"summary\">\n  <input type=\"hidden\" name=\"col\" value=\"status\">\n  <input type=\"hidden\" name=\"col\" value=\"milestone\">\n  <input type=\"hidden\" name=\"col\" value=\"version\">\n  <input type=\"hidden\" name=\"col\" value=\"owner\">\n  <input type=\"hidden\" name=\"col\" value=\"priority\">\n  <input type=\"hidden\" name=\"col\" value=\"component\">\n  -->\n  </form>\n  }}}\n  }}}\n}}}\n{{{#!td valign=top style=\"border: none; padding: 1em\"\n  {{{\n  #!html\n  <form action=\"/query\" method=\"get\">\n  <input type=\"text\" name=\"keywords\" value=\"~\" size=\"30\">\n  <input type=\"submit\" value=\"Search by Keywords\">\n  <!-- To control what fields show up use hidden fields\n  <input type=\"hidden\" name=\"col\" value=\"id\">\n  <input type=\"hidden\" name=\"col\" value=\"summary\">\n  <input type=\"hidden\" name=\"col\" value=\"status\">\n  <input type=\"hidden\" name=\"col\" value=\"milestone\">\n  <input type=\"hidden\" name=\"col\" value=\"version\">\n  <input type=\"hidden\" name=\"col\" value=\"owner\">\n  <input type=\"hidden\" name=\"col\" value=\"priority\">\n  <input type=\"hidden\" name=\"col\" value=\"component\">\n  -->\n  </form>\n  }}}\n}}}\n== Available Processors ==\n\nThe following processors are included in the Trac distribution:\n\n `#!default` :: Present the text verbatim in a preformatted text block. \n                This is the same as specifying \'\'no\'\' processor name\n                (and no `#!`)\n `#!comment` :: Do not process the text in this section (i.e. contents exist\n                only in the plain text - not in the rendered page).\n\n=== HTML related ===\n\n `#!html`        :: Insert custom HTML in a wiki page.\n `#!htmlcomment` :: Insert an HTML comment in a wiki page (\'\'since 0.12\'\').\n\nNote that `#!html` blocks have to be \'\'self-contained\'\',\ni.e. you can\'t start an HTML element in one block and close it later in a second block. Use the following processors for achieving a similar effect. \n\n  `#!div` :: Wrap an arbitrary Wiki content inside a <div> element\n             (\'\'since 0.11\'\').\n `#!span` :: Wrap an arbitrary Wiki content inside a <span> element \n             (\'\'since 0.11\'\'). \n\n `#!td` :: Wrap an arbitrary Wiki content inside a <td> element (\'\'since 0.12\'\')\n `#!th` :: Wrap an arbitrary Wiki content inside a <th> element (\'\'since 0.12\'\') \n `#!tr` :: Can optionally be used for wrapping `#!td` and `#!th` blocks,\n       either for specifying row attributes of better visual grouping\n       (\'\'since 0.12\'\')\n\nSee WikiHtml for example usage and more details about these processors.\n\n=== Other Markups ===\n\n     `#!rst` :: Trac support for Restructured Text. See WikiRestructuredText.\n `#!textile` :: Supported if [http://cheeseshop.python.org/pypi/textile Textile] \n                is installed. \n                See [http://www.textism.com/tools/textile/ a Textile reference].\n\n\n=== Code Highlighting Support ===\n\nTrac includes processors to provide inline syntax highlighting:\n `#!c` (C), `#!cpp` (C++), `#!python` (Python), `#!perl` (Perl), \n `#!ruby` (Ruby), `#!php` (PHP), `#!asp` (ASP), `#!java` (Java), \n `#!js` (Javascript), `#!sql (SQL)`, `#!xml` (XML or HTML),\n `#!sh` (!Bourne/Bash shell), etc.\n\nTrac relies on external software packages for syntax coloring,\nlike [http://pygments.org Pygments]. \n\nSee TracSyntaxColoring for information about which languages\nare supported and how to enable support for more languages.\n\nNote also that by using the MIME type as processor, it is possible to syntax-highlight the same languages that are supported when browsing source code. For example, you can write:\n{{{\n{{{\n#!text/html\n<h1>text</h1>\n}}}\n}}}\n\nThe result will be syntax highlighted HTML code:\n{{{\n#!text/html\n<h1>text</h1>\n}}}\n\nThe same is valid for all other [TracSyntaxColoring#SyntaxColoringSupport mime types supported].\n\n\nFor more processor macros developed and/or contributed by users, visit: \n * [trac:ProcessorBazaar]\n * [trac:MacroBazaar]\n * [th:WikiStart Trac Hacks] community site\n\nDeveloping processors is no different from Wiki macros. \nIn fact they work the same way, only the usage syntax differs. \nSee WikiMacros#DevelopingCustomMacros for more information.\n\n\n----\nSee also: WikiMacros, WikiHtml, WikiRestructuredText, TracSyntaxColoring, WikiFormatting, TracGuide\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiRestructuredText',1,1327389819647871,'trac','127.0.0.1','= reStructuredText Support in Trac =\n\nTrac supports using \'\'reStructuredText\'\' (RST) as an alternative to wiki markup in any context WikiFormatting is used.\n\nFrom the reStucturedText webpage:\n \"\'\'reStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax and parser   system. It is useful for in-line program documentation (such as Python docstrings), for quickly creating  simple web pages, and for standalone documents. reStructuredText is designed for extensibility for  specific application domains. \'\'\"\n\nIf you want a file from your Subversion repository be displayed as reStructuredText in Trac\'s source browser, set `text/x-rst` as value for the Subversion property `svn:mime-type`. See [trac:source:/trunk/INSTALL this example].\n\n=== Requirements ===\nNote that to activate RST support in Trac, the python docutils package must be installed. \nIf not already available on your operating system, you can download it at the [http://docutils.sourceforge.net/rst.html RST Website].\n\nInstall docutils using `easy_install docutils`. Do not use the package manager of your OS (e.g. `apt-get install python-docutils`), because Trac will not find docutils then.\n\n=== More information on RST ===\n\n * reStructuredText Website -- http://docutils.sourceforge.net/rst.html\n * RST Quick Reference -- http://docutils.sourceforge.net/docs/rst/quickref.html\n\n----\n\n== Using RST in Trac ==\nTo specify that a block of text should be parsed using RST, use the \'\'rst\'\' processor. \n\n=== TracLinks in reStructuredText ===\n\n * Trac provides a custom RST directive `trac::` to allow TracLinks from within RST text.\n\n Example:\n {{{\n {{{\n #!rst\n This is a reference to |a ticket|\n\n .. |a ticket| trac:: #42\n }}}\n }}}\n\n * Trac allows an even easier way of creating TracLinks in RST, using the custom `:trac:` role.\n\n Example:\n {{{\n {{{\n #!rst\n This is a reference to ticket `#12`:trac:\n\n To learn how to use Trac, see `TracGuide`:trac:\n }}}\n }}}\n\n For a complete example of all uses of the `:trac:` role, please see WikiRestructuredTextLinks. \n\n\n=== Syntax highlighting in reStructuredText ===\n\nThere is a directive for doing TracSyntaxColoring in RST as well. The directive is called\ncode-block\n\nExample\n\n{{{\n{{{\n#!rst\n\n.. code-block:: python\n\n class Test:\n\n    def TestFunction(self):\n        pass\n\n}}}\n}}}\n\nWill result in the below.\n\n{{{\n#!rst\n\n.. code-block:: python\n\n class Test:\n\n    def TestFunction(self):\n        pass\n\n}}}\n\n=== Wiki Macros in reStructuredText ===\n\nFor doing [WikiMacros Wiki Macros] in RST you use the same directive as for syntax highlighting i.e code-block.\n\n=== Wiki Macro Example ===\n\n{{{\n{{{\n#!rst\n\n.. code-block:: RecentChanges\n\n   Trac,3\n\n}}}\n}}}\n\nWill result in the below:\n\n     [[RecentChanges(Trac,3)]]\n\nOr a more concise Wiki Macro like syntax is also available:\n\n{{{\n{{{\n#!rst\n\n:code-block:`RecentChanges:Trac,3`\n}}}\n}}}\n\n=== Bigger RST Example ===\nThe example below should be mostly self-explanatory:\n{{{\n#!html\n<pre class=\"wiki\">{{{\n#!rst\nFooBar Header\n=============\nreStructuredText is **nice**. It has its own webpage_.\n\nA table:\n\n=====  =====  ======\n   Inputs     Output\n------------  ------\n  A      B    A or B\n=====  =====  ======\nFalse  False  False\nTrue   False  True\nFalse  True   True\nTrue   True   True\n=====  =====  ======\n\nRST TracLinks\n-------------\n\nSee also ticket `#42`:trac:.\n\n.. _webpage: http://docutils.sourceforge.net/rst.html\n}}}</pre>\n}}}\n\n\nResults in:\n{{{\n#!rst\nFooBar Header\n=============\nreStructuredText is **nice**. It has its own webpage_.\n\nA table:\n\n=====  =====  ======\n   Inputs     Output\n------------  ------\n  A      B    A or B\n=====  =====  ======\nFalse  False  False\nTrue   False  True\nFalse  True   True\nTrue   True   True\n=====  =====  ======\n\nRST TracLinks\n-------------\n\nSee also ticket `#42`:trac:.\n\n.. _webpage: http://docutils.sourceforge.net/rst.html\n}}}\n\n\n----\nSee also: WikiRestructuredTextLinks, WikiProcessors, WikiFormatting\n',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiRestructuredTextLinks',1,1327389819647871,'trac','127.0.0.1','= TracLinks in reStructuredText =\n\nThis document illustrates how to use the `:trac:` role in reStructuredText. The page is written like:\n\n{{{\n{{{\n#!rst \nExamples:\n\n * Tickets: :trac:`#1` or :trac:`ticket:1`\n * Ticket comments: :trac:`comment:ticket:1:2`\n * Reports: :trac:`{1}` or :trac:`report:1`\n * Changesets: :trac:`r1`, :trac:`[1]` or :trac:`changeset:1`\n * Revision log: :trac:`r1:3`, :trac:`[1:3]` or :trac:`log:@1:3`, :trac:`log:trunk@1:3`\n * Diffs (since version 0.10): :trac:`diff:@20:30`, :trac:`diff:tags/trac-0.9.2/wiki-default//tags/trac-0.9.3/wiki-default` or :trac:`diff:trunk/trac@3538//sandbox/vc-refactoring/trac@3539`\n * Wiki pages: :trac:`CamelCase` or :trac:`wiki:CamelCase`\n * Milestones: :trac:`milestone:1.0`\n * Attachment: :trac:`attachment:ticket:944:attachment.1073.diff`\n * Files: :trac:`source:trunk/COPYING`\n * A specific file revision: :trac:`source:/trunk/COPYING@200`\n * A particular line of a specific file revision: :trac:`source:/trunk/COPYING@200#L25`\n\nAn explicit label can be specified, separated from the link by a space:\n\n * See :trac:`#1 ticket 1` and the :trac:`source:trunk/COPYING license`.\n}}}\n}}}\n\nProvided you have docutils installed, the above block will render as:\n----\n{{{\n#!rst \nExamples:\n\n * Tickets: :trac:`#1` or :trac:`ticket:1`\n * Ticket comments: :trac:`comment:ticket:1:2`\n * Reports: :trac:`{1}` or :trac:`report:1`\n * Changesets: :trac:`r1`, :trac:`[1]` or :trac:`changeset:1`\n * Revision log: :trac:`r1:3`, :trac:`[1:3]` or :trac:`log:@1:3`, :trac:`log:trunk@1:3`\n * Diffs (since version 0.10): :trac:`diff:@20:30`, :trac:`diff:tags/trac-0.9.2/wiki-default//tags/trac-0.9.3/wiki-default` or :trac:`diff:trunk/trac@3538//sandbox/vc-refactoring/trac@3539`\n * Wiki pages: :trac:`CamelCase` or :trac:`wiki:CamelCase`\n * Milestones: :trac:`milestone:1.0`\n * Attachment: :trac:`attachment:ticket:944:attachment.1073.diff`\n * Files: :trac:`source:trunk/COPYING`\n * A specific file revision: :trac:`source:/trunk/COPYING@200`\n * A particular line of a specific file revision: :trac:`source:/trunk/COPYING@200#L25`\n\nAn explicit label can be specified, separated from the link by a space:\n\n * See :trac:`#1 ticket 1` and the :trac:`source:trunk/COPYING license`.\n}}}\n----\n\nNote also that any of the above could have been written using substitution references and the `trac::` directive:\n{{{\n{{{\n#!rst\nSee |ticket123|.\n\n .. |ticket123| trac:: ticket:123 this ticket\n}}}\n}}}\n\nThis renders as:\n----\n\n{{{\n#!rst\nSee |ticket123|.\n\n .. |ticket123| trac:: ticket:123 this ticket\n}}}\n\n----\nSee also: WikiRestructuredText, TracLinks',NULL,NULL);
INSERT INTO `wiki` VALUES ('WikiStart',1,1327389819647871,'trac','127.0.0.1','\n[[WelcomeText()]]\nThis is your project wiki start page. We created this page to help you get started, now just press the \"Edit this page\" button below to start editing this page.\n\n== Getting started ==\nHere is a list of things you probably want to do when starting a project\n * Use [/admin/permissions/groups Admin|Permissions] to give rights for your project team\n   - If you flagged your project as public (default) anyone can visit your project, but only registered users to Developer Nokia can write messages in your discussion boards and open tickets.\n   - If you flagged the project as private, then you should start adding some new members that can access your project and work with you.\n   - Either way, you can add \'\'project members\'\' that will have write access to your project and can start pushing software in the SCM.\n   - If the default groups are not enough for you, you can add more.\n * Tailor your ticketing system to have types and resolutions suitable for your project in [/admin/ticket Admin|Ticket System]\n   - Defaults usually work fine, but it\'s good to be aware of the possibility to make changes\n   - You can also [/admin/ticket/milestones define a roadmap] in the ticket system panel with milestones\n* Last but not least, create your SummaryPage to show more information about your project, embed images and videos and deep link to your code or documentation\n* Want to know more? Check out the [//developer.nokia.com/Community/Projects/HelpAndSupport/wiki Help and Support] pages\n\n== Project information ==\n\n  * Project name: [[ProjectName()]]\n  * Project identifier: [[ProjectIdentifier()]]\n  * Owner: [[ProjectOwner()]]\n  * Create date: [[ProjectCreateDate()]]\n  * Project url: [[ProjectUrl()]]\n  * Version control: [[ProjectVersioncontrolUrl()]]\n  * Project (WebDAV) shared folder: [[ProjectWebDavUrl()]]\n  * Downloads: [wiki:Downloads]\n\n== Release downloads ==\n[[FeaturedDownloads()]]\n',NULL,NULL);
/*!40000 ALTER TABLE `wiki` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'home'
--

--
-- Current Database: `trac_admin`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `trac_admin` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;

USE `trac_admin`;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `action` (
  `action_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `action_string` varchar(32) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`action_id`) USING BTREE,
  UNIQUE KEY `action_string` (`action_string`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `action`
--
-- ORDER BY:  `action_id`

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
INSERT INTO `action` VALUES (87,'ATTACHMENT_CREATE');
INSERT INTO `action` VALUES (88,'BROWSER_VIEW');
INSERT INTO `action` VALUES (89,'CHANGESET_VIEW');
INSERT INTO `action` VALUES (90,'CREATE');
INSERT INTO `action` VALUES (91,'DELETE');
INSERT INTO `action` VALUES (93,'EMAIL_VIEW');
INSERT INTO `action` VALUES (94,'FILE_VIEW');
INSERT INTO `action` VALUES (95,'LOG_VIEW');
INSERT INTO `action` VALUES (96,'MILESTONE_ADMIN');
INSERT INTO `action` VALUES (97,'MILESTONE_CREATE');
INSERT INTO `action` VALUES (98,'MILESTONE_DELETE');
INSERT INTO `action` VALUES (99,'MILESTONE_MODIFY');
INSERT INTO `action` VALUES (100,'MILESTONE_VIEW');
INSERT INTO `action` VALUES (101,'MODIFY');
INSERT INTO `action` VALUES (102,'PERMISSION_ADMIN');
INSERT INTO `action` VALUES (103,'PERMISSION_GRANT');
INSERT INTO `action` VALUES (104,'PERMISSION_REVOKE');
INSERT INTO `action` VALUES (105,'ROADMAP_ADMIN');
INSERT INTO `action` VALUES (106,'ROADMAP_VIEW');
INSERT INTO `action` VALUES (107,'SEARCH_VIEW');
INSERT INTO `action` VALUES (108,'TEAM_VIEW');
INSERT INTO `action` VALUES (109,'TICKET_ADMIN');
INSERT INTO `action` VALUES (110,'TICKET_APPEND');
INSERT INTO `action` VALUES (111,'TICKET_BATCH_MODIFY');
INSERT INTO `action` VALUES (112,'TICKET_CHGPROP');
INSERT INTO `action` VALUES (113,'TICKET_CREATE');
INSERT INTO `action` VALUES (114,'TICKET_EDIT_CC');
INSERT INTO `action` VALUES (115,'TICKET_EDIT_DESCRIPTION');
INSERT INTO `action` VALUES (116,'TICKET_MODIFY');
INSERT INTO `action` VALUES (117,'TICKET_VIEW');
INSERT INTO `action` VALUES (118,'TIMELINE_VIEW');
INSERT INTO `action` VALUES (119,'TRAC_ADMIN');
INSERT INTO `action` VALUES (120,'VERSION_CONTROL');
INSERT INTO `action` VALUES (121,'VERSION_CONTROL_VIEW');
INSERT INTO `action` VALUES (122,'VIEW');
INSERT INTO `action` VALUES (123,'WEBDAV');
INSERT INTO `action` VALUES (124,'WIKI_ADMIN');
INSERT INTO `action` VALUES (125,'WIKI_CREATE');
INSERT INTO `action` VALUES (126,'WIKI_DELETE');
INSERT INTO `action` VALUES (127,'WIKI_MODIFY');
INSERT INTO `action` VALUES (128,'WIKI_VIEW');
INSERT INTO `action` VALUES (129,'XML_RPC');
INSERT INTO `action` VALUES (130,'DISCUSSION_ATTACH');
INSERT INTO `action` VALUES (131,'DISCUSSION_ADMIN');
INSERT INTO `action` VALUES (132,'DISCUSSION_APPEND');
INSERT INTO `action` VALUES (133,'DISCUSSION_MODERATE');
INSERT INTO `action` VALUES (134,'DISCUSSION_VIEW');
INSERT INTO `action` VALUES (135,'SUMMARY_VIEW');
INSERT INTO `action` VALUES (136,'WEBDAV_VIEW');
INSERT INTO `action` VALUES (137,'TICKET_EDIT_COMMENT');
INSERT INTO `action` VALUES (138,'ALLOW_REQUEST_MEMBERSHIP');
INSERT INTO `action` VALUES (139,'PRIVATE_SUMMARY_VIEW');
INSERT INTO `action` VALUES (140,'REPORT_VIEW');
INSERT INTO `action` VALUES (141,'REPORT_MODIFY');
INSERT INTO `action` VALUES (142,'REPORT_DELETE');
INSERT INTO `action` VALUES (143,'REPORT_ADMIN');
INSERT INTO `action` VALUES (144,'CONFIG_VIEW');
INSERT INTO `action` VALUES (145,'DOWNLOADS_VIEW');
INSERT INTO `action` VALUES (146,'DOWNLOADS_ADMIN');
INSERT INTO `action` VALUES (147,'WIKI_RENAME');
INSERT INTO `action` VALUES (148,'DOWNLOADS_ADD');
INSERT INTO `action` VALUES (149,'DISCUSSION_ANNOUNCEAPPEND');
INSERT INTO `action` VALUES (150,'WELCOME_VIEW');
INSERT INTO `action` VALUES (151,'CREATE_PROJECT');
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_cookie`
--

DROP TABLE IF EXISTS `auth_cookie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_cookie` (
  `cookie` text COLLATE utf8_bin NOT NULL,
  `name` text COLLATE utf8_bin NOT NULL,
  `ipnr` text COLLATE utf8_bin NOT NULL,
  `time` int(11) DEFAULT NULL,
  PRIMARY KEY (`cookie`(111),`ipnr`(111),`name`(111))
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_cookie`
--
-- ORDER BY:  `cookie`,`ipnr`,`name`

LOCK TABLES `auth_cookie` WRITE;
/*!40000 ALTER TABLE `auth_cookie` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_cookie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authentication`
--

DROP TABLE IF EXISTS `authentication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authentication` (
  `id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT COMMENT 'TINYINT allows only 256 authentication types',
  `method` varchar(32) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_method` (`method`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authentication`
--
-- ORDER BY:  `id`

LOCK TABLES `authentication` WRITE;
/*!40000 ALTER TABLE `authentication` DISABLE KEYS */;
INSERT INTO `authentication` VALUES (5,'LocalDB');
/*!40000 ALTER TABLE `authentication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `category_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `category_name` varchar(64) COLLATE utf8_bin NOT NULL,
  `description` varchar(256) COLLATE utf8_bin NOT NULL,
  `parent_id` smallint(5) unsigned DEFAULT NULL,
  `context_id` tinyint(4) unsigned NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `cat` (`category_name`),
  KEY `categories_fk_parent` (`parent_id`),
  KEY `categories_fk_contexts` (`context_id`),
  CONSTRAINT `categories_fk_contexts` FOREIGN KEY (`context_id`) REFERENCES `contexts` (`context_id`),
  CONSTRAINT `categories_fk_parent` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=306 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Categories';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--
-- ORDER BY:  `category_id`

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (29,'GPL 2.0','GNU General Public License 2.0',NULL,3);
INSERT INTO `categories` VALUES (30,'LGPL 2.1','GNU Lesser General Public License 2.1',NULL,3);
INSERT INTO `categories` VALUES (33,'GPL 3.0','GNU General Public License 3.0',NULL,3);
INSERT INTO `categories` VALUES (34,'Apache License','Apache License',NULL,3);
INSERT INTO `categories` VALUES (35,'MIT License','MIT License',NULL,3);
INSERT INTO `categories` VALUES (38,'Mozilla Public License 1.1 (MPL)','Mozilla Public License',NULL,3);
INSERT INTO `categories` VALUES (40,'Eclipse Public License','Eclipse Public License',NULL,3);
INSERT INTO `categories` VALUES (41,'LGPL 3.0','GNU Lesser General Public License 3.0',NULL,3);
INSERT INTO `categories` VALUES (44,'CDDL','Common Development and Distribution License',NULL,3);
INSERT INTO `categories` VALUES (48,'Proprietary','Proprietary',NULL,3);
INSERT INTO `categories` VALUES (55,'Planning','Planning',NULL,6);
INSERT INTO `categories` VALUES (56,'Development','Development',NULL,6);
INSERT INTO `categories` VALUES (57,'Alpha','Alpha',NULL,6);
INSERT INTO `categories` VALUES (58,'Beta','Beta',NULL,6);
INSERT INTO `categories` VALUES (59,'Release','Release',NULL,6);
INSERT INTO `categories` VALUES (60,'Abkhaz','ab',NULL,4);
INSERT INTO `categories` VALUES (61,'Afar','aa',NULL,4);
INSERT INTO `categories` VALUES (62,'Afrikaans','af',NULL,4);
INSERT INTO `categories` VALUES (63,'Akan','ak',NULL,4);
INSERT INTO `categories` VALUES (64,'Albanian','sq',NULL,4);
INSERT INTO `categories` VALUES (65,'Amharic','am',NULL,4);
INSERT INTO `categories` VALUES (66,'Arabic','ar',NULL,4);
INSERT INTO `categories` VALUES (67,'Aragonese','an',NULL,4);
INSERT INTO `categories` VALUES (68,'Armenian','hy',NULL,4);
INSERT INTO `categories` VALUES (69,'Assamese','as',NULL,4);
INSERT INTO `categories` VALUES (70,'Avaric','av',NULL,4);
INSERT INTO `categories` VALUES (71,'Avestan','ae',NULL,4);
INSERT INTO `categories` VALUES (72,'Aymara','ay',NULL,4);
INSERT INTO `categories` VALUES (73,'Azerbaijani','az',NULL,4);
INSERT INTO `categories` VALUES (74,'Bambara','bm',NULL,4);
INSERT INTO `categories` VALUES (75,'Bashkir','ba',NULL,4);
INSERT INTO `categories` VALUES (76,'Basque','eu',NULL,4);
INSERT INTO `categories` VALUES (77,'Belarusian','be',NULL,4);
INSERT INTO `categories` VALUES (78,'Bengali','bn',NULL,4);
INSERT INTO `categories` VALUES (79,'Bihari','bh',NULL,4);
INSERT INTO `categories` VALUES (80,'Bislama','bi',NULL,4);
INSERT INTO `categories` VALUES (81,'Bosnian','bs',NULL,4);
INSERT INTO `categories` VALUES (82,'Breton','br',NULL,4);
INSERT INTO `categories` VALUES (83,'Bulgarian','bg',NULL,4);
INSERT INTO `categories` VALUES (84,'Burmese','my',NULL,4);
INSERT INTO `categories` VALUES (85,'Catalan','ca',NULL,4);
INSERT INTO `categories` VALUES (86,'Chamorro','ch',NULL,4);
INSERT INTO `categories` VALUES (87,'Chechen','ce',NULL,4);
INSERT INTO `categories` VALUES (88,'Nyanja','ny',NULL,4);
INSERT INTO `categories` VALUES (89,'Chinese','zh',NULL,4);
INSERT INTO `categories` VALUES (90,'Chuvash','cv',NULL,4);
INSERT INTO `categories` VALUES (91,'Cornish','kw',NULL,4);
INSERT INTO `categories` VALUES (92,'Corsican','co',NULL,4);
INSERT INTO `categories` VALUES (93,'Cree','cr',NULL,4);
INSERT INTO `categories` VALUES (94,'Croatian','hr',NULL,4);
INSERT INTO `categories` VALUES (95,'Czech','cs',NULL,4);
INSERT INTO `categories` VALUES (96,'Danish','da',NULL,4);
INSERT INTO `categories` VALUES (97,'Divehi','dv',NULL,4);
INSERT INTO `categories` VALUES (98,'Dutch','nl',NULL,4);
INSERT INTO `categories` VALUES (99,'Dzongkha','dz',NULL,4);
INSERT INTO `categories` VALUES (100,'English','en',NULL,4);
INSERT INTO `categories` VALUES (101,'Esperanto','eo',NULL,4);
INSERT INTO `categories` VALUES (102,'Estonian','et',NULL,4);
INSERT INTO `categories` VALUES (103,'Ewe','ee',NULL,4);
INSERT INTO `categories` VALUES (104,'Faroese','fo',NULL,4);
INSERT INTO `categories` VALUES (105,'Fijian','fj',NULL,4);
INSERT INTO `categories` VALUES (106,'Finnish','fi',NULL,4);
INSERT INTO `categories` VALUES (107,'French','fr',NULL,4);
INSERT INTO `categories` VALUES (108,'Fulah','ff',NULL,4);
INSERT INTO `categories` VALUES (109,'Galician','gl',NULL,4);
INSERT INTO `categories` VALUES (110,'Georgian','ka',NULL,4);
INSERT INTO `categories` VALUES (111,'German','de',NULL,4);
INSERT INTO `categories` VALUES (112,'Greek','el',NULL,4);
INSERT INTO `categories` VALUES (113,'Gujarati','gu',NULL,4);
INSERT INTO `categories` VALUES (114,'Haitian','ht',NULL,4);
INSERT INTO `categories` VALUES (115,'Hausa','ha',NULL,4);
INSERT INTO `categories` VALUES (116,'Hebrew','he',NULL,4);
INSERT INTO `categories` VALUES (117,'Herero','hz',NULL,4);
INSERT INTO `categories` VALUES (118,'Hindi','hi',NULL,4);
INSERT INTO `categories` VALUES (119,'Hiri Motu','ho',NULL,4);
INSERT INTO `categories` VALUES (120,'Hungarian','hu',NULL,4);
INSERT INTO `categories` VALUES (121,'Interlingua','ia',NULL,4);
INSERT INTO `categories` VALUES (122,'Indonesian','id',NULL,4);
INSERT INTO `categories` VALUES (123,'Interlingue','ie',NULL,4);
INSERT INTO `categories` VALUES (124,'Irish','ga',NULL,4);
INSERT INTO `categories` VALUES (125,'Igbo','ig',NULL,4);
INSERT INTO `categories` VALUES (126,'Inupiaq','ik',NULL,4);
INSERT INTO `categories` VALUES (127,'Ido','io',NULL,4);
INSERT INTO `categories` VALUES (128,'Icelandic','is',NULL,4);
INSERT INTO `categories` VALUES (129,'Italian','it',NULL,4);
INSERT INTO `categories` VALUES (130,'Inuktitut','iu',NULL,4);
INSERT INTO `categories` VALUES (131,'Japanese','ja',NULL,4);
INSERT INTO `categories` VALUES (132,'Javanese','jv',NULL,4);
INSERT INTO `categories` VALUES (133,'Kalaallisut','kl',NULL,4);
INSERT INTO `categories` VALUES (134,'Kannada','kn',NULL,4);
INSERT INTO `categories` VALUES (135,'Kanuri','kr',NULL,4);
INSERT INTO `categories` VALUES (136,'Kashmiri','ks',NULL,4);
INSERT INTO `categories` VALUES (137,'Kazakh','kk',NULL,4);
INSERT INTO `categories` VALUES (138,'Khmer','km',NULL,4);
INSERT INTO `categories` VALUES (139,'Kikuyu','ki',NULL,4);
INSERT INTO `categories` VALUES (140,'Kinyarwanda','rw',NULL,4);
INSERT INTO `categories` VALUES (141,'Kyrgyz','ky',NULL,4);
INSERT INTO `categories` VALUES (142,'Komi','kv',NULL,4);
INSERT INTO `categories` VALUES (143,'Kongo','kg',NULL,4);
INSERT INTO `categories` VALUES (144,'Korean','ko',NULL,4);
INSERT INTO `categories` VALUES (145,'Kurdish','ku',NULL,4);
INSERT INTO `categories` VALUES (146,'Kwanyama','kj',NULL,4);
INSERT INTO `categories` VALUES (147,'Latin','la',NULL,4);
INSERT INTO `categories` VALUES (148,'Luxembourgish','lb',NULL,4);
INSERT INTO `categories` VALUES (149,'Luganda','lg',NULL,4);
INSERT INTO `categories` VALUES (150,'Limburgish','li',NULL,4);
INSERT INTO `categories` VALUES (151,'Lingala','ln',NULL,4);
INSERT INTO `categories` VALUES (152,'Lao','lo',NULL,4);
INSERT INTO `categories` VALUES (153,'Lithuanian','lt',NULL,4);
INSERT INTO `categories` VALUES (154,'Luba-Katanga','lu',NULL,4);
INSERT INTO `categories` VALUES (155,'Latvian','lv',NULL,4);
INSERT INTO `categories` VALUES (156,'Manx','gv',NULL,4);
INSERT INTO `categories` VALUES (157,'Macedonian','mk',NULL,4);
INSERT INTO `categories` VALUES (158,'Malagasy','mg',NULL,4);
INSERT INTO `categories` VALUES (159,'Malay','ms',NULL,4);
INSERT INTO `categories` VALUES (160,'Malayalam','ml',NULL,4);
INSERT INTO `categories` VALUES (161,'Maltese','mt',NULL,4);
INSERT INTO `categories` VALUES (162,'Marathi','mr',NULL,4);
INSERT INTO `categories` VALUES (163,'Marshallese','mh',NULL,4);
INSERT INTO `categories` VALUES (164,'Mongolian','mn',NULL,4);
INSERT INTO `categories` VALUES (165,'Nauru','na',NULL,4);
INSERT INTO `categories` VALUES (166,'Navajo','nv',NULL,4);
INSERT INTO `categories` VALUES (167,'North Ndebele','nd',NULL,4);
INSERT INTO `categories` VALUES (168,'Nepali','ne',NULL,4);
INSERT INTO `categories` VALUES (169,'Ndonga','ng',NULL,4);
INSERT INTO `categories` VALUES (170,'Norwegian Nynorsk','nn',NULL,4);
INSERT INTO `categories` VALUES (171,'Norwegian','no',NULL,4);
INSERT INTO `categories` VALUES (172,'Nuosu','ii',NULL,4);
INSERT INTO `categories` VALUES (173,'South Ndebele','nr',NULL,4);
INSERT INTO `categories` VALUES (174,'Occitan','oc',NULL,4);
INSERT INTO `categories` VALUES (175,'Ojibwa','oj',NULL,4);
INSERT INTO `categories` VALUES (176,'Old Church Slavonic','cu',NULL,4);
INSERT INTO `categories` VALUES (177,'Oromo','om',NULL,4);
INSERT INTO `categories` VALUES (178,'Oriya','or',NULL,4);
INSERT INTO `categories` VALUES (179,'Ossetian','os',NULL,4);
INSERT INTO `categories` VALUES (180,'Panjabi','pa',NULL,4);
INSERT INTO `categories` VALUES (181,'Persian','fa',NULL,4);
INSERT INTO `categories` VALUES (182,'Polish','pl',NULL,4);
INSERT INTO `categories` VALUES (183,'Pashto','ps',NULL,4);
INSERT INTO `categories` VALUES (184,'Portuguese','pt',NULL,4);
INSERT INTO `categories` VALUES (185,'Quechua','qu',NULL,4);
INSERT INTO `categories` VALUES (186,'Romansh','rm',NULL,4);
INSERT INTO `categories` VALUES (187,'Kirundi','rn',NULL,4);
INSERT INTO `categories` VALUES (188,'Romanian','ro',NULL,4);
INSERT INTO `categories` VALUES (189,'Russian','ru',NULL,4);
INSERT INTO `categories` VALUES (190,'Sanskrit','sa',NULL,4);
INSERT INTO `categories` VALUES (191,'Sardinian','sc',NULL,4);
INSERT INTO `categories` VALUES (192,'Sindhi','sd',NULL,4);
INSERT INTO `categories` VALUES (193,'Northern Sami','se',NULL,4);
INSERT INTO `categories` VALUES (194,'Samoan','sm',NULL,4);
INSERT INTO `categories` VALUES (195,'Sango','sg',NULL,4);
INSERT INTO `categories` VALUES (196,'Serbian','sr',NULL,4);
INSERT INTO `categories` VALUES (197,'Scottish Gaelic','gd',NULL,4);
INSERT INTO `categories` VALUES (198,'Shona','sn',NULL,4);
INSERT INTO `categories` VALUES (199,'Sinhala','si',NULL,4);
INSERT INTO `categories` VALUES (200,'Slovak','sk',NULL,4);
INSERT INTO `categories` VALUES (201,'Slovene','sl',NULL,4);
INSERT INTO `categories` VALUES (202,'Somali','so',NULL,4);
INSERT INTO `categories` VALUES (203,'Southern Sotho','st',NULL,4);
INSERT INTO `categories` VALUES (204,'Spanish','es',NULL,4);
INSERT INTO `categories` VALUES (205,'Sundanese','su',NULL,4);
INSERT INTO `categories` VALUES (206,'Swahili','sw',NULL,4);
INSERT INTO `categories` VALUES (207,'Swati','ss',NULL,4);
INSERT INTO `categories` VALUES (208,'Swedish','sv',NULL,4);
INSERT INTO `categories` VALUES (209,'Tamil','ta',NULL,4);
INSERT INTO `categories` VALUES (210,'Telugu','te',NULL,4);
INSERT INTO `categories` VALUES (211,'Tajik','tg',NULL,4);
INSERT INTO `categories` VALUES (212,'Thai','th',NULL,4);
INSERT INTO `categories` VALUES (213,'Tigrinya','ti',NULL,4);
INSERT INTO `categories` VALUES (214,'Tibetan Standard','bo',NULL,4);
INSERT INTO `categories` VALUES (215,'Turkmen','tk',NULL,4);
INSERT INTO `categories` VALUES (216,'Tagalog','tl',NULL,4);
INSERT INTO `categories` VALUES (217,'Tswana','tn',NULL,4);
INSERT INTO `categories` VALUES (218,'Tonga','to',NULL,4);
INSERT INTO `categories` VALUES (219,'Turkish','tr',NULL,4);
INSERT INTO `categories` VALUES (220,'Tsonga','ts',NULL,4);
INSERT INTO `categories` VALUES (221,'Tatar','tt',NULL,4);
INSERT INTO `categories` VALUES (222,'Twi','tw',NULL,4);
INSERT INTO `categories` VALUES (223,'Tahitian','ty',NULL,4);
INSERT INTO `categories` VALUES (224,'Uighur','ug',NULL,4);
INSERT INTO `categories` VALUES (225,'Ukrainian','uk',NULL,4);
INSERT INTO `categories` VALUES (226,'Urdu','ur',NULL,4);
INSERT INTO `categories` VALUES (227,'Uzbek','uz',NULL,4);
INSERT INTO `categories` VALUES (228,'Venda','ve',NULL,4);
INSERT INTO `categories` VALUES (229,'Vietnamese','vi',NULL,4);
INSERT INTO `categories` VALUES (230,'Walloon','wa',NULL,4);
INSERT INTO `categories` VALUES (231,'Welsh','cy',NULL,4);
INSERT INTO `categories` VALUES (232,'Wolof','wo',NULL,4);
INSERT INTO `categories` VALUES (233,'Western Frisian','fy',NULL,4);
INSERT INTO `categories` VALUES (234,'Xhosa','xh',NULL,4);
INSERT INTO `categories` VALUES (235,'Yiddish','yi',NULL,4);
INSERT INTO `categories` VALUES (236,'Yoruba','yo',NULL,4);
INSERT INTO `categories` VALUES (237,'Zhuang','za',NULL,4);
INSERT INTO `categories` VALUES (238,'Zulu','zu',NULL,4);
INSERT INTO `categories` VALUES (267,'Python','http://sw.nokia.com/FN-1/Topic/python',NULL,1);
INSERT INTO `categories` VALUES (268,'Qt','http://sw.nokia.com/FN-1/Topic/qt',NULL,1);
INSERT INTO `categories` VALUES (271,'Qt Mobility','http://sw.nokia.com/FN-1/Topic/qt_mobility',268,1);
INSERT INTO `categories` VALUES (272,'Qt Quick','http://sw.nokia.com/FN-1/Topic/qt_quick',268,1);
INSERT INTO `categories` VALUES (281,'UI','http://sw.nokia.com/FN-1/Topic/ui',NULL,1);
INSERT INTO `categories` VALUES (283,'Web','http://sw.nokia.com/FN-1/Topic/web_technology',NULL,1);
INSERT INTO `categories` VALUES (290,'Linux','Linux',NULL,8);
INSERT INTO `categories` VALUES (304,'AGPL 3','AGPL 3',NULL,3);
INSERT INTO `categories` VALUES (305,'New BSD','New BSD',NULL,3);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contexts`
--

DROP TABLE IF EXISTS `contexts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contexts` (
  `context_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `context_name` varchar(63) COLLATE utf8_bin NOT NULL,
  `context_description` varchar(255) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`context_id`),
  UNIQUE KEY `contx` (`context_name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Contexes that categories can belong to';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contexts`
--
-- ORDER BY:  `context_id`

LOCK TABLES `contexts` WRITE;
/*!40000 ALTER TABLE `contexts` DISABLE KEYS */;
INSERT INTO `contexts` VALUES (1,'Categories','Forum Nokia Core+Community Topics');
INSERT INTO `contexts` VALUES (3,'License','Licenses that product will be distributed with');
INSERT INTO `contexts` VALUES (4,'Natural language','Main language used in project web content');
INSERT INTO `contexts` VALUES (6,'Development status','Project maturity');
INSERT INTO `contexts` VALUES (8,'Custom','Custom');
/*!40000 ALTER TABLE `contexts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deny_dav_protocol`
--

DROP TABLE IF EXISTS `deny_dav_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deny_dav_protocol` (
  `project_key` int(10) unsigned NOT NULL,
  `protocol_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`project_key`,`protocol_key`),
  KEY `protocol_dav_proto_fk` (`protocol_key`),
  CONSTRAINT `project_dav_proto_fk` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `protocol_dav_proto_fk` FOREIGN KEY (`protocol_key`) REFERENCES `protocol` (`protocol_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table to list dav schemes that are not allowed for a project';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deny_dav_protocol`
--
-- ORDER BY:  `project_key`,`protocol_key`

LOCK TABLES `deny_dav_protocol` WRITE;
/*!40000 ALTER TABLE `deny_dav_protocol` DISABLE KEYS */;
/*!40000 ALTER TABLE `deny_dav_protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deny_scm_protocol`
--

DROP TABLE IF EXISTS `deny_scm_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deny_scm_protocol` (
  `project_key` int(10) unsigned NOT NULL,
  `protocol_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`project_key`,`protocol_key`),
  KEY `protocol_scm_proto_fk` (`protocol_key`),
  CONSTRAINT `project_scm_proto_fk` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `protocol_scm_proto_fk` FOREIGN KEY (`protocol_key`) REFERENCES `protocol` (`protocol_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table to list scm schemes that are not allowed for a project';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deny_scm_protocol`
--
-- ORDER BY:  `project_key`,`protocol_key`

LOCK TABLES `deny_scm_protocol` WRITE;
/*!40000 ALTER TABLE `deny_scm_protocol` DISABLE KEYS */;
/*!40000 ALTER TABLE `deny_scm_protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group` (
  `group_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `group_name` varchar(127) COLLATE utf8_bin NOT NULL,
  `trac_environment_key` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `project_group_name` (`trac_environment_key`,`group_name`(16)),
  KEY `project` (`trac_environment_key`),
  CONSTRAINT `fk_group_trac_env` FOREIGN KEY (`trac_environment_key`) REFERENCES `trac_environment` (`environment_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User groups';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--
-- ORDER BY:  `group_id`

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
INSERT INTO `group` VALUES (2,'trac_admin',677);
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_permission`
--

DROP TABLE IF EXISTS `group_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_permission` (
  `group_key` int(10) unsigned NOT NULL,
  `permission_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`group_key`,`permission_key`),
  KEY `permission` (`permission_key`),
  CONSTRAINT `gp_fk_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `gp_fk_permission` FOREIGN KEY (`permission_key`) REFERENCES `action` (`action_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Group permissions';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_permission`
--
-- ORDER BY:  `group_key`,`permission_key`

LOCK TABLES `group_permission` WRITE;
/*!40000 ALTER TABLE `group_permission` DISABLE KEYS */;
INSERT INTO `group_permission` VALUES (2,119);
/*!40000 ALTER TABLE `group_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_template`
--

DROP TABLE IF EXISTS `group_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_template` (
  `group_template_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `group_template_name` varchar(255) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`group_template_id`),
  UNIQUE KEY `name` (`group_template_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User group template';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_template`
--
-- ORDER BY:  `group_template_id`

LOCK TABLES `group_template` WRITE;
/*!40000 ALTER TABLE `group_template` DISABLE KEYS */;
INSERT INTO `group_template` VALUES (1,'Writers');
INSERT INTO `group_template` VALUES (2,'Readers');
/*!40000 ALTER TABLE `group_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_template_permission`
--

DROP TABLE IF EXISTS `group_template_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_template_permission` (
  `group_template_key` smallint(5) unsigned NOT NULL,
  `permission_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`group_template_key`,`permission_key`),
  KEY `fk_template_permissions` (`permission_key`),
  CONSTRAINT `fk_template_permissions` FOREIGN KEY (`permission_key`) REFERENCES `action` (`action_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_template_template` FOREIGN KEY (`group_template_key`) REFERENCES `group_template` (`group_template_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Permissions belonging for group templates';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_template_permission`
--
-- ORDER BY:  `group_template_key`,`permission_key`

LOCK TABLES `group_template_permission` WRITE;
/*!40000 ALTER TABLE `group_template_permission` DISABLE KEYS */;
INSERT INTO `group_template_permission` VALUES (1,91);
INSERT INTO `group_template_permission` VALUES (1,120);
INSERT INTO `group_template_permission` VALUES (1,123);
INSERT INTO `group_template_permission` VALUES (1,129);
INSERT INTO `group_template_permission` VALUES (2,121);
INSERT INTO `group_template_permission` VALUES (2,122);
INSERT INTO `group_template_permission` VALUES (2,129);
/*!40000 ALTER TABLE `group_template_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ldapgroup`
--

DROP TABLE IF EXISTS `ldapgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ldapgroup` (
  `ldapgroup_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ldapgroup_name` varchar(128) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`ldapgroup_id`),
  UNIQUE KEY `uniq_name` (`ldapgroup_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ldapgroup`
--
-- ORDER BY:  `ldapgroup_id`

LOCK TABLES `ldapgroup` WRITE;
/*!40000 ALTER TABLE `ldapgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `ldapgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ldapgroup_group`
--

DROP TABLE IF EXISTS `ldapgroup_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ldapgroup_group` (
  `ldapgroup_key` int(10) unsigned NOT NULL,
  `group_key` int(10) unsigned NOT NULL,
  PRIMARY KEY (`group_key`,`ldapgroup_key`),
  KEY `fk_group_to_ldapgroup` (`ldapgroup_key`),
  CONSTRAINT `fk_ldapgroup_group_to_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ldapgroup_group_to_ldapgroup` FOREIGN KEY (`ldapgroup_key`) REFERENCES `ldapgroup` (`ldapgroup_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ldapgroup_group`
--
-- ORDER BY:  `group_key`,`ldapgroup_key`

LOCK TABLES `ldapgroup_group` WRITE;
/*!40000 ALTER TABLE `ldapgroup_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `ldapgroup_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membership_request`
--

DROP TABLE IF EXISTS `membership_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `membership_request` (
  `project_key` int(10) unsigned NOT NULL,
  `user_key` int(10) unsigned NOT NULL,
  PRIMARY KEY (`project_key`,`user_key`),
  KEY `fk_membership_req_user` (`user_key`),
  CONSTRAINT `fk_membership_req_project` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_membership_req_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership_request`
--
-- ORDER BY:  `project_key`,`user_key`

LOCK TABLES `membership_request` WRITE;
/*!40000 ALTER TABLE `membership_request` DISABLE KEYS */;
/*!40000 ALTER TABLE `membership_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `migration`
--

DROP TABLE IF EXISTS `migration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `migration` (
  `migration_name` varchar(255) COLLATE utf8_bin NOT NULL,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`migration_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table to track migration status';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `migration`
--
-- ORDER BY:  `migration_name`

LOCK TABLES `migration` WRITE;
/*!40000 ALTER TABLE `migration` DISABLE KEYS */;
INSERT INTO `migration` VALUES ('20110906120000_authentication_method_datatype','2011-12-15 10:33:27');
INSERT INTO `migration` VALUES ('20111207083300_wiki_start_time_to_utimestamp','2011-12-15 10:33:27');
/*!40000 ALTER TABLE `migration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization`
--

DROP TABLE IF EXISTS `organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organization` (
  `organization_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT COMMENT 'TINYINT allows only 256 organizations',
  `organization_name` varchar(128) COLLATE utf8_bin NOT NULL,
  `sorting` tinyint(3) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`organization_id`),
  UNIQUE KEY `uniq_name` (`organization_name`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organization`
--
-- ORDER BY:  `organization_id`

LOCK TABLES `organization` WRITE;
/*!40000 ALTER TABLE `organization` DISABLE KEYS */;
INSERT INTO `organization` VALUES (1,'Local users',2);
INSERT INTO `organization` VALUES (2,'Nokia users',1);
INSERT INTO `organization` VALUES (3,'Ovi users',3);
/*!40000 ALTER TABLE `organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization_group`
--

DROP TABLE IF EXISTS `organization_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `organization_group` (
  `organization_key` tinyint(3) unsigned NOT NULL,
  `group_key` int(10) unsigned NOT NULL,
  PRIMARY KEY (`group_key`,`organization_key`),
  KEY `fk_org_group_to_org` (`organization_key`),
  CONSTRAINT `fk_org_group_to_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_org_group_to_org` FOREIGN KEY (`organization_key`) REFERENCES `organization` (`organization_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Maps organizations into groups';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organization_group`
--
-- ORDER BY:  `group_key`,`organization_key`

LOCK TABLES `organization_group` WRITE;
/*!40000 ALTER TABLE `organization_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `organization_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_activity`
--

DROP TABLE IF EXISTS `project_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_activity` (
  `project_key` int(10) unsigned NOT NULL,
  `ticket_changes` float DEFAULT NULL,
  `wiki_changes` float DEFAULT NULL,
  `scm_changes` float DEFAULT NULL,
  `attachment_changes` float DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `project_description` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `discussion_changes` float DEFAULT NULL,
  PRIMARY KEY (`project_key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_activity`
--
-- ORDER BY:  `project_key`

LOCK TABLES `project_activity` WRITE;
/*!40000 ALTER TABLE `project_activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_archive`
--

DROP TABLE IF EXISTS `project_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_archive` (
  `project_archive_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `orig_project_id` int(10) unsigned NOT NULL,
  `project_name` varchar(64) COLLATE utf8_bin NOT NULL,
  `environment_name` varchar(32) COLLATE utf8_bin NOT NULL,
  `orig_author_id` int(10) unsigned NOT NULL,
  `creation_date` datetime NOT NULL,
  `orig_parent_id` int(10) unsigned NOT NULL,
  `archive_folder_name` varchar(255) COLLATE utf8_bin NOT NULL,
  `archived_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `remove_due` datetime NOT NULL,
  `removed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`project_archive_id`)
) ENGINE=MyISAM AUTO_INCREMENT=80 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Archived projects';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_archive`
--
-- ORDER BY:  `project_archive_id`

LOCK TABLES `project_archive` WRITE;
/*!40000 ALTER TABLE `project_archive` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_archive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_backup`
--

DROP TABLE IF EXISTS `project_backup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_backup` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_key` int(10) unsigned NOT NULL,
  `description` text COLLATE utf8_bin,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `restored` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `created_by` int(10) unsigned DEFAULT NULL,
  `restored_by` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_key` (`project_key`),
  KEY `created_by` (`created_by`),
  KEY `restored_by` (`restored_by`),
  CONSTRAINT `project_backup_ibfk_1` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `project_backup_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `user` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `project_backup_ibfk_3` FOREIGN KEY (`restored_by`) REFERENCES `user` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Information about project backups and restores';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_backup`
--
-- ORDER BY:  `id`

LOCK TABLES `project_backup` WRITE;
/*!40000 ALTER TABLE `project_backup` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_backup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_categories`
--

DROP TABLE IF EXISTS `project_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_categories` (
  `project_key` int(10) unsigned NOT NULL,
  `category_key` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`project_key`,`category_key`),
  KEY `pc_fk_categories` (`category_key`),
  CONSTRAINT `pc_fk_categories` FOREIGN KEY (`category_key`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pc_fk_projects` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Projects - Categories Mapping';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_categories`
--
-- ORDER BY:  `project_key`,`category_key`

LOCK TABLES `project_categories` WRITE;
/*!40000 ALTER TABLE `project_categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_icon`
--

DROP TABLE IF EXISTS `project_icon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_icon` (
  `icon_id` int(11) NOT NULL AUTO_INCREMENT,
  `icon_data` blob NOT NULL,
  `content_type` varchar(64) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`icon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_icon`
--
-- ORDER BY:  `icon_id`

LOCK TABLES `project_icon` WRITE;
/*!40000 ALTER TABLE `project_icon` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_icon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_selected`
--

DROP TABLE IF EXISTS `project_selected`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_selected` (
  `project_id` int(10) unsigned NOT NULL,
  `value` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`project_id`),
  CONSTRAINT `project_selected_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_selected`
--
-- ORDER BY:  `project_id`

LOCK TABLES `project_selected` WRITE;
/*!40000 ALTER TABLE `project_selected` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_selected` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_user_visibility`
--

DROP TABLE IF EXISTS `project_user_visibility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_user_visibility` (
  `project_id` int(10) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`project_id`,`user_id`),
  UNIQUE KEY `uniq_user_visibility` (`user_id`,`project_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_user_visibility`
--
-- ORDER BY:  `project_id`,`user_id`

LOCK TABLES `project_user_visibility` WRITE;
/*!40000 ALTER TABLE `project_user_visibility` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_user_visibility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects` (
  `project_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_name` varchar(64) CHARACTER SET utf8 NOT NULL,
  `environment_name` varchar(32) COLLATE utf8_bin NOT NULL,
  `description` text CHARACTER SET utf8,
  `author` int(10) unsigned NOT NULL,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `published` datetime DEFAULT NULL,
  `parent_id` int(10) unsigned DEFAULT NULL,
  `icon_id` int(10) unsigned DEFAULT NULL,
  `trac_environment_key` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`project_id`),
  UNIQUE KEY `env_uniq` (`environment_name`),
  KEY `env_index` (`environment_name`(16)),
  KEY `name_index` (`project_name`),
  KEY `author_index` (`author`),
  KEY `parent_fk` (`parent_id`),
  KEY `fk_projects_trac_env` (`trac_environment_key`),
  CONSTRAINT `author_fk_user` FOREIGN KEY (`author`) REFERENCES `user` (`user_id`),
  CONSTRAINT `fk_projects_trac_env` FOREIGN KEY (`trac_environment_key`) REFERENCES `trac_environment` (`environment_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `parent_fk` FOREIGN KEY (`parent_id`) REFERENCES `projects` (`project_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=678 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='List of all projects';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--
-- ORDER BY:  `project_id`

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (677,'home','home','home project',4,'2011-10-28 12:17:41','2011-10-28 12:17:41',NULL,NULL,NULL,677);
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `protocol`
--

DROP TABLE IF EXISTS `protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `protocol` (
  `protocol_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `scheme` varchar(16) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`protocol_id`),
  UNIQUE KEY `scheme` (`scheme`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table to contain possible access protocols';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `protocol`
--
-- ORDER BY:  `protocol_id`

LOCK TABLES `protocol` WRITE;
/*!40000 ALTER TABLE `protocol` DISABLE KEYS */;
INSERT INTO `protocol` VALUES (1,'http');
INSERT INTO `protocol` VALUES (2,'https');
INSERT INTO `protocol` VALUES (3,'ssh');
/*!40000 ALTER TABLE `protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ssh_key_update`
--

DROP TABLE IF EXISTS `ssh_key_update`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ssh_key_update` (
  `update_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `added` datetime NOT NULL,
  PRIMARY KEY (`update_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ssh_key_update`
--
-- ORDER BY:  `update_id`

LOCK TABLES `ssh_key_update` WRITE;
/*!40000 ALTER TABLE `ssh_key_update` DISABLE KEYS */;
/*!40000 ALTER TABLE `ssh_key_update` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ssh_keys`
--

DROP TABLE IF EXISTS `ssh_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ssh_keys` (
  `key_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `ssh_key` text COLLATE utf8_bin NOT NULL,
  `comment` varchar(200) COLLATE utf8_bin DEFAULT NULL,
  `added` datetime NOT NULL,
  PRIMARY KEY (`key_id`),
  KEY `fk_ssh_keys_to_user` (`user_id`),
  CONSTRAINT `fk_ssh_keys_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ssh_keys`
--
-- ORDER BY:  `key_id`

LOCK TABLES `ssh_keys` WRITE;
/*!40000 ALTER TABLE `ssh_keys` DISABLE KEYS */;
/*!40000 ALTER TABLE `ssh_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `super_user`
--

DROP TABLE IF EXISTS `super_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `super_user` (
  `username` varchar(255) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `fk_super_username` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `super_user`
--
-- ORDER BY:  `username`

LOCK TABLES `super_user` WRITE;
/*!40000 ALTER TABLE `super_user` DISABLE KEYS */;
INSERT INTO `super_user` (`username`) VALUES ('tracadmin');
/*!40000 ALTER TABLE `super_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timeline_cache`
--

DROP TABLE IF EXISTS `timeline_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `timeline_cache` (
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `dateuid` int(10) unsigned NOT NULL,
  `project_id` int(10) unsigned NOT NULL,
  `project_identifier` varchar(32) COLLATE utf8_bin NOT NULL,
  `project_name` varchar(64) COLLATE utf8_bin NOT NULL,
  `author` varchar(255) COLLATE utf8_bin NOT NULL,
  `kind` varchar(32) COLLATE utf8_bin NOT NULL,
  `filter` varchar(32) COLLATE utf8_bin NOT NULL,
  `title` varchar(128) COLLATE utf8_bin NOT NULL,
  `summary` varchar(255) COLLATE utf8_bin NOT NULL,
  `description` varchar(255) COLLATE utf8_bin NOT NULL,
  `url` varchar(255) COLLATE utf8_bin NOT NULL,
  `checksum` binary(16) NOT NULL,
  PRIMARY KEY (`date`,`checksum`),
  UNIQUE KEY `checksum_idx` (`checksum`),
  KEY `date_prj` (`date`,`project_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Cache recent events into this table to minimize timeline gen';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timeline_cache`
--
-- ORDER BY:  `date`,`checksum`

LOCK TABLES `timeline_cache` WRITE;
/*!40000 ALTER TABLE `timeline_cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `timeline_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trac_environment`
--

DROP TABLE IF EXISTS `trac_environment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trac_environment` (
  `environment_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `identifier` varchar(32) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`environment_id`),
  UNIQUE KEY `environment_name` (`identifier`)
) ENGINE=InnoDB AUTO_INCREMENT=678 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table that represents a single trac environment';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trac_environment`
--
-- ORDER BY:  `environment_id`

LOCK TABLES `trac_environment` WRITE;
/*!40000 ALTER TABLE `trac_environment` DISABLE KEYS */;
INSERT INTO `trac_environment` VALUES (677,'home');
/*!40000 ALTER TABLE `trac_environment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8_bin NOT NULL,
  `mail` varchar(255) COLLATE utf8_bin NOT NULL,
  `mobile` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `givenName` varchar(32) COLLATE utf8_bin DEFAULT NULL,
  `lastName` varchar(64) COLLATE utf8_bin DEFAULT NULL,
  `icon_id` int(10) unsigned DEFAULT NULL,
  `SHA1_PW` varchar(40) COLLATE utf8_bin NOT NULL,
  `insider` tinyint(1) NOT NULL DEFAULT '0',
  `authentication_key` tinyint(3) unsigned DEFAULT NULL,
  `user_status_key` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `last_login` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uniquser` (`username`),
  KEY `user_fast` (`username`(16)),
  KEY `fk_user_status` (`user_status_key`),
  KEY `fk_user_authentication` (`authentication_key`),
  CONSTRAINT `fk_user_authentication` FOREIGN KEY (`authentication_key`) REFERENCES `authentication` (`id`),
  CONSTRAINT `fk_user_status` FOREIGN KEY (`user_status_key`) REFERENCES `user_status` (`user_status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--
-- ORDER BY:  `user_id`

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'authenticated','',NULL,NULL,NULL,NULL,'c52450fab1f6e5dba6e2db8023448950abc0a728',0,NULL,1,'0000-00-00 00:00:00');
INSERT INTO `user` VALUES (2,'anonymous','',NULL,NULL,NULL,NULL,'c52450fab1f6e5dba6e2db8023448950abc0a728',0,NULL,2,'0000-00-00 00:00:00');
INSERT INTO `user` VALUES (4,'tracadmin','',NULL,NULL,NULL,NULL,'588532bbea60a2b56a819ab0bc5a56ee7153ee16',0,5,2,'0000-00-00 00:00:00');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group` (
  `user_key` int(10) unsigned NOT NULL,
  `group_key` int(10) unsigned NOT NULL,
  PRIMARY KEY (`user_key`,`group_key`),
  KEY `group_index` (`group_key`),
  CONSTRAINT `ug_fk_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ug_fk_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Maps users to groups';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group`
--
-- ORDER BY:  `user_key`,`group_key`

LOCK TABLES `user_group` WRITE;
/*!40000 ALTER TABLE `user_group` DISABLE KEYS */;
INSERT INTO `user_group` VALUES (4,2);
/*!40000 ALTER TABLE `user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_icon`
--

DROP TABLE IF EXISTS `user_icon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_icon` (
  `icon_id` int(11) NOT NULL AUTO_INCREMENT,
  `icon_data` blob NOT NULL,
  `content_type` varchar(64) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`icon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_icon`
--
-- ORDER BY:  `icon_id`

LOCK TABLES `user_icon` WRITE;
/*!40000 ALTER TABLE `user_icon` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_icon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_organization`
--

DROP TABLE IF EXISTS `user_organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_organization` (
  `user_key` int(10) unsigned NOT NULL,
  `organization_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`user_key`,`organization_key`),
  KEY `fk_user_organization_b` (`organization_key`),
  CONSTRAINT `fk_user_organization_a` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_organization_b` FOREIGN KEY (`organization_key`) REFERENCES `organization` (`organization_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_organization`
--
-- ORDER BY:  `user_key`,`organization_key`

LOCK TABLES `user_organization` WRITE;
/*!40000 ALTER TABLE `user_organization` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_preference`
--

DROP TABLE IF EXISTS `user_preference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_preference` (
  `user_key` int(10) unsigned NOT NULL,
  `item` varchar(50) COLLATE utf8_bin NOT NULL,
  `value` varchar(50) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`user_key`,`item`),
  UNIQUE KEY `item_index` (`user_key`,`item`),
  CONSTRAINT `up_fk_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User preferences';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_preference`
--
-- ORDER BY:  `user_key`,`item`

LOCK TABLES `user_preference` WRITE;
/*!40000 ALTER TABLE `user_preference` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_preference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_status`
--

DROP TABLE IF EXISTS `user_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_status` (
  `user_status_id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `status_label` varchar(16) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`user_status_id`),
  UNIQUE KEY `status_label_uniq` (`status_label`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_status`
--
-- ORDER BY:  `user_status_id`

LOCK TABLES `user_status` WRITE;
/*!40000 ALTER TABLE `user_status` DISABLE KEYS */;
INSERT INTO `user_status` VALUES (1,'inactive');
INSERT INTO `user_status` VALUES (2,'active');
INSERT INTO `user_status` VALUES (3,'banned');
INSERT INTO `user_status` VALUES (4,'disabled');
/*!40000 ALTER TABLE `user_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `watchlist`
--

DROP TABLE IF EXISTS `watchlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `watchlist` (
  `user_key` int(10) unsigned NOT NULL,
  `project_key` int(10) unsigned NOT NULL,
  `notification` enum('immediate','daily','weekly','none') COLLATE utf8_bin NOT NULL DEFAULT 'immediate',
  PRIMARY KEY (`user_key`,`project_key`),
  KEY `w_fk_project` (`project_key`),
  CONSTRAINT `w_fk_project` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `w_fk_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Watchlist';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `watchlist`
--
-- ORDER BY:  `user_key`,`project_key`

LOCK TABLES `watchlist` WRITE;
/*!40000 ALTER TABLE `watchlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `watchlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'trac_admin'
--
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_context` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `add_context`(con_name CHAR(255), con_description CHAR(255))
BEGIN
START TRANSACTION;
IF NOT EXISTS (SELECT * FROM contexts WHERE context_name = con_name) THEN
  INSERT INTO contexts (context_id, context_name, context_description)
  VALUES(null, con_name, con_description);
END IF;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_ldapgroup_to_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `add_ldapgroup_to_group`(ldapgroup_id INT, group_id INT)
BEGIN
START TRANSACTION;
INSERT INTO `ldapgroup_group`(ldapgroup_key,group_key) VALUES(ldapgroup_id, group_id);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_organization_to_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `add_organization_to_group`(organization_id INT, group_id INT)
BEGIN
START TRANSACTION;
INSERT INTO organization_group VALUES(organization_id, group_id);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_superuser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `add_superuser`(super_username VARCHAR(255))
BEGIN
START TRANSACTION;
INSERT INTO super_user(username) VALUES(super_username);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_user_to_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `add_user_to_group`(user_id INT, group_id INT)
BEGIN
START TRANSACTION;
INSERT INTO user_group VALUES(user_id, group_id);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `archive_project_record` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `archive_project_record`(project_key INT)
BEGIN
START TRANSACTION;

INSERT INTO project_archive
SELECT  null,
        project_id,
        project_name,
        environment_name,
        author,
        created,
        parent_id,
        null,
        null,
        DATE_ADD(now(), INTERVAL 1 WEEK),
        null
FROM projects
WHERE project_id = project_key;

SELECT LAST_INSERT_ID() FROM `project_archive` LIMIT 0,1;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_group_from_template` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `create_group_from_template`(template_id INT, new_group_name VARCHAR(128), trac_environment_id INT)
BEGIN
DECLARE new_group_id INT;
START TRANSACTION;
INSERT INTO `group` VALUES(null, new_group_name, trac_environment_id);
SELECT LAST_INSERT_ID() INTO new_group_id FROM `group` LIMIT 0,1;
INSERT INTO `group_permission`
(
SELECT new_group_id, permission_key
FROM group_template_permission
WHERE group_template_permission.group_template_key = template_id
);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_ldapgroup` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `create_ldapgroup`(ldapgroupname VARCHAR(128))
BEGIN
START TRANSACTION;
INSERT INTO `ldapgroup`(ldapgroup_name) VALUES(ldapgroupname);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_organization` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `create_organization`(organization_name VARCHAR(128))
BEGIN
  START TRANSACTION;
  INSERT INTO organization VALUES(null, organization_name);
  COMMIT;
  END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_project` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `create_project`(name VARCHAR(64), environment_name VARCHAR(32), description TEXT, author_id INT, parent_id INT)
BEGIN

DECLARE new_environment_id INT;
START TRANSACTION;

INSERT INTO trac_environment(identifier) VALUES(environment_name);
SELECT LAST_INSERT_ID() INTO new_environment_id FROM trac_environment LIMIT 0,1;

INSERT INTO projects(project_name, environment_name, description, author, parent_id, created, published, trac_environment_key)
VALUES(name, environment_name, description, author_id, parent_id, now(), null, new_environment_id);

COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `create_template` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `create_template`(template_name VARCHAR(255))
BEGIN
START TRANSACTION;
INSERT INTO group_template VALUES(null, template_name);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_group_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_group_permissions`(trac_environment_id INT)
BEGIN
SELECT group.group_name, action.action_string
FROM `group`
LEFT JOIN group_permission ON group_permission.group_key = group.group_id
LEFT JOIN action ON action.action_id = group_permission.permission_key
WHERE group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_ldap_groups_by_trac_environment_key` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_ldap_groups_by_trac_environment_key`(trac_environment_id INT)
BEGIN
SELECT ldapgroup.ldapgroup_name, group.group_name FROM `group`
INNER JOIN ldapgroup_group ON ldapgroup_group.group_key = group.group_id
INNER JOIN ldapgroup ON ldapgroup_group.ldapgroup_key = ldapgroup.ldapgroup_id
WHERE group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_organization_groups` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_organization_groups`(trac_environment_id INT)
BEGIN
SELECT organization.organization_name, group.group_name FROM `group`
INNER JOIN organization_group ON organization_group.group_key = group.group_id
INNER JOIN organization ON organization_group.organization_key = organization.organization_id
WHERE group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_permissions`(project_id INT)
BEGIN
SELECT user.username, action.action_string FROM `group`
INNER JOIN user_group ON user_group.group_key = group.group_id
INNER JOIN user ON user.user_id = user_group.user_key
INNER JOIN group_permission ON group_permission.group_key = group.group_id
INNER JOIN action ON action.action_id = group_permission.permission_key
WHERE group.project_key = project_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_template_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_template_permissions`()
BEGIN
SELECT group_template.group_template_name, action.action_string
FROM `group_template`
LEFT JOIN group_template_permission ON group_template_permission.group_template_key = group_template.group_template_id
LEFT JOIN action ON action.action_id = group_template_permission.permission_key;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_all_user_groups` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_all_user_groups`(trac_environment_id INT)
BEGIN
SELECT user.username, group.group_name FROM `group`
INNER JOIN user_group ON user_group.group_key = group.group_id
INNER JOIN user ON user_group.user_key = user.user_id
WHERE group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_authentications` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_authentications`()
BEGIN
SELECT * FROM authentication;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_authentication_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_authentication_id`(method VARCHAR(128))
BEGIN
  SELECT id FROM authentication
  WHERE authentication.method = method;
  END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_authentication_methods` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_authentication_methods`()
BEGIN
  SHOW COLUMNS FROM authentication LIKE 'method';
  END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_available_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_available_permissions`()
BEGIN
SELECT action.action_string
FROM `action`;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_groups` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_groups`(trac_environment_id INT)
BEGIN
SELECT group_name FROM `group`
WHERE group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_group_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_group_id`(group_name VARCHAR(128), trac_environment_id INT)
BEGIN
SELECT group_id FROM `group`
WHERE group.group_name = group_name
AND group.trac_environment_key = trac_environment_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_ldapgroups` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_ldapgroups`()
BEGIN
SELECT (ldapgroup_id, ldapgroup_name) FROM ldapgroup WHERE 1;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_ldapgroup_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_ldapgroup_id`(ldapgroup_name VARCHAR(128))
BEGIN
SELECT ldapgroup_id FROM ldapgroup
WHERE ldapgroup.ldapgroup_name = ldapgroup_name;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_ldapgroup_ids_with_group_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_ldapgroup_ids_with_group_id`(group_id INT)
BEGIN
SELECT (ldapgroup_key) FROM ldapgroup_group
WHERE ldapgroup_group.group_key = group_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_organizations` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_organizations`()
BEGIN
SELECT * FROM organization ORDER BY sorting;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_organization_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_organization_id`(organization_name VARCHAR(128))
BEGIN
SELECT organization_id FROM organization
WHERE organization.organization_name = organization_name;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_project_public_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_project_public_permissions`(trac_environment_id INT)
BEGIN
SELECT DISTINCT action.action_string FROM `group`
INNER JOIN user_group ON user_group.group_key = group.group_id
INNER JOIN user ON user.user_id = user_group.user_key
INNER JOIN group_permission ON group_permission.group_key = group.group_id
INNER JOIN action ON action.action_id = group_permission.permission_key
WHERE group.trac_environment_key = trac_environment_id AND user.username = 'anonymous';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_superusers` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_superusers`()
BEGIN
SELECT `username` FROM `super_user`;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_templates` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_templates`()
BEGIN
SELECT group_template_name FROM group_template WHERE 1;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_template_id` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_template_id`(template_name VARCHAR(255))
BEGIN
SELECT group_template_id FROM group_template WHERE group_template_name = template_name;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_user_permissions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `get_user_permissions`(user_id INT, project_id INT)
BEGIN
SELECT action.action_string FROM `group`
INNER JOIN user_group ON group.group_id = user_group.group_key
INNER JOIN group_permission ON group.group_id = group_permission.group_key
INNER JOIN action ON group_permission.permission_key = action.action_id
WHERE user_group.user_key = user_id
AND group.project_key = project_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `grant_permission_to_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `grant_permission_to_group`(group_id INT, permission_id INT)
BEGIN
START TRANSACTION;
INSERT INTO group_permission VALUES(group_id, permission_id);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `grant_permission_to_template` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `grant_permission_to_template`(template_name VARCHAR(255), permission_name VARCHAR(32))
BEGIN
DECLARE permission_key INT;
DECLARE template_key INT;
START TRANSACTION;
SELECT action_id INTO permission_key FROM action
WHERE action_string = permission_name;
SELECT group_template_id INTO template_key FROM group_template
WHERE group_template_name = template_name;
INSERT INTO group_template_permission VALUES(template_key, permission_key);
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `mark_archived_project_removed` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `mark_archived_project_removed`(archive_id INT)
BEGIN
START TRANSACTION;

UPDATE project_archive
SET removed_at = now()
WHERE project_archive_id = archive_id;

COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `move_category` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `move_category`(cat_name CHAR(255), cat_context_id SMALLINT(4))
BEGIN
START TRANSACTION;
UPDATE categories SET context_id = cat_context_id, parent_id = null WHERE category_name = cat_name;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_archived_project_record` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_archived_project_record`(archive_id INT)
BEGIN
START TRANSACTION;

DELETE FROM project_archive
WHERE project_archive_id = archive_id;

COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_group`(groupid INT)
BEGIN
START TRANSACTION;
DELETE FROM `group` WHERE group.group_id = groupid;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_ldapgroup` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_ldapgroup`(ldapgroup_name VARCHAR(128))
BEGIN
START TRANSACTION;
DELETE FROM ldapgroup WHERE ldapgroup.ldapgroup_name = ldapgroup_name;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_ldapgroup_from_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_ldapgroup_from_group`(ldapgroup_id INT, group_id INT)
BEGIN
START TRANSACTION;
DELETE FROM ldapgroup_group
WHERE ldapgroup_group.ldapgroup_key = ldapgroup_id
AND ldapgroup_group.group_key = group_id;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_organization` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_organization`(organization_name VARCHAR(128))
BEGIN
START TRANSACTION;
DELETE FROM organization WHERE organization.organization_name = organization_name;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_organization_from_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_organization_from_group`(organization_id INT, group_id INT)
BEGIN
START TRANSACTION;
DELETE FROM organization_group
WHERE organization_group.organization_key = organization_id
AND organization_group.group_key = group_id;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_superuser` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_superuser`(super_username VARCHAR(255))
BEGIN
START TRANSACTION;
DELETE FROM `super_user` WHERE `username` = `super_username` LIMIT 1;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_template` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_template`(template_name VARCHAR(255))
BEGIN
START TRANSACTION;
DELETE FROM group_template WHERE group_template_name = template_name;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_user_from_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `remove_user_from_group`(user_id INT, group_id INT)
BEGIN
START TRANSACTION;
DELETE FROM user_group
WHERE user_group.user_key = user_id
AND user_group.group_key = group_id;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `rename_category` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `rename_category`(cat_name CHAR(255), cat_new_name CHAR(255))
BEGIN
START TRANSACTION;
UPDATE categories SET category_name = cat_new_name WHERE category_name = cat_name;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `rename_context` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `rename_context`(cont_name CHAR(255), cont_new_name CHAR(255))
BEGIN
START TRANSACTION;
UPDATE contexts SET context_name = cont_new_name WHERE context_name = cont_name;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `revoke_permission_from_group` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `revoke_permission_from_group`(group_id INT, permission_id INT)
BEGIN
START TRANSACTION;
DELETE FROM group_permission
WHERE group_permission.group_key = group_id
AND group_permission.permission_key = permission_id;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `revoke_permission_from_template` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `revoke_permission_from_template`(template_name VARCHAR(255), permission_name VARCHAR(32))
BEGIN
DECLARE permission_key INT;
DECLARE template_key INT;
START TRANSACTION;
SELECT action_id INTO permission_key FROM action
WHERE action_string = permission_name;
SELECT group_template_id INTO template_key FROM group_template
WHERE group_template_name = template_name;
DELETE FROM group_template_permission
WHERE group_template_key = template_key
AND group_template_permission.permission_key = permission_key;
COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `unwatch_project` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `unwatch_project`(user_id int(10), project_id int(10))
BEGIN

START TRANSACTION;
DELETE FROM watchlist WHERE user_key = user_id AND project_key = project_id;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_project_archive_folder` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `update_project_archive_folder`(archive_id INT, folder_name TEXT)
BEGIN
START TRANSACTION;

UPDATE project_archive
SET archive_folder_name = folder_name
WHERE project_archive_id = archive_id;

COMMIT;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `watch_project` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `watch_project`(user_id int(10), project_id int(10), w_notification varchar(20))
BEGIN

START TRANSACTION;
IF NOT EXISTS (SELECT * FROM watchlist WHERE user_key = user_id AND project_key = project_id) THEN
  INSERT INTO watchlist (user_key, project_key, notification)
  VALUES(user_id, project_id, w_notification);
ELSE
  UPDATE watchlist SET notification = w_notification WHERE user_key = user_id AND project_key = project_id;
END IF;
COMMIT;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `trac_analytical`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `trac_analytical` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;

USE `trac_analytical`;

--
-- Table structure for table `context_dim`
--

DROP TABLE IF EXISTS `context_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `context_dim` (
  `context_sk` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `context` varchar(32) NOT NULL,
  `environment_type` varchar(16) NOT NULL,
  `path_info` varchar(128) NOT NULL,
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime DEFAULT NULL,
  PRIMARY KEY (`context_sk`),
  KEY `context_name_idx` (`context`(8)),
  KEY `path_info_idx` (`path_info`(16)),
  KEY `full_idx` (`context`(8),`path_info`(16))
) ENGINE=MyISAM AUTO_INCREMENT=556 DEFAULT CHARSET=utf8 COMMENT='Dimension that represents a context in a trac instance';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `context_dim`
--
-- ORDER BY:  `context_sk`

LOCK TABLES `context_dim` WRITE;
/*!40000 ALTER TABLE `context_dim` DISABLE KEYS */;
INSERT INTO `context_dim` VALUES (1,'<Inapplicable>','<Inapplicable>',' <Inapplicable>','0000-00-00 00:00:00','9999-00-00 00:00:00');
INSERT INTO `context_dim` VALUES (2,'Welcome page','home','/','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (3,'Login / out','home','/user','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (4,'Explore Projects','home','/project/explore','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (5,'My Projects','home','/myprojects','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (6,'New project form','home','/project/new','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (7,'Create project','home','/project/project/create','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (8,'Remove project','home','/project/remove','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (9,'Preferences','home','/prefs','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (10,'Basic settings','home','/prefs/basic','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (11,'Password change','home','/prefs/changepw','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (12,'Timezone settings','home','/prefs/datetime','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (13,'Avatar settings','home','/prefs/image','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (14,'Key binding settings','home','/prefs/keybindings','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (15,'Pygment settings','home','/prefs/pygments','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (16,'Admin','home','/admin','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (17,'Edit categories','home','/admin/general/categoryeditor','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (18,'Logging settings','home','/admin/general/logging','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (19,'View migrations','home','/admin/general/migrations','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (20,'Plugin settings','home','/admin/general/plugin','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (21,'Group templates','home','/admin/permissions/grouptemplates','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (22,'Home permissions','home','/admin/permissions/perm','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (23,'Project archive','home','/admin/projects/prjarchive','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (24,'Storage usage','home','/admin/projects/storageusage','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (25,'Create user','home','/admin/users/create','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (26,'Edit user','home','/admin/users/edit','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (27,'Remove user','home','/admin/users/remove','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (28,'Attachment Wiki','project','/attachment/wiki.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (29,'Attachment Ticket','project','/attachment/ticket.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (30,'Attachment Discussion','project','/attachment/discussion.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (31,'Attachment Milestone','project','/attachment/milestone.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (32,'Summary page','project','/','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (33,'Summary page','project','/summary','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (34,'Source browser','project','/browser.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (35,'Changeset','project','/changeset.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (36,'Categorization AJAX','project','/categories','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (37,'Autocomplete categories','project','/catautocomplete','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (38,'Changeset diff','project','/diff','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (39,'Discussion list','project','/discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (40,'Discussion forum','project','/discussion/forum.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (41,'Discussion topic','project','/discussion/topic.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (42,'Files','project','/files.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (43,'Changeset log','project','/log','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (44,'Milestones','project','/milestone','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (45,'Milestone','project','/milestone/.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (46,'New ticket','project','/newticket','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (47,'Ticket query','project','/query','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (48,'Roadmap','project','/roadmap','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (49,'Search','project','/search','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (50,'Team','project','/team','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (51,'Ticket','project','/ticket/.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (52,'Timeline','project','/timeline.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (53,'Wiki','project','/wiki.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (54,'Downloads','project','/downloads.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (55,'Admin','project','/admin','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (56,'Admin Basic settings','project','/admin/general/basics','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (57,'Admin Categorization','project','/admin/general/categorization','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (58,'Admin Project Icon','project','/admin/general/projecticon','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (59,'Admin Project Relations','project','/admin/general/relations','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (60,'Admin Storages','project','/admin/general/storages','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (61,'Admin System','project','/admin/general/system','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (62,'Admin Forums','project','/admin/discussion/forum.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (63,'Admin Forum groups','project','/admin/discussion/group.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (64,'Admin Downloads','project','/admin/downloads/downloads.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (65,'Admin Download platforms','project','/admin/downloads/platform.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (66,'Admin Download types','project','/admin/downloads/types.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (67,'Admin Users','project','/admin/permissions/group','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (68,'Admin Groups','project','/admin/permissions/groupspermissions','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (69,'Admin Ticket components','project','/admin/ticket/components.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (70,'Admin Ticket milestones','project','/admin/ticket/milestones.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (71,'Admin Ticket priorities','project','/admin/ticket/priority.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (72,'Admin Ticket resolutions','project','/admin/ticket/resolution.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (73,'Admin Ticket severities','project','/admin/ticket/severity.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (74,'Admin Ticket types','project','/admin/ticket/type.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (75,'Admin Ticket versions','project','/admin/ticket/versions.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (76,'Admin Repositories','project','/admin/versioncontrol/repository.*','2011-01-27 09:08:05',NULL);
INSERT INTO `context_dim` VALUES (77,'Unlisted user page','home','/user.*','2011-01-27 07:24:02',NULL);
INSERT INTO `context_dim` VALUES (78,'Version control log','project','/log.*','2011-01-27 07:24:02',NULL);
INSERT INTO `context_dim` VALUES (79,'Unlisted RSS','home','/rss.*','2011-01-27 07:30:02',NULL);
INSERT INTO `context_dim` VALUES (80,'Home Wiki / Help','home','/wiki.*','2011-01-27 07:30:02',NULL);
INSERT INTO `context_dim` VALUES (81,'Search','project','/search.*','2011-01-27 07:36:02',NULL);
INSERT INTO `context_dim` VALUES (82,'/project','home','/project.*','2011-01-27 07:36:02',NULL);
INSERT INTO `context_dim` VALUES (83,'Unlisted admin panel','project','/admin.*','2011-01-27 07:48:02',NULL);
INSERT INTO `context_dim` VALUES (84,'Unlisted raw-attachment','project','/raw-attachment.*','2011-01-27 08:06:02',NULL);
INSERT INTO `context_dim` VALUES (85,'Unlisted discussion page','project','/discussion.*','2011-01-27 08:18:02',NULL);
INSERT INTO `context_dim` VALUES (86,'Export from SCM','project','/export.*','2011-01-27 09:18:02',NULL);
INSERT INTO `context_dim` VALUES (87,'Project list','home','/project/list','2011-01-27 11:30:39',NULL);
INSERT INTO `context_dim` VALUES (88,'Most active RSS','home','/rss/mostactive.xml','2011-01-27 11:31:43',NULL);
INSERT INTO `context_dim` VALUES (89,'Discussion message','project','/discussion/message.*','2011-01-27 11:33:03',NULL);
INSERT INTO `context_dim` VALUES (90,'Raw Attachment Wiki','project','/raw-attachment/wiki.*','2011-01-27 11:36:30',NULL);
INSERT INTO `context_dim` VALUES (91,'Raw Attachment Ticket','project','/raw-attachment/ticket.*','2011-01-27 11:36:44',NULL);
INSERT INTO `context_dim` VALUES (92,'Raw Attachment Discussion','project','/raw-attachment/discussion.*','2011-01-27 11:37:00',NULL);
INSERT INTO `context_dim` VALUES (93,'Raw Attachment Milestone','project','/raw-attachment/milestone.*','2011-01-27 11:37:36',NULL);
INSERT INTO `context_dim` VALUES (94,'User profile','project','/user/.*','2011-01-27 11:40:52',NULL);
/*!40000 ALTER TABLE `context_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_management`
--

DROP TABLE IF EXISTS `data_management`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_management` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `table` varchar(128) NOT NULL,
  `buffer_partitions` smallint(5) unsigned NOT NULL COMMENT 'How many days to store data',
  `partition_size` smallint(5) unsigned NOT NULL COMMENT 'How many days to fit in one partition',
  `partition_count` smallint(5) unsigned NOT NULL,
  `archive_table` varchar(128) DEFAULT NULL COMMENT 'Where to archive old data, NULL to delete',
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COMMENT='Table for partitioning and data management plan';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_management`
--
-- ORDER BY:  `id`

LOCK TABLES `data_management` WRITE;
/*!40000 ALTER TABLE `data_management` DISABLE KEYS */;
INSERT INTO `data_management` VALUES (1,'project_activity_fact',2,90,40,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (2,'event_fact',2,30,120,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (3,'discussion_activity_fact',2,90,40,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (4,'user_activity_fact',2,90,40,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (5,'request_project_summary',2,90,40,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (6,'request_hour_summary',2,90,40,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
INSERT INTO `data_management` VALUES (7,'request_fact',2,30,120,NULL,'2011-01-01 00:00:00','2014-01-01 00:00:00');
/*!40000 ALTER TABLE `data_management` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `date_dim`
--

DROP TABLE IF EXISTS `date_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `date_dim` (
  `date_sk` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `year` smallint(5) unsigned NOT NULL,
  `quarter` tinyint(3) unsigned NOT NULL COMMENT '1 ... 4',
  `month` tinyint(3) unsigned NOT NULL COMMENT '1,2 ... 12',
  `month_name` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'January, February ... December',
  `week` tinyint(3) unsigned NOT NULL COMMENT '0,1,2 ... 53',
  `week_day` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'Monday, Tuesday ... Sunday',
  `day_of_month` tinyint(3) unsigned NOT NULL COMMENT '1, 2 ... 31',
  `date` date NOT NULL COMMENT 'Normal SQL date',
  PRIMARY KEY (`date_sk`),
  KEY `YMD_idx` (`year`,`month`,`day_of_month`),
  KEY `YQ_idx` (`year`,`quarter`),
  KEY `YW_idx` (`year`,`week`),
  KEY `YWD_idx` (`year`,`week_day`),
  KEY `sql_date_idx` (`date`) USING BTREE,
  KEY `YMN_idx` (`year`,`month_name`(3))
) ENGINE=MyISAM AUTO_INCREMENT=732 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `date_dim`
--
-- ORDER BY:  `date_sk`

LOCK TABLES `date_dim` WRITE;
/*!40000 ALTER TABLE `date_dim` DISABLE KEYS */;
INSERT INTO `date_dim` VALUES (366,2012,1,1,'January',52,'Sunday',1,'2012-01-01');
INSERT INTO `date_dim` VALUES (367,2012,1,1,'January',1,'Monday',2,'2012-01-02');
INSERT INTO `date_dim` VALUES (368,2012,1,1,'January',1,'Tuesday',3,'2012-01-03');
INSERT INTO `date_dim` VALUES (369,2012,1,1,'January',1,'Wednesday',4,'2012-01-04');
INSERT INTO `date_dim` VALUES (370,2012,1,1,'January',1,'Thursday',5,'2012-01-05');
INSERT INTO `date_dim` VALUES (371,2012,1,1,'January',1,'Friday',6,'2012-01-06');
INSERT INTO `date_dim` VALUES (372,2012,1,1,'January',1,'Saturday',7,'2012-01-07');
INSERT INTO `date_dim` VALUES (373,2012,1,1,'January',1,'Sunday',8,'2012-01-08');
INSERT INTO `date_dim` VALUES (374,2012,1,1,'January',2,'Monday',9,'2012-01-09');
INSERT INTO `date_dim` VALUES (375,2012,1,1,'January',2,'Tuesday',10,'2012-01-10');
INSERT INTO `date_dim` VALUES (376,2012,1,1,'January',2,'Wednesday',11,'2012-01-11');
INSERT INTO `date_dim` VALUES (377,2012,1,1,'January',2,'Thursday',12,'2012-01-12');
INSERT INTO `date_dim` VALUES (378,2012,1,1,'January',2,'Friday',13,'2012-01-13');
INSERT INTO `date_dim` VALUES (379,2012,1,1,'January',2,'Saturday',14,'2012-01-14');
INSERT INTO `date_dim` VALUES (380,2012,1,1,'January',2,'Sunday',15,'2012-01-15');
INSERT INTO `date_dim` VALUES (381,2012,1,1,'January',3,'Monday',16,'2012-01-16');
INSERT INTO `date_dim` VALUES (382,2012,1,1,'January',3,'Tuesday',17,'2012-01-17');
INSERT INTO `date_dim` VALUES (383,2012,1,1,'January',3,'Wednesday',18,'2012-01-18');
INSERT INTO `date_dim` VALUES (384,2012,1,1,'January',3,'Thursday',19,'2012-01-19');
INSERT INTO `date_dim` VALUES (385,2012,1,1,'January',3,'Friday',20,'2012-01-20');
INSERT INTO `date_dim` VALUES (386,2012,1,1,'January',3,'Saturday',21,'2012-01-21');
INSERT INTO `date_dim` VALUES (387,2012,1,1,'January',3,'Sunday',22,'2012-01-22');
INSERT INTO `date_dim` VALUES (388,2012,1,1,'January',4,'Monday',23,'2012-01-23');
INSERT INTO `date_dim` VALUES (389,2012,1,1,'January',4,'Tuesday',24,'2012-01-24');
INSERT INTO `date_dim` VALUES (390,2012,1,1,'January',4,'Wednesday',25,'2012-01-25');
INSERT INTO `date_dim` VALUES (391,2012,1,1,'January',4,'Thursday',26,'2012-01-26');
INSERT INTO `date_dim` VALUES (392,2012,1,1,'January',4,'Friday',27,'2012-01-27');
INSERT INTO `date_dim` VALUES (393,2012,1,1,'January',4,'Saturday',28,'2012-01-28');
INSERT INTO `date_dim` VALUES (394,2012,1,1,'January',4,'Sunday',29,'2012-01-29');
INSERT INTO `date_dim` VALUES (395,2012,1,1,'January',5,'Monday',30,'2012-01-30');
INSERT INTO `date_dim` VALUES (396,2012,1,1,'January',5,'Tuesday',31,'2012-01-31');
INSERT INTO `date_dim` VALUES (397,2012,1,2,'February',5,'Wednesday',1,'2012-02-01');
INSERT INTO `date_dim` VALUES (398,2012,1,2,'February',5,'Thursday',2,'2012-02-02');
INSERT INTO `date_dim` VALUES (399,2012,1,2,'February',5,'Friday',3,'2012-02-03');
INSERT INTO `date_dim` VALUES (400,2012,1,2,'February',5,'Saturday',4,'2012-02-04');
INSERT INTO `date_dim` VALUES (401,2012,1,2,'February',5,'Sunday',5,'2012-02-05');
INSERT INTO `date_dim` VALUES (402,2012,1,2,'February',6,'Monday',6,'2012-02-06');
INSERT INTO `date_dim` VALUES (403,2012,1,2,'February',6,'Tuesday',7,'2012-02-07');
INSERT INTO `date_dim` VALUES (404,2012,1,2,'February',6,'Wednesday',8,'2012-02-08');
INSERT INTO `date_dim` VALUES (405,2012,1,2,'February',6,'Thursday',9,'2012-02-09');
INSERT INTO `date_dim` VALUES (406,2012,1,2,'February',6,'Friday',10,'2012-02-10');
INSERT INTO `date_dim` VALUES (407,2012,1,2,'February',6,'Saturday',11,'2012-02-11');
INSERT INTO `date_dim` VALUES (408,2012,1,2,'February',6,'Sunday',12,'2012-02-12');
INSERT INTO `date_dim` VALUES (409,2012,1,2,'February',7,'Monday',13,'2012-02-13');
INSERT INTO `date_dim` VALUES (410,2012,1,2,'February',7,'Tuesday',14,'2012-02-14');
INSERT INTO `date_dim` VALUES (411,2012,1,2,'February',7,'Wednesday',15,'2012-02-15');
INSERT INTO `date_dim` VALUES (412,2012,1,2,'February',7,'Thursday',16,'2012-02-16');
INSERT INTO `date_dim` VALUES (413,2012,1,2,'February',7,'Friday',17,'2012-02-17');
INSERT INTO `date_dim` VALUES (414,2012,1,2,'February',7,'Saturday',18,'2012-02-18');
INSERT INTO `date_dim` VALUES (415,2012,1,2,'February',7,'Sunday',19,'2012-02-19');
INSERT INTO `date_dim` VALUES (416,2012,1,2,'February',8,'Monday',20,'2012-02-20');
INSERT INTO `date_dim` VALUES (417,2012,1,2,'February',8,'Tuesday',21,'2012-02-21');
INSERT INTO `date_dim` VALUES (418,2012,1,2,'February',8,'Wednesday',22,'2012-02-22');
INSERT INTO `date_dim` VALUES (419,2012,1,2,'February',8,'Thursday',23,'2012-02-23');
INSERT INTO `date_dim` VALUES (420,2012,1,2,'February',8,'Friday',24,'2012-02-24');
INSERT INTO `date_dim` VALUES (421,2012,1,2,'February',8,'Saturday',25,'2012-02-25');
INSERT INTO `date_dim` VALUES (422,2012,1,2,'February',8,'Sunday',26,'2012-02-26');
INSERT INTO `date_dim` VALUES (423,2012,1,2,'February',9,'Monday',27,'2012-02-27');
INSERT INTO `date_dim` VALUES (424,2012,1,2,'February',9,'Tuesday',28,'2012-02-28');
INSERT INTO `date_dim` VALUES (425,2012,1,2,'February',9,'Wednesday',29,'2012-02-29');
INSERT INTO `date_dim` VALUES (426,2012,1,3,'March',9,'Thursday',1,'2012-03-01');
INSERT INTO `date_dim` VALUES (427,2012,1,3,'March',9,'Friday',2,'2012-03-02');
INSERT INTO `date_dim` VALUES (428,2012,1,3,'March',9,'Saturday',3,'2012-03-03');
INSERT INTO `date_dim` VALUES (429,2012,1,3,'March',9,'Sunday',4,'2012-03-04');
INSERT INTO `date_dim` VALUES (430,2012,1,3,'March',10,'Monday',5,'2012-03-05');
INSERT INTO `date_dim` VALUES (431,2012,1,3,'March',10,'Tuesday',6,'2012-03-06');
INSERT INTO `date_dim` VALUES (432,2012,1,3,'March',10,'Wednesday',7,'2012-03-07');
INSERT INTO `date_dim` VALUES (433,2012,1,3,'March',10,'Thursday',8,'2012-03-08');
INSERT INTO `date_dim` VALUES (434,2012,1,3,'March',10,'Friday',9,'2012-03-09');
INSERT INTO `date_dim` VALUES (435,2012,1,3,'March',10,'Saturday',10,'2012-03-10');
INSERT INTO `date_dim` VALUES (436,2012,1,3,'March',10,'Sunday',11,'2012-03-11');
INSERT INTO `date_dim` VALUES (437,2012,1,3,'March',11,'Monday',12,'2012-03-12');
INSERT INTO `date_dim` VALUES (438,2012,1,3,'March',11,'Tuesday',13,'2012-03-13');
INSERT INTO `date_dim` VALUES (439,2012,1,3,'March',11,'Wednesday',14,'2012-03-14');
INSERT INTO `date_dim` VALUES (440,2012,1,3,'March',11,'Thursday',15,'2012-03-15');
INSERT INTO `date_dim` VALUES (441,2012,1,3,'March',11,'Friday',16,'2012-03-16');
INSERT INTO `date_dim` VALUES (442,2012,1,3,'March',11,'Saturday',17,'2012-03-17');
INSERT INTO `date_dim` VALUES (443,2012,1,3,'March',11,'Sunday',18,'2012-03-18');
INSERT INTO `date_dim` VALUES (444,2012,1,3,'March',12,'Monday',19,'2012-03-19');
INSERT INTO `date_dim` VALUES (445,2012,1,3,'March',12,'Tuesday',20,'2012-03-20');
INSERT INTO `date_dim` VALUES (446,2012,1,3,'March',12,'Wednesday',21,'2012-03-21');
INSERT INTO `date_dim` VALUES (447,2012,1,3,'March',12,'Thursday',22,'2012-03-22');
INSERT INTO `date_dim` VALUES (448,2012,1,3,'March',12,'Friday',23,'2012-03-23');
INSERT INTO `date_dim` VALUES (449,2012,1,3,'March',12,'Saturday',24,'2012-03-24');
INSERT INTO `date_dim` VALUES (450,2012,1,3,'March',12,'Sunday',25,'2012-03-25');
INSERT INTO `date_dim` VALUES (451,2012,1,3,'March',13,'Monday',26,'2012-03-26');
INSERT INTO `date_dim` VALUES (452,2012,1,3,'March',13,'Tuesday',27,'2012-03-27');
INSERT INTO `date_dim` VALUES (453,2012,1,3,'March',13,'Wednesday',28,'2012-03-28');
INSERT INTO `date_dim` VALUES (454,2012,1,3,'March',13,'Thursday',29,'2012-03-29');
INSERT INTO `date_dim` VALUES (455,2012,1,3,'March',13,'Friday',30,'2012-03-30');
INSERT INTO `date_dim` VALUES (456,2012,1,3,'March',13,'Saturday',31,'2012-03-31');
INSERT INTO `date_dim` VALUES (457,2012,2,4,'April',13,'Sunday',1,'2012-04-01');
INSERT INTO `date_dim` VALUES (458,2012,2,4,'April',14,'Monday',2,'2012-04-02');
INSERT INTO `date_dim` VALUES (459,2012,2,4,'April',14,'Tuesday',3,'2012-04-03');
INSERT INTO `date_dim` VALUES (460,2012,2,4,'April',14,'Wednesday',4,'2012-04-04');
INSERT INTO `date_dim` VALUES (461,2012,2,4,'April',14,'Thursday',5,'2012-04-05');
INSERT INTO `date_dim` VALUES (462,2012,2,4,'April',14,'Friday',6,'2012-04-06');
INSERT INTO `date_dim` VALUES (463,2012,2,4,'April',14,'Saturday',7,'2012-04-07');
INSERT INTO `date_dim` VALUES (464,2012,2,4,'April',14,'Sunday',8,'2012-04-08');
INSERT INTO `date_dim` VALUES (465,2012,2,4,'April',15,'Monday',9,'2012-04-09');
INSERT INTO `date_dim` VALUES (466,2012,2,4,'April',15,'Tuesday',10,'2012-04-10');
INSERT INTO `date_dim` VALUES (467,2012,2,4,'April',15,'Wednesday',11,'2012-04-11');
INSERT INTO `date_dim` VALUES (468,2012,2,4,'April',15,'Thursday',12,'2012-04-12');
INSERT INTO `date_dim` VALUES (469,2012,2,4,'April',15,'Friday',13,'2012-04-13');
INSERT INTO `date_dim` VALUES (470,2012,2,4,'April',15,'Saturday',14,'2012-04-14');
INSERT INTO `date_dim` VALUES (471,2012,2,4,'April',15,'Sunday',15,'2012-04-15');
INSERT INTO `date_dim` VALUES (472,2012,2,4,'April',16,'Monday',16,'2012-04-16');
INSERT INTO `date_dim` VALUES (473,2012,2,4,'April',16,'Tuesday',17,'2012-04-17');
INSERT INTO `date_dim` VALUES (474,2012,2,4,'April',16,'Wednesday',18,'2012-04-18');
INSERT INTO `date_dim` VALUES (475,2012,2,4,'April',16,'Thursday',19,'2012-04-19');
INSERT INTO `date_dim` VALUES (476,2012,2,4,'April',16,'Friday',20,'2012-04-20');
INSERT INTO `date_dim` VALUES (477,2012,2,4,'April',16,'Saturday',21,'2012-04-21');
INSERT INTO `date_dim` VALUES (478,2012,2,4,'April',16,'Sunday',22,'2012-04-22');
INSERT INTO `date_dim` VALUES (479,2012,2,4,'April',17,'Monday',23,'2012-04-23');
INSERT INTO `date_dim` VALUES (480,2012,2,4,'April',17,'Tuesday',24,'2012-04-24');
INSERT INTO `date_dim` VALUES (481,2012,2,4,'April',17,'Wednesday',25,'2012-04-25');
INSERT INTO `date_dim` VALUES (482,2012,2,4,'April',17,'Thursday',26,'2012-04-26');
INSERT INTO `date_dim` VALUES (483,2012,2,4,'April',17,'Friday',27,'2012-04-27');
INSERT INTO `date_dim` VALUES (484,2012,2,4,'April',17,'Saturday',28,'2012-04-28');
INSERT INTO `date_dim` VALUES (485,2012,2,4,'April',17,'Sunday',29,'2012-04-29');
INSERT INTO `date_dim` VALUES (486,2012,2,4,'April',18,'Monday',30,'2012-04-30');
INSERT INTO `date_dim` VALUES (487,2012,2,5,'May',18,'Tuesday',1,'2012-05-01');
INSERT INTO `date_dim` VALUES (488,2012,2,5,'May',18,'Wednesday',2,'2012-05-02');
INSERT INTO `date_dim` VALUES (489,2012,2,5,'May',18,'Thursday',3,'2012-05-03');
INSERT INTO `date_dim` VALUES (490,2012,2,5,'May',18,'Friday',4,'2012-05-04');
INSERT INTO `date_dim` VALUES (491,2012,2,5,'May',18,'Saturday',5,'2012-05-05');
INSERT INTO `date_dim` VALUES (492,2012,2,5,'May',18,'Sunday',6,'2012-05-06');
INSERT INTO `date_dim` VALUES (493,2012,2,5,'May',19,'Monday',7,'2012-05-07');
INSERT INTO `date_dim` VALUES (494,2012,2,5,'May',19,'Tuesday',8,'2012-05-08');
INSERT INTO `date_dim` VALUES (495,2012,2,5,'May',19,'Wednesday',9,'2012-05-09');
INSERT INTO `date_dim` VALUES (496,2012,2,5,'May',19,'Thursday',10,'2012-05-10');
INSERT INTO `date_dim` VALUES (497,2012,2,5,'May',19,'Friday',11,'2012-05-11');
INSERT INTO `date_dim` VALUES (498,2012,2,5,'May',19,'Saturday',12,'2012-05-12');
INSERT INTO `date_dim` VALUES (499,2012,2,5,'May',19,'Sunday',13,'2012-05-13');
INSERT INTO `date_dim` VALUES (500,2012,2,5,'May',20,'Monday',14,'2012-05-14');
INSERT INTO `date_dim` VALUES (501,2012,2,5,'May',20,'Tuesday',15,'2012-05-15');
INSERT INTO `date_dim` VALUES (502,2012,2,5,'May',20,'Wednesday',16,'2012-05-16');
INSERT INTO `date_dim` VALUES (503,2012,2,5,'May',20,'Thursday',17,'2012-05-17');
INSERT INTO `date_dim` VALUES (504,2012,2,5,'May',20,'Friday',18,'2012-05-18');
INSERT INTO `date_dim` VALUES (505,2012,2,5,'May',20,'Saturday',19,'2012-05-19');
INSERT INTO `date_dim` VALUES (506,2012,2,5,'May',20,'Sunday',20,'2012-05-20');
INSERT INTO `date_dim` VALUES (507,2012,2,5,'May',21,'Monday',21,'2012-05-21');
INSERT INTO `date_dim` VALUES (508,2012,2,5,'May',21,'Tuesday',22,'2012-05-22');
INSERT INTO `date_dim` VALUES (509,2012,2,5,'May',21,'Wednesday',23,'2012-05-23');
INSERT INTO `date_dim` VALUES (510,2012,2,5,'May',21,'Thursday',24,'2012-05-24');
INSERT INTO `date_dim` VALUES (511,2012,2,5,'May',21,'Friday',25,'2012-05-25');
INSERT INTO `date_dim` VALUES (512,2012,2,5,'May',21,'Saturday',26,'2012-05-26');
INSERT INTO `date_dim` VALUES (513,2012,2,5,'May',21,'Sunday',27,'2012-05-27');
INSERT INTO `date_dim` VALUES (514,2012,2,5,'May',22,'Monday',28,'2012-05-28');
INSERT INTO `date_dim` VALUES (515,2012,2,5,'May',22,'Tuesday',29,'2012-05-29');
INSERT INTO `date_dim` VALUES (516,2012,2,5,'May',22,'Wednesday',30,'2012-05-30');
INSERT INTO `date_dim` VALUES (517,2012,2,5,'May',22,'Thursday',31,'2012-05-31');
INSERT INTO `date_dim` VALUES (518,2012,2,6,'June',22,'Friday',1,'2012-06-01');
INSERT INTO `date_dim` VALUES (519,2012,2,6,'June',22,'Saturday',2,'2012-06-02');
INSERT INTO `date_dim` VALUES (520,2012,2,6,'June',22,'Sunday',3,'2012-06-03');
INSERT INTO `date_dim` VALUES (521,2012,2,6,'June',23,'Monday',4,'2012-06-04');
INSERT INTO `date_dim` VALUES (522,2012,2,6,'June',23,'Tuesday',5,'2012-06-05');
INSERT INTO `date_dim` VALUES (523,2012,2,6,'June',23,'Wednesday',6,'2012-06-06');
INSERT INTO `date_dim` VALUES (524,2012,2,6,'June',23,'Thursday',7,'2012-06-07');
INSERT INTO `date_dim` VALUES (525,2012,2,6,'June',23,'Friday',8,'2012-06-08');
INSERT INTO `date_dim` VALUES (526,2012,2,6,'June',23,'Saturday',9,'2012-06-09');
INSERT INTO `date_dim` VALUES (527,2012,2,6,'June',23,'Sunday',10,'2012-06-10');
INSERT INTO `date_dim` VALUES (528,2012,2,6,'June',24,'Monday',11,'2012-06-11');
INSERT INTO `date_dim` VALUES (529,2012,2,6,'June',24,'Tuesday',12,'2012-06-12');
INSERT INTO `date_dim` VALUES (530,2012,2,6,'June',24,'Wednesday',13,'2012-06-13');
INSERT INTO `date_dim` VALUES (531,2012,2,6,'June',24,'Thursday',14,'2012-06-14');
INSERT INTO `date_dim` VALUES (532,2012,2,6,'June',24,'Friday',15,'2012-06-15');
INSERT INTO `date_dim` VALUES (533,2012,2,6,'June',24,'Saturday',16,'2012-06-16');
INSERT INTO `date_dim` VALUES (534,2012,2,6,'June',24,'Sunday',17,'2012-06-17');
INSERT INTO `date_dim` VALUES (535,2012,2,6,'June',25,'Monday',18,'2012-06-18');
INSERT INTO `date_dim` VALUES (536,2012,2,6,'June',25,'Tuesday',19,'2012-06-19');
INSERT INTO `date_dim` VALUES (537,2012,2,6,'June',25,'Wednesday',20,'2012-06-20');
INSERT INTO `date_dim` VALUES (538,2012,2,6,'June',25,'Thursday',21,'2012-06-21');
INSERT INTO `date_dim` VALUES (539,2012,2,6,'June',25,'Friday',22,'2012-06-22');
INSERT INTO `date_dim` VALUES (540,2012,2,6,'June',25,'Saturday',23,'2012-06-23');
INSERT INTO `date_dim` VALUES (541,2012,2,6,'June',25,'Sunday',24,'2012-06-24');
INSERT INTO `date_dim` VALUES (542,2012,2,6,'June',26,'Monday',25,'2012-06-25');
INSERT INTO `date_dim` VALUES (543,2012,2,6,'June',26,'Tuesday',26,'2012-06-26');
INSERT INTO `date_dim` VALUES (544,2012,2,6,'June',26,'Wednesday',27,'2012-06-27');
INSERT INTO `date_dim` VALUES (545,2012,2,6,'June',26,'Thursday',28,'2012-06-28');
INSERT INTO `date_dim` VALUES (546,2012,2,6,'June',26,'Friday',29,'2012-06-29');
INSERT INTO `date_dim` VALUES (547,2012,2,6,'June',26,'Saturday',30,'2012-06-30');
INSERT INTO `date_dim` VALUES (548,2012,3,7,'July',26,'Sunday',1,'2012-07-01');
INSERT INTO `date_dim` VALUES (549,2012,3,7,'July',27,'Monday',2,'2012-07-02');
INSERT INTO `date_dim` VALUES (550,2012,3,7,'July',27,'Tuesday',3,'2012-07-03');
INSERT INTO `date_dim` VALUES (551,2012,3,7,'July',27,'Wednesday',4,'2012-07-04');
INSERT INTO `date_dim` VALUES (552,2012,3,7,'July',27,'Thursday',5,'2012-07-05');
INSERT INTO `date_dim` VALUES (553,2012,3,7,'July',27,'Friday',6,'2012-07-06');
INSERT INTO `date_dim` VALUES (554,2012,3,7,'July',27,'Saturday',7,'2012-07-07');
INSERT INTO `date_dim` VALUES (555,2012,3,7,'July',27,'Sunday',8,'2012-07-08');
INSERT INTO `date_dim` VALUES (556,2012,3,7,'July',28,'Monday',9,'2012-07-09');
INSERT INTO `date_dim` VALUES (557,2012,3,7,'July',28,'Tuesday',10,'2012-07-10');
INSERT INTO `date_dim` VALUES (558,2012,3,7,'July',28,'Wednesday',11,'2012-07-11');
INSERT INTO `date_dim` VALUES (559,2012,3,7,'July',28,'Thursday',12,'2012-07-12');
INSERT INTO `date_dim` VALUES (560,2012,3,7,'July',28,'Friday',13,'2012-07-13');
INSERT INTO `date_dim` VALUES (561,2012,3,7,'July',28,'Saturday',14,'2012-07-14');
INSERT INTO `date_dim` VALUES (562,2012,3,7,'July',28,'Sunday',15,'2012-07-15');
INSERT INTO `date_dim` VALUES (563,2012,3,7,'July',29,'Monday',16,'2012-07-16');
INSERT INTO `date_dim` VALUES (564,2012,3,7,'July',29,'Tuesday',17,'2012-07-17');
INSERT INTO `date_dim` VALUES (565,2012,3,7,'July',29,'Wednesday',18,'2012-07-18');
INSERT INTO `date_dim` VALUES (566,2012,3,7,'July',29,'Thursday',19,'2012-07-19');
INSERT INTO `date_dim` VALUES (567,2012,3,7,'July',29,'Friday',20,'2012-07-20');
INSERT INTO `date_dim` VALUES (568,2012,3,7,'July',29,'Saturday',21,'2012-07-21');
INSERT INTO `date_dim` VALUES (569,2012,3,7,'July',29,'Sunday',22,'2012-07-22');
INSERT INTO `date_dim` VALUES (570,2012,3,7,'July',30,'Monday',23,'2012-07-23');
INSERT INTO `date_dim` VALUES (571,2012,3,7,'July',30,'Tuesday',24,'2012-07-24');
INSERT INTO `date_dim` VALUES (572,2012,3,7,'July',30,'Wednesday',25,'2012-07-25');
INSERT INTO `date_dim` VALUES (573,2012,3,7,'July',30,'Thursday',26,'2012-07-26');
INSERT INTO `date_dim` VALUES (574,2012,3,7,'July',30,'Friday',27,'2012-07-27');
INSERT INTO `date_dim` VALUES (575,2012,3,7,'July',30,'Saturday',28,'2012-07-28');
INSERT INTO `date_dim` VALUES (576,2012,3,7,'July',30,'Sunday',29,'2012-07-29');
INSERT INTO `date_dim` VALUES (577,2012,3,7,'July',31,'Monday',30,'2012-07-30');
INSERT INTO `date_dim` VALUES (578,2012,3,7,'July',31,'Tuesday',31,'2012-07-31');
INSERT INTO `date_dim` VALUES (579,2012,3,8,'August',31,'Wednesday',1,'2012-08-01');
INSERT INTO `date_dim` VALUES (580,2012,3,8,'August',31,'Thursday',2,'2012-08-02');
INSERT INTO `date_dim` VALUES (581,2012,3,8,'August',31,'Friday',3,'2012-08-03');
INSERT INTO `date_dim` VALUES (582,2012,3,8,'August',31,'Saturday',4,'2012-08-04');
INSERT INTO `date_dim` VALUES (583,2012,3,8,'August',31,'Sunday',5,'2012-08-05');
INSERT INTO `date_dim` VALUES (584,2012,3,8,'August',32,'Monday',6,'2012-08-06');
INSERT INTO `date_dim` VALUES (585,2012,3,8,'August',32,'Tuesday',7,'2012-08-07');
INSERT INTO `date_dim` VALUES (586,2012,3,8,'August',32,'Wednesday',8,'2012-08-08');
INSERT INTO `date_dim` VALUES (587,2012,3,8,'August',32,'Thursday',9,'2012-08-09');
INSERT INTO `date_dim` VALUES (588,2012,3,8,'August',32,'Friday',10,'2012-08-10');
INSERT INTO `date_dim` VALUES (589,2012,3,8,'August',32,'Saturday',11,'2012-08-11');
INSERT INTO `date_dim` VALUES (590,2012,3,8,'August',32,'Sunday',12,'2012-08-12');
INSERT INTO `date_dim` VALUES (591,2012,3,8,'August',33,'Monday',13,'2012-08-13');
INSERT INTO `date_dim` VALUES (592,2012,3,8,'August',33,'Tuesday',14,'2012-08-14');
INSERT INTO `date_dim` VALUES (593,2012,3,8,'August',33,'Wednesday',15,'2012-08-15');
INSERT INTO `date_dim` VALUES (594,2012,3,8,'August',33,'Thursday',16,'2012-08-16');
INSERT INTO `date_dim` VALUES (595,2012,3,8,'August',33,'Friday',17,'2012-08-17');
INSERT INTO `date_dim` VALUES (596,2012,3,8,'August',33,'Saturday',18,'2012-08-18');
INSERT INTO `date_dim` VALUES (597,2012,3,8,'August',33,'Sunday',19,'2012-08-19');
INSERT INTO `date_dim` VALUES (598,2012,3,8,'August',34,'Monday',20,'2012-08-20');
INSERT INTO `date_dim` VALUES (599,2012,3,8,'August',34,'Tuesday',21,'2012-08-21');
INSERT INTO `date_dim` VALUES (600,2012,3,8,'August',34,'Wednesday',22,'2012-08-22');
INSERT INTO `date_dim` VALUES (601,2012,3,8,'August',34,'Thursday',23,'2012-08-23');
INSERT INTO `date_dim` VALUES (602,2012,3,8,'August',34,'Friday',24,'2012-08-24');
INSERT INTO `date_dim` VALUES (603,2012,3,8,'August',34,'Saturday',25,'2012-08-25');
INSERT INTO `date_dim` VALUES (604,2012,3,8,'August',34,'Sunday',26,'2012-08-26');
INSERT INTO `date_dim` VALUES (605,2012,3,8,'August',35,'Monday',27,'2012-08-27');
INSERT INTO `date_dim` VALUES (606,2012,3,8,'August',35,'Tuesday',28,'2012-08-28');
INSERT INTO `date_dim` VALUES (607,2012,3,8,'August',35,'Wednesday',29,'2012-08-29');
INSERT INTO `date_dim` VALUES (608,2012,3,8,'August',35,'Thursday',30,'2012-08-30');
INSERT INTO `date_dim` VALUES (609,2012,3,8,'August',35,'Friday',31,'2012-08-31');
INSERT INTO `date_dim` VALUES (610,2012,3,9,'September',35,'Saturday',1,'2012-09-01');
INSERT INTO `date_dim` VALUES (611,2012,3,9,'September',35,'Sunday',2,'2012-09-02');
INSERT INTO `date_dim` VALUES (612,2012,3,9,'September',36,'Monday',3,'2012-09-03');
INSERT INTO `date_dim` VALUES (613,2012,3,9,'September',36,'Tuesday',4,'2012-09-04');
INSERT INTO `date_dim` VALUES (614,2012,3,9,'September',36,'Wednesday',5,'2012-09-05');
INSERT INTO `date_dim` VALUES (615,2012,3,9,'September',36,'Thursday',6,'2012-09-06');
INSERT INTO `date_dim` VALUES (616,2012,3,9,'September',36,'Friday',7,'2012-09-07');
INSERT INTO `date_dim` VALUES (617,2012,3,9,'September',36,'Saturday',8,'2012-09-08');
INSERT INTO `date_dim` VALUES (618,2012,3,9,'September',36,'Sunday',9,'2012-09-09');
INSERT INTO `date_dim` VALUES (619,2012,3,9,'September',37,'Monday',10,'2012-09-10');
INSERT INTO `date_dim` VALUES (620,2012,3,9,'September',37,'Tuesday',11,'2012-09-11');
INSERT INTO `date_dim` VALUES (621,2012,3,9,'September',37,'Wednesday',12,'2012-09-12');
INSERT INTO `date_dim` VALUES (622,2012,3,9,'September',37,'Thursday',13,'2012-09-13');
INSERT INTO `date_dim` VALUES (623,2012,3,9,'September',37,'Friday',14,'2012-09-14');
INSERT INTO `date_dim` VALUES (624,2012,3,9,'September',37,'Saturday',15,'2012-09-15');
INSERT INTO `date_dim` VALUES (625,2012,3,9,'September',37,'Sunday',16,'2012-09-16');
INSERT INTO `date_dim` VALUES (626,2012,3,9,'September',38,'Monday',17,'2012-09-17');
INSERT INTO `date_dim` VALUES (627,2012,3,9,'September',38,'Tuesday',18,'2012-09-18');
INSERT INTO `date_dim` VALUES (628,2012,3,9,'September',38,'Wednesday',19,'2012-09-19');
INSERT INTO `date_dim` VALUES (629,2012,3,9,'September',38,'Thursday',20,'2012-09-20');
INSERT INTO `date_dim` VALUES (630,2012,3,9,'September',38,'Friday',21,'2012-09-21');
INSERT INTO `date_dim` VALUES (631,2012,3,9,'September',38,'Saturday',22,'2012-09-22');
INSERT INTO `date_dim` VALUES (632,2012,3,9,'September',38,'Sunday',23,'2012-09-23');
INSERT INTO `date_dim` VALUES (633,2012,3,9,'September',39,'Monday',24,'2012-09-24');
INSERT INTO `date_dim` VALUES (634,2012,3,9,'September',39,'Tuesday',25,'2012-09-25');
INSERT INTO `date_dim` VALUES (635,2012,3,9,'September',39,'Wednesday',26,'2012-09-26');
INSERT INTO `date_dim` VALUES (636,2012,3,9,'September',39,'Thursday',27,'2012-09-27');
INSERT INTO `date_dim` VALUES (637,2012,3,9,'September',39,'Friday',28,'2012-09-28');
INSERT INTO `date_dim` VALUES (638,2012,3,9,'September',39,'Saturday',29,'2012-09-29');
INSERT INTO `date_dim` VALUES (639,2012,3,9,'September',39,'Sunday',30,'2012-09-30');
INSERT INTO `date_dim` VALUES (640,2012,4,10,'October',40,'Monday',1,'2012-10-01');
INSERT INTO `date_dim` VALUES (641,2012,4,10,'October',40,'Tuesday',2,'2012-10-02');
INSERT INTO `date_dim` VALUES (642,2012,4,10,'October',40,'Wednesday',3,'2012-10-03');
INSERT INTO `date_dim` VALUES (643,2012,4,10,'October',40,'Thursday',4,'2012-10-04');
INSERT INTO `date_dim` VALUES (644,2012,4,10,'October',40,'Friday',5,'2012-10-05');
INSERT INTO `date_dim` VALUES (645,2012,4,10,'October',40,'Saturday',6,'2012-10-06');
INSERT INTO `date_dim` VALUES (646,2012,4,10,'October',40,'Sunday',7,'2012-10-07');
INSERT INTO `date_dim` VALUES (647,2012,4,10,'October',41,'Monday',8,'2012-10-08');
INSERT INTO `date_dim` VALUES (648,2012,4,10,'October',41,'Tuesday',9,'2012-10-09');
INSERT INTO `date_dim` VALUES (649,2012,4,10,'October',41,'Wednesday',10,'2012-10-10');
INSERT INTO `date_dim` VALUES (650,2012,4,10,'October',41,'Thursday',11,'2012-10-11');
INSERT INTO `date_dim` VALUES (651,2012,4,10,'October',41,'Friday',12,'2012-10-12');
INSERT INTO `date_dim` VALUES (652,2012,4,10,'October',41,'Saturday',13,'2012-10-13');
INSERT INTO `date_dim` VALUES (653,2012,4,10,'October',41,'Sunday',14,'2012-10-14');
INSERT INTO `date_dim` VALUES (654,2012,4,10,'October',42,'Monday',15,'2012-10-15');
INSERT INTO `date_dim` VALUES (655,2012,4,10,'October',42,'Tuesday',16,'2012-10-16');
INSERT INTO `date_dim` VALUES (656,2012,4,10,'October',42,'Wednesday',17,'2012-10-17');
INSERT INTO `date_dim` VALUES (657,2012,4,10,'October',42,'Thursday',18,'2012-10-18');
INSERT INTO `date_dim` VALUES (658,2012,4,10,'October',42,'Friday',19,'2012-10-19');
INSERT INTO `date_dim` VALUES (659,2012,4,10,'October',42,'Saturday',20,'2012-10-20');
INSERT INTO `date_dim` VALUES (660,2012,4,10,'October',42,'Sunday',21,'2012-10-21');
INSERT INTO `date_dim` VALUES (661,2012,4,10,'October',43,'Monday',22,'2012-10-22');
INSERT INTO `date_dim` VALUES (662,2012,4,10,'October',43,'Tuesday',23,'2012-10-23');
INSERT INTO `date_dim` VALUES (663,2012,4,10,'October',43,'Wednesday',24,'2012-10-24');
INSERT INTO `date_dim` VALUES (664,2012,4,10,'October',43,'Thursday',25,'2012-10-25');
INSERT INTO `date_dim` VALUES (665,2012,4,10,'October',43,'Friday',26,'2012-10-26');
INSERT INTO `date_dim` VALUES (666,2012,4,10,'October',43,'Saturday',27,'2012-10-27');
INSERT INTO `date_dim` VALUES (667,2012,4,10,'October',43,'Sunday',28,'2012-10-28');
INSERT INTO `date_dim` VALUES (668,2012,4,10,'October',44,'Monday',29,'2012-10-29');
INSERT INTO `date_dim` VALUES (669,2012,4,10,'October',44,'Tuesday',30,'2012-10-30');
INSERT INTO `date_dim` VALUES (670,2012,4,10,'October',44,'Wednesday',31,'2012-10-31');
INSERT INTO `date_dim` VALUES (671,2012,4,11,'November',44,'Thursday',1,'2012-11-01');
INSERT INTO `date_dim` VALUES (672,2012,4,11,'November',44,'Friday',2,'2012-11-02');
INSERT INTO `date_dim` VALUES (673,2012,4,11,'November',44,'Saturday',3,'2012-11-03');
INSERT INTO `date_dim` VALUES (674,2012,4,11,'November',44,'Sunday',4,'2012-11-04');
INSERT INTO `date_dim` VALUES (675,2012,4,11,'November',45,'Monday',5,'2012-11-05');
INSERT INTO `date_dim` VALUES (676,2012,4,11,'November',45,'Tuesday',6,'2012-11-06');
INSERT INTO `date_dim` VALUES (677,2012,4,11,'November',45,'Wednesday',7,'2012-11-07');
INSERT INTO `date_dim` VALUES (678,2012,4,11,'November',45,'Thursday',8,'2012-11-08');
INSERT INTO `date_dim` VALUES (679,2012,4,11,'November',45,'Friday',9,'2012-11-09');
INSERT INTO `date_dim` VALUES (680,2012,4,11,'November',45,'Saturday',10,'2012-11-10');
INSERT INTO `date_dim` VALUES (681,2012,4,11,'November',45,'Sunday',11,'2012-11-11');
INSERT INTO `date_dim` VALUES (682,2012,4,11,'November',46,'Monday',12,'2012-11-12');
INSERT INTO `date_dim` VALUES (683,2012,4,11,'November',46,'Tuesday',13,'2012-11-13');
INSERT INTO `date_dim` VALUES (684,2012,4,11,'November',46,'Wednesday',14,'2012-11-14');
INSERT INTO `date_dim` VALUES (685,2012,4,11,'November',46,'Thursday',15,'2012-11-15');
INSERT INTO `date_dim` VALUES (686,2012,4,11,'November',46,'Friday',16,'2012-11-16');
INSERT INTO `date_dim` VALUES (687,2012,4,11,'November',46,'Saturday',17,'2012-11-17');
INSERT INTO `date_dim` VALUES (688,2012,4,11,'November',46,'Sunday',18,'2012-11-18');
INSERT INTO `date_dim` VALUES (689,2012,4,11,'November',47,'Monday',19,'2012-11-19');
INSERT INTO `date_dim` VALUES (690,2012,4,11,'November',47,'Tuesday',20,'2012-11-20');
INSERT INTO `date_dim` VALUES (691,2012,4,11,'November',47,'Wednesday',21,'2012-11-21');
INSERT INTO `date_dim` VALUES (692,2012,4,11,'November',47,'Thursday',22,'2012-11-22');
INSERT INTO `date_dim` VALUES (693,2012,4,11,'November',47,'Friday',23,'2012-11-23');
INSERT INTO `date_dim` VALUES (694,2012,4,11,'November',47,'Saturday',24,'2012-11-24');
INSERT INTO `date_dim` VALUES (695,2012,4,11,'November',47,'Sunday',25,'2012-11-25');
INSERT INTO `date_dim` VALUES (696,2012,4,11,'November',48,'Monday',26,'2012-11-26');
INSERT INTO `date_dim` VALUES (697,2012,4,11,'November',48,'Tuesday',27,'2012-11-27');
INSERT INTO `date_dim` VALUES (698,2012,4,11,'November',48,'Wednesday',28,'2012-11-28');
INSERT INTO `date_dim` VALUES (699,2012,4,11,'November',48,'Thursday',29,'2012-11-29');
INSERT INTO `date_dim` VALUES (700,2012,4,11,'November',48,'Friday',30,'2012-11-30');
INSERT INTO `date_dim` VALUES (701,2012,4,12,'December',48,'Saturday',1,'2012-12-01');
INSERT INTO `date_dim` VALUES (702,2012,4,12,'December',48,'Sunday',2,'2012-12-02');
INSERT INTO `date_dim` VALUES (703,2012,4,12,'December',49,'Monday',3,'2012-12-03');
INSERT INTO `date_dim` VALUES (704,2012,4,12,'December',49,'Tuesday',4,'2012-12-04');
INSERT INTO `date_dim` VALUES (705,2012,4,12,'December',49,'Wednesday',5,'2012-12-05');
INSERT INTO `date_dim` VALUES (706,2012,4,12,'December',49,'Thursday',6,'2012-12-06');
INSERT INTO `date_dim` VALUES (707,2012,4,12,'December',49,'Friday',7,'2012-12-07');
INSERT INTO `date_dim` VALUES (708,2012,4,12,'December',49,'Saturday',8,'2012-12-08');
INSERT INTO `date_dim` VALUES (709,2012,4,12,'December',49,'Sunday',9,'2012-12-09');
INSERT INTO `date_dim` VALUES (710,2012,4,12,'December',50,'Monday',10,'2012-12-10');
INSERT INTO `date_dim` VALUES (711,2012,4,12,'December',50,'Tuesday',11,'2012-12-11');
INSERT INTO `date_dim` VALUES (712,2012,4,12,'December',50,'Wednesday',12,'2012-12-12');
INSERT INTO `date_dim` VALUES (713,2012,4,12,'December',50,'Thursday',13,'2012-12-13');
INSERT INTO `date_dim` VALUES (714,2012,4,12,'December',50,'Friday',14,'2012-12-14');
INSERT INTO `date_dim` VALUES (715,2012,4,12,'December',50,'Saturday',15,'2012-12-15');
INSERT INTO `date_dim` VALUES (716,2012,4,12,'December',50,'Sunday',16,'2012-12-16');
INSERT INTO `date_dim` VALUES (717,2012,4,12,'December',51,'Monday',17,'2012-12-17');
INSERT INTO `date_dim` VALUES (718,2012,4,12,'December',51,'Tuesday',18,'2012-12-18');
INSERT INTO `date_dim` VALUES (719,2012,4,12,'December',51,'Wednesday',19,'2012-12-19');
INSERT INTO `date_dim` VALUES (720,2012,4,12,'December',51,'Thursday',20,'2012-12-20');
INSERT INTO `date_dim` VALUES (721,2012,4,12,'December',51,'Friday',21,'2012-12-21');
INSERT INTO `date_dim` VALUES (722,2012,4,12,'December',51,'Saturday',22,'2012-12-22');
INSERT INTO `date_dim` VALUES (723,2012,4,12,'December',51,'Sunday',23,'2012-12-23');
INSERT INTO `date_dim` VALUES (724,2012,4,12,'December',52,'Monday',24,'2012-12-24');
INSERT INTO `date_dim` VALUES (725,2012,4,12,'December',52,'Tuesday',25,'2012-12-25');
INSERT INTO `date_dim` VALUES (726,2012,4,12,'December',52,'Wednesday',26,'2012-12-26');
INSERT INTO `date_dim` VALUES (727,2012,4,12,'December',52,'Thursday',27,'2012-12-27');
INSERT INTO `date_dim` VALUES (728,2012,4,12,'December',52,'Friday',28,'2012-12-28');
INSERT INTO `date_dim` VALUES (729,2012,4,12,'December',52,'Saturday',29,'2012-12-29');
INSERT INTO `date_dim` VALUES (730,2012,4,12,'December',52,'Sunday',30,'2012-12-30');
INSERT INTO `date_dim` VALUES (731,2012,4,12,'December',1,'Monday',31,'2012-12-31');
/*!40000 ALTER TABLE `date_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussion_activity_fact`
--

DROP TABLE IF EXISTS `discussion_activity_fact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussion_activity_fact` (
  `discussion_sk` int(10) unsigned NOT NULL,
  `project_sk` int(10) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `event_sk` smallint(5) unsigned NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL COMMENT 'Degenerated time dimension in hour granularity.',
  `count` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`discussion_sk`,`project_sk`,`date_sk`,`event_sk`,`hour`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_99 VALUES LESS THAN (99) ENGINE = MyISAM,
 PARTITION p_189 VALUES LESS THAN (189) ENGINE = MyISAM,
 PARTITION p_279 VALUES LESS THAN (279) ENGINE = MyISAM,
 PARTITION p_369 VALUES LESS THAN (369) ENGINE = MyISAM,
 PARTITION p_459 VALUES LESS THAN (459) ENGINE = MyISAM,
 PARTITION p_549 VALUES LESS THAN (549) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussion_activity_fact`
--
-- ORDER BY:  `discussion_sk`,`project_sk`,`date_sk`,`event_sk`,`hour`

LOCK TABLES `discussion_activity_fact` WRITE;
/*!40000 ALTER TABLE `discussion_activity_fact` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussion_activity_fact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussion_dim`
--

DROP TABLE IF EXISTS `discussion_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussion_dim` (
  `discussion_sk` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `discussion_name` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `author` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `moderators` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `subscribers` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `subject` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `forum_key` int(10) unsigned NOT NULL,
  `project_key` int(10) unsigned NOT NULL,
  `project_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `project_identifier` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime DEFAULT NULL,
  PRIMARY KEY (`discussion_sk`),
  KEY `name_idx` (`discussion_name`(16)),
  KEY `author_idx` (`author`(16)),
  KEY `discussion_key_idx` (`forum_key`),
  KEY `project_key_idx` (`project_key`),
  KEY `project_name_idx` (`project_name`(16)),
  KEY `project_identifier_idx` (`project_identifier`(16))
) ENGINE=MyISAM AUTO_INCREMENT=250 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussion_dim`
--
-- ORDER BY:  `discussion_sk`

LOCK TABLES `discussion_dim` WRITE;
/*!40000 ALTER TABLE `discussion_dim` DISABLE KEYS */;
INSERT INTO `discussion_dim` VALUES (1,'<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>',0,0,'<Inapplicable>','<Inapplicable>','0000-00-00 00:00:00','9999-00-00 00:00:00');
/*!40000 ALTER TABLE `discussion_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_dim`
--

DROP TABLE IF EXISTS `event_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_dim` (
  `event_sk` smallint(8) unsigned NOT NULL AUTO_INCREMENT,
  `action_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'Ticket created, Ticket deleted, Dibo message created, page_request',
  `CRUD` varchar(8) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'Create, Read, Update, Delete',
  `context` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'Wiki, Tickets, Discussion...',
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime DEFAULT NULL,
  PRIMARY KEY (`event_sk`),
  KEY `context_crud_idx` (`context`(4),`CRUD`(4)),
  KEY `action_name_idx` (`action_name`(16))
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_dim`
--
-- ORDER BY:  `event_sk`

LOCK TABLES `event_dim` WRITE;
/*!40000 ALTER TABLE `event_dim` DISABLE KEYS */;
INSERT INTO `event_dim` VALUES (1,'<Inapplicable>','<None>','<Inapplicable>','0000-00-00 00:00:00','9999-00-00 00:00:00');
INSERT INTO `event_dim` VALUES (2,'wiki_created','Create','Wiki','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (3,'wiki_edited','Update','Wiki','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (4,'topic_created','Create','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (5,'topic_edited','Update','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (6,'topic_deleted','Delete','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (7,'message_created','Create','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (8,'message_edited','Update','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (9,'message_deleted','Delete','Discussion','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (10,'page_request','Read','Project','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (11,'ticket_created','Create','Ticket','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (12,'ticket_closed','Update','Ticket','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (13,'source_checkin','Update','Source','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (14,'source_checkout','Read','Source','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (15,'file_uploaded','Create','Files','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (16,'file_downloaded','Read','Files','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (17,'file_moved','Update','Files','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (18,'file_deleted','Delete','Files','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (19,'release_downloaded','Read','Releases','2011-01-27 09:08:05',NULL);
INSERT INTO `event_dim` VALUES (20,'release_uploaded','Create','Releases','2011-01-27 09:08:05',NULL);
/*!40000 ALTER TABLE `event_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_fact`
--

DROP TABLE IF EXISTS `event_fact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_fact` (
  `date_sk` smallint(5) unsigned NOT NULL,
  `project_sk` mediumint(8) unsigned NOT NULL,
  `user_sk` mediumint(8) unsigned NOT NULL,
  `event_sk` smallint(5) unsigned NOT NULL,
  `discussion_sk` int(10) unsigned NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `micros` mediumint(5) unsigned NOT NULL,
  PRIMARY KEY (`date_sk`,`project_sk`,`user_sk`,`event_sk`,`timestamp`,`micros`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_91 VALUES LESS THAN (91) ENGINE = MyISAM,
 PARTITION p_121 VALUES LESS THAN (121) ENGINE = MyISAM,
 PARTITION p_151 VALUES LESS THAN (151) ENGINE = MyISAM,
 PARTITION p_181 VALUES LESS THAN (181) ENGINE = MyISAM,
 PARTITION p_211 VALUES LESS THAN (211) ENGINE = MyISAM,
 PARTITION p_241 VALUES LESS THAN (241) ENGINE = MyISAM,
 PARTITION p_271 VALUES LESS THAN (271) ENGINE = MyISAM,
 PARTITION p_301 VALUES LESS THAN (301) ENGINE = MyISAM,
 PARTITION p_331 VALUES LESS THAN (331) ENGINE = MyISAM,
 PARTITION p_361 VALUES LESS THAN (361) ENGINE = MyISAM,
 PARTITION p_391 VALUES LESS THAN (391) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_fact`
--
-- ORDER BY:  `date_sk`,`project_sk`,`user_sk`,`event_sk`,`timestamp`,`micros`

LOCK TABLES `event_fact` WRITE;
/*!40000 ALTER TABLE `event_fact` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_fact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_activity_fact`
--

DROP TABLE IF EXISTS `project_activity_fact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_activity_fact` (
  `project_sk` mediumint(8) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `event_sk` smallint(5) unsigned NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL COMMENT 'Degenerated hour dimension.',
  `count` int(10) unsigned NOT NULL COMMENT 'Actual fact. Count of events in the specified time.',
  PRIMARY KEY (`project_sk`,`date_sk`,`event_sk`,`hour`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='project activity counts collected in hourly level'
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_99 VALUES LESS THAN (99) ENGINE = MyISAM,
 PARTITION p_189 VALUES LESS THAN (189) ENGINE = MyISAM,
 PARTITION p_279 VALUES LESS THAN (279) ENGINE = MyISAM,
 PARTITION p_369 VALUES LESS THAN (369) ENGINE = MyISAM,
 PARTITION p_459 VALUES LESS THAN (459) ENGINE = MyISAM,
 PARTITION p_549 VALUES LESS THAN (549) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_activity_fact`
--
-- ORDER BY:  `project_sk`,`date_sk`,`event_sk`,`hour`

LOCK TABLES `project_activity_fact` WRITE;
/*!40000 ALTER TABLE `project_activity_fact` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_activity_fact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_dim`
--

DROP TABLE IF EXISTS `project_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_dim` (
  `project_sk` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `identifier` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `project_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `author` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `created` datetime NOT NULL,
  `updated` datetime DEFAULT NULL,
  `published` datetime DEFAULT NULL,
  `project_key` int(10) unsigned NOT NULL,
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime DEFAULT NULL,
  PRIMARY KEY (`project_sk`),
  KEY `created_idx` (`created`) USING BTREE,
  KEY `updated_idx` (`updated`) USING BTREE,
  KEY `published_idx` (`published`) USING BTREE,
  KEY `identifier_idx` (`identifier`(16)) USING BTREE,
  KEY `name_idx` (`project_name`(16)) USING BTREE,
  KEY `author_idx` (`author`(16)) USING BTREE,
  KEY `project_key_idx` (`project_key`)
) ENGINE=MyISAM AUTO_INCREMENT=2715 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_dim`
--
-- ORDER BY:  `project_sk`

LOCK TABLES `project_dim` WRITE;
/*!40000 ALTER TABLE `project_dim` DISABLE KEYS */;
INSERT INTO `project_dim` VALUES (1,'<Inapplicable>','<Inapplicable>','<Inapplicable>','0000-00-00 00:00:00','0000-00-00 00:00:00','0000-00-00 00:00:00',0,'0000-00-00 00:00:00','9999-00-00 00:00:00');
INSERT INTO `project_dim` VALUES (2,'home','Home environment','<Inapplicable>','0000-00-00 00:00:00','0000-00-00 00:00:00','0000-00-00 00:00:00',0,'2011-01-27 09:08:05',NULL);
/*!40000 ALTER TABLE `project_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request_fact`
--

DROP TABLE IF EXISTS `request_fact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request_fact` (
  `project_sk` mediumint(8) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `context_sk` tinyint(3) unsigned NOT NULL,
  `user_sk` int(10) unsigned NOT NULL,
  `datetime` datetime NOT NULL,
  `micros` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`project_sk`,`date_sk`,`context_sk`,`user_sk`,`datetime`,`micros`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Page request activity'
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_79 VALUES LESS THAN (79) ENGINE = MyISAM,
 PARTITION p_109 VALUES LESS THAN (109) ENGINE = MyISAM,
 PARTITION p_139 VALUES LESS THAN (139) ENGINE = MyISAM,
 PARTITION p_169 VALUES LESS THAN (169) ENGINE = MyISAM,
 PARTITION p_199 VALUES LESS THAN (199) ENGINE = MyISAM,
 PARTITION p_229 VALUES LESS THAN (229) ENGINE = MyISAM,
 PARTITION p_259 VALUES LESS THAN (259) ENGINE = MyISAM,
 PARTITION p_289 VALUES LESS THAN (289) ENGINE = MyISAM,
 PARTITION p_319 VALUES LESS THAN (319) ENGINE = MyISAM,
 PARTITION p_349 VALUES LESS THAN (349) ENGINE = MyISAM,
 PARTITION p_379 VALUES LESS THAN (379) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request_fact`
--
-- ORDER BY:  `project_sk`,`date_sk`,`context_sk`,`user_sk`,`datetime`,`micros`

LOCK TABLES `request_fact` WRITE;
/*!40000 ALTER TABLE `request_fact` DISABLE KEYS */;
/*!40000 ALTER TABLE `request_fact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request_hour_summary`
--

DROP TABLE IF EXISTS `request_hour_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request_hour_summary` (
  `project_sk` mediumint(8) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `context_sk` tinyint(3) unsigned NOT NULL,
  `user_sk` int(10) unsigned NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL,
  `count` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`project_sk`,`date_sk`,`context_sk`,`user_sk`,`hour`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Page request activity'
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_169 VALUES LESS THAN (169) ENGINE = MyISAM,
 PARTITION p_259 VALUES LESS THAN (259) ENGINE = MyISAM,
 PARTITION p_349 VALUES LESS THAN (349) ENGINE = MyISAM,
 PARTITION p_439 VALUES LESS THAN (439) ENGINE = MyISAM,
 PARTITION p_529 VALUES LESS THAN (529) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request_hour_summary`
--
-- ORDER BY:  `project_sk`,`date_sk`,`context_sk`,`user_sk`,`hour`

LOCK TABLES `request_hour_summary` WRITE;
/*!40000 ALTER TABLE `request_hour_summary` DISABLE KEYS */;
/*!40000 ALTER TABLE `request_hour_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request_project_summary`
--

DROP TABLE IF EXISTS `request_project_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request_project_summary` (
  `project_sk` mediumint(8) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `context_sk` tinyint(3) unsigned NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL,
  `count` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`project_sk`,`date_sk`,`context_sk`,`hour`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Page request activity summary for project'
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_169 VALUES LESS THAN (169) ENGINE = MyISAM,
 PARTITION p_259 VALUES LESS THAN (259) ENGINE = MyISAM,
 PARTITION p_349 VALUES LESS THAN (349) ENGINE = MyISAM,
 PARTITION p_439 VALUES LESS THAN (439) ENGINE = MyISAM,
 PARTITION p_529 VALUES LESS THAN (529) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request_project_summary`
--
-- ORDER BY:  `project_sk`,`date_sk`,`context_sk`,`hour`

LOCK TABLES `request_project_summary` WRITE;
/*!40000 ALTER TABLE `request_project_summary` DISABLE KEYS */;
/*!40000 ALTER TABLE `request_project_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_activity_fact`
--

DROP TABLE IF EXISTS `user_activity_fact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_activity_fact` (
  `user_sk` int(10) unsigned NOT NULL,
  `date_sk` smallint(5) unsigned NOT NULL,
  `event_sk` smallint(5) unsigned NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL COMMENT 'Degenerated time dimension in hour granularity.',
  `count` int(11) NOT NULL COMMENT 'Actual fact. Count of events in an hour.',
  PRIMARY KEY (`user_sk`,`date_sk`,`event_sk`,`hour`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
/*!50100 PARTITION BY RANGE (date_sk)
(PARTITION p_99 VALUES LESS THAN (99) ENGINE = MyISAM,
 PARTITION p_189 VALUES LESS THAN (189) ENGINE = MyISAM,
 PARTITION p_279 VALUES LESS THAN (279) ENGINE = MyISAM,
 PARTITION p_369 VALUES LESS THAN (369) ENGINE = MyISAM,
 PARTITION p_459 VALUES LESS THAN (459) ENGINE = MyISAM,
 PARTITION p_549 VALUES LESS THAN (549) ENGINE = MyISAM) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activity_fact`
--
-- ORDER BY:  `user_sk`,`date_sk`,`event_sk`,`hour`

LOCK TABLES `user_activity_fact` WRITE;
/*!40000 ALTER TABLE `user_activity_fact` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_activity_fact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_dim`
--

DROP TABLE IF EXISTS `user_dim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_dim` (
  `user_sk` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `mail` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `mobile` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `givenName` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `lastName` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `authentication` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `status` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `user_key` int(11) NOT NULL,
  `VALID_FROM` datetime NOT NULL,
  `VALID_TO` datetime DEFAULT NULL,
  PRIMARY KEY (`user_sk`),
  KEY `username_idx` (`username`(16)),
  KEY `mail_idx` (`mail`(16)),
  KEY `mobile_idx` (`mobile`(8)),
  KEY `given_name_idx` (`givenName`(16)),
  KEY `last_name_idx` (`lastName`(16)),
  KEY `status_idx` (`status`(8)),
  KEY `user_key_idx` (`user_key`),
  KEY `authentication_idx` (`authentication`)
) ENGINE=MyISAM AUTO_INCREMENT=7816 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_dim`
--
-- ORDER BY:  `user_sk`

LOCK TABLES `user_dim` WRITE;
/*!40000 ALTER TABLE `user_dim` DISABLE KEYS */;
INSERT INTO `user_dim` VALUES (1,'<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>','<Inapplicable>',0,'0000-00-00 00:00:00','9999-00-00 00:00:00');
INSERT INTO `user_dim` VALUES (2,'anonymous','','','','','<No organization>','active',0,'2011-01-27 07:24:02','2011-06-24 01:00:15');
/*!40000 ALTER TABLE `user_dim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'trac_analytical'
--
/*!50003 DROP PROCEDURE IF EXISTS `pre_populate_date` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`tracuser`@`localhost`*/ /*!50003 PROCEDURE `pre_populate_date`(IN start_dt DATE, IN end_dt DATE)
BEGIN
    WHILE start_dt <= end_dt DO
        INSERT INTO date_dim(
          date_sk
        , year
        , quarter
        , month
        , month_name
        , week
        , week_day
        , day_of_month
        , date
        )
        VALUES(
          NULL
        , YEAR(start_dt)
        , QUARTER(start_dt)
        , MONTH(start_dt)
        , MONTHNAME(start_dt)
        , WEEKOFYEAR(start_dt)
        , DAYNAME(start_dt)
        , DAYOFMONTH(start_dt)
        , start_dt
        );
        SET start_dt = ADDDATE(start_dt, 1);
    END WHILE;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
DELIMITER ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-11-28 15:43:36

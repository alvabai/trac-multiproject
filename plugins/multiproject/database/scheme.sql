-- MySQL dump 10.11
--
-- Host: 127.0.0.1    Database: trac_admin
-- ------------------------------------------------------
-- Server version	5.0.77

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
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `action` (
  `action_id` tinyint(3) unsigned NOT NULL auto_increment,
  `action_string` varchar(32) collate utf8_bin NOT NULL,
  PRIMARY KEY  USING BTREE (`action_id`),
  UNIQUE KEY `action_string` (`action_string`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_cookie`
--

DROP TABLE IF EXISTS `auth_cookie`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_cookie` (
  `cookie` text collate utf8_bin NOT NULL,
  `name` text collate utf8_bin NOT NULL,
  `ipnr` text collate utf8_bin NOT NULL,
  `time` int(11) default NULL,
  PRIMARY KEY  (`cookie`(111),`ipnr`(111),`name`(111))
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `categories` (
  `category_id` smallint(5) unsigned NOT NULL auto_increment,
  `category_name` varchar(64) collate utf8_bin NOT NULL,
  `description` varchar(256) collate utf8_bin NOT NULL,
  `parent_id` smallint(5) unsigned default NULL,
  `context_id` tinyint(4) unsigned NOT NULL,
  PRIMARY KEY  (`category_id`),
  UNIQUE KEY `cat` (`category_name`),
  KEY `categories_fk_parent` (`parent_id`),
  KEY `categories_fk_contexts` (`context_id`),
  CONSTRAINT `categories_fk_contexts` FOREIGN KEY (`context_id`) REFERENCES `contexts` (`context_id`),
  CONSTRAINT `categories_fk_parent` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=307 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Categories';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `contexts`
--

DROP TABLE IF EXISTS `contexts`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `contexts` (
  `context_id` tinyint(3) unsigned NOT NULL auto_increment,
  `context_name` varchar(63) collate utf8_bin NOT NULL,
  `context_description` varchar(255) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`context_id`),
  UNIQUE KEY `contx` (`context_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Contexes that categories can belong to';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `group` (
  `group_id` int(10) unsigned NOT NULL auto_increment,
  `group_name` varchar(127) collate utf8_bin NOT NULL,
  `project_key` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`group_id`),
  UNIQUE KEY `project_group_name` (`project_key`,`group_name`(16)),
  KEY `project` (`project_key`),
  CONSTRAINT `group_fk_project` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=132697 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User groups';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `group_permission`
--

DROP TABLE IF EXISTS `group_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `group_permission` (
  `group_key` int(10) unsigned NOT NULL,
  `permission_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY  (`group_key`,`permission_key`),
  KEY `permission` (`permission_key`),
  CONSTRAINT `gp_fk_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `gp_fk_permission` FOREIGN KEY (`permission_key`) REFERENCES `action` (`action_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Group permissions';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `group_template`
--

DROP TABLE IF EXISTS `group_template`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `group_template` (
  `group_template_id` smallint(5) unsigned NOT NULL auto_increment,
  `group_template_name` varchar(255) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`group_template_id`),
  UNIQUE KEY `name` (`group_template_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='User group template';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `group_template_permission`
--

DROP TABLE IF EXISTS `group_template_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `group_template_permission` (
  `group_template_key` smallint(5) unsigned NOT NULL,
  `permission_key` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY  (`group_template_key`,`permission_key`),
  KEY `fk_template_permissions` (`permission_key`),
  CONSTRAINT `fk_template_permissions` FOREIGN KEY (`permission_key`) REFERENCES `action` (`action_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_template_template` FOREIGN KEY (`group_template_key`) REFERENCES `group_template` (`group_template_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Permissions belonging for group templates';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `membership_request`
--

DROP TABLE IF EXISTS `membership_request`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `membership_request` (
  `project_key` int(10) unsigned NOT NULL,
  `user_key` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`project_key`,`user_key`),
  KEY `fk_membership_req_user` (`user_key`),
  CONSTRAINT `fk_membership_req_project` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_membership_req_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `migration`
--

DROP TABLE IF EXISTS `migration`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `migration` (
  `migration_name` varchar(255) collate utf8_bin NOT NULL,
  `datetime` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`migration_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table to track migration status';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `organization`
--

DROP TABLE IF EXISTS `organization`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `organization` (
  `organization_id` tinyint(3) unsigned NOT NULL auto_increment COMMENT 'TINYINT allows only 256 organizations',
  `organization_name` varchar(128) collate utf8_bin NOT NULL,
  `authentication_method` enum('LDAP','Ovi','Forum','LocalDB') collate utf8_bin NOT NULL,
  `sorting` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`organization_id`),
  UNIQUE KEY `uniq_name` (`organization_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `organization_group`
--

DROP TABLE IF EXISTS `organization_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `organization_group` (
  `organization_key` tinyint(3) unsigned NOT NULL,
  `group_key` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`group_key`,`organization_key`),
  KEY `fk_org_group_to_org` (`organization_key`),
  CONSTRAINT `fk_org_group_to_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_org_group_to_org` FOREIGN KEY (`organization_key`) REFERENCES `organization` (`organization_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Maps organizations into groups';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `project_activity`
--

DROP TABLE IF EXISTS `project_activity`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `project_activity` (
  `project_key` int(10) unsigned NOT NULL default '0',
  `ticket_changes` int(11) default NULL,
  `wiki_changes` int(11) default NULL,
  `scm_changes` int(11) default NULL,
  `attachment_changes` int(11) default NULL,
  `last_update` datetime default NULL,
  `project_description` varchar(255) collate utf8_bin default NULL,
  `discussion_changes` int(11) default NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `project_archive`
--

DROP TABLE IF EXISTS `project_archive`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `project_archive` (
  `project_archive_id` int(10) unsigned NOT NULL auto_increment,
  `orig_project_id` int(10) unsigned NOT NULL,
  `project_name` varchar(64) collate utf8_bin NOT NULL,
  `environment_name` varchar(32) collate utf8_bin NOT NULL,
  `orig_author_id` int(10) unsigned NOT NULL,
  `creation_date` datetime NOT NULL,
  `orig_parent_id` int(10) unsigned NOT NULL,
  `archive_folder_name` varchar(255) collate utf8_bin NOT NULL,
  `archived_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `remove_due` datetime NOT NULL,
  `removed_at` datetime default NULL,
  PRIMARY KEY  (`project_archive_id`)
) ENGINE=MyISAM AUTO_INCREMENT=136 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Archived projects';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `project_categories`
--

DROP TABLE IF EXISTS `project_categories`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `project_categories` (
  `project_key` int(10) unsigned NOT NULL,
  `category_key` smallint(5) unsigned NOT NULL,
  PRIMARY KEY  (`project_key`,`category_key`),
  KEY `pc_fk_categories` (`category_key`),
  CONSTRAINT `pc_fk_categories` FOREIGN KEY (`category_key`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pc_fk_projects` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Projects - Categories Mapping';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `project_icon`
--

DROP TABLE IF EXISTS `project_icon`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `project_icon` (
  `icon_id` int(11) NOT NULL auto_increment,
  `icon_data` blob NOT NULL,
  `content_type` varchar(64) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`icon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `project_tags`
--

DROP TABLE IF EXISTS `project_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `project_tags` (
  `project_key` int(10) unsigned NOT NULL,
  `tag_key` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY  (`project_key`,`tag_key`),
  KEY `new_fk_constraint2` (`tag_key`),
  CONSTRAINT `new_fk_constraint` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `new_fk_constraint2` FOREIGN KEY (`tag_key`) REFERENCES `tags` (`tag_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `projects` (
  `project_id` int(10) unsigned NOT NULL auto_increment,
  `project_name` varchar(64) collate utf8_bin NOT NULL,
  `environment_name` varchar(32) collate utf8_bin NOT NULL,
  `author` int(10) unsigned NOT NULL,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `published` datetime default NULL,
  `parent_id` int(10) unsigned default NULL,
  `icon_id` int(10) unsigned default NULL,
  PRIMARY KEY  (`project_id`),
  UNIQUE KEY `env_uniq` (`environment_name`),
  KEY `env_index` (`environment_name`(16)),
  KEY `name_index` (`project_name`),
  KEY `author_index` (`author`),
  KEY `parent_fk` (`parent_id`),
  CONSTRAINT `author_fk_user` FOREIGN KEY (`author`) REFERENCES `user` (`user_id`),
  CONSTRAINT `parent_fk` FOREIGN KEY (`parent_id`) REFERENCES `projects` (`project_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=686 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='List of all projects';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `super_user`
--

DROP TABLE IF EXISTS `super_user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `super_user` (
  `username` varchar(255) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`username`),
  CONSTRAINT `fk_super_username` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tags` (
  `tag_id` mediumint(8) unsigned NOT NULL auto_increment,
  `tag_name` varchar(64) collate utf8_bin NOT NULL,
  `tag_count` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY  (`tag_id`),
  UNIQUE KEY `tagname_idx` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='List of tags';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user` (
  `user_id` int(10) unsigned NOT NULL auto_increment,
  `username` varchar(255) collate utf8_bin NOT NULL,
  `mail` varchar(255) collate utf8_bin NOT NULL,
  `mobile` varchar(20) collate utf8_bin default NULL,
  `givenName` varchar(32) collate utf8_bin default NULL,
  `lastName` varchar(64) collate utf8_bin default NULL,
  `icon_id` int(10) unsigned default NULL,
  `SHA1_PW` varchar(40) collate utf8_bin NOT NULL,
  `insider` tinyint(1) NOT NULL default '0',
  `organization_key` tinyint(3) unsigned default NULL,
  `user_status_key` tinyint(3) unsigned NOT NULL default '1',
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `uniquser` (`username`),
  KEY `user_fast` (`username`(16)),
  KEY `fk_user_organization` (`organization_key`),
  KEY `fk_user_status` (`user_status_key`),
  CONSTRAINT `fk_user_organization` FOREIGN KEY (`organization_key`) REFERENCES `organization` (`organization_id`),
  CONSTRAINT `fk_user_status` FOREIGN KEY (`user_status_key`) REFERENCES `user_status` (`user_status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1817 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_group` (
  `user_key` int(10) unsigned NOT NULL,
  `group_key` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`user_key`,`group_key`),
  KEY `group_index` (`group_key`),
  CONSTRAINT `ug_fk_group` FOREIGN KEY (`group_key`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ug_fk_user` FOREIGN KEY (`user_key`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Maps users to groups';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_icon`
--

DROP TABLE IF EXISTS `user_icon`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_icon` (
  `icon_id` int(11) NOT NULL auto_increment,
  `icon_data` blob NOT NULL,
  `content_type` varchar(64) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`icon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_status`
--

DROP TABLE IF EXISTS `user_status`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_status` (
  `user_status_id` tinyint(3) unsigned NOT NULL auto_increment,
  `status_label` varchar(16) collate utf8_bin NOT NULL,
  PRIMARY KEY  (`user_status_id`),
  UNIQUE KEY `status_label_uniq` (`status_label`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'trac_admin'
--
DELIMITER ;;
DELIMITER ;

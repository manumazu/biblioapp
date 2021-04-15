-- MySQL dump 10.18  Distrib 10.3.27-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: bibliobus
-- ------------------------------------------------------
-- Server version	10.3.27-MariaDB-0+deb10u1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `biblio_app`
--

DROP TABLE IF EXISTS `biblio_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `arduino_name` varchar(64) NOT NULL,
  `id_ble` varchar(32) NOT NULL,
  `nb_lines` int(11) NOT NULL,
  `nb_cols` int(11) NOT NULL,
  `strip_length` float(5,1) NOT NULL COMMENT 'Length for LEDs strip in cm',
  `leds_interval` float(3,2) NOT NULL COMMENT 'Interval btw leds cm',
  `mood_color` varchar(16) DEFAULT NULL,
  `uuid` varchar(64) DEFAULT NULL,
  `mac` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_ble` (`id_ble`),
  UNIQUE KEY `mac` (`mac`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_book`
--

DROP TABLE IF EXISTS `biblio_book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_book` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) NOT NULL,
  `isbn` varchar(32) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `editor` varchar(255) DEFAULT NULL,
  `year` varchar(10) DEFAULT NULL,
  `pages` varchar(10) DEFAULT NULL,
  `reference` varchar(32) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `width` smallint(6) DEFAULT NULL COMMENT 'book width in cm',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`,`id_user`),
  KEY `id_user` (`id_user`),
  KEY `title` (`title`,`author`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_customcode`
--

DROP TABLE IF EXISTS `biblio_customcode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_customcode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) NOT NULL,
  `id_app` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `customvars` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `customcode` blob DEFAULT NULL,
  `date_add` datetime NOT NULL DEFAULT current_timestamp(),
  `date_upd` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `published` tinyint(1) NOT NULL DEFAULT 0,
  `position` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`,`id_app`),
  KEY `published` (`published`),
  KEY `id_user_2` (`id_user`,`id_app`,`published`),
  KEY `position` (`position`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_customcolors`
--

DROP TABLE IF EXISTS `biblio_customcolors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_customcolors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) NOT NULL,
  `id_app` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `coordinates` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `date_add` datetime NOT NULL DEFAULT current_timestamp(),
  `date_upd` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`,`id_app`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_position`
--

DROP TABLE IF EXISTS `biblio_position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_position` (
  `id_app` int(11) NOT NULL,
  `id_item` int(11) NOT NULL,
  `item_type` varchar(10) NOT NULL,
  `position` smallint(6) NOT NULL,
  `row` smallint(6) NOT NULL,
  `range` int(2) NOT NULL,
  `led_column` int(4) NOT NULL,
  `borrowed` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_app`,`id_item`,`item_type`,`row`),
  KEY `range` (`range`),
  KEY `id_app_4` (`id_app`,`id_item`,`position`,`row`),
  KEY `id_app` (`id_app`,`id_item`,`item_type`,`borrowed`),
  KEY `id_app_3` (`id_app`,`item_type`,`row`,`led_column`),
  KEY `id_app_2` (`id_app`,`item_type`,`position`,`row`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_request`
--

DROP TABLE IF EXISTS `biblio_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_request` (
  `id_app` int(11) NOT NULL,
  `id_node` int(11) NOT NULL,
  `id_tag` int(11) DEFAULT NULL,
  `color` varchar(16) DEFAULT NULL,
  `node_type` varchar(10) NOT NULL DEFAULT 'book',
  `column` smallint(5) NOT NULL,
  `row` smallint(5) NOT NULL,
  `range` smallint(5) NOT NULL,
  `date_add` datetime NOT NULL DEFAULT current_timestamp(),
  `sent` tinyint(4) NOT NULL DEFAULT 0,
  `led_column` int(5) NOT NULL,
  `action` enum('add','remove') NOT NULL,
  `client` varchar(10) NOT NULL DEFAULT 'server',
  PRIMARY KEY (`id_app`,`row`,`range`,`led_column`),
  KEY `id_app` (`id_app`,`id_node`,`node_type`),
  KEY `id_app_4` (`id_app`,`client`),
  KEY `id_app_5` (`id_app`,`client`,`action`),
  KEY `biblio_request_id_app_IDX` (`id_app`,`action`) USING BTREE,
  KEY `biblio_hasRequest` (`id_app`,`column`,`row`,`action`) USING BTREE,
  KEY `biblio_request_hasTag` (`id_app`,`id_tag`,`action`) USING BTREE,
  KEY `biblio_request_isSent` (`id_app`,`sent`,`action`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `biblio_search`
--

DROP TABLE IF EXISTS `biblio_search`;
/*!50001 DROP VIEW IF EXISTS `biblio_search`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `biblio_search` (
  `id_app` tinyint NOT NULL,
  `id` tinyint NOT NULL,
  `title` tinyint NOT NULL,
  `author` tinyint NOT NULL,
  `editor` tinyint NOT NULL,
  `description` tinyint NOT NULL,
  `tags` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `biblio_tag_node`
--

DROP TABLE IF EXISTS `biblio_tag_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_tag_node` (
  `node_type` varchar(10) NOT NULL,
  `id_node` int(11) NOT NULL,
  `id_tag` int(11) NOT NULL,
  UNIQUE KEY `node_type` (`node_type`,`id_node`,`id_tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_tag_user`
--

DROP TABLE IF EXISTS `biblio_tag_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_tag_user` (
  `id_tag` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `color` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id_tag`,`id_user`),
  UNIQUE KEY `biblio_tag_user_id_tag_IDX` (`id_tag`,`id_user`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='tag customize color for user';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_tags`
--

DROP TABLE IF EXISTS `biblio_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  `id_taxonomy` int(11) NOT NULL,
  `color` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`),
  KEY `id_taxonomy` (`id_taxonomy`),
  KEY `color` (`color`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_taxonomy`
--

DROP TABLE IF EXISTS `biblio_taxonomy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_taxonomy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_user`
--

DROP TABLE IF EXISTS `biblio_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `hash_email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `lastname` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `hash_email` (`hash_email`),
  KEY `email_2` (`email`,`password`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `biblio_user_app`
--

DROP TABLE IF EXISTS `biblio_user_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biblio_user_app` (
  `id_user` int(11) NOT NULL,
  `id_app` int(11) NOT NULL,
  PRIMARY KEY (`id_user`,`id_app`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'bibliobus'
--

--
-- Final view structure for view `biblio_search`
--

/*!50001 DROP TABLE IF EXISTS `biblio_search`*/;
/*!50001 DROP VIEW IF EXISTS `biblio_search`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013  SQL SECURITY DEFINER */
/*!50001 VIEW `biblio_search` AS select `p`.`id_app` AS `id_app`,`b`.`id` AS `id`,`b`.`title` AS `title`,`b`.`author` AS `author`,`b`.`editor` AS `editor`,`b`.`description` AS `description`,group_concat(' ',`t`.`tag` separator ',') AS `tags` from ((((`biblio_book` `b` left join `biblio_tag_node` `tn` on(`b`.`id` = `tn`.`id_node`)) join `biblio_tags` `t` on(`t`.`id` = `tn`.`id_tag`)) join `biblio_taxonomy` `taxo` on(`taxo`.`id` = `t`.`id_taxonomy`)) join `biblio_position` `p` on(`p`.`id_item` = `b`.`id` and `p`.`item_type` = 'book')) group by `b`.`id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-03-18 14:36:26

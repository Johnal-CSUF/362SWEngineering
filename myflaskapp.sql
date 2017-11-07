-- MySQL dump 10.13  Distrib 5.7.20, for Linux (x86_64)
--
-- Host: localhost    Database: myflaskapp
-- ------------------------------------------------------
-- Server version	5.7.20-0ubuntu0.16.04.1

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
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customers` (
  `CustID` int(5) NOT NULL,
  `Fname` varchar(20) NOT NULL,
  `Lname` varchar(30) NOT NULL,
  `Phone` varchar(15) NOT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `YTD_Sales` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`CustID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (18273,'Tana','Livingston','928-013-6823','Tana.Living@yahoo.com',NULL),(23847,'Justine','Fu','555-555-5555','justine.fu@gmail.com',NULL),(34811,'Hanna','Mila','909-398-0012','hanna.mila@gmail.com',NULL),(38217,'Julia','Lowell','909-312-1124','julia.lowell@gmail.com',NULL),(38821,'Henrike','Gwynn','626-901-3331','henrike.gwynn@gmail.com',NULL),(40182,'Kerry','Marika','909-321-8364','kerry.marika@gmail.com',NULL),(61938,'Ivona','Severin','909-213-5928','ivona.severin@yahoo.com',NULL);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `ItemNumber` int(5) NOT NULL,
  `CustID` int(5) NOT NULL,
  `OrderDate` varchar(10) NOT NULL,
  `Quantity` int(5) NOT NULL,
  PRIMARY KEY (`ItemNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (12383,19283,'03/14/2012',56),(12847,12938,'02/12/2006',12),(39851,94857,'03/05/2007',32),(47291,19384,'12/31/2000',102),(99933,47236,'03/21/2010',5);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `ItemNumber` int(10) unsigned NOT NULL,
  `Description` varchar(20) NOT NULL,
  `Available` int(5) unsigned NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  `Class` varchar(10) NOT NULL,
  `Origin` varchar(15) NOT NULL,
  `Lead_Time` varchar(20) NOT NULL,
  PRIMARY KEY (`ItemNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (15675,'Exhaust',213,799.99,'Ehaust','Japan','5-6 weeks'),(25531,'Bucket Seat',75,1299.99,'Interior','Italy','2-3 weeks'),(55677,'Coilovers',0,1399.99,'Suspension','Japan','4-6 weeks'),(63215,'Turbocharger',0,6299.99,'Enginer','USA','7-8 weeks'),(67052,'Oil Cap',47,59.99,'Engine','Japan','2-3 weeks'),(73372,'Filter',0,59.99,'Engine','Japan','1-2 weeks'),(74515,'Steering Wheel',75,199.99,'Interior','Italy','2-3 weeks'),(88222,'Intake',572,249.99,'Engine','Japan','3-4 weeks'),(98742,'Supercharger',0,4599.99,'Engine','USA','5-6 weeks');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reports`
--

DROP TABLE IF EXISTS `reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `author` varchar(100) DEFAULT NULL,
  `body` text,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reports`
--

LOCK TABLES `reports` WRITE;
/*!40000 ALTER TABLE `reports` DISABLE KEYS */;
INSERT INTO `reports` VALUES (12,'When The Edit Button Doesn\'t Want To WORK','AngNet','<p>I mentioned this in a previous report but I thought I&#39;d expand it a little onto another report cause this actually bothers me. Adding and deleting works just fine. I can get to the edit page after pressing the edit button but then once I try to submit the changes, I get an error. The error is weird too. Something about a long or len() type which I&#39;m not sure what it&#39;s talking about since I don&#39;t have long or len in any of my files. Sigh, we&#39;ll see what happens. I hope this works soon though because it would be nice to be able to edit on this application.&nbsp;</p>','2017-11-04 07:00:47'),(13,'Overview of the Team','CrazySailor','<p>This team is great. We don&#39;t have an official team name yet though so I don&#39;t know what we&#39;re called. I actually joined this team after being reassigned by our professor. I was told that they didn&#39;t have a team name. Now I&#39;m wondering what we should call ourselves. We&#39;re gonna present soon so we should have a team name to associate ourselves with right?&nbsp;</p>','2017-11-04 07:01:46'),(14,'World War III','Sharcade','<p>So many things are coming up. It&#39;s a battlefield out there. I hope my comrades are alright. Everyone seems ok besides the fact that midterms are upon us and are bombarding our base. For me, two of my miterms got moved to next week so I have 4 in one week. I need backup. Send help please. It&#39;s needed very much.&nbsp;</p>','2017-11-04 07:02:29'),(15,'Things still need to be done','Wizart','<p>As title says, lots of stuff still need to be done. There&#39;s also stuff that needs to be done in other projects but for this one, there&#39;s stuff that I want working that isn&#39;t working. For example, the edit button still doesn&#39;t want to work and I&#39;ve been researching days on it. I would leave it alone, work one something else, come back, research again, and then it doesn&#39;t work. Why edit button. Why.</p>','2017-11-04 07:03:05'),(16,'Going Strong','GamingBee','<p>So the team is doing well so far. We&#39;re currently in the 9th week of school and are getting closer to the deadline. We need to have our finished software done before thanksgiving break. I&#39;m sure that we&#39;re on the right track to getting there. I&#39;m surprised that the SRC requirement paper isn&#39;t due till the end of the semester. I feel better about that.</p>','2017-11-04 07:03:40'),(17,'Random Report','JollyEmu','<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed molestie, lorem a ultrices maximus, turpis sapien euismod nisl, eget finibus arcu augue convallis nisl. Ut dui leo, molestie id metus et, auctor ullamcorper ex. Nam dictum rutrum posuere. Maecenas eleifend elementum scelerisque. Sed dictum tristique lacus pharetra hendrerit. Sed porta enim eu ex faucibus interdum. Donec in libero lacus. Praesent ante ex, rhoncus eu elementum id, placerat quis purus. In quis purus mi.</p>','2017-11-04 07:04:13'),(18,'testfefvfvefvfvefvefvevevefv','shorts','<p>testsferrfvewrververvefvfvsfvfvfvsdfvdfvdfvdfs</p>','2017-11-04 18:48:51');
/*!40000 ALTER TABLE `reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `manager` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Net Ang','somethin@gmail.com','AngNet','$5$rounds=535000$RK4Oz1yJC3sWGeyi$iZMycGmteoKVmSsvz6c17d9x/AR24skaZqXnmaSxaq5','2017-10-05 02:16:04','yes'),(2,'Grant Goodman','grant.goodman@yahoo.com','Wizart','$5$rounds=535000$AILjikNCxPUNSK0c$jubQHL/xyyYJoFC.GzcZjnRgisZgLxfIMY..6DQKumA','2017-11-04 00:25:59','no'),(3,'Roxanne Yates','roxanne.yates@gmail.com','JollyEmu','$5$rounds=535000$MuRlUrBUfHYHt/Hh$isLRJtqVl3ut0b7nsYNpZOQ.gYFTQzNy2L.vJt70v08','2017-11-04 00:26:30','no'),(5,'Erika Tate','erika.tate@gmail.com','CrazySailor','$5$rounds=535000$WPfNfgk5eyXsGrVi$bK3RcVAaxWuwT.NDJDWQmCOhHXKiKPUkLQNgZhZK0Q5','2017-11-04 00:27:29','yes'),(6,'Kathy Jones','kathy.jones@yahoo.com','Griffinite','$5$rounds=535000$Tfiw0kfl.97SnsKz$YSJ/cB8XaB/7gtG2Uf1wj2KVS9Ioz.VDqTS2VEPed96','2017-11-04 00:27:53','no'),(7,'Delia Cain','deila.cain@gmail.com','Sharcade','$5$rounds=535000$ebn8MesLmEi6ITVA$dWqSbglV3RY24CCOetNbrgoY1DOtO7K/8YEzS1eXSN4','2017-11-04 00:28:35','no'),(8,'Oscar Hill','oscar.hill@gmail.com','GamingBee','$5$rounds=535000$wpO.whXmakdlGN7S$2jtpGN7aKpNl11Fc6Z7RRhpVowlRxfhSxtuPwZqGlH5','2017-11-04 00:29:04','yes'),(9,'Wilbert Bowers','wilbert.bowers@yahoo.com','Bachelord','$5$rounds=535000$4mtygB/Pmy/Qbfn8$BQ26JZx3jy3eF6QTNx6uDAj4Um4T.KrzLzfQdxfCKx3','2017-11-04 00:32:48','no');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-11-06 22:58:25

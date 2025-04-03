-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: db_forum
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_name` varchar(255) NOT NULL,
  `login` varchar(255) NOT NULL,
  `password` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_login` (`login`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Alex Di','Fix','$2b$12$ScYBgmZYzbHOtUNdJSSoB.KyuzZOG8tfIyU2n3qKvBAAvXpJgDG8.'),(5,'Гарри Поттер','Выживший','$2b$12$lUTkJPXnSiv1El9r5BoICu5zwk3roQuxS5xZ3qkYDP116td7tGtFm'),(6,'Vasya Pupkin','VasP','$2b$12$GGPvKlmoD7ReSwx6XaxAHOF9D46mM5wSfK/0jPtQ5kxvD5ayrYaSm'),(10,'Vasya Pupkin','PiVo','$2b$12$dsHIYNu2NheCaUR./yIke.EA7s80x.LZQK6iUfA/2.OprIg.vNDk6'),(11,'Vasya Pupkin','PiVk0','$2b$12$pwvz.RAQxJ4waWZ5SlsCx.hfkcsCwdwHi6QRaRz.FCKjIzXOExPkq'),(13,'Петрович','Petrovich','$2b$12$.zD/iwwfSYhbZ8q8wkgLN.ZQ7QZWrnhHFSGZDQ0vFFC1yH.qj0nHy'),(14,'Петрович','KKKetr','$2b$12$E7z0qZ/F2NViyMmJHCbXSeNMhBG1xsB/iTW9zsEeZRxqIxGhRSEVy'),(15,'Валерия','VaL','$2b$12$SljP0YmmWY8S.7q0qXw1lu9CAPp5e0xzQPvbyiHH9PDIdIgGVuIhK'),(16,'Test User','TUser','$2b$12$bV92rYyjxcLGitbc0M.Nb.nRNzfBE3t1sZefJ76M4fnk4wSyYLH5S');
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

-- Dump completed on 2025-04-03 20:05:05

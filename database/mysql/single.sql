CREATE TABLE IF NOT EXISTS `single` (
  `single_id` int unsigned NOT NULL AUTO_INCREMENT,
  `single_name` varchar(255) NOT NULL,
  `single_cover` varchar(255) DEFAULT NULL,
  `single_boomscore` int NOT NULL,
  `spotify_uid` varchar(22) DEFAULT NULL,
  `artists` varchar(255) DEFAULT NULL,
  `preview_url` varchar(255) DEFAULT NULL,
  `release_date` varchar(15) DEFAULT NULL,
  `likes` int unsigned DEFAULT '0',
  `dislikes` int unsigned DEFAULT '0',
   PRIMARY KEY (`single_id`),
   UNIQUE KEY `spotify_uid` (`spotify_uid`)
);


CREATE TABLE IF NOT EXISTS `album` (
  `album_id` int unsigned NOT NULL AUTO_INCREMENT,
  `album_cover` varchar(255) DEFAULT NULL,
  `album_name` varchar(255) NOT NULL,
  `album_boomscore` int NOT NULL,
  `spotify_uid` varchar(22) DEFAULT NULL,
  `tracks` json DEFAULT NULL,
  `artists` json DEFAULT NULL,
  `release_date` varchar(15) DEFAULT NULL,
  `likes` int unsigned DEFAULT 0,
  `dislikes` int unsigned DEFAULT 0,
  PRIMARY KEY (`album_id`),
  UNIQUE KEY `spotify_uid` (`spotify_uid`),
  FULLTEXT KEY `album_name_index` (`album_name`)
);


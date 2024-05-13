CREATE TABLE IF NOT EXISTS `album_entry` (
  `entry_id` int unsigned NOT NULL AUTO_INCREMENT,
  `entry_length` varchar(8) DEFAULT NULL,
  `album_id` int unsigned NOT NULL,
  `entry_name` varchar(255) NOT NULL,
  `spotify_uid` varchar(22) DEFAULT NULL,
  PRIMARY KEY (`entry_id`),
  UNIQUE KEY `spotify_uid` (`spotify_uid`),
  KEY `album_id` (`album_id`),
  CONSTRAINT `album_entry_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `album` (`album_id`)
);

CREATE TABLE IF NOT EXISTS `music` (
  `music_id` int unsigned NOT NULL AUTO_INCREMENT,
  `release_date` date DEFAULT NULL,
  `is_album` tinyint(1) NOT NULL,
  `single_id` int unsigned DEFAULT NULL,
  `album_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`music_id`),
  KEY `single_id` (`single_id`),
  KEY `album_id` (`album_id`),
  CONSTRAINT `music_ibfk_2` FOREIGN KEY (`single_id`) REFERENCES `single` (`single_id`) ON DELETE SET NULL,
  CONSTRAINT `music_ibfk_3` FOREIGN KEY (`album_id`) REFERENCES `album` (`album_id`) ON DELETE SET NULL
);

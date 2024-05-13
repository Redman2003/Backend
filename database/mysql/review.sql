CREATE TABLE IF NOT EXISTS `review` (
  `review_id` int unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int unsigned NOT NULL,
  `music_id` int unsigned NOT NULL,
  `like_count` int NOT NULL,
  `dislike_count` int NOT NULL,
  `creation_date` date NOT NULL DEFAULT (CURRENT_DATE()),
  `review` text NOT NULL,
  PRIMARY KEY (`review_id`),
  KEY `account_id` (`account_id`),
  KEY `music_id` (`music_id`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `acct` (`account_id`),
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`music_id`) REFERENCES `music` (`music_id`)
);

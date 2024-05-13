
CREATE TABLE IF NOT EXISTS `review_comment` (
  `review_comment_id` int unsigned NOT NULL AUTO_INCREMENT,
  `review_id` int unsigned NOT NULL,
  `comment` text NOT NULL,
  `like_count` int NOT NULL,
  `dislike_count` int NOT NULL,
  `creation_date` date NOT NULL,
  PRIMARY KEY (`review_comment_id`,`review_id`),
  KEY `review_comment_ibfk_1` (`review_id`),
  CONSTRAINT `review_comment_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `review` (`review_id`)
);


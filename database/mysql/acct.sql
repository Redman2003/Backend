CREATE TABLE IF NOT EXISTS`acct` (
  `account_id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `follower_count` int unsigned DEFAULT NULL,
  `following_count` int unsigned DEFAULT NULL,
  `creation_date` date DEFAULT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `user_email` (`user_email`),
  UNIQUE KEY `username` (`username`)
);

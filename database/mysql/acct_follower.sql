CREATE TABLE IF NOT EXISTS `acct_follower` (
  `follower_account_id` int unsigned NOT NULL,
  `following_account_id` int unsigned NOT NULL,
  PRIMARY KEY (`follower_account_id`,`following_account_id`),
  KEY `acct_follower_ibfk_2` (`following_account_id`),
  CONSTRAINT `acct_follower_ibfk_1` FOREIGN KEY (`follower_account_id`) REFERENCES `acct` (`account_id`),
  CONSTRAINT `acct_follower_ibfk_2` FOREIGN KEY (`following_account_id`) REFERENCES `acct` (`account_id`)
);

CREATE TABLE IF NOT EXISTS `acct_playlist_music` (
    `entry_id` int UNSIGNED NOT NULL AUTO_INCREMENT,
    `account_id` int UNSIGNED NOT NULL,
    `playlist_id` int UNSIGNED NOT NULL,
    `spotify_uid` varchar(22) NOT NULL,
    `image_url`	varchar(255),
    `song_name`	varchar(255),
    PRIMARY KEY (`entry_id`),
    CONSTRAINT `acct_playlist_music_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `acct` (`account_id`) ON DELETE CASCADE,
    CONSTRAINT `acct_playlist_music_ibfk_2` FOREIGN KEY (`playlist_id`) REFERENCES `playlist` (`playlist_id`) ON DELETE CASCADE
);


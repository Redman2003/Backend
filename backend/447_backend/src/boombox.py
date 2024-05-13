import os
import logging
from flask import Flask, jsonify, make_response, request
from database import MySQL_Database
from pathlib import Path
from files import read_file_in
from demo_4_16_24 import demo

from artist_endpoints.artist_crud import blueprint as artist_blueprint, artist_init_db
from single_endpoints.single_crud import blueprint as single_blueprint, single_init_db
from acct_endpoints.acct_crud import blueprint as acct_blueprint, acct_init_db
from album_endpoints.album_crud import blueprint as album_blueprint, album_init_db
from search_endpoint.search_endpoint import search_blueprint
from review_endpoints.review_crud import blueprint as review_blueprint, review_init_db
from review_endpoints.review_comment_crud import blueprint as review_comment_blueprint, review_comment_init_db
from playlist_endpoints.playlist_endpoint import playlist_blueprint as playlist_blueprint
from localData.localDataEndpoints import blueprint as localdata_blueprint
from music_endpoints.music_endpoint import blueprint as music_blueprint, music_init_db

# init log file
# print() will not work, so if you want to "print" anything...
# you will need to do app.logger.info(<message>) then check the log file.
logging.basicConfig(filename="boombox.log", format="%(levelname)s:%(name)s:%(message)s")

MYSQL_HOST = "monorail.proxy.rlwy.net"
MYSQL_USER = "root"
MYSQL_PASSWORD = "AdTuTnYhHQyeKOaiTDldwvDyLbTzWmIm"
MYSQL_DATABASE = "boombox"




# driver
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

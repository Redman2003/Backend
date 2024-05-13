import os
import logging
from flask import Flask, jsonify, make_response
from database import MySQL_Database
from files import read_file_in
from demo_4_16_24 import demo

from artist_endpoints.artist_crud import blueprint as artist_blueprint, artist_init_db
from single_endpoints.single_crud import blueprint as single_blueprint, single_init_db
from acct_endpoints.acct_crud import blueprint as acct_blueprint, acct_init_db
from album_endpoints.album_crud import blueprint as album_blueprint, album_init_db
from search_endpoint.search_endpoint import search_blueprint
from review_endpoints.review_crud import blueprint as review_blueprint, review_init_db
from review_endpoints.review_comment_crud import blueprint as review_comment_blueprint, review_comment_init_db
from playlist_endpoints.playlist_endpoint import playlist_blueprint as playlist_blueprint, playlist_init_db 


# init log file
# print() will not work, so if you want to "print" anything...
# you will need to do app.logger.info(<message>) then check the log file.
logging.basicConfig(filename="boombox.log", format="%(levelname)s:%(name)s:%(message)s")

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Mancity2003*"
MYSQL_DATABASE = "boombox"

# grab directory for mysql source files
# have to do this before running flask, or flask will break!
CWD = os.getcwd()
os.chdir("../../../database/mysql")
MYSQL_SOURCE_DIRECTORY = os.getcwd()
os.chdir(CWD)

# init flask
app = Flask(__name__)


app.register_blueprint(artist_blueprint)
app.register_blueprint(single_blueprint)
app.register_blueprint(acct_blueprint)
app.register_blueprint(album_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(review_blueprint)
app.register_blueprint(review_comment_blueprint)
app.register_blueprint(playlist_blueprint)




app_context = app.app_context()
app_context.push()


# init database
database = MySQL_Database(
    host = MYSQL_HOST,
    user = MYSQL_USER,
    password = MYSQL_PASSWORD
)

# Create database and use database
# Note: Will only create database if it does not already exist
database.create(MYSQL_DATABASE)

if not database.use(MYSQL_DATABASE):
    raise RuntimeError(f"Could not find database {MYSQL_DATABASE}")

# Create tables - they MUST be created in this order
# Note: This will only create tables if they do not already exist
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "artist.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "single.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "album.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "album_entry.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "music.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "acct.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "acct_follower.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "playlist.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "acct_playlist_music.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "review.sql"))
database.execute(read_file_in(MYSQL_SOURCE_DIRECTORY, "review_comment.sql"))

database.commit()

# Init databases for crud files

artist_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
single_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
acct_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
album_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
review_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
review_comment_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
playlist_init_db(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)



# update 4/16/2024
# demo(app, database)


# driver
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

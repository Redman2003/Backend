from flask import Flask
from album_endpoints.album_crud import blueprint as album_endpoints
from search_endpoint.search_endpoint import search_blueprint as search_endpoints
from playlist_endpoints.playlist_endpoint import playlist_blueprint as playlist_endpoints


#THIS FILE IS JUST SO I DONT RESET MY TABLES EVERYTIME SINCE BOOMBOX.py creates tables on execution

app = Flask(__name__)
app.register_blueprint(album_endpoints)
app.register_blueprint(search_endpoints)
app.register_blueprint(playlist_endpoints)


if __name__ == '__main__':
    app.run(debug=True)
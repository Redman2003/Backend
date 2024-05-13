import sys
from pathlib import Path

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)


from flask import Blueprint, request, Response, make_response, jsonify
from libapi.query.query_builder import QueryBuilder
from libapi.access.access_token import extract_access_token as SPOTIFY_ACCESS_TOKEN
from database import MySQL_Database 
from utils import escape_single_quotes

blueprint = Blueprint("artist", __name__)
database = None
artist_table = None

def artist_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, artist_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    artist_table = database.get_table("acct")

    if artist_table == None:
        raise RuntimeError(f"Could not find artist table in database")
    

def create_artist(json) -> Response:
    artist_name = escape_single_quotes(json["artist_name"])
    artist_picture = escape_single_quotes(json["artist_picture"])
    spotify_uid = json["spotify_uid"]
    
    columns = ["`artist_name`", "`artist_picture`", "`artist_boomscore`", "`spotify_uid`"]
    values = [f"\'{artist_name}\'", f"\'{artist_picture}\'", 0, f"\'{spotify_uid}\'"]
    artist_table.insert(columns, values)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_artists(json) -> Response:
    artist_name = escape_single_quotes(json["artist_name"])
    
    artists = artist_table.get_all("`artist_name`", artist_name)
    results = []

    for artist in artists:
        (artist_id, artist_name, artist_picture, artist_boomscore, spotify_uid) = artist
        results.append({
            "artist_id" : artist_id, 
            "artist_picture" : artist_picture, 
            "artist_boomscore" : artist_boomscore, 
            "spotify_uid" : spotify_uid
        })

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"

    return response
    

def delete_artist(json) -> Response:
    artist_id = json[artist_id]

    music_table = database.get_table("music")
    single_table = database.get_table("single")
    album_table = database.get_table("album")
    playlist_table = database.get_table("playlist")
    acct_playlist_music_table = database.get_table("acct_playlist_music")
    review_table = database.get_table("review")

    if music_table == None\
        or single_table == None\
        or album_table == None\
        or playlist_table == None\
        or acct_playlist_music_table == None\
        or review_table == None:
        response = make_response(
            jsonify({"error":"table not found in database"}),
            500
        )
        response.headers["Content-Type"] = "application/json"
        return response

    musics = music_table.get("`music_id`", "`artist_id`", artist_id)

    for (music_id,) in musics:
        # delete playlists
        playlists = acct_playlist_music_table.get("`playlist_id`", "`music_id`", music_id)

        for (playlist_id,) in playlists:
            playlist_table.delete("`playlist_id`", playlist_id)

        review_table.delete("`music_id`", music_id)

    album_table.delete("`artist_id`", artist_id)
    single_table.delete("`artist_id`", artist_id)
    artist_table.delete("`artist_id`", artist_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_artists_spotify(json) -> Response:
    artist_name = json["artist_name"]
    limit = json["limit"]

    query = QueryBuilder(url='https://api.spotify.com/v1/search')
    get_request_response = query.add_params("q", artist_name)\
        .add_params("type", "artist")\
        .add_header("Authorization", SPOTIFY_ACCESS_TOKEN)\
        .add_header("User-Agent", "Boombox\\V1")\
        .add_params("limit", f"{limit}")\
        .make_get_request()
    
    if get_request_response.status_code != 200:
        response = make_response(
            jsonify({"error":"spotify web api error"}),
            500
        )
        response.headers["Content-Type"] = "application/json"
        return response
    
    json = get_request_response.json()
    results = []

    for artist in json["items"]:
        items = {}
        items["artist_name"] = artist["name"]
        
        if len(artist["images"]) > 0:
            items["artist_picture"] = artist["images"][0]["url"]

        items.append(artist["id"]) # spotify uid
        items["spotify_uid"] = artist[id]

        results.append(items)

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"
    
    return response


@blueprint.route("/create_artist", methods=["POST"])
def app_create_artist() -> Response:
    if request.method == "POST":
        return create_artist(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
    

@blueprint.route("/get_artists_db", methods=["POST"])
def app_get_artists_db() -> Response:
    if request.method == "POST":
        return get_artists(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"
    
    return response
    

@blueprint.route("/get_artists_spotify", methods=["POST"])
def app_get_artists_spotify() -> Response:
    if request.method == "POST":
        return get_artists_spotify(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/delete_artist", methods=["POST"])
def app_delete_artist() -> Response:
    if request.method == "POST":
        return delete_artist(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"
    
    return response
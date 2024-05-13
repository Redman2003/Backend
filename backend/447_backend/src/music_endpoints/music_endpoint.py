import sys
from pathlib import Path

sys.path.append(Path(__file__).parent)

from flask import Blueprint, request, Response, make_response, jsonify
from database import MySQL_Database # type: ignore
from utils import escape_single_quotes # type: ignore


blueprint = Blueprint("music", __name__, url_prefix='/music')
database = None
music_table = None
single_table = None
album_table = None
artist_table = None



def music_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, music_table, single_table, album_table, artist_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password,
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    music_table = database.get_table("music")
    single_table = database.get_table("single")
    album_table = database.get_table("album")
    artist_table = database.get_table("artist")

    if music_table == None:
        raise RuntimeError(f"Could not find music table in database")



def get_music(json) -> Response:
    database.commit()

    music_id = json["music_id"]

    music = music_table.get_all("`music_id`", music_id)

    if music == []:
        print("plz no")
        response = make_response(jsonify({"error":"music_id does not exist"}), 400)
        response.headers["Content-Type"] = "application/json"
        return response

    (_, release_date, is_album, single_id, album_id) = music[0]
    
    result = {}

    if (is_album == 1):
        (_, album_cover, album_name, _, _, _, album_artists, _, _, _) = album_table.get_all("`album_id`", album_id)[0]
        result["is_album"] = True
        result["name"] = album_name
        result["cover"] = album_cover
        result["artists"] = album_artists
    else:
        (_, single_name, single_cover, _, _, single_artists, _, _, _, _) = single_table.get_all("`single_id`", single_id)[0]
        result["is_album"] = False
        result["name"] = single_name
        result["cover"] = single_cover
        result["artists"] = single_artists

    result["release_date"] = release_date

    response = make_response(jsonify({"result":result}), 200)
    response.headers["Content-Type"] = "application/json"

    return response



@blueprint.route("/get_music", methods=["POST"])
def app_get_music() -> Response:
    if request.method == "POST":
        return get_music(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
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

blueprint = Blueprint("single", __name__)
database = None
single_table = None

def single_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, single_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    single_table = database.get_table("single")

    if single_table == None:
        raise RuntimeError(f"Could not find single table in database")


def create_single(json) -> Response:
    single_name = escape_single_quotes(json["single_name"])
    single_length = json["single_length"]
    single_cover = escape_single_quotes(json["single_cover"])
    artist_id = json["artist_id"]
    spotify_uid = json["spotify_uid"]
    
    columns = ["`single_name`", "`single_length`", "`single_cover`", "`artist_id`", "`single_boomscore`","`spotify_uid`"]
    values = [f"\'{single_name}\'", f"\'{single_length}\'", f"\'{single_cover}\'", artist_id, 0, f"\'{spotify_uid}\'"]
    single_table.insert(columns, values)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_singles(json) -> Response:
    single_name = escape_single_quotes(json["single_name"])
    
    singles = single_table.get_all("`single_name`", single_name)
    results = []

    for single in singles:
        (single_id, single_name, single_length, single_cover, artist_id, single_boomscore, spotify_uid) = single
        results.append({
            "single_id" : single_id,
            "single_name" : single_name,
            "single_length" : single_length,
            "single_cover" : single_cover,
            "artist_id" : artist_id,
            "single_boomscore" : single_boomscore,
            "spotify_uid" : spotify_uid
        })

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"

    return response


def delete_single(json) -> Response:
    single_id = json["single_id"]
    
    single_table.delete("`single_id`", single_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_tracks_spotify(json) -> Response:
    single_name = json["single_name"]
    limit = json["limit"]
    
    query = QueryBuilder(url='https://api.spotify.com/v1/search')
    get_request_response = query.add_params("q", single_name)\
        .add_params("type", "track")\
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

    for track in json["items"]:
        items = {}
        items["artist_name"] = track["album"]["artists"][0]["name"]
        items["artist_spotify_uid"] = track["album"]["artists"][0]["id"]
        items["track_name"] = track["name"]
        items["track_spotify_uid"] = track["id"]
        items["is_album"] = track["album"]["album_type"] != "single"
        items["album_name"] = track["album"]["name"]
        items["album_spotify_uid"] = track["album"]["id"]
        results.append[items]

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"
    
    return response


@blueprint.route("/create_single", methods=["POST"])
def app_create_single() -> Response:
    if request.method == "POST":
        return create_single(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
    

@blueprint.route("/get_singles_db", methods=["POST"])
def app_get_singles_db() -> Response:
    if request.method == "POST":
        return get_singles(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/get_tracks_spotify", methods=["POST"])
def app_get_tracks_spotify() -> Response:
    if request.method == "POST":
        return get_tracks_spotify(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
    

@blueprint.route("/delete_single", methods=["POST"])
def app_delete_single() -> Response:
    if request.method == "POST":
        return delete_single(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
import sys
import requests
import pprint
from pathlib import Path


LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)

from flask import Blueprint, request, Response, make_response, jsonify
from libapi.query.query_builder import QueryBuilder # type: ignore
from libapi.query.spot_track_builder import SpotifyTrackEndpoint # type: ignore
from libapi.access import access_token #type ignore
from database import MySQL_Database # type: ignore
from utils import escape_single_quotes # type: ignore



def _get_valid_access_token():
    #PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\
    PATH_TO_TOKEN = f'{LIBAPI_FP}\\libapi\\access\\'
    if access_token.check_expiration(path=PATH_TO_TOKEN):
        access_token.load_access_token(path=PATH_TO_TOKEN)
    ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)
    return ACCESS_TOKEN

ACCESS_TOKEN = _get_valid_access_token()

blueprint = Blueprint("single", __name__, url_prefix='/single')
database = None
single_table = None
music_table = None

def single_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, single_table, music_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password,
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    single_table = database.get_table("single")
    music_table = database.get_table("music")

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


def get_single(json) -> Response:
    database.commit()

    uid = json['uid']
    QUERY  = f'SELECT single_id FROM single WHERE spotify_uid = \'{uid}\''
    database.execute(QUERY)
    ret = database.fetchall()


    if (len(ret) == 0):
        URL = f'https://api.spotify.com/v1/tracks/{uid}'  
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        tracks = requests.get(URL, headers=headers).json()

        name = tracks['name']
        cover = tracks['album']['images'][0]['url']
        artists  = ""
        for i in range(len(tracks['artists'])):
            if(i < (len(tracks['artists']) - 1)):
                artists += f"{tracks['artists'][i]['name']},"
            else:
                artists+= f"{tracks['artists'][i]['name']}"
        preview = tracks['preview_url']
        release_date = tracks['album']['release_date']

        if len(release_date) == 4:
            release_date = f"{release_date}-01-01"

        boomscore = tracks['popularity']

        QUERY = '''INSERT INTO single(single_name, single_cover,single_boomscore,spotify_uid,artists,preview_url, release_date) VALUES(%s,%s,%s,%s,%s,%s,%s)'''

        database.execute(QUERY,(name,cover,boomscore,uid,artists,preview,release_date))
        database.commit()

        QUERY = f'SELECT single_id FROM single where spotify_uid = \'{uid}\''
        database.execute(QUERY)
        single_id = database.fetchall()[0][0]

        QUERY = f'INSERT INTO music(release_date,is_album,single_id) VALUES(\'{release_date}\',0,{single_id})'
        database.execute(QUERY)
        database.commit()

    
    QUERY  = f'SELECT single_name,single_cover,single_boomscore,spotify_uid,artists,preview_url,release_date,likes,dislikes,single_id FROM single WHERE spotify_uid = \'{uid}\''
    database.execute(QUERY)
    
    response  = database.fetchall()

    single_id =  response[0][9]

    QUERY = f'SELECT music_id FROM music WHERE single_id = {single_id}'

    database.execute(QUERY)

    music_id = database.fetchall()[0][0]

    QUERY = f'SELECT * FROM review WHERE music_id = {music_id}'

    database.execute(QUERY)
    review = database.fetchall()

    #(music_id,) = music_table.get("`music_id`", "`single_id`", single_id)

    data  ={
        'music_id': music_id,
        'track_name':response[0][0],
        'track_cover':response[0][1],
        'track_boomscore':response[0][2],
        'artists':response[0][4],
        'track_preview':response[0][5],
        'track_release':response[0][6],
        'likes': response[0][7],
        'dislikes': response[0][8],
        'reviews':len(review)
    }

    response = make_response(
        jsonify({"result":data}),
        200
    )
        
        

    return response



    



def delete_single(json) -> Response:
    single_id = json["single_id"]
    
    single_table.delete("`single_id`", single_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_tracks_spotify(json) -> Response:
    
    SPOTIFY_ACCESS_TOKEN = json['access_token']
    single_name = json["single_name"]
    limit = json["limit"]
    
    URL = f'https://api.spotify.com/v1/search?q={single_name}&type=track&limit={limit}'  
    headers = {
        "Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"
    }
    get_request_response = requests.get(URL, headers=headers)
    print(get_request_response)
    
    if get_request_response.status_code != 200:
        response = make_response(
            jsonify({"error":"spotify web api error"}),
            500
        )
        response.headers["Content-Type"] = "application/json"
        return response
    
    json = get_request_response.json()
    results = []
    for track in json['tracks']["items"]:
        items = {}
        items["artist_name"] = track["album"]["artists"][0]["name"]
        items["artist_spotify_uid"] = track["album"]["artists"][0]["id"]
        items["track_name"] = track["name"]
        items["track_spotify_uid"] = track["id"]
        items["is_album"] = track["album"]["album_type"] != "single"
        items["album_name"] = track["album"]["name"]
        items["album_spotify_uid"] = track["album"]["id"]
        items['image'] =  track["album"]['images'][0]["url"]
        results.append(items)

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


@blueprint.route("/get_single_db", methods=["POST"])
def app_get_single_db() -> Response:
    if request.method == "POST":
        return get_single(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response
 


@blueprint.route("/get_tracks_spotify", methods=["POST"])
def app_get_tracks_spotify() -> Response:
    if request.method == "POST":
        return get_tracks_spotify(request.json)
    
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
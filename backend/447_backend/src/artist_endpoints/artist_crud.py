import sys
import pprint
import json
import requests
from pathlib import Path

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)


from flask import Blueprint, request, Response, make_response, jsonify
from libapi.query.query_builder import QueryBuilder
from libapi.access import access_token

from database import MySQL_Database 
from utils import escape_single_quotes



def _get_valid_access_token():
    #PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\
    PATH_TO_TOKEN = f'{LIBAPI_FP}\\libapi\\access\\'
    if access_token.check_expiration(path=PATH_TO_TOKEN):
        access_token.load_access_token(path=PATH_TO_TOKEN)
    ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)
    return ACCESS_TOKEN

ACCESS_TOKEN = _get_valid_access_token()


blueprint = Blueprint("artist", __name__, url_prefix='/artist')
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
    

def create_artist(data) -> Response:
    artist_name = escape_single_quotes(data["artist_name"])
    artist_picture = escape_single_quotes(data["artist_picture"])
    artist_boomscore = data['artist_boomscore']
    spotify_uid = data["spotify_uid"]
    albums  = json.dumps(data['albums'])
     



   
    QUERY = '''INSERT INTO artist (artist_name, artist_picture, artist_boomscore, spotify_uid, albums) VALUES(%s,%s,%s,%s,%s)'''
    database.execute(QUERY, (artist_name,artist_picture,artist_boomscore,spotify_uid,albums))
    database.commit()

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"
    

    return response
    


def get_artists(json) -> Response:
    artist_name = escape_single_quotes(json["artist_name"])
    
    artists = artist_table.get_all("\"spotify_uid\"", artist_name)
    results = []

    for artist in artists:
        (artist_id, artist_name, artist_picture, artist_boomscore, spotify_uid, album) = artist
        results.append({
            "artist_id" : artist_id, 
            "artist_picture" : artist_picture, 
            "artist_boomscore" : artist_boomscore, 
            "spotify_uid" : spotify_uid,
            'album':album
        })

    

    return results

def get_artist(dict) -> Response:
    uid = dict['uid']
    QUERY  = f'SELECT artist_id FROM artist WHERE spotify_uid = \'{uid}\''
    database.execute(QUERY)
    ret = database.fetchall()

    

    
    if (len(ret) == 0):
        URL = f'https://api.spotify.com/v1/artists/{uid}'  
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        get_request_response = requests.get(URL, headers=headers).json()
        
        URL = f'https://api.spotify.com/v1/artists/{uid}/albums'  
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        albums = requests.get(URL, headers=headers).json()

        artist_albums = []

        for album in albums['items']:
            album_data ={
                'album_image': album['images'][0]['url'],
                'album_name' : album['name'],
                'uri': album['id']
            }
            artist_albums.append(album_data)
        

        
        data ={
            'artist_name':get_request_response['name'],
            'artist_picture':get_request_response['images'][0]['url'],
            'artist_boomscore':get_request_response['popularity'],
            'albums': artist_albums,
            'spotify_uid':uid
        }

        create_artist(data)

   

    QUERY  = f'SELECT artist_name,artist_picture,artist_boomscore,albums,likes,dislikes FROM artist WHERE spotify_uid = \'{uid}\''

    
    database.execute(QUERY)
    resp  = database.fetchall()


    artist_albums = json.loads(resp[0][3])
    album_names = []
    album_covers = []
    album_uid  = []

    for artist in artist_albums:
        album_names.append(artist['album_name'])
        album_covers.append(artist['album_image'])
        album_uid.append(artist['uri'])
        


   
    
    metadata = [
        resp[0][0],
        resp[0][1],
        resp[0][2],
        album_covers,
        album_names,
        album_uid,
        resp[0][4],
        resp[0][5]
    ]
    

  

    response = make_response(
        jsonify({"result":metadata}),
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

    URL = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit={limit}'  
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
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
    
    for artist in json['artists']["items"]:
        items = {}
        items["artist_name"] = artist["name"]
        if len(artist['images']) > 0:
            items['image'] = artist['images'][0]['url']
        else:
            items['image'] = 'https://i.pinimg.com/originals/91/2c/e1/912ce19bfeadb1e9e2b7cee8f0a4f1bc.jpg'
        items['artist_uri'] = artist['id']
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



@blueprint.route("/get_artist", methods=["POST"])
def app_get_artist_db() -> Response:
   
    return get_artist(request.get_json())
    
   
    

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
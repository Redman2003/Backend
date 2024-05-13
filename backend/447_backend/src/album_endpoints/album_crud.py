import sys
import requests
import pprint
import json
from pathlib import Path
from flask import request

### Add folder with libapi to sys path. This is so when we import from libapi, python knows where to look

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)


sys.path.append(str(Path(__file__).parent.parent))

import traceback
from flask import Blueprint, Flask, request, jsonify, make_response, Response
from libapi.query.spot_album_builder import SpotifyAlbumEndpoint
from libapi.query.spot_artist_builder import SpotifyArtistEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print
from release import Release_Table
from album_entry import Album_Entry_Table
from artist import Artist_Table
from database import MySQL_Database

blueprint = Blueprint('album_crud', __name__,url_prefix="/album")
db = None
album_table = None    
album_entry_table = None
artist_table = None
music_table = None


def album_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global db, album_table, artist_table, album_entry_table, music_table
    db = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )
    if not db.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    album_table = Release_Table(db, is_single=False)    
    album_entry_table = Album_Entry_Table(db)
    artist_table = Artist_Table(db)
    music_table = db.get_table("music")





def _get_valid_access_token():
    #PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
    PATH_TO_TOKEN = LIBAPI_FP + '/libapi/access/'
    if access_token.check_expiration(path=PATH_TO_TOKEN):
        access_token.load_access_token(path=PATH_TO_TOKEN)
    ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)
    return ACCESS_TOKEN

ACCESS_TOKEN = _get_valid_access_token()

@blueprint.route("/test")
def test():
    return "hello"    

@blueprint.route("/create", methods=['POST'])
def create_album() -> Response:
    if request.method == "POST":
        return _create_album(request.json)

    response = make_response(
        jsonify({"error": "only POST method allowed"}),
        405
    )
    response.headers["Content-Type"] = 'application/json'
    return response

def _create_album(data):
    # create album based on spotify api
    if "method" in data and data["method"] == "Spotify":
        if "uid" in data:
            return _get_album_from_spotify(data["uid"])
    # create album based on user details -> for our project lets just base it off spot, Im just putting the option here
    elif "method" in data and data["method"] == "User":
        response = make_response(
            405,
        ) 
        response.headers["Content-Type"] = 'application/json'
        return response
    
    response = make_response(
        jsonify({"error": "pass in valid creation method (Spotify or User)"}),
        405
    )
    response.headers["Content-Type"] = 'application/json'
    return response 

### 30zwjSQEodaUXCn11nmiVF testing with this uid
def _get_album_from_spotify(uid):
    if len(album_table.exists_by_uid(f'\'{uid}\'')) != 0:
        return make_api_response({"error:": f'album with uid: {uid} already exists in database or you passed an invalid uid'}, 409)
    
    album_builder = SpotifyAlbumEndpoint(ACCESS_TOKEN)
    artist_builder = SpotifyArtistEndpoint(ACCESS_TOKEN) 
    album_info, artist_info = {}, {}

    response = album_builder.get_album(uid) 
    #return make_api_response({"breaking here for testing"}, 200)

    if response.status_code != 200:
        return make_api_response({"error": f"error in retrieving album uid: {uid} from the spotify api"}, 404)
    
    # take the first artist
    artist = response.json()["artists"][0]
    #pretty_print(artist)
    artist_info["spotify_uid"] = artist["id"]
    
    artist_returned = artist_table.exists_by_uid(f'\'{artist_info["spotify_uid"]}\'')
    # if None lets create the artist 
    if artist_returned == None:
        artist_response = artist_builder.get_artist(artist["id"]) ## returned artist
        #pretty_print(artist_response.json())
        #return make_api_response({"s": "s"}, 200)
        if artist_response != None and artist_response.status_code == 200:
            artist_info["artist_boomscore"] = 0
            artist_info["artist_picture"] = escape_single_quotes(artist_response.json()["images"][0]["url"])
            artist_info["artist_name"] = escape_single_quotes(artist["name"])
            artist_response = artist_response.json()
            artist_table.create_with_uid(
                f'\'{artist_info["spotify_uid"]}\'', 
                f'\'{artist_info["artist_name"]}\'', 
                f'\'{artist_info["artist_boomscore"]}\'', 
                f'\'{artist_info["artist_picture"]}\''
            )
            artist_returned = artist_table.exists_by_uid(f'\'{artist_info["spotify_uid"]}\'')
        else:
            artist_returned = None

    album_info["artist_id"] = artist_returned[0] if artist_returned != None else None ### insert the artist_id
    album_info["album_name"] = escape_single_quotes(response.json()["name"])
    album_info["spotify_uid"] = response.json()["id"]
    album_info["album_length"] = escape_single_quotes(response.json()["total_tracks"])
    album_info["album_boomscore"] = "0"
    album_info["album_cover"] = escape_single_quotes(response.json()["images"][0]["url"])


    print('album name', album_info["album_name"])
    album_table.create_by_uid(
        album_info["album_name"], album_info["album_length"], album_info["artist_id"], album_info["album_boomscore"], 
        album_info["spotify_uid"], album_info["album_cover"]
    )
    
    newly_created_album = album_table.get_by_uid(f'\'{album_info["spotify_uid"]}\'')
    print(newly_created_album)
    album_response = {
        "album_id": newly_created_album[0][0],
        "album_name": newly_created_album[0][4],
        "artist_id": newly_created_album[0][3],
        "spotify_uid": newly_created_album[0][6] ,
        "album_boomscore": newly_created_album[0][5], 
        "album_length": newly_created_album[0][1],
        "album_picture": newly_created_album[0][2]
    }
    print('res', create_album_entrys(response.json()["tracks"], album_response["album_id"]))
    return make_api_response(album_response, 200)

def get_albums_spotify(json) -> Response:
    
    SPOTIFY_ACCESS_TOKEN = json['access_token']
    album_name = json["album_name"]
    limit = json["limit"]
    
    URL = f'https://api.spotify.com/v1/search?q={album_name}&type=album&limit={limit}'  
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
    for album in json['albums']["items"]:
        items = {}
        items["album_name"] = album["name"]
        items["album_spotify_uid"] = album["id"]
        items["image"] = album['images'][0]['url']
        results.append(items)
    

   
    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"
    
    return response
   

# helper methods
def make_api_response(payload, status_code):
    response = make_response(jsonify(payload), status_code)
    response.headers["Content-Type"] = 'application/json'
    return response


def create_album_entrys(tracks, album_id) -> True|False:
    if "items" not in tracks: return False
    for track in tracks["items"]:
        album_entry_info = {
            "entry_length": None,
            "album_id": album_id,
            "entry_name": escape_single_quotes(track["name"]), 
            "spotify_uid": track["id"]
        }
        try:
            db.execute(
                f'INSERT INTO album_entry (entry_length, album_id, entry_name, spotify_uid)\
                VALUES (\'{album_entry_info["entry_length"]}\', \'{album_id}\', \'{album_entry_info["entry_name"]}\', \'{album_entry_info["spotify_uid"]}\')'
            )
            db.commit()
        except Exception as e:
            print(f'track: {album_entry_info["entry_name"]} could not be added')
            traceback.print_exc()
            print('TRACEBACK DONE')
    return True


@blueprint.route("/delete", methods=["DELETE"])
def delete_album():
    if request.method == "DELETE" and "album_id" in request.json:
        return _delete_album(request.json["album_id"])
    return "delete album"

def _delete_album(album_id):
    album_to_delete = album_table.get_by_release_id(album_id)
    if len(album_to_delete) == 0:
        return make_api_response({"error":"album with id:{album_id} does not exist"})    
    album_entry_table.delete_album_id(album_id)
    album_table.delete_release_id(album_id)
    return make_api_response({"message": f"deletion of album with id:{album_id} is successfull"}, 200)

@blueprint.route('/get/',methods = ["POST"])
def get_album():
    db.commit()

    
    uid = request.get_json()['uri']
    
    
    if uid != None:
        return _get_album_by_uid(uid)
    
    id = request.args.get("id")
    if id == None:
        return make_api_response({"error": "please provide a valid id"}, 400)
    album = album_table.get_by_release_id(id)
    if not len(album):
        return make_api_response({"error": f"please provide a valid id, album with {id} not found"}, 400)
    else:
        album = album[0]
        (music_id,) = music_table.get("`music_id`", "`album_id`", id)[0]
        print(album) # id, length, cover link, artist id, album name, boomscore spotify uid
        response = {
            "music_id": music_id,
            "album_id": album[0],
            "album_length": album[1],
            "album_picture": album[2],
            "artist_id": album[3],
            "album_name": album[4],
            "album_boomscore": album[5], 
            "spotify_uid": album[6]
        }
        return make_api_response(response, 200)
        
   
        
def _get_album_by_uid(uid):
    QUERY = f'SELECT album_id FROM album WHERE spotify_uid = \'{uid}\''
    db.execute(QUERY)
    album = db.fetchall()
    if len(album) == 0:
        URL = f'https://api.spotify.com/v1/albums/{uid}'  
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        album = requests.get(URL, headers=headers).json()
        
        name = album['name']
        release_date = album['release_date']

        if len(release_date) == 4:
            release_date = f"{release_date}-01-01"

        boomscore = album['popularity']
        image = album['images'][0]['url']
        artists  = ""
        for i in range(len(album['artists'])):
            if(i < len(album['artists']) - 1):
                artists+= f"{album['artists'][i]['name']},"
            else:
                artists+= f"{album['artists'][i]['name']}"

        tracks = []
        for track in album['tracks']['items']:
            data = {
                'track_name':track['name'],
                'track_uid':track['id']
            }
            tracks.append(data)

        QUERY = '''INSERT INTO album(album_cover,album_name,album_boomscore,spotify_uid,tracks,artists,release_date) VALUES(%s,%s,%s,%s,%s,%s, %s)'''
        db.execute(QUERY,(image,name,boomscore,uid,json.dumps(tracks),json.dumps(artists), release_date))
        db.commit()

        QUERY = f'SELECT album_id FROM album where spotify_uid = \'{uid}\''
        db.execute(QUERY)
        album_id = db.fetchall()[0][0]

        QUERY = f'INSERT INTO music(release_date,is_album,album_id) VALUES(\'{release_date}\',1,{album_id})'
        db.execute(QUERY)
        db.commit()
            
    

    QUERY = f'SELECT * FROM album WHERE spotify_uid = \'{uid}\''

    db.execute(QUERY)
    album = db.fetchall()

    album_id = album[0][0]

    QUERY = f'SELECT music_id FROM music WHERE album_id = {album_id}'

    db.execute(QUERY)
    music_id = db.fetchall()[0][0]

    QUERY = f'SELECT * FROM review WHERE music_id = {music_id}'

    db.execute(QUERY)
    review = db.fetchall()



    tracks = json.loads(album[0][5])

    track_names = []
    track_uids = []

    for track in tracks:
        track_names.append(track['track_name'])
        track_uids.append(track['track_uid'])

    (music_id,) = music_table.get("`music_id`", "`album_id`", album_id)[0]

    response = {
            "music_id": music_id,
            "album_cover": album[0][1],
            "artists": album[0][6],
            "album_name": album[0][2],
            "album_boomscore": album[0][3], 
            "track_names": track_names,
            'track_uids': track_uids,
            'release_date': album[0][7],
            'likes':album[0][8],
            'dislikes':album[0][9],
            'reviews':len(review)
        }
    

    return make_api_response(response, 200)


    
 
    
def escape_single_quotes(data):
  if type(data) != str:
    return data
  return data.replace("'", r"\'")



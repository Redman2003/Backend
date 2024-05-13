import sys
from pathlib import Path
### Add folder with libapi to sys path. This is so when we import from libapi, python knows where to look

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)


sys.path.append(str(Path(__file__).parent.parent))

import traceback
from flask import Blueprint, Flask, request, jsonify, make_response, Response
from libapi.query.spot_album_builder import SpotifyAlbumEndpoint # type: ignore
from libapi.query.spot_artist_builder import SpotifyArtistEndpoint # type: ignore
from libapi.access import access_token # type: ignore
from libapi.utils.utils import pretty_print # type: ignore
from release import Release_Table # type: ignore
from album_entry import Album_Entry_Table # type: ignore
from artist import Artist_Table # type: ignore
from database import MySQL_Database # type: ignore
from table import MySQL_Table # type: ignore
import mysql.connector

playlist_blueprint = Blueprint('playlist_crud', __name__,url_prefix="/playlist")





    


def _get_valid_access_token():
    #PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
    PATH_TO_TOKEN = LIBAPI_FP + '/libapi/access/'
    if access_token.check_expiration(path=PATH_TO_TOKEN):
        access_token.load_access_token(path=PATH_TO_TOKEN)
    ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)
    return ACCESS_TOKEN

ACCESS_TOKEN = _get_valid_access_token()

def make_api_response(payload, status_code):
    response = make_response(jsonify(payload), status_code)
    response.headers["Content-Type"] = 'application/json'
    return response


def get_playlist_by_name(json):
    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")


    playlist_name = json['playlist_name']
    
    if not  playlist_name:
        return make_api_response({"error": "provide valid playlist_name"}, 404)
    
    db.execute(
        f'SELECT * FROM playlist where playlist_name=\'{escape_single_quotes(playlist_name)}\''
    )
    response = db.fetchall()


    resp = []

    for playlist in response:
        data =  {
            'playlist_id': playlist[0],
            'playlist_name':playlist[3],
            'image':playlist[4]
        }
        resp.append(data)

    
    response = make_response(
        jsonify({"result":resp}),
        200
    )
    response.headers["Content-Type"] = "application/json"


    
    return response
   
    

@playlist_blueprint.route("/create", methods=['POST'])
def create_playlist():
    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")
    

    data = request.json
    acct_id = data.get("acct_id")
    uid_list = data.get("uid_list")
    imageURL = request.json.get("image_url")
    playlist_name = data.get("playlist_name")
    track_names = data.get("track_names")



    if playlist_name == None:
        return make_api_response({"error": "please pass a playlist_name"}, 400)
    if acct_id == None:
        return make_api_response({"error": "please pass a acct_id"}, 400)
    if uid_list == None or (type(uid_list) == list and len(uid_list) == 0):
        return make_api_response({"error": "please pass a valid list of spotify uid's into uid_list"}, 400)

    # check if account exists
    QUERY = f'SELECT * FROM  acct WHERE account_id = {acct_id}'



    db.execute(QUERY)

    results = db.fetchall()

    if not len(results): 
        return make_api_response({"error": f"acct_id of {acct_id} does not exist"}, 400)
    
    #[(1, 'johndoe@gmail.com', 'john', 'hash', 0, 0, datetime.date(2024, 4, 25))]
    _, email, username, _, _, _, _ = results[0]

    playlist_id = None
    try:
        PLAYLIST_INSERT_QUERY = f"INSERT INTO PLAYLIST (creation_date, account_id, playlist_name, image_url) \
            VALUES (CURDATE(), {acct_id}, '{escape_single_quotes(playlist_name)}', '{imageURL[0]}')" 
        db.execute(PLAYLIST_INSERT_QUERY)
        db.commit()
        playlist_id = db.get_last_id_inserted()
    except mysql.connector.Error as Error:
        print(f"Error during insert: {Error}")
        return make_api_response({"error": "error while creating playlist"}, 500)
    
    try:
        i = 0
        for uid in uid_list:
            if('\"' in track_names[i]):
                db.execute(
                    f"INSERT INTO acct_playlist_music (account_id, playlist_id, spotify_uid, image_url, song_name) VALUES ({acct_id}, {playlist_id}, \'{uid}\',\'{imageURL[i]}\', \'{track_names[i]}\')"
                )
            else:
                db.execute(
                    f"INSERT INTO acct_playlist_music (account_id, playlist_id, spotify_uid, image_url, song_name) VALUES ({acct_id}, {playlist_id}, \'{uid}\',\'{imageURL[i]}\', \"{track_names[i]}\")"
                )

            db.commit()
            i+=1
    except mysql.connector.Error as Error:
        print(f"Error during insert: {Error}")
        return make_api_response({"error": "error while inserting entries into playlist"}, 500)

    

    return make_api_response({"playlist": uid_list}, 200)


  


@playlist_blueprint.route('/delete', methods=['POST','DELETE'])
def delete_playlist():
    
    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")


    data = request.json
    acct_id = data.get("acct_id")
    playlist_id = data.get("playlist_id")
   
    if playlist_id == None:
        return make_api_response({"error": "please pass a playlist_id"}, 400)
    if acct_id == None:
        return make_api_response({"error": "please pass a acct_id"}, 400)

    try:
        DELETE_PLAYLIST_ENTRY = f'DELETE FROM playlist WHERE playlist_id={playlist_id} AND account_id = {acct_id}'
        db.execute(DELETE_PLAYLIST_ENTRY)
        db.commit()
    except mysql.connector.Error as Error:
        print(f"Error during playlist entry deletion: {Error}")
        return make_api_response({"error": "error while deleting entries from  playlist"}, 500)

    
    return make_api_response({"success": f"{playlist_id} deleted"}, 200)



    


@playlist_blueprint.route('/get_by_id', methods=['GET'])
def get_playlist_by_id():

    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")


    playlist_id = request.args.get("playlist_id")

    if not playlist_id:
        return make_api_response({"error": "provide valid playlist_id"}, 404)
    
    db.execute(
        f' SELECT spotify_uid,image_url,song_name FROM acct_playlist_music WHERE playlist_id = {playlist_id}'
    )
    playlist = db.fetchall()

    
    songs = []
    for song in playlist:
        data = {
            'spotify_uid': song[0],
            'image_url':song[1],
            'song_name':song[2]
        }
        songs.append(data)

    

   
    return make_api_response(songs, 200)




@playlist_blueprint.route('/getAll', methods=['GET'])
def get_all_playlists():

    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")


    acct_id = request.args.get("acct_id")

    if not acct_id :
        return make_api_response({"error": "provide valid acct_id and playlist_name"}, 404)
    
    QUERY = f'SELECT playlist_id , image_url, playlist_name FROM playlist where account_id={acct_id}'
    
    db.execute(QUERY)
    playlists = db.fetchall()
    playlist_list = []

    for playlist in playlists:
        playlist_data= {
            'playlist_id': playlist[0],
            'playlist_image': playlist[1],
            'playlist_name':playlist[2]
        }
        playlist_list.append(playlist_data)

    

    return make_api_response(playlist_list, 200)


@playlist_blueprint.route('/get_playlist_table', methods=['GET'])
def get_playlist_table():


    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")

    QUERY = f'SELECT * FROM playlist '
    
    db.execute(QUERY)
    playlists = db.fetchall()

  

    playlist_list = []

    for playlist in playlists:
        playlist_data= {
            'playlist_id': playlist[0],
            'playlist_image': playlist[4],
            'playlist_name':playlist[3]
        }
        playlist_list.append(playlist_data)

    
    return make_api_response(playlist_list, 200)
  
    
    
    

        
@playlist_blueprint.route("/add", methods=['POST'])
def add_to_playlist():


    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")

    uid = request.json.get("uid")
    acct_id = request.json.get("acct_id")
    playlist_id = request.json.get("playlist_id")
    imageURL = request.json.get("image_url")
    track_name = request.json.get("track_name")

    
    if not uid or not acct_id or not playlist_id:
        return make_api_response({"error": "provide a vaild uid, acct_id, playlist_id"}, 400)
    
    db.execute(
        f'SELECT playlist_id FROM playlist where account_id={acct_id} and playlist_id={playlist_id}'
    )
    
    playlist = db.fetchall()
    if not len(playlist):
        return make_api_response({"error": f'playlist does not exist or acct_id by {acct_id} is not valid'}, 404)
   

    try:
        QUERY = ""  
        if('\"' in track_name):
            QUERY =f"INSERT INTO acct_playlist_music (account_id, playlist_id, spotify_uid, image_url, song_name) VALUES ({acct_id}, {playlist_id}, \'{uid}\',\'{imageURL}\', \'{track_name}\')"
        else:    
            QUERY = f"INSERT INTO acct_playlist_music (account_id, playlist_id, spotify_uid, image_url, song_name) VALUES ({acct_id}, {playlist_id}, \'{uid}\',\'{imageURL}\', \"{track_name}\")"
                
        db.execute(QUERY)
        db.commit()
    except mysql.connector.Error as Err:
        return make_api_response({"error": "error while inserting uid {uid}"}, 404)
    

    return make_api_response({"success": f"{uid} added to {playlist_id}"}, 200)
    

    
    

@playlist_blueprint.route('/remove', methods=['POST'])
def remove_from_playlist():

    db = MySQL_Database(host = 'localhost', user = 'root', password = 'Mancity2003*')
    if not db.use('boombox'):
        raise RuntimeError(f"Could not find database {mysql_database}")


    uid = request.json.get("uid")
    acct_id = request.json.get("acct_id")
    playlist_id = request.json.get("playlist_id")

    if not uid or not acct_id or not playlist_id:
        print(uid)
        return make_api_response({"error": "provide a vaild uid, acct_id, playlist_name"}, 400)

    db.execute(
        f'SELECT * FROM acct_playlist_music where account_id={acct_id} and playlist_id = {playlist_id} and spotify_uid = \'{uid}\''
    )
    playlist = db.fetchall()
    if(len(playlist) > 1):
        try:  
            QUERY = f'DELETE FROM ACCT_PLAYLIST_MUSIC WHERE account_id = {acct_id} and playlist_id = {playlist_id} and spotify_uid = \'{uid}\' LIMIT 1'
            db.execute(QUERY)
            db.commit()
        except mysql.connector.Error as Err:
            print(f'Error while deleting: {Err}')
            return make_api_response({"error": "error while removing uid {uid}"}, 404)
    else:
        try:  
            QUERY = f'DELETE FROM ACCT_PLAYLIST_MUSIC WHERE account_id = {acct_id} and playlist_id = {playlist_id} and spotify_uid = \'{uid}\''
            db.execute(QUERY)
            db.commit()
        except mysql.connector.Error as Err:
            print(f'Error while deleting: {Err}')
            return make_api_response({"error": "error while removing uid {uid}"}, 404)

    
    return make_api_response({"success": f"{uid} removed from {playlist_id}"}, 200)
    
    


def escape_single_quotes(data):
  if type(data) != str:
    return data
  return data.replace("'", r"\'")


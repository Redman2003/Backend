import sys
from pathlib import Path
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
from table import MySQL_Table
import mysql.connector

playlist_blueprint = Blueprint('playlist_crud', __name__,url_prefix="/playlist")
db = None
album_table = None
album_entry_table = None
artist_table = None
playlist_table = None
acct_playlist_music_table = None




def playlist_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global db, album_table, artist_table, album_entry_table,acct_table,playlist_table,acct_playlist_music_table
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
    acct_table = MySQL_Table(db, "acct")
    playlist_table = MySQL_Table(db, "playlist")
    acct_playlist_music_table = MySQL_Table(db, "acct_playlist_music")






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

@playlist_blueprint.route("/create", methods=['POST'])
def create_playlist():
    data = request.json
    acct_id = data.get("acct_id")
    uid_list = data.get("uid_list")
    playlist_name = data.get("playlist_name")
    if playlist_name == None:
        return make_api_response({"error": "please pass a playlist_name"}, 400)
    if acct_id == None:
        return make_api_response({"error": "please pass a acct_id"}, 400)
    if uid_list == None or (type(uid_list) == list and len(uid_list) == 0):
        return make_api_response({"error": "please pass a valid list of spotify uid's into uid_list"}, 400)

    # check if account exists
    results = acct_table.get("*", "account_id", acct_id)
    if not len(results): 
        return make_api_response({"error": f"acct_id of {acct_id} does not exist"}, 400)
    
    #[(1, 'johndoe@gmail.com', 'john', 'hash', 0, 0, datetime.date(2024, 4, 25))]
    _, email, username, _, _, _, _ = results[0]

    playlist_id = None
    try:
        PLAYLIST_INSERT_QUERY = f"INSERT INTO PLAYLIST (creation_date, account_id, playlist_name) \
            VALUES (CURDATE(), {acct_id}, '{escape_single_quotes(playlist_name)}')" 
        db.execute(PLAYLIST_INSERT_QUERY)
        db.commit()
        playlist_id = db.get_last_id_inserted()
    except mysql.connector.Error as Error:
        print(f"Error during insert: {Error}")
        return make_api_response({"error": "error while creating playlist"}, 500)
    
    try:
        for uid in uid_list:
            db.execute(
                f"INSERT INTO acct_playlist_music (acct_id, playlist_id, spotify_uid) VALUES ({acct_id}, {playlist_id}, \'{uid}\')"
            )
            db.commit()
    except mysql.connector.Error as Error:
        print(f"Error during insert: {Error}")
        return make_api_response({"error": "error while inserting entries into playlist"}, 500)

    return make_api_response({"playlist": uid_list}, 200)


@playlist_blueprint.route('/delete', methods=['POST','DELETE'])
def delete_playlist():
    data = request.json
    acct_id = data.get("acct_id")
    playlist_name = data.get("playlist_name")
    if playlist_name == None:
        return make_api_response({"error": "please pass a playlist_name"}, 400)
    if acct_id == None:
        return make_api_response({"error": "please pass a acct_id"}, 400)
    
    db.execute(f'SELECT * FROM ACCT WHERE account_id={acct_id}')
    if len(db.fetchall()) == 0:
        return make_api_response({"error": f"acct_id of {acct_id} does not exist"}, 404)

    playlist_id = None
    db.execute(
        f'SELECT playlist_id FROM playlist where account_id={acct_id} and playlist_name=\'{escape_single_quotes(playlist_name)}\''
    )
    playlists = db.fetchall()
    if len(playlists) == 0:
        return make_api_response({"error": f"playlist name: {playlist_name} not found"}, 404)
    playlist_id = playlists[0][0]

    try:
        DELETE_PLAYLIST_ENTRY = f'DELETE FROM ACCT_PLAYLIST_MUSIC WHERE playlist_id={playlist_id}'
        db.execute(DELETE_PLAYLIST_ENTRY)
        db.commit()
    except mysql.connector.Error as Error:
        print(f"Error during playlist entry deletion: {Error}")
        return make_api_response({"error": "error while deleting entries from  playlist"}, 500)

    try:
        DELETE_FROM_PLAYLIST = f'DELETE FROM PLAYLIST WHERE ACCOUNT_ID={acct_id} AND playlist_name=\'{escape_single_quotes(playlist_name)}\''
        db.execute(DELETE_FROM_PLAYLIST)
        db.commit()
    except mysql.connector.Error as Error:
        print(f"Error during playlist deletion: {Error}")
        return make_api_response({"error": "error while deleting playlist"}, 500)
    
    return make_api_response({"success": f"{playlist_name} deleted"}, 200)

@playlist_blueprint.route('/get', methods=['GET'])
def get_playlist():
    acct_id = request.args.get("acct_id")
    playlist_name = request.args.get("playlist_name")
    print(acct_id, playlist_name)

    if not acct_id or not playlist_name:
        return make_api_response({"error": "provide valid acct_id and playlist_name"}, 404)
    
    db.execute(
        f'SELECT playlist_id FROM playlist where account_id={acct_id} and playlist_name=\'{escape_single_quotes(playlist_name)}\''
    )
    playlist = db.fetchall()
    if not len(playlist):
        return make_api_response({"error": f'playlist by name {playlist_name} does not exist or acct_id by {acct_id} is not valid'}, 404)
    playlist_id = playlist[0][0]
    response = {"playlist": []}
    db.execute(
        f'SELECT * FROM ACCT_PLAYLIST_MUSIC WHERE ACCT_ID={acct_id} AND PLAYLIST_ID={playlist_id}'
    )
    playlist_entries = db.fetchall()
    for entry in playlist_entries:
        response["playlist"].append(entry[-1])
        print(entry)

    return make_api_response(response, 200)
    

        
@playlist_blueprint.route("/add", methods=['POST'])
def add_to_playlist():
    uid = request.json.get("uid")
    acct_id = request.json.get("acct_id")
    playlist_name = request.json.get("playlist_name")
    if not uid or not acct_id or not playlist_name:
        return make_api_response({"error": "provide a vaild uid, acct_id, playlist_name"}, 400)
    
    db.execute(
        f'SELECT playlist_id FROM playlist where account_id={acct_id} and playlist_name=\'{escape_single_quotes(playlist_name)}\''
    )
    playlist = db.fetchall()
    if not len(playlist):
        return make_api_response({"error": f'playlist by name {playlist_name} does not exist or acct_id by {acct_id} is not valid'}, 404)
    playlist_id = playlist[0][0]

    try:  
        QUERY = f'INSERT INTO ACCT_PLAYLIST_MUSIC (acct_id, playlist_id, spotify_uid) values({acct_id}, {playlist_id}, \'{uid}\')'
        db.execute(QUERY)
        db.commit()
    except mysql.connector.Error as Err:
        return make_api_response({"error": "error while inserting uid {uid}"}, 404)
    
    return make_api_response({"success": f"{uid} added to {playlist_name}"}, 200)
    

    
    

@playlist_blueprint.route('/remove', methods=['POST'])
def remove_from_playlist():
    uid = request.json.get("uid")
    acct_id = request.json.get("acct_id")
    playlist_name = request.json.get("playlist_name")
    
    if not uid or not acct_id or not playlist_name:
        return make_api_response({"error": "provide a vaild uid, acct_id, playlist_name"}, 400)

    db.execute(
        f'SELECT playlist_id FROM playlist where account_id={acct_id} and playlist_name=\'{escape_single_quotes(playlist_name)}\''
    )
    playlist = db.fetchall()
    if not len(playlist):
        return make_api_response({"error": f'playlist by name {playlist_name} does not exist or acct_id by {acct_id} is not valid'}, 404)
    playlist_id = playlist[0][0]

    try:  
        QUERY = f'DELETE FROM ACCT_PLAYLIST_MUSIC WHERE acct_id = {acct_id} and playlist_id = {playlist_id} and spotify_uid = \'{uid}\''
        db.execute(QUERY)
        db.commit()
    except mysql.connector.Error as Err:
        print(f'Error while deleting: {Err}')
        return make_api_response({"error": "error while removing uid {uid}"}, 404)
    
    return make_api_response({"success": f"{uid} removed from {playlist_name}"}, 200)


def escape_single_quotes(data):
  if type(data) != str:
    return data
  return data.replace("'", r"\'")


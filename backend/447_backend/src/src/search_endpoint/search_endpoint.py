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
from libapi.query.spot_search_builder import SpotifySearchEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print
from release import Release_Table
from album_entry import Album_Entry_Table
from artist import Artist_Table
from database import MySQL_Database
from album_endpoints.album_crud import _get_album_from_spotify



search_blueprint = Blueprint('search_crud', __name__,url_prefix="/search")

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

@search_blueprint.route("/search", methods=['GET'])
def search_endpoint():
    search_type = request.args.get("type")
    print( search_type not in ('album', 'artist', 'review', 'user'))

    query = request.args.get("q")
    limit = 20 if request.args.get("limit") == None else request.args.get("limit") 
    offset = 0 if request.args.get("offset") == None else request.args.get("offset")

    if query == None:
        return make_api_response({"error": "include query in q parameter"}, 400)

    if search_type == None or\
    search_type not in ('album', 'artist', 'review', 'user'):
        return make_api_response({"error": "include parameter \'type\', types includes album, artist, review, and users"}, 400)
    
    if search_type == "album":
        return search_albums(query, search_type, limit, offset)
    
def search_albums(query, search_type, limit, offset):
    search_builder = SpotifySearchEndpoint() 
    search_builder.set_params({
        "q": query,
        "type": search_type,
        "limit": limit, 
        "offset": offset
    }).set_header({'Authorization': f'Bearer {ACCESS_TOKEN}'})
    response = search_builder.make_request()
    for album in response.json()["albums"]["items"]:
        endpoint_response = _get_album_from_spotify(album["id"])
        if endpoint_response.status_code != 200:
            print('error in album creation or it already exists in db')
        else:
            print(f"UID: {album['id']} created in db")
 
    return make_api_response(response.json(), 200)






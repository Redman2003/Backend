import sys
import json
from pathlib import Path
### Add folder with libapi to sys path. This is so when we import from libapi, python knows where to look




from flask import Blueprint, Flask, request, jsonify, make_response, Response


blueprint = Blueprint('localData', __name__,url_prefix="/localData")

@blueprint.route('/get_albums_by_genre',methods = ['POST'])
def get_albums_by_genre():

    
    data = request.json

    genre = data['genre']
    

    DIR = f'{str(Path(__file__).parent.parent)}\\albumsCategory\\{genre}.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)

    return data


@blueprint.route('/get_songs_by_genre',methods = ['POST'])
def get_songs_by_genre():

    
    data = request.json

    genre = data['genre']
    

    DIR = f'{str(Path(__file__).parent.parent)}\\songsCategory\\{genre}.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)


    return data


@blueprint.route('/get_artists_by_genre', methods = ['POST'])
def get_artist_by_genre():

    data = request.json

    genre = data['genre']

    DIR = f'{str(Path(__file__).parent.parent)}\\artistsCategory\\{genre}.json'


    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
    return data


@blueprint.route('/get_recent_albums', methods = ['GET'])
def get_recent():

    DIR = f'{str(Path(__file__).parent.parent)}\\albumsCategory\\recentAlbums.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
   
  

    return data

@blueprint.route('/get_recent_artists', methods = ['GET'])
def get_recent_artists():
    DIR = f'{str(Path(__file__).parent.parent)}\\artistsCategory\\recentArtists.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
 
  
    return data

@blueprint.route('/get_recent_songs', methods = ['GET'])
def get_recent_songs():

    DIR = f'{str(Path(__file__).parent.parent)}\\songsCategory\\recentTracks.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
    return data

@blueprint.route('/get_popular_albums',methods = ['GET'])
def get_popular_albums():


    DIR = f'{str(Path(__file__).parent.parent)}\\albumsCategory\\popularAlbums.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)

    return data

@blueprint.route('/get_popular_songs', methods = ['GET'])
def get_popular_songs():

    DIR = f'{str(Path(__file__).parent.parent)}\\songsCategory\\popularSongs.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
 
  

    return data

@blueprint.route('/get_popular_artists', methods = ['GET'])
def get_popular_artists():
    DIR = f'{str(Path(__file__).parent.parent)}\\artistsCategory\\popularArtists.json'

    data = None
    with open(DIR, 'r') as f:
        data = json.load(f)
 
  

    return data
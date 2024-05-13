import json
import requests
import pprint
from pathlib import Path
#from ..access.access_token import load_access_token


'''
albums, artist, singles
'''

# {'error': {'status': 401, 'message': 'The access token expired'}} access token expired error

def extract_access_token() -> str:

    access_token_path = f'{str(Path(__file__).parent.parent)}\\access\\access_token.json'
    json_data = None
    with open(access_token_path, 'r') as file:
        json_data = json.load(file)
        if json_data.get("expired") != None:
            return None
    return json_data["access_token"]


def search_for_artist(artist_name, limit=1):
    URL = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit={limit}'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    params = {'q': artist_name}
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json() if res else None


def search_for_albums(album_name, limit=10):
    URL = f'https://api.spotify.com/v1/search?q={album_name}&type=album&limit={limit}'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    params = {'q': album_name}
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json() if res else None


def search_for_tracks(track_name, limit=1):
    URL = f'https://api.spotify.com/v1/search?q={track_name}&type=track&limit={limit}'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    params = {'q': track_name}
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers, params=params).json()
    return res if res else None



def serach_for_artist_by_genre(genre, limit  =  50):
    URL = f'https://api.spotify.com/v1/search'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {'q': f'genre:"{genre}"', 'type': 'artist', 'limit': limit}
    res = requests.get(URL, headers=headers, params=params).json()
    
    artists = []

    
    for artist in res['artists']['items']:
        artists.append(artist['name'])
    return artists


def serach_for_artist_by_genre_with_image(genre, limit  =  50):
    URL = f'https://api.spotify.com/v1/search'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {'q': f'genre:"{genre}"', 'type': 'artist', 'limit': limit}
    res = requests.get(URL, headers=headers, params=params).json()
    
    artists = []

    
    for artist in res['artists']['items']:
        artists.append({'artist_name':artist['name'] , 'artist_cover':artist['images'][0]['url'], 'uid':artist['id']})
    return artists

def get_most_popular_song(artist_id):
    URL =  f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers).json()

    
    
    
    songs  = res['tracks']

    most_popular_song = max(songs, key=lambda album: album.get('popularity', 0))


    song_data  = {
        'song_name' : most_popular_song['name'],
        'song_cover': res['tracks'][0]['album']['images'][0]['url'],
        'uid': most_popular_song['id']
    }
    

    return song_data

def get_most_popular_song_album(album_id):
    URL =  f'https://api.spotify.com/v1/albums/{album_id}'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers).json()

  
    
    songs  = res['tracks']['items']

    most_popular_song = max(songs, key=lambda album: album.get('popularity', 0))

    

    song_data  = {
        'song_name' : most_popular_song['name'],
        'image': res['images'][0]['url'],
        'uid': most_popular_song['id']
    }
    
   
    return song_data

  
    



def get_most_popular_album(artist_id):
    URL =  f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(URL, headers=headers).json()
    albums  = res['items']

    most_popular_album = max(albums, key=lambda album: album.get('popularity', 0))

    album_data  = {
        'album_name' : most_popular_album['name'],
        'album_cover': most_popular_album['images'][0]['url'],
        'uid': most_popular_album['id']
    }

    return album_data


def get_artist_id(artist):
     artist = search_for_artist(artist)
     return artist['artists']['items'][0]['uri'].split(':')[-1]

def get_album_id(album):
     album = search_for_albums(album)
     return album['albums']['items'][0]['uri'].split(':')[-1]


def get_album_data(album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    album_info = response.json()

    popularity = album_info['popularity']
    tracklist = [track['name'] for track in album_info['tracks']['items']]
    image = album_info['images'][0]['url']
    release_date = album_info['release_date']
    artist = [name['name'] for name in album_info['artists']]
    

    return popularity,tracklist,image,release_date,artist




def get_most_recent_albums():
    url = f"https://api.spotify.com/v1/browse/new-releases"
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers).json()

    albums  = []
    for item in response['albums']['items']:
        album_info = {
            'album_name' : item['name'],
            'album_cover': item['images'][0]['url'],
            'uid': item['id']
        }
        albums.append(album_info)
    

    return albums




def get_most_recent_tracks():
    # Define the URL for the new releases endpoint, specifying that you want tracks
    url  = f"https://api.spotify.com/v1/browse/new-releases"
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()


  
    albums = []
   
    
    for album in data['albums']['items']:
        albums.append(album['name'])
    
    album_ids = [get_album_id(album) for album in albums ]

   
    songs  = [get_most_popular_song_album(album_id) for album_id in album_ids]

    
    
    

    return songs



def get_most_recent_artists():
    # Define the URL for the new releases endpoint, specifying that you want tracks
    url  = f"https://api.spotify.com/v1/browse/new-releases"
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers).json()
    artist_names = [name['artists'][0]['name'] for name in response['albums']['items']]

    recent_artists = []

    for name in artist_names:
        artist_info  = search_for_artist(name)
        artist_image =  artist_info['artists']['items'][0]['images'][0]['url']
        artist_name = artist_info['artists']['items'][0]['name']
        artist_id = artist_info['artists']['items'][0]['id']

        artist_data ={
            'artist_image': artist_image,
            'artist_name': artist_name,
            'uid': artist_id
        }

        recent_artists.append(artist_data)
    
    return recent_artists




def get_albums_from_artist(artist_id):
    url  =  f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    access_token = extract_access_token()
    if not access_token:
        raise Exception("Access token not found")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers).json()

    return response
   








if __name__ == '__main__':
    get_most_recent_artists()
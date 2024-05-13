import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest  
from libapi.query.spot_artist_builder import SpotifyArtistEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print

### will use to store uids for searching
from libapi.query.spot_search_builder import SpotifySearchEndpoint
from libapi.query.spot_artist_builder import SpotifyArtistEndpoint

PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
if access_token.check_expiration(path=PATH_TO_TOKEN):
    access_token.load_access_token(path=PATH_TO_TOKEN)
ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)

### get uids

search_builder = SpotifySearchEndpoint()
search_builder.set_params({
    "q": "Kanye West",
    "type": "artist",
    "limit": "1"
})\
.set_header({
    "Authorization": f"Bearer {ACCESS_TOKEN}"
})

response = search_builder.make_request()
test_uids = [] ## contains uids, and the associated album name
for album in response.json()["artists"]["items"]:
    test_uids.append((album["id"], album["name"]))

search_builder.clear()
search_builder = SpotifySearchEndpoint()
search_builder.set_params({
    "q": "Travis Scott",
    "type": "artist",
    "limit": "1"
})\
.set_header({
    "Authorization": f"Bearer {ACCESS_TOKEN}"
})

response = search_builder.make_request()
for album in response.json()["artists"]["items"]:
    test_uids.append((album["id"], album["name"]))

print(f'UIDS for testing: {test_uids}')

class ArtistsEndPointClassTests(unittest.TestCase):
    def test_get_artist(self):
        artist_id, artist_name = test_uids[0]
        builder = SpotifyArtistEndpoint(ACCESS_TOKEN)
        response = builder.get_artist(artist_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], artist_name)

    def test_get_multiple_artists(self):
        just_uids = [uid for uid, _ in test_uids]
        builder = SpotifyArtistEndpoint(ACCESS_TOKEN)
        response = builder.get_multiple_artists(just_uids)
        if response == None:
            print(builder.error)
            return
        self.assertEqual(response.status_code, 200)
        
        artists_returned = set()
        for artist in response.json()["artists"]:
            artists_returned.add(artist["name"])
        comparsion = set()
        for _, name in test_uids:
            comparsion.add(name)
        self.assertSetEqual(comparsion, artists_returned)
        

    def test_get_artists_albums_endpoints(self):
        artist_id, _ = test_uids[0]
        builder = SpotifyArtistEndpoint(ACCESS_TOKEN)
        response = builder.get_artist_albums(artist_id)
        if response == None:
            print(builder.error)
            return        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    print('RUNNING TESTS...')
    unittest.main()
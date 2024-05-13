import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest  
from libapi.query.spot_album_builder import SpotifyAlbumEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print

### will use to store uids for searching
from libapi.query.spot_search_builder import SpotifySearchEndpoint


PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
if access_token.check_expiration(path=PATH_TO_TOKEN):
    access_token.load_access_token(path=PATH_TO_TOKEN)
ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)

### get uids

search_builder = SpotifySearchEndpoint()
search_builder.set_params({
    "q": "Kanye West",
    "type": "album",
    "limit": "8"
})\
.set_header({
    "Authorization": f"Bearer {ACCESS_TOKEN}"
})

response = search_builder.make_request()
test_uids = [] ## contains uids, and the associated album name
for album in response.json()["albums"]["items"]:
    test_uids.append((album["id"], album["name"]))
    print(test_uids[-1])

class AlbumEndPointClassTests(unittest.TestCase):
    def test_get_album(self):
        print("TEST GET ONE ALBUM...")
        album_id, album_name = test_uids[0]
        builder = SpotifyAlbumEndpoint(access_token=ACCESS_TOKEN)
        response = builder.get_album(album_id)
        '''print(f"response returned for {album_id}")
        print("track names:")
        for track in response.json()["tracks"]["items"]:
            print(track["name"])'''
        self.assertEqual(response.json()["name"], album_name)
        print("TEST PASSED")

    def test_get_multiple_albums(self):
        print("TEST GET MULTPLE ALBUMS...")
        builder = SpotifyAlbumEndpoint(access_token=ACCESS_TOKEN)
        just_uids = [uid for uid, _ in test_uids]
        results = []
        response = builder.get_several_albums(just_uids)
        for album in response.json()["albums"]:
            results.append(album["name"])

        results = set(results)
        comparsion = set()
        for _, album_name in test_uids:
            comparsion.add(album_name)
        self.assertSetEqual(comparsion, results)
        print("TEST PASSED")

    def test_get_albums_tracks(self):
        print("TEST GET ALBUM TRACKS")
        builder = SpotifyAlbumEndpoint(access_token=ACCESS_TOKEN)
        album_id, album_name = test_uids[0]
        response = builder.get_albums_tracks(album_id, 2)
        '''pretty_print(response.json()["items"])'''        
        self.assertEqual(200, response.status_code)
        print("TEST PASSED")



if __name__ == '__main__':
    print('RUNNING TESTS...')
    unittest.main()




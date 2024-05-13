import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest  
from libapi.query.spot_track_builder import SpotifyTrackEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print

### will use to store uids for searching
from libapi.query.spot_search_builder import SpotifySearchEndpoint

PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
if access_token.check_expiration(path=PATH_TO_TOKEN):
    access_token.load_access_token(path=PATH_TO_TOKEN)
ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)

search_builder = SpotifySearchEndpoint()
search_builder.set_params({
    "q": "Nightcrawler",
    "type": "track",
    "limit": "1"
})\
.set_header({
    "Authorization": f"Bearer {ACCESS_TOKEN}"
})

response = search_builder.make_request()
test_uids = [] ## contains uids, and the associated album name

for track in response.json()["tracks"]["items"]:
    test_uids.append((track["id"], track["name"]))

print(f'UIDS for testing {test_uids}')
class TrackEndPointClassTests(unittest.TestCase):
    def test_get_track(self):
        track_id, track_name = test_uids[0]
        builder = SpotifyTrackEndpoint(access_token=ACCESS_TOKEN)
        response = builder.get_track(track_id)
        if response == None:
            print(builder.error)
            return
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], track_name)

    def test_get_multiple_tracks(self):
        just_uids = [uid for uid, _ in test_uids]
        builder = SpotifyTrackEndpoint(access_token=ACCESS_TOKEN)
        response = builder.get_multiple_tracks(just_uids)
        if response == None:
            print(builder.error)
            return
        self.assertEqual(response.status_code, 200)
        pretty_print(response.json())

if __name__ == '__main__':
    print('RUNNING TESTS...')
    unittest.main()
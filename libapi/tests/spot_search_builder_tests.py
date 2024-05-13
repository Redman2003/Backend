import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest  
from libapi.query.spot_search_builder import SpotifySearchEndpoint
from libapi.access import access_token
from libapi.utils.utils import pretty_print

PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
if access_token.check_expiration(path=PATH_TO_TOKEN):
    access_token.load_access_token(path=PATH_TO_TOKEN)
ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)
print(PATH_TO_TOKEN, ACCESS_TOKEN)
class TestSearchQueryBuilder(unittest.TestCase):
    def test_call_search_endpoint(self):
        builder = SpotifySearchEndpoint("https://api.spotify.com/v1/search")
        response = builder\
            .set_params({
                "q": "Kanye West",
                "type": "album", 
                "limit": 4
            })\
            .set_header({
                "Authorization": f'Bearer {ACCESS_TOKEN}'
            })\
            .make_request()
        #pretty_print(response.json())
        self.assertEqual(response.status_code, 200)

print('RUNNING TESTS...')
unittest.main()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest  
from libapi.query.query_builder import QueryBuilder
from libapi.access import access_token
from libapi.utils.utils import pretty_print

PATH_TO_TOKEN = f'{str(Path("../access/").absolute())}\\'
if access_token.check_expiration(path=PATH_TO_TOKEN):
    access_token.load_access_token(path=PATH_TO_TOKEN)
ACCESS_TOKEN = access_token.extract_access_token(path=PATH_TO_TOKEN)

print(PATH_TO_TOKEN, ACCESS_TOKEN)
class TestQueryBuilder(unittest.TestCase):
    def test_make_get_request(self):
        builder = QueryBuilder(url='https://api.spotify.com/v1/search')
        response = builder\
            .add_params("q", "travis scott")\
            .add_params("type", "artist")\
            .add_header("Authorization", f'Bearer {ACCESS_TOKEN}')\
            .add_header("User-Agent", "Boombox\\V1")\
            .add_params("limit", "2")\
            .make_get_request()
        self.assertTrue(response.status_code, 200)
        
    
if __name__ == '__main__':
    print("RUNNING TESTS...")
    unittest.main()  
        


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import unittest
from libapi.access.access_token import check_expiration
PATH_TO_TOKEN_FOLDER = './'
class AccessTokenTests(unittest.TestCase):
    def test_token_expiration(self):
        self.assertEqual(check_expiration(path=PATH_TO_TOKEN_FOLDER), True)


    

if __name__ == "__main__":
    print("RUNNING TESTS...")
    unittest.main()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from libapi.query.query_builder import QueryBuilder

class SpotifyEndpoint():
    def __init__(self, access_token=None):
        self.error = ""
        self.token = access_token
        self.builder = QueryBuilder()

    def _checks(self):
        if self.token == None:
            self.error = "access token improperly initalized"
            return False
        self.error = "0"
        return True
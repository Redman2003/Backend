import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from libapi.query.query_builder import QueryBuilder

class SpotifySearchEndpoint:
    def __init__(self, params={}, headers={}):
        self.url = "https://api.spotify.com/v1/search"
        self.builder = QueryBuilder(url=self.url)

    def set_params(self, params: dict[str, str]):
        for key, val in params.items():
            self.builder.add_params(key, val)
        return self
    
    def set_header(self, headers: dict[str, str]):
        for key, val in headers.items():
            self.builder.add_header(key, val)
        return self
    
    def clear(self):
        self.builder.clear()
        return self
    
    def make_request(self):
        return self.builder.make_get_request()

    
    
        




    





import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from libapi.query.query_builder import QueryBuilder

class SpotifyAlbumEndpoint():
    def __init__(self, access_token=None):
        self.error = ""
        self.url = 'https://api.spotify.com/v1'
        self.token = access_token
        self.builder = QueryBuilder(url=self.url)

    def get_album(self, uid: str):
        if not self._checks():
            return {"error": {"liberror": self.error}}
        ### build the request 
        response = self.builder\
            .add_to_url("albums")\
            .add_to_url(uid)\
            .add_header("Authorization", f'Bearer {self.token}')\
            .make_get_request()
        ### clear the http params, and reset the base url

        self.builder\
            .clear()\
            .add_to_url(self.url)
        return response

    def get_several_albums(self, uids: list[str]):
        if not self._checks():
            return {"error": {"liberror": self.error}}
        ### build the request 
        response = self.builder\
            .add_to_url("albums")\
            .add_params("ids", ",".join(uids))\
            .add_header("Authorization", f'Bearer {self.token}')\
            .make_get_request()
        ### clear the http params, and reset the base url
        self.builder\
            .clear()\
            .add_to_url(self.url)
        return response
        

    ### offset param and market param not tested as of now
    def get_albums_tracks(self, uid:str, limit:str=None, offset=None, market=None):
        if not self._checks():
            return {"error": {"liberror": self.error}}
        ### build the minimum request without optional parameters
        self.builder\
            .add_to_url("albums")\
            .add_to_url(uid)\
            .add_to_url("tracks")\
            .add_header("Authorization", f'Bearer {self.token}')\
        ### add to request based on optional params
        if limit != None:
            if type(limit) != str: 
                limit = str(limit)
            self.builder.add_params("limit", limit)
        if offset != None:
            if type(offset) != str:
                offset = str(offset)
            self.builder.add_params("offset", offset)
        if market != None:
            if type(market) != str:
                market = str(market)
            self.builder.add_params("market", market)
        ### make request and store
        response = self.builder.make_get_request()
        ### clear the http params, and reset the base url
        self.builder\
            .clear()\
            .add_to_url(self.url)
        return response

    def _checks(self) -> bool:
        if self.token == None:
            self.error = "access token improperly initalized"
            return False
        self.error = "0"
        return True
        





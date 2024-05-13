import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from libapi.query.spot_endpoint_builder import SpotifyEndpoint

class SpotifyTrackEndpoint(SpotifyEndpoint):
    def __init__(self, access_token=None):
        self.url = 'https://api.spotify.com/v1/tracks'
        super().__init__(access_token=access_token)
        self.builder.add_to_url(self.url)

    def get_track(self, uid:str=""):
        if not self._checks():
            return None
        if type(uid) != str:
            self.error = "uid is not of type str"
            return None
        res = self.builder\
            .add_to_url(uid)\
            .add_header("Authorization", f'Bearer {self.token}')\
            .make_get_request()
        self.reset_url()
        return res

    def get_multiple_tracks(self, uids:list[str]=[]):
        if not self._checks():
            return None
        if len(uids) == 0:
            self.error = "uids list is empty"
            return None
        for uid in uids:
            if type(uid) != str:
                self.error = "all uids in list are not of type str"
                return None  
        res = self.builder\
            .add_header("Authorization", f'Bearer {self.token}')\
            .add_params("ids", ','.join(uids))\
            .make_get_request()
        return res

    def reset_url(self):
        self.builder.clear().add_to_url(self.url)
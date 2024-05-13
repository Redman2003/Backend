import sys
from pathlib import Path
### Add folder with libapi to sys path. This is so when we import from libapi, python knows where to look
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from pathlib import Path
'''PATH="../../../../"
sys.path.append(str(Path(PATH).absolute()))'''

from flask import Blueprint
#from libapi.query.spot_album_builder import SpotifyAlbumEndpoint
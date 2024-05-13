from dataclasses import dataclass

###
### dataclass to store info about artists that we care about
###
@dataclass
class ArtistPayload:
    external_urls: list[dict] = []
    followers: int = 0
    genres: list[int] = []
    uid: str = ""
    image_link: list[tuple[int, str, int]] = []
    name: str = ""
    popularity: int = 0

    ###
    ### pass in one json object from items list
    ###
    def extract_from_payload(self, artist):
        if "external_url" in artist:
            self.external_urls = [url for url in artist["external_url"]]      
            for urls in artist["external_url"]:
                self.external_urls[urls] = artist["external_url"][urls]
        if "followers" in artist:
            self.followers = artist["followers"]["total"]
        ### according to our db we don't track genre
        self.genres = None
        if "id" in artist:
            self.id = artist["id"]
        if "images" in artist:
            for image in artist["images"]:
                self.image_link.append((image["height"], image["url"], image["width"]))
        if "name" in artist:
            self.name = artist["name"]
        if "popularity" in artist:
            self.popularity = artist["popularity"]

@dataclass
class AlbumPayload:
    artists: list[dict[str, str]] = {}
    external_urls: dict[str, str] = {}
    id: str = ""
    images: list[tuple[int, str, int]] = []
    name: str = ""
    release_date: str = ""
    total_tracks: int = 0
    
    ###
    ### pass in one json object from items list
    ###
    def extract_from_payload(self, album):
        if "artists" in album:
            for artist in album["artists"]:
                _dict = {}
                _dict["external_urls"]["spotify"] = artist["external_urls"]["spotify"]
                _dict["id"] = artist["id"]
                _dict["name"] = artist["name"]
                self.artists.append(_dict)                
        if "external_urls" in album:
            self.external_urls["spotify"] = album["external_urls"]["spotify"]

        if "id" in album:
            self.id = album["id"]

        if "images" in album:
            for image in album["images"]:
                self.images.append((image[0], image[1], image[2]))

        if "name" in album:
            self.name = album["name"]

        if "release_date" in album:
            self.release_date = album["release_date"]

        if "total_tracks" in album:
            self.total_tracks = album["total_tracks"]

'''
[
    {
        "album_type": "album",
        "artists": [
            {
                "external_urls": {
                    "spotify": "https://open.spotify.com/artist/0Y5tJX1MQlPlqiwlOH1tJY"
                },
                "href": "https://api.spotify.com/v1/artists/0Y5tJX1MQlPlqiwlOH1tJY",
                "id": "0Y5tJX1MQlPlqiwlOH1tJY",
                "name": "Travis Scott",
                "type": "artist",
                "uri": "spotify:artist:0Y5tJX1MQlPlqiwlOH1tJY"
            }
        ],
        "available_markets": [
            "AR",
            "AU",
            "AT",
            "BE",
            "BO",
            "BR",
            "BG",
            "CA",
            "CL",
            "CO",
            "CR",
            "CY",
            "CZ",
            "DK",
            "DO",
            "DE",
            "EC",
            "EE",
            "SV",
            "FI",
            "FR",
            "GR",
            "GT",
            "HN",
            "HK",
            "HU",
            "IS",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MY",
            "MT",
            "MX",
            "NL",
            "NZ",
            "NI",
            "NO",
            "PA",
            "PY",
            "PE",
            "PH",
            "PL",
            "PT",
            "SG",
            "SK",
            "ES",
            "SE",
            "CH",
            "TW",
            "TR",
            "UY",
            "US",
            "GB",
            "AD",
            "LI",
            "MC",
            "ID",
            "JP",
            "TH",
            "VN",
            "RO",
            "IL",
            "ZA",
            "SA",
            "AE",
            "BH",
            "QA",
            "OM",
            "KW",
            "EG",
            "MA",
            "DZ",
            "TN",
            "LB",
            "JO",
            "PS",
            "IN",
            "BY",
            "KZ",
            "MD",
            "UA",
            "AL",
            "BA",
            "HR",
            "ME",
            "MK",
            "RS",
            "SI",
            "KR",
            "BD",
            "PK",
            "LK",
            "GH",
            "KE",
            "NG",
            "TZ",
            "UG",
            "AG",
            "AM",
            "BS",
            "BB",
            "BZ",
            "BT",
            "BW",
            "BF",
            "CV",
            "CW",
            "DM",
            "FJ",
            "GM",
            "GE",
            "GD",
            "GW",
            "GY",
            "HT",
            "JM",
            "KI",
            "LS",
            "LR",
            "MW",
            "MV",
            "ML",
            "MH",
            "FM",
            "NA",
            "NR",
            "NE",
            "PW",
            "PG",
            "PR",
            "WS",
            "SM",
            "ST",
            "SN",
            "SC",
            "SL",
            "SB",
            "KN",
            "LC",
            "VC",
            "SR",
            "TL",
            "TO",
            "TT",
            "TV",
            "VU",
            "AZ",
            "BN",
            "BI",
            "KH",
            "CM",
            "TD",
            "KM",
            "GQ",
            "SZ",
            "GA",
            "GN",
            "KG",
            "LA",
            "MO",
            "MR",
            "MN",
            "NP",
            "RW",
            "TG",
            "UZ",
            "ZW",
            "BJ",
            "MG",
            "MU",
            "MZ",
            "AO",
            "CI",
            "DJ",
            "ZM",
            "CD",
            "CG",
            "IQ",
            "LY",
            "TJ",
            "VE",
            "ET",
            "XK"
        ],
        "external_urls": {
            "spotify": "https://open.spotify.com/album/4PWBTB6NYSKQwfo79I3prg"
        },
        "href": "https://api.spotify.com/v1/albums/4PWBTB6NYSKQwfo79I3prg",
        "id": "4PWBTB6NYSKQwfo79I3prg",
        "images": [
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab67616d0000b273715973050587fe3c93033aad",
                "width": 640
            },
            {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67616d00001e02715973050587fe3c93033aad",
                "width": 300
            },
            {
                "height": 64,
                "url": "https://i.scdn.co/image/ab67616d00004851715973050587fe3c93033aad",
                "width": 64
            }
        ],
        "name": "Rodeo",
        "release_date": "2015-09-04",
        "release_date_precision": "day",
        "total_tracks": 16,
        "type": "album",
        "uri": "spotify:album:4PWBTB6NYSKQwfo79I3prg"
    }
]

'''



'''
sample artist playload
[
    {
        "external_urls": {
            "spotify": "https://open.spotify.com/artist/0Y5tJX1MQlPlqiwlOH1tJY"
        },
        "followers": {
            "href": null,
            "total": 28528914
        },
        "genres": [
            "hip hop",
            "rap",
            "slap house"
        ],
        "href": "https://api.spotify.com/v1/artists/0Y5tJX1MQlPlqiwlOH1tJY",
        "id": "0Y5tJX1MQlPlqiwlOH1tJY",
        "images": [
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb19c2790744c792d05570bb71",
                "width": 640
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab6761610000517419c2790744c792d05570bb71",
                "width": 320
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f17819c2790744c792d05570bb71",
                "width": 160
            }
        ],
        "name": "Travis Scott",
        "popularity": 94,
        "type": "artist",
        "uri": "spotify:artist:0Y5tJX1MQlPlqiwlOH1tJY"
    }
]    
'''

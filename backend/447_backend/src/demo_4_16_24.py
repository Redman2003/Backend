from artist import Artist_Table
from release import Release_Table
from album_entry import Album_Entry_Table
from music import Music_Table

def demo(app, database):
    artists = Artist_Table(database)
    singles = Release_Table(database, True)
    albums = Release_Table(database, False)
    album_entries = Album_Entry_Table(database)
    music = Music_Table(database)

    input("Create?")

    artists.create("Imagine Dragons", 150)
    (artist_id,_,_,_,_) = artists.get_artists("Imagine Dragons")[0]

    singles.create("Radioactive", "3:07", artist_id, 500)
    (single_id,_,_,_,_,_,_) = singles.get_by_artist_id(artist_id)[0]

    albums.create("Evolve", "39:12", artist_id, 1672)
    (album_id,_,_,_,_,_,_) = albums.get_by_artist_id(artist_id)[0]

    album_entries.create("Believer", "3:24", album_id)

    music.create_single(artist_id, single_id)
    music.create_album(artist_id, album_id)


    input("Update?")

    artists.update_boomscore(artist_id, 200)
    singles.update_boomscore(single_id, 300)
    albums.update_boomscore(album_id, 1000)


    input("Delete?")

    music.delete_artist_id(artist_id)
    album_entries.delete_album_id(album_id)
    albums.delete_artist_id(artist_id)
    singles.delete_artist_id(artist_id)
    artists.delete(artist_id)
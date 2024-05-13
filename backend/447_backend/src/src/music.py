class Music_Table:
    def __init__(self, database):
        self.table = database.get_table("music")

        if self.table == None:
            raise ValueError("Music table does not exist in given database")

    
    def create_single(self, artist_id, single_id):
        columns = ["`artist_id`", "`single_id`", "`is_album`"]
        values = [artist_id, single_id, 0]
        self.table.insert(columns, values)


    def create_album(self, artist_id, album_id):
        columns = ["`artist_id`", "`album_id`", "`is_album`"]
        values = [artist_id, album_id, 1]
        self.table.insert(columns, values)


    def get_by_music_id(self, music_id):
        return self.table.get_all("`music_id`", music_id)

    
    def get_by_artist_id(self, artist_id):
        return self.table.get_all("`artist_id`", artist_id)
    

    def get_by_single_id(self, single_id):
        return self.table.get_all("`single_id`", single_id)
    

    def get_by_album_id(self, album_id):
        return self.table.get_all("`album_id`", album_id)
    

    def exists(self, music_id):
        return self.get_by_music_id(music_id) != []
    

    def any_exists_by_artist_id(self, artist_id):
        return self.get_by_artist_id(artist_id) != []
    

    def any_exists_by_single_id(self, single_id):
        return self.get_by_single_id(single_id) != []
    

    def any_exists_by_album_id(self, album_id):
        return self.get_by_album_id(album_id) != []
    

    def is_album(self, music_id):
        is_album = self.table.get("`is_album`", "`music_id`", music_id)

        if is_album == []:
            return None
        
        (is_album,) = is_album[0]
        return is_album == 1


    def update_artist_id(self, music_id, artist_id):
        self.table.update("`artist_id`", artist_id, "`music_id`", music_id)


    def update_single_id(self, music_id, single_id):
        self.table.update("`single_id`", single_id, "`music_id`", music_id)
        self.table.update("`is_album`", 0, "`music_id`", music_id)


    def update_album_id(self, music_id, album_id):
        self.table.update("`album_id`", album_id, "`music_id`", music_id)
        self.table.update("`is_album`", 1, "`music_id`", music_id)


    def delete_music_id(self, music_id):
        self.table.delete("`music_id`", music_id)


    def delete_artist_id(self, artist_id):
        self.table.delete("`artist_id`", artist_id)


    def delete_single_id(self, single_id):
        self.table.delete("`single_id`", single_id)


    def delete_album_id(self, album_id):
        self.table.delete("`album_id`", album_id)
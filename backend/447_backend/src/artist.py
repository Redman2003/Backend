class Artist_Table:
    def __init__(self, database):
        self.table = database.get_table("artist")

        if self.table == None:
            raise ValueError("Artist table does not exist in given database")


    def create(self, artist_name, artist_boomscore):
        columns = ["`artist_name`", "`artist_boomscore`"]
        values = [f"\'{artist_name}\'", artist_boomscore]
        self.table.insert(columns, values)


    def get_artists(self, artist_name):
        #return self.table.get_all("`artist_name`", f"\'{artist_name}\'")
        return self.table.get_all(f"\'{artist_name}\'", "`artist_name`")


    def get(self, artist_id):
        artist = self.table.get_all("`artist_id`", artist_id)

        if artist == []:
            return None
        
        return artist[0]


    def get_boomscore(self, artist_id):
        boomscore = self.table.get("`artist_boomscore`", "`artist_id`", artist_id)

        if boomscore == []:
            return None
        
        (boomscore,) = boomscore[0]
        return boomscore


    def exists(self, artist_id):
        return self.get(artist_id) != None
    
    
    def any_exists(self, artist_name):
        return self.get_artists(artist_name) != []


    def update_boomscore(self, artist_id, artist_boomscore):
        self.table.update("`artist_boomscore`", artist_boomscore, "`artist_id`", artist_id)
    

    def delete(self, artist_id):
        self.table.delete("`artist_id`", artist_id)

    def exists_by_uid(self, uid):
        artist = self.table.get_all("`spotify_uid`", uid)
        if artist == []:
            return None
        return artist[0]
    
    def create_with_uid(self, spotify_uid, artist_name, artist_boomscore, artist_picture_path):
        columns = ["`artist_name`", "`artist_boomscore`", "`spotify_uid`", "`artist_picture`"]
        values = [str(artist_name), artist_boomscore, spotify_uid, artist_picture_path]
        self.table.insert(columns, values)

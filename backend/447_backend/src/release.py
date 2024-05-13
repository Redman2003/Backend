# Single and Album tables have same formats, but with different names. Thus this class represents both tables
# Indicate Single or album via the is_single bool in __init__
class Release_Table:
    def __init__(self, database, is_single=True):
        table_string = "single" if is_single else "album"
        self.table = database.get_table(table_string)

        if self.table == None:
            raise ValueError(f"{table_string} table does not exist in given database")

        self.table_id = f"`{table_string}_id`"
        self.table_length = f"`{table_string}_length`"
        self.table_boomscore = f"`{table_string}_boomscore`"
        self.table_name = f"`{table_string}_name`"


    def create(self, release_name, release_length): 
        columns = [self.table_name, self.table_length]
        values = [f"\'{release_name}\'", f"\'{release_length}\'"]
        self.table.insert(columns, values)


    def create(self, release_name, release_length, artist_id, release_boomscore):
        columns = [self.table_name, self.table_length, "`artist_id`", self.table_boomscore]
        values = [f"\'{release_name}\'", f"\'{release_length}\'", artist_id, release_boomscore]
        self.table.insert(columns, values)


    def get_by_release_id(self, release_id):
        return self.table.get_all(self.table_id, release_id)
    

    def get_by_artist_id(self, artist_id):
        return self.table.get_all("`artist_id`", artist_id)
    

    def get_boomscore(self, release_id):
        boomscore = self.table.get(self.table_boomscore, self.table_id, release_id)

        if boomscore == []:
            return None
        
        (boomscore,) = boomscore[0]
        return boomscore
    

    def exists(self, release_id):
        return self.get_by_release_id(release_id) != []
    

    def any_exists_by_artist_id(self, artist_id):
        return self.get_by_artist_id(artist_id) != []


    def update_release_name(self, release_id, name):
        self.table.update(self.table_name, name, self.table_id, release_id)

    
    def update_release_length(self, release_id, length):
        self.table.update(self.table_length, length, self.table_id, release_id)


    def update_artist_id(self, release_id, artist_id):
        self.table.update("`artist_id`", artist_id, self.table_id, release_id)


    def update_boomscore(self, release_id, boomscore):
        self.table.update(self.table_boomscore, boomscore, self.table_id, release_id)
        

    def delete_release_id(self, id):
        self.table.delete(self.table_id, id)

    
    def delete_artist_id(self, artist_id):
        self.table.delete("`artist_id`", artist_id)


    def get_by_uid(self, uid):
        return self.table.get_all("`spotify_uid`", uid)
    
    def exists_by_uid(self, uid):
        return self.get_by_uid(uid)
    
    def create_by_uid(self, release_name, release_length, artist_id, release_boomscore, spotify_uid, album_cover_filepath):
        columns = [self.table_name, self.table_length, "`artist_id`", self.table_boomscore, "spotify_uid", "album_cover"]
        values = [
            f"\'{release_name}\'", f"\'{release_length}\'", f'\'{artist_id}\'', 
            f'\'{release_boomscore}\'', f'\'{spotify_uid}\'', f'\'{album_cover_filepath}\''
        ]
        self.table.insert(columns, values)


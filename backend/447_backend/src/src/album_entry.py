class Album_Entry_Table:
    def __init__(self, database):
        self.table = database.get_table("album_entry")

        if self.table == None:
            raise ValueError("Album_Entry table does not exist in given database")


    def create(self, entry_name, entry_length, album_id):
        columns = ["`entry_name`", "`entry_length`", "`album_id`"]
        values = [f"\'{entry_name}\'", f"\'{entry_length}\'", album_id]
        self.table.insert(columns, values)


    def get_by_entry_id(self, entry_id):
        return self.table.get_all("`entry_id`", entry_id)
    

    def get_by_album_id(self, album_id):
        return self.table.get_all("`album_id`", album_id)
    

    def exists(self, entry_id):
        return self.get_by_entry_id(entry_id) != []
    

    def any_exists_by_album_id(self, album_id):
        return self.get_by_album_id(album_id) != []


    def update_entry_name(self, entry_name, entry_id):
        self.table.update("`entry_name`", entry_name, "`entry_id`", entry_id)

    
    def update_entry_length(self, entry_length, entry_id):
        self.table.update("`entry_length`", entry_length, "`entry_id`", entry_id)


    def delete_entry_id(self, entry_id):
        self.table.delete("`entry_id`", entry_id)


    def delete_album_id(self, album_id):
        self.table.delete("`album_id`", album_id)
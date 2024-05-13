class MySQL_Table:
    def __init__(self, database, table_name) -> None:
        self.database = database
        self.table_name = table_name


    def insert(self, columns, values):
        columns_len = len(columns)
        values_len = len(values)

        if columns_len < 1 or values_len < 1 or columns_len != values_len:
            return
            
        columns_with_commas = split_with_commas(columns)
        values_with_commas = split_with_commas(values)

        self.database.execute(f"INSERT INTO {self.table_name} ({columns_with_commas}) VALUES ({values_with_commas});")
        self.database.commit()

        
    def get(self, what_column, where_column, where_id):
        self.database.execute(f"SELECT {what_column} FROM {self.table_name} WHERE {where_column}={where_id};")
        return self.database.fetchall()
    

    def get_all(self, where_column, where_id):
        return self.get("*", where_column, where_id)


    def update(self, set_column, set_value, where_column, where_id):
        self.database.execute(f"UPDATE {self.table_name} SET {set_column}={set_value} WHERE {where_column}={where_id};")
        self.database.commit()


    def delete(self, column, id):
        self.database.execute(f"DELETE FROM {self.table_name} WHERE {column}={id};")
        self.database.commit()

           
def split_with_commas(list):
    list_len = len(list)

    if list_len == 0: 
        return ""

    string = list[0]
    
    for i in range(1, list_len):
        string = f"{string}, {list[i]}"

    return string
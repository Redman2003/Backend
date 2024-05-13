import mysql.connector
from table import MySQL_Table

class MySQL_Database:
    def __init__(self, host, user, password) -> None:
        self.database = mysql.connector.connect(
            host = host,
            user = user,
            passwd = password,
            port = 35376
        )
        self.cursor = self.database.cursor()
        self.database_name = None


    def commit(self):
        self.database.commit()


    # for right now, use this to create tables or any other misc things
    def execute(self, source,vals = None):
        if vals != None:
            self.cursor.execute(source, vals)
        else:
            self.cursor.execute(source)

    def get_last_id_inserted(self):
        return self.cursor.lastrowid

    def fetchall(self):
        return self.cursor.fetchall()


    def create(self, database_name):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
        self.commit()

    
    def use(self, database_name) -> bool:
        self.execute(f"SHOW DATABASES;")
        databases = self.fetchall()

        if (database_name,) in databases:
            self.execute(f"USE {database_name};")
            self.database_name = database_name
            return True

        return False


    def using_database(self):
        return self.database_name
    

    def is_using_database(self):
        return self.database_name != None


    def get_table(self, table_name):
        if self.database_name == None: 
            return None
        
        self.execute("SHOW TABLES;")
        tables = self.fetchall()

        if (table_name,) in tables:
            return MySQL_Table(self, table_name)
        
        return None
    
    def close(self):
        self.close()

    def cursor_close(self):
        self.cursor.close()

    
        
        
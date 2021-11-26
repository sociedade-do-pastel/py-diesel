import sqlite3
import threading


class SimpleDB:
    def __init__(self, table_name="generic", new=True, **kwargs):
        self.table_name = table_name
        self.db_location = table_name + ".db"
        self.hash_table = {}
        # here begins our initialization statements
        self.begin_connection()
        if new:
            self.drop_table()
            self.create_table()

        if kwargs:
            for value1, value2 in kwargs.items():
                self.insert(value1, value2)
        self.end_connection()

    def update(self, ptype, value):
        self.execute(f'''UPDATE {self.table_name}
                         SET valor = ?
                         WHERE produto = ?;''', value, ptype)

    def increment(self, ptype, increment):
        self.execute(f'''UPDATE {self.table_name}
        SET valor = valor + ?
        WHERE produto = ?;''', increment, ptype)

    def insert(self, value1, value2):
        if self.get(value1) is None:
            self.execute(
                f'''INSERT into {self.table_name} (produto, valor)
                VALUES (?, ?);''', value1, value2)
            return 1
        return None

    def execute(self, command, *args):
        ret_value = []
        try:
            cursor = self.hash_table.get(self.get_cur_thread()).cursor()
            cursor.execute(command, args)
            if "INSERT" or "UPDATE" in command.upper():
                self.hash_table.get(self.get_cur_thread()).commit()
            ret_value = cursor.fetchall()
        except IndexError as ind_error:
            print(f'''{ind_error}
            Remember to always use begin_connection in order to
            stablish a connection with the database!''')
        except sqlite3.OperationalError as db_error:
            print(f'''Error originated from the db - {self.db_location}
            {db_error}''')
        return ret_value

    def get(self, ptype):
        ret_value = self.execute(f'''SELECT valor FROM {self.table_name}
                                      WHERE produto = ?;''', ptype)
        if len(ret_value) == 0:
            return None
        return ret_value[0][0]

    def create_table(self):
        self.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
                         produto TEXT,
                         valor REAL DEFAULT 0.0);''')

    def drop_table(self):
        self.execute(f'''DROP TABLE IF EXISTS {self.table_name};''')

    def print_table(self):
        data = self.execute(f'''SELECT * FROM {self.table_name};''')
        print("| {:-^30} + {:-^25} |".format("", ""))
        print("| {:<30} | {:<25} |".format("produto", "valor"))
        print("| {:-^30} + {:-^25} |".format("", ""))
        for lines in data:
            print("| {:<30} | {:<25.3f} |".format(lines[0], lines[1]))
        print("| {:-^30} + {:-^25} |".format("", ""))

    def begin_connection(self):
        key = self.get_cur_thread()
        return self.hash_table.setdefault(key,
                                          sqlite3.connect(self.db_location))

    def end_connection(self):
        key = self.get_cur_thread()
        self.hash_table.pop(key).close()

    def get_cur_thread(self):
        return threading.get_ident()


def get_db(db_location="generic.db"):
    table_name = db_location.split(".")[0]
    dummy_db = SimpleDB(table_name, False)

    return dummy_db

import sqlite3


class SimpleDB:
    def __init__(self, table_name="generic", **kwargs):
        self.table_name = table_name
        self.db_location = table_name + ".db"
        self.con_stack = []
        # here begins our initialization statements
        self.begin_connection()
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
            cursor = self.con_stack[-1].cursor()
            cursor.execute(command, args)
            if "INSERT" or "UPDATE" in command.upper():
                self.con_stack[-1].commit()
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
        print("| {:-^10} + {:-^50} |".format("", ""))
        print("| {:<10} | {:<50} |".format("produto", "valor"))
        print("| {:-^10} + {:-^50} |".format("", ""))
        for lines in data:
            print("| {:<10} | {:<50} |".format(lines[0], lines[1]))
        print("| {:-^10} + {:-^50} |".format("", ""))

    def begin_connection(self):
        self.con_stack.append(sqlite3.connect(self.db_location))
        return self.con_stack[-1]

    def end_connection(self):
        con = self.con_stack.pop()
        con.close()

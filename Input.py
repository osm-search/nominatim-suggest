import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor, register_hstore
import json

class DBConnection:
    def __init__(self):
        self.connection = self.connect_to_db()


    def test_connection(self):
        self.connection.get_dsn_parameters()
        self.connection.fetch_test()
        # self.connection.fetch_and_create_doc()


    def connect_to_db(self):
        print("=================================================================")
        print("Trying to create a connection")
        try:
            connection = psycopg2.connect(
                user="nominatim",
                password="",              # Replace with your password while using
                host="127.0.0.1",
                port="5432",
                database="nominatim"
            )
            register_hstore(connection, globally=True, unicode=True)
            print("Success")
            return connection
        except:
            print("Failed")
            exit

    def get_dsn_parameters(self):
        print("=================================================================")
        print("Trying to print DSN parameters: ")
        try:
            print(self.connection.connection.get_dsn_parameters())
        except:
            print("Failed")
            exit

    def fetch_test(self):
        print("=================================================================")
        print("Trying to fetch from placex table: ")

        try:
            sql = "SELECT * from placex limit 1;"
            cursor = self.connection.cursor(cursor_factory=DictCursor)
            cursor.execute(sql)
            record = cursor.fetchone()
            print(sql, "\n")
            print(json.dumps(record))
            cursor.close()

        except:
            print("Failed")
            exit


if __name__ == "__main__":
    conn = DBConnection()
    conn.test_connection()

# test_doc()

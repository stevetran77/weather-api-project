import psycopg2
from api_request import mock_fetch_data

def connect_to_db():
    print('Connecting to the PostgreSQL database..')
    try:
        conn = psycopg2.connect(
        host = "localhost",
        port = 5000,
        dbname="db",
        user = "db_user",
        password = "db_password"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed:{e}")
        raise
connect_to_db()
import psycopg2
import config

def connect():
    conn = None
    try:
        params = config.config()
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


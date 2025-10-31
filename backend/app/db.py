import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():

    print(os.getenv("DB_PASSWORD"))

    config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }
    conn = conn = psycopg2.connect(**config)
    return conn
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }
    # Basic validation
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise RuntimeError(f"Missing DB env vars: {', '.join(missing)}")
    conn = psycopg2.connect(**config)
    return conn

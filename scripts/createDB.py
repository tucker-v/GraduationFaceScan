import psycopg2
from psycopg2 import sql
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# NEW: for password hashing
from passlib.hash import bcrypt


'''
Creates DB
'''


def load_db_config():
    """Load database configuration from .env file"""
    load_dotenv()
    config = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }

    for key, value in config.items():
        if value is None:
            print(f"ERROR: '{key}' not found in .env")
            exit(1)
    
    return config


# Load configuration from JSON file
DB_CONFIG = load_db_config()


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database to create new database
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT * FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
        exists = cursor.fetchone()
        print(exists)
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_CONFIG['dbname'])
            ))
            print(f"✓ Database '{DB_CONFIG['dbname']}' created successfully!")
        else:
            print(f"✓ Database '{DB_CONFIG['dbname']}' already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating database: {e}")


def create_tables():
    """Create all tables with proper constraints"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Enable PGVector extension
        cursor.execute(""" 
            CREATE EXTENSION IF NOT EXISTS vector;
        """)
        
        # Drop tables if they exist (for fresh start)
        cursor.execute("""
            DROP TABLE IF EXISTS QUEUED CASCADE;
            DROP TABLE IF EXISTS MANAGES CASCADE;
            DROP TABLE IF EXISTS FACE_IMAGE CASCADE;
            DROP TABLE IF EXISTS STUDENT CASCADE;
            DROP TABLE IF EXISTS CEREMONY CASCADE;
            DROP TABLE IF EXISTS DEGREE CASCADE;
            DROP TABLE IF EXISTS STAFF CASCADE;
        """)
        
                       
        # Create CEREMONY table
        cursor.execute("""
            CREATE TABLE CEREMONY (
                ceremony_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                date_time TIMESTAMP NOT NULL,
                location VARCHAR(200) NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL
            );
        """)
        print("✓ CEREMONY table created.")


        # Create DEGREE table
        cursor.execute("""
            CREATE TABLE DEGREE (
                degree_name VARCHAR(100) PRIMARY KEY,
                ceremony_id INTEGER,
                FOREIGN KEY (ceremony_id) REFERENCES CEREMONY(ceremony_id) ON DELETE SET NULL
            );
        """)
        print("✓ DEGREE table created.")

        # Create STUDENT table
        cursor.execute("""
            CREATE TABLE STUDENT (
                PID VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                degree_name VARCHAR(100),
                degree_type VARCHAR(50),
                opt_in_biometric BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (degree_name) REFERENCES DEGREE(degree_name)
            );
        """)
        print("✓ STUDENT table created.")
        
        # Create STAFF table
        cursor.execute("""
            CREATE TABLE STAFF (
                staff_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'active'
            );
        """)
        print("✓ STAFF table created.")
        
        # Create FACE_IMAGE table (weak entity dependent on STUDENT)
        cursor.execute("""
            CREATE TABLE FACE_IMAGE (
                face_id SERIAL PRIMARY KEY,
                SPID VARCHAR(20) NOT NULL,
                storage_uri VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding vector(512) NOT NULL,
                FOREIGN KEY (SPID) REFERENCES STUDENT(PID) ON DELETE CASCADE
            );
        """)
        print("✓ FACE_IMAGE table created.")
        
        # Create MANAGES relationship table
        cursor.execute("""
            CREATE TABLE MANAGES (
                staff_id VARCHAR(20),
                ceremony_id INTEGER,
                role VARCHAR(50),
                PRIMARY KEY (staff_id, ceremony_id),
                FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id) ON DELETE CASCADE,
                FOREIGN KEY (ceremony_id) REFERENCES CEREMONY(ceremony_id) ON DELETE CASCADE
            );
        """)
        print("✓ MANAGES table created.")
        
        # Create QUEUED relationship table (identifying relationship)
        cursor.execute("""
            CREATE TABLE QUEUED (
                SPID VARCHAR(20),
                ceremony_id INTEGER,
                time_queued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                PRIMARY KEY (SPID, ceremony_id),
                FOREIGN KEY (SPID) REFERENCES STUDENT(PID) ON DELETE CASCADE,
                FOREIGN KEY (ceremony_id) REFERENCES CEREMONY(ceremony_id) ON DELETE CASCADE
            );
        """)
        print("✓ QUEUED table created.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✓ All tables created successfully!")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")


# ---------- NEW: USER_ACCOUNT + seed first admin ----------

def create_user_table_and_seed_admin():
    """
    Create USER_ACCOUNT table (if not exists) and seed a first admin
    if there are no users yet. Does NOT touch existing tables.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create USER_ACCOUNT table if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER_ACCOUNT (
            user_id       SERIAL PRIMARY KEY,
            username      VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin      BOOLEAN NOT NULL DEFAULT FALSE,
            created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✓ USER_ACCOUNT table created (or already exists).")

        # Seed first admin only if there are no users
        cursor.execute("SELECT COUNT(*) FROM USER_ACCOUNT;")
        count = cursor.fetchone()[0]
        if count == 0:
            default_username = "admin"
            default_password = "ChangeMeNow123!"
            default_hash = bcrypt.hash(default_password)

            cursor.execute(
                """
                INSERT INTO USER_ACCOUNT (username, password_hash, is_admin)
                VALUES (%s, %s, TRUE)
                """,
                (default_username, default_hash),
            )

            print(
                "✓ Seeded initial admin user:\n"
                f"   username = '{default_username}'\n"
                f"   password = '{default_password}'\n"
                "   (change this from the app via change-password)"
            )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating USER_ACCOUNT / seeding admin: {e}")

import psycopg2
from psycopg2 import sql
import json
from datetime import datetime, timedelta

'''
Creates DB
'''

def load_db_config(config_file='db_config.json'):
    """Load database configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"✓ Database configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        print(f"Error: {config_file} not found!")
        print("Please create a db_config.json file with your database credentials.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not valid JSON!")
        exit(1)

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
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
        exists = cursor.fetchone()
        
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
        
        # Drop tables if they exist (for fresh start)
        cursor.execute("""
            DROP TABLE IF EXISTS QUEUED CASCADE;
            DROP TABLE IF EXISTS MANAGES CASCADE;
            DROP TABLE IF EXISTS FACE_IMAGE CASCADE;
            DROP TABLE IF EXISTS STUDENT CASCADE;
            DROP TABLE IF EXISTS CEREMONY CASCADE;
            DROP TABLE IF EXISTS STAFF CASCADE;
        """)
        
        # Create STUDENT table
        cursor.execute("""
            CREATE TABLE STUDENT (
                PID VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                degree_name VARCHAR(100),
                degree_type VARCHAR(50),
                opt_in_biometric BOOLEAN DEFAULT FALSE
            );
        """)
        print("✓ STUDENT table created.")
        
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

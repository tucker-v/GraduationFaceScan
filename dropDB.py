import psycopg2
from psycopg2 import sql
import json

'''
Deletes DB
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
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not valid JSON!")
        exit(1)

def terminate_database_connections(config):
    """Terminate all active connections to the database before dropping it"""
    try:
        # Connect to the postgres database (not the one we want to drop)
        conn = psycopg2.connect(
            dbname='postgres',
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Terminate all connections to the target database
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid();
        """, (config['dbname'],))
        
        print(f"✓ Terminated all connections to '{config['dbname']}'")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error terminating connections: {e}")
        return False

def delete_database(config):
    """Delete the PostgreSQL database"""
    try:
        # Connect to the default 'postgres' database
        conn = psycopg2.connect(
            dbname='postgres',
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()

        dbname = config['dbname']
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"ℹ Database '{dbname}' does not exist.")
            cursor.close()
            conn.close()
            return False
        
        # Drop the database
        cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(dbname)))
        print(f"✓ Database '{dbname}' deleted successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error deleting database: {e}")
        return False

def verify_deletion(config):
    """Verify that the database has been deleted"""
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config['dbname'],))
        exists = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if exists:
            print(f"✗ Database '{config['dbname']}' still exists!")
            return False
        else:
            print(f"✓ Verified: Database '{config['dbname']}' has been deleted.")
            return True
            
    except Exception as e:
        print(f"✗ Error verifying deletion: {e}")
        return False

def main():
    """Main function to delete database"""
    print("="*60)
    print("PostgreSQL Database Deletion Tool")
    print("="*60)
    
    # Load database configuration
    config = load_db_config()
    
    # Warning prompt
    print(f"\n⚠️  WARNING: You are about to delete the database '{config['dbname']}'")
    print("⚠️  This action is IRREVERSIBLE and will permanently delete all data!")
    print("\nMake sure you have a backup before proceeding.")
    
    confirmation = input("\nType the database name to confirm deletion: ").strip()
    
    if confirmation != config['dbname']:
        print("\n✗ Database name does not match. Deletion cancelled.")
        return
    
    final_confirm = input("\nAre you absolutely sure? Type 'YES' to proceed: ").strip()
    
    if final_confirm != 'YES':
        print("\n✗ Deletion cancelled.")
        return
    
    print("\nProceeding with deletion...")
    print("-"*60)
    
    # Step 1: Terminate active connections
    print("\nStep 1: Terminating active connections...")
    terminate_database_connections(config)
    
    # Step 2: Delete the database
    print("\nStep 2: Deleting database...")
    success = delete_database(config)
    
    if success:
        # Step 3: Verify deletion
        print("\nStep 3: Verifying deletion...")
        verify_deletion(config)
        
        print("\n" + "="*60)
        print("DATABASE DELETION COMPLETE")
        print("="*60)
    else:
        print("\n✗ Database deletion failed.")

if __name__ == "__main__":
    main()

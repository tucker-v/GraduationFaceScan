import psycopg2
import pandas as pd
import json
from createDB import load_db_config


'''
May or may not work properly depending on system

'''
# Load database config
config = load_db_config()

# Connect to database
conn = psycopg2.connect(**config)

# View STUDENT table
student_df = pd.read_sql_query("SELECT * FROM student", conn)
print("STUDENT TABLE:\n", student_df)

# View QUEUED table
queued_df = pd.read_sql_query("SELECT * FROM queued", conn)
print("\nQUEUED TABLE:\n", queued_df)

conn.close()

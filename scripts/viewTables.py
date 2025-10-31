import psycopg2
import pandas as pd
import json


'''
May or may not work properly depending on system

'''
# Load database config
with open("db_config.json") as f:
    config = json.load(f)

# Connect to database
conn = psycopg2.connect(**config)

# View STUDENT table
student_df = pd.read_sql_query("SELECT * FROM student", conn)
print("STUDENT TABLE:\n", student_df)

# View QUEUED table
queued_df = pd.read_sql_query("SELECT * FROM queued", conn)
print("\nQUEUED TABLE:\n", queued_df)

conn.close()

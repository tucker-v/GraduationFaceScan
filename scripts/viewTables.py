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

cursor = conn.cursor()

cursor.execute("""SELECT * FROM QUEUED""")

row = cursor.fetchall()
print(row)


conn.commit()
cursor.close()
conn.close()

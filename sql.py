import os
import pyodbc
from dotenv import load_dotenv

# Gather parameters
SQL_SERVER=os.getenv('SQL_SERVER')
SQL_DB=os.getenv('SQL_DB')
SQL_USER=os.getenv('SQL_USER')
SQL_PASS=os.getenv('SQL_PASS')

# Connect to SQL Database
sql_client = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER="+SQL_SERVER+";DATABASE="+SQL_DB+";UID="+SQL_USER+";PWD="+SQL_PASS)
cursor = sql_client.cursor()
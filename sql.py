import os
import pyodbc
from dotenv import load_dotenv

# Gather parameters
load_dotenv()
SQL_SERVER=os.getenv('SQL_SERVER')
SQL_DB=os.getenv('SQL_DB')
SQL_USER=os.getenv('SQL_USER')
SQL_PASS=os.getenv('SQL_PASS')

# Connect to SQL Database
def sql_connect():
    sql_client = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+SQL_SERVER+";DATABASE="+SQL_DB+";UID="+SQL_USER+";PWD="+SQL_PASS)
    cursor = sql_client.cursor()
    return cursor, sql_client

def create_table():
    cursor, sql_client = sql_connect()
    try:
        cursor.execute("""CREATE TABLE [dbo].[alarms]([id] [int] NOT NULL,[timestamp] [time](7) NOT NULL,[reminder_time] [time](7) NOT NULL,[message] [varchar](200) NOT NULL,[channel] [varchar](20) NOT NULL,[channel_id] [int] NOT NULL,[guild_name] [varchar](30) NOT NULL,[author_id] [int] NOT NULL) ON [PRIMARY]""")
        sql_client.commit()
    except pyodbc.Error as msg:
        print(f"Error in command: {msg}")
    finally:
        cursor.close()
        sql_client.close()

def alarm_table_exists():
    cursor, sql_client = sql_connect()
    if cursor.tables(table='alarms', tableType='TABLE').fetchone():
        return True
    else:
        return False
    
    cursor.close()
    sql_client.close()
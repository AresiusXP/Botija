import os
import pyodbc
import alarm
from dotenv import load_dotenv
import time
from datetime import datetime,timedelta 

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
        cursor.execute("""CREATE TABLE [dbo].[alarms]([id] [int] NOT NULL IDENTITY(1,1) PRIMARY KEY,[timestamp] [datetime] NOT NULL,[reminder_time] [datetime] NOT NULL,[message] [varchar](200) NOT NULL,[channel] [varchar](20) NOT NULL,[channel_id] [bigint] NOT NULL,[guild_name] [varchar](30) NOT NULL,[author_id] [bigint] NOT NULL, [author_name] [varchar](30)) ON [PRIMARY]""")
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

def create_alarm(new_alarm: alarm.Alarm):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reminder_time = new_alarm.reminder_time.strftime('%Y-%m-%d %H:%M:%S')
    cursor, sql_client = sql_connect()
    query_template =  """INSERT INTO alarms (timestamp, reminder_time, message, channel, channel_id, guild_name, author_id, author_name) VALUES (\'{0}\',\'{1}\',\'{2}\',\'{3}\',{4},\'{5}\',{6},\'{7}\')"""
    query = query_template.format(current_time, reminder_time, new_alarm.message, new_alarm.channel, new_alarm.channel_id, new_alarm.guild_name.replace("\'"," "), new_alarm.author_id, new_alarm.author_name)
    try:
        cursor.execute(query)
        sql_client.commit()
    except pyodbc.Error as msg:
        print(f"Error creating alarm: {msg}")
    finally:
        cursor.close()
        sql_client.close()

def get_next_alarm():
    cursor, sql_client = sql_connect()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = "SELECT TOP 1 * FROM alarms WHERE alarms.reminder_time > \'{0}\' ORDER BY alarms.reminder_time ASC".format(current_time)
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            next_alarm = alarm.Alarm(row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        else:
            next_alarm = None
    except pyodbc.Error as msg:
        print(f"Error getting nest alarm: {msg}")
    finally:
        cursor.close()
        sql_client.close()
    return next_alarm

def test_sql_connection():
    try:
        cursor, sql_client = sql_connect()
        return "success"
    except pyodbc.Error as msg:
        print(f"Error getting nest alarm: {msg}")
        raise
    finally:
        cursor.close()
        sql_client.close()

def import_lines(csv, dbname):
    cursor, sql_client = sql_connect()
    csv_file = open(csv)
    try:
        for l in csv_file:
            if len(l) < 300:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                l = l.replace("'", "''")
                query = "INSERT INTO {0} (timestamp, message) VALUES (\'{1}\',\'{2}\')".format(dbname, now, l[:-1])
                print(query)
                cursor.execute(query)
                sql_client.commit()
    except pyodbc.Error as msg:
        print(f"Error inserting pepi line: {msg}")
    finally:
        cursor.close()
        sql_client.close()
        csv_file.close()

def create_lines_table(dbname):
    cursor, sql_client = sql_connect()
    try:
        cursor.execute("""CREATE TABLE [dbo].[{0}]([id] [int] NOT NULL IDENTITY(1,1) PRIMARY KEY, [timestamp] [datetime] NOT NULL, [message] text NOT NULL) ON [PRIMARY]""".format(dbname))
        sql_client.commit()
    except pyodbc.Error as msg:
        print(f"Error in command: {msg}")
    finally:
        cursor.close()
        sql_client.close()

def get_line(dbname):
    cursor, sql_client = sql_connect()
    try:
        cursor.execute("""SELECT TOP 1 message FROM {0} ORDER BY NEWID()""".format(dbname))
        return cursor.fetchone()[0]
    except pyodbc.Error as msg:
        print(f"Error in command: {msg}")
    finally:
        cursor.close()
        sql_client.close()

def get_line_mention(dbname, nick):
    cursor, sql_client = sql_connect()
    try:
        cursor.execute("""SELECT TOP 1 message FROM {0} WHERE message LIKE '%{1}%' ORDER BY NEWID()""".format(dbname, nick))
        return cursor.fetchone()[0]
    except pyodbc.Error as msg:
        print(f"Error in command: {msg}")
    finally:
        cursor.close()
        sql_client.close()
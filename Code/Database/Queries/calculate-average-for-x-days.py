import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

def rows_by_x_days(conn, cursor, start_timestamp, end_timestamp) :
    try:
        cursor.execute(''' SELECT * FROM pest_monitory WHERE timestamp > ? AND timestamp < ?''', ((start_timestamp,), (end_timestamp,)))
        row = cursor.fetchall()
        return row, None
    except sqlite3.OperationalError as e:
        return None, e

def average_over_x_days(conn, cursor, timestamp, x):
    start = timestamp
    end = timestamp - relativedelta(days=x)

    list, error = rows_by_x_days(conn, cursor, start, end)
    if error is not None :
        print(f"Error: {error}")
        return
    else:
        return list


    
    
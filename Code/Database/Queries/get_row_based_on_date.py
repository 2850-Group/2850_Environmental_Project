import sqlite3
import time 
import datetime
from datetime import timedelta

def row_by_timestamp(conn, cursor, timestamp) -> tuple :
    """
    SQL select statement for row by timestamp.

    Parameters
    ----------
    conn : 
        Pre-established database connection.
    cursor :
        Pre-established database cursor.
    timestamp :
        Used to find specific row.

    Returns
    -------
    tuple
        Returned row with same timestamp.
    string
        Indicates an error. 
    """
    cursor.execute("SELECT * FROM pest_monitoring  WHERE time=?", (timestamp,))
    output = cursor.fetchall()
    return output

    
def timer(conn,cursor):

    """
    Timer to select a row in 15 minute increments every 3 seconds.

    Parameters
    ----------
    conn : 
        Pre-established database connection.
    cursor :
        Pre-established database cursor.

    Returns
    -------
    tuple
        Returned row with same timestamp.
    string
        Indicates an error. 
    """

    year =2023
    month = 12
    day = 31
    hour = 22
    minute = 0
    second = 0
    timestamp = datetime.datetime(year,month,day,hour,minute,second)

    end_date = datetime.datetime(2023,12,31,23,15,0)

    while True:
        output = row_by_timestamp(conn,cursor,timestamp)
        print(output)

        timestamp = timestamp + timedelta(minutes = 15)
        if timestamp == end_date:
            print("End of Data")
            break
        time.sleep(1)

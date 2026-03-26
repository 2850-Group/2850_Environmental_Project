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

    if(timestamp.year > 2023 or timestamp.year < 2022):
        raise ValueError("year is out of range")
    if(timestamp.minute%15 != 0):
        raise ValueError("minutes must divide by 15")
    
    cursor.execute("SELECT * FROM pest_monitoring  WHERE time=?", (timestamp,))
    output = cursor.fetchall()
    return output


def loop(conn,cursor,timestamp):
        
        output = row_by_timestamp(conn,cursor,timestamp)
        print(output)
        return output
    
def timer(conn,cursor,year,month,day,hour,minute):

    """
    Timer to select a row in 15 minute increments every 3 seconds.

    Parameters
    ----------
    conn : 
        Pre-established database connection.
    cursor :
        Pre-established database cursor.
    year :
        The year the user wishes to start at
    month :
        The month the user wishes to start at
    day :
        The day the user wishes to start at
    hour :
        The hour the user wishes to start at
    minute :
        The minute the user wishes to start at
    second :
        The second the user wishes to start at

    Returns
    -------
    tuple
        Returned row with same timestamp.
    string
        Indicates an error. 
    """
    if(year > 2023 or year < 2022):
        raise ValueError("year is out of range")
    if(minute%15 != 0):
        raise ValueError("minutes must divide by 15")

    timestamp = datetime.datetime(year,month,day,hour,minute,0)

    end_date = datetime.datetime(2023,12,31,23,15,0)

    while True:
        loop(conn,cursor,timestamp)

        timestamp = timestamp + timedelta(minutes = 15)
        if timestamp == end_date:
            print("End of Data")
            break
        time.sleep(1)

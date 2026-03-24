import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

def data_between_times(conn, cursor, start_timestamp, end_timestamp) :
    """
    SQL select statement to return all entries between two dates.

    Parameters
    ----------
    conn : 
        Pre-established database connection.
    cursor :
        Pre-established database cursor.
    start_timestamp :
        Indicates the lower bound of the search field.
    end_timestamp :
        Indicates the upper bound of the search field.

    Returns
    -------
    tuple
        Returned row with same timestamp.
    string
        Indicates an error. 
    """
    
    cursor.execute(''' SELECT * FROM pest_monitoring WHERE time >= ? AND time <= ?''', (start_timestamp, end_timestamp))
    row = cursor.fetchall()
    return row

def data_over_x_days(conn, cursor, timestamp, x):
    """
    Calculates the start and end time and returns the data between them.

    Parameters
    ----------
    conn : 
        Pre-established database connection.
    cursor :
        Pre-established database cursor.
    timestamp :
        Indicates the current/starting bound of the search field.
    x : int
    """
    start = timestamp
    end = timestamp - relativedelta(days=x)

    list = data_between_times(conn, cursor, start, end)
    return list

def remove_record_null(data):
    """
    Removes rows from a tuple-list where one entry in the row is null.

    Parameters
    ----------
    data : tuple-list
        Raw records returned from the database.

    Returns
    -------
    tuple-list
        Data where all null value rows have been removed.
    """
    num_columns = len(data[0])
    for i in range(0, len(data)-1):
        for j in range(0, num_columns):
            if data[i][j] == None:
                data.remove(data[i])
    
    return data

def average_data_all_rows(data):
    """
    Calculate the average for all columns in the data.

    Parameters
    ----------
    data : tuple-list
        Cleaned data from the database.

    Returns
    -------
    average_all_data :
        Average of all columns in the data,
    """
    average = []
    num_rows = len(data)

    for j in range(0, 5):
        average.append(0)
        for i in range(0, num_rows):
            average[j] += data[i][j+2]
    
    average.append(0)
    for i in range(0, num_rows):
        average[6] += data[i][14]
    
    for i in range(0, 6):
        average[i] = average[i]/num_rows

    return average

    

        
            




    
    
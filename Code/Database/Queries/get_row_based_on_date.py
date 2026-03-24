import sqlite3

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

    

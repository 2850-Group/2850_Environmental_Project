import sqlite3

def row_by_timestamp(conn, cursor, timestamp) -> tuple :
    try:
        cursor.execute(''' SELECT * FROM pest_monitory WHERE timestamp=?''', (timestamp,))
        row = cursor.fetchall()
        return row, None
    except sqlite3.OperationalError as e:
        return None, e
    

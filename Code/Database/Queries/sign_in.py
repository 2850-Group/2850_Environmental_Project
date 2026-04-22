import sqlite3
import bcrypt

def sign_in_query(conn, cursor, user, pwd):
    pwd_byte = pwd.encode()
    cursor.execute("SELECT password_hash FROM user WHERE username = ?", (user,))
    row = cursor.fetchone()
    if row and bcrypt.checkpw(pwd.encode(), row[0]):
        return True
    else:
        return False
    
def sign_up_query(conn, cursor, name, user, pwd):
    pwd_byte = pwd.encode()
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(pwd_byte, salt)
    role = "User"
    cursor.execute("SELECT COUNT(user_id) FROM user WHERE username = ?", (user,))
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute("INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)", (user, pwd_hash, role, ))
        conn.commit()
        return True
    else:
        return False



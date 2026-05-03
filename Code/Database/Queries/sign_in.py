import sqlite3
import bcrypt

def sign_in_query(conn, cursor, user, pwd):
    pwd_byte = pwd.encode()
    cursor.execute("SELECT password_hash, role, fullname, username FROM user WHERE username = ?", (user,))
    row = cursor.fetchone()
    if row and bcrypt.checkpw(pwd_byte, row[0]):
        return {
            "role": row[1],
            "fullname": row[2],
            "username": row[3]
        }
    
    return None

def sign_up_query(conn, cursor, name, user, pwd, fullname_val, role="Farmer"):
    pwd_byte = pwd.encode()
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(pwd_byte, salt)
    cursor.execute("SELECT COUNT(user_id) FROM user WHERE username = ?", (user,))
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute("INSERT INTO user (username, password_hash, role, fullname) VALUES (?, ?, ?, ?)", (user, pwd_hash, role, fullname_val))
        conn.commit()
        return True
    else:
        return False



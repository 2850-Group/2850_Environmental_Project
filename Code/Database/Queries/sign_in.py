import bcrypt


def sign_in_query(conn, cursor, user, pwd):
    pwd_byte = pwd.encode()
    query = """
        SELECT password_hash, role, fullname, username
        FROM user WHERE username = ?
    """
    cursor.execute(query, (user,))
    row = cursor.fetchone()
    if row and bcrypt.checkpw(pwd_byte, row[0]):
        return {"role": row[1], "fullname": row[2], "username": row[3]}

    return None


def sign_up_query(conn, cursor, name, user, pwd, fullname_val, role="Farmer"):
    pwd_byte = pwd.encode()
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(pwd_byte, salt)
    query = """
        SELECT COUNT(user_id) FROM user WHERE username = ?
    """
    cursor.execute(query, (user,))
    result = cursor.fetchone()
    if result[0] == 0:
        query = """
            INSERT INTO user (username, password_hash, role, fullname)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(
            query, (user, pwd_hash, role, fullname_val))
        conn.commit()
        return True
    else:
        return False

def authenticate_user(username, password, conn):
    cursor = conn.execute("SELECT * FROM student WHERE email = %s",username)
    pass
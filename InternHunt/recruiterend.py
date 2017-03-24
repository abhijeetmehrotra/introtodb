def authenticate_recruiter(username, password, conn):
    cursor = conn.execute("SELECT * FROM hr WHERE email = %s", username)
    pass
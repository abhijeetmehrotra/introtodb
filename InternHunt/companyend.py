
def authenticate_company(username, password, conn):
    cursor = conn.execute("SELECT * FROM student WHERE email = %s",(username))
    record = cursor.fetchone()
    if record is None:
        return (False)
    elif record["password"] == password:
        print(record)
        return (True, record["sid"])
    else:
        return (False)

def get_hr_and_jobs(cid, conn):
    hrs = []
    jobs = []
    cursor = conn.execute("SELECT hid, firstname, lastname FROM hr WHERE com_cid = %s",(cid))
    for row in cursor:
        hrs.append(dict(row))
    cursor = conn.execute("SELECT type, status, description, fromdate, todate FROM hr WHERE com_cid = %s", (cid))
    for row in cursor:
        jobs.append(dict(row))

    result = {"hr":hrs, "jobs":jobs}
    return result
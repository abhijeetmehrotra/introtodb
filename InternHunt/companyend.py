
def authenticate_company(username, password, conn):
    cursor = conn.execute("SELECT * FROM company WHERE email = %s",(username))
    record = cursor.fetchone()
    if record is None:
        return [False]
    elif record["password"] == password:
        print(record)
        return [True, record["cid"]]
    else:
        return [False]

def get_hr_and_jobs(cid, conn):
    hrs = []
    jobs = []
    cursor = conn.execute("SELECT hid, first_name, last_name FROM hr WHERE com_cid = %s",(cid))
    for row in cursor:
        hrs.append(dict(row))
    cursor = conn.execute("SELECT type, status, description, fromdate, todate FROM jobposition WHERE com_cid = %s", (cid))
    for row in cursor:
        jobs.append(dict(row))
    print hrs
    print jobs
    result = {"hr":hrs, "jobs":jobs}
    return result
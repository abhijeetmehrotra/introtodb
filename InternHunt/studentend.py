def user_authenticate(username, password, conn):
    cursor = conn.execute("SELECT * FROM student WHERE email = %s",username)
    record = cursor.fetchone()
    if record is None:
        return False
    elif record["password"] == password:
        return True
    else:
        return False

def get_applications(userid, conn):
    applications = []
    cursor = conn.execute("select resume, app.status, type, company_name from application as app INNER JOIN jobposition as jp using (pid) INNER JOIN company on com_cid=cid WHERE sid = %s", userid)
    for row in cursor:
        applications.append(dict(row))
    return applications

job_sortname = {"position": "type", "company": "company_name", "startdate": "fromdate"}

def get_jobpositions(conn, sortby = None):
    jobpositions = []
    if sortby is not None:
        sorting_type = job_sortname[sortby]
        query = "select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='OPEN' ORDER BY "+sorting_type
        cursor = conn.execute(query)
    else:
        cursor = conn.execute("select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='OPEN'")
    for row in cursor:
        jobpositions.append(dict(row))
    return jobpositions

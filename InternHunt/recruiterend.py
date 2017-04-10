def authenticate_recruiter(username, password, conn):
    cursor = conn.execute("SELECT * FROM hr WHERE email = %s", (username))
    record = cursor.fetchone()
    if record is None:
        return [False]
    elif record["password"] == password:
        print(record)
        return [True, record["hid"]]
    else:
        return [False]

def get_applicants(hid, conn, pid, status):
    query2 = "select pid, sid, resume, status from application where pid = %s and status = %s and pid in (select pid from jobposition where hr_hid="+hid+")"
    #print (query2,pid,status,hid)
    cursor2 = conn.execute(query2, (pid,status))
    applicants = []
    for row in cursor2:
        student = dict(row)
        query3 = "select * from education where stu_sid =%s"
        cursor3 = conn.execute(query3, str(student.get("sid")))
        education = []
        for row3 in cursor3:
            education.append(dict(row3))
        student['education'] = education

        query4 = "select * from experience where stu_sid =%s"
        cursor4 = conn.execute(query4, str(student.get("sid")))
        experience = []
        for row4 in cursor4:
            experience.append(dict(row4))
        student['experience'] = experience

        query5 = "select * from skills where stu_sid =%s"
        cursor5 = conn.execute(query5, str(student.get("sid")))
        skills = []
        for row5 in cursor5:
            skills.append(dict(row5))
        student['skills'] = skills

        applicants.append(student)

    return applicants

def get_job(hid, conn, pid):
    query1 = "select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where pid =%s and hr_hid=%s"
    cursor1 = conn.execute(query1, (pid,hid))
    openjobpositions = []
    for row in cursor1:
        openjobpositions.append(dict(row))

    return {'positiondata': openjobpositions, 'applicants': get_applicants(hid, conn,pid,"PENDING"), 'accepted':get_applicants(hid, conn,pid,"ACCEPT"), 'rejected':get_applicants(hid, conn,pid,"REJECT")}


def get_jobs(hid, conn, sortby):
    openjobpositions = []
    closedjobpositions = []
    if sortby is not None:
        sorting_type = sortby
        query1 = "select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='OPEN' and hr_hid = %s ORDER BY "+sorting_type
        cursor1 = conn.execute(query1,(hid))
        query2 = "select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='CLOSED' and hr_hid = %s ORDER BY " + sorting_type
        cursor2 = conn.execute(query2, (hid))
    else:
        cursor1 = conn.execute("select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='OPEN' and hr_hid = %s",(hid))
        cursor2 = conn.execute("select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status='CLOSED' and hr_hid = %s",(hid))
    for row in cursor1:
        openjobpositions.append(dict(row))
    for row in cursor2:
        closedjobpositions.append(dict(row))
    return {'openpositions':openjobpositions, 'closedpositions':closedjobpositions}

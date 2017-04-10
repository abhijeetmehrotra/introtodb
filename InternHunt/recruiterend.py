def authenticate_recruiter(username, password, conn):
    cursor = conn.execute("SELECT * FROM hr WHERE email = %s", (username))
    record = cursor.fetchone()
    if record is None:
        return [False]
    elif record["password"] == password:
        # print(record)
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
        query3 = "select * from education where stu_sid =%s order by fromdate DESC"
        cursor3 = conn.execute(query3, str(student.get("sid")))
        education = []
        for row3 in cursor3:
            education.append(dict(row3))
        student['education'] = education

        query4 = "select * from experience where stu_sid =%s order by fromdate DESC"
        cursor4 = conn.execute(query4, str(student.get("sid")))
        experience = []
        for row4 in cursor4:
            experience.append(dict(row4))
        student['experience'] = experience

        query5 = "select * from skills where stu_sid =%s order by proficiency DESC"
        cursor5 = conn.execute(query5, str(student.get("sid")))
        skills = []
        for row5 in cursor5:
            skills.append(dict(row5))
        student['skills'] = skills

        query6 = "select first_name, last_name from student where sid =%s"
        cursor6 = conn.execute(query6, str(student.get("sid")))
        student['name'] = dict(cursor6.fetchone())

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
    job_info = []
    query3 = "select pid, application.status, count(*) from application inner join jobposition using(pid) group by pid,application.status,hr_hid having hr_hid=%s"
    cursor3 = conn.execute(query3,(hid))
    pos_countinfo = dict()
    for row in cursor3:
        #job_info.append(dict(row))
        if row["pid"] not in pos_countinfo.keys():
            pos_countinfo[row["pid"]] = dict()
        pos_countinfo[row["pid"]][row["status"]] = row["count"]

    if sortby is not None:
        sorting_type = sortby
        query1 = "select pid, todate, description, industry, fromdate, company_name, type, size, status from jobposition INNER JOIN company on com_cid=cid where hr_hid = %s ORDER BY "+sorting_type
        cursor1 = conn.execute(query1,(hid))

    else:
        cursor1 = conn.execute("select pid, todate, description, industry, fromdate, company_name, type, size, status from jobposition INNER JOIN company on com_cid=cid where hr_hid = %s",(hid))

    for row in cursor1:
        pos = dict(row)
        if (pos.get("status") == "OPEN"):
            if pos['pid'] in pos_countinfo.keys():
                mydict = pos_countinfo[pos['pid']]
                if 'PENDING' in mydict:
                    pos['pending'] = mydict['PENDING']
                else:
                    pos['pending'] = 0
                if 'ACCEPT' in mydict:
                    pos['accept'] = mydict['ACCEPT']
                else:
                    pos['accept'] = 0
                if 'REJECT' in mydict:
                    pos['reject'] = mydict['REJECT']
                else:
                    pos['reject'] = 0
            else:
                pos['accept'] = 0
                pos['reject'] = 0
                pos['pending'] = 0
            openjobpositions.append(pos)
        elif (pos.get("status") == "CLOSED"):
            closedjobpositions.append(pos)

    return {'openpositions':openjobpositions, 'closedpositions':closedjobpositions}


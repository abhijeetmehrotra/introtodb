from __future__ import print_function

def authenticate_student(username, password, conn):
    cursor = conn.execute("SELECT * FROM student WHERE email = %s",(username))
    record = cursor.fetchone()
    cursor.close()
    if record is None:
        return [False]
    elif record["password"] == password:
        print(record)
        return [True, record["sid"]]
    else:
        return [False]

def get_applications(userid, conn):
    applications = []
    cursor = conn.execute("select resume, app.status, type, company_name from application as app INNER JOIN jobposition as jp using (pid) INNER JOIN company on com_cid=cid WHERE sid = %s", userid)
    for row in cursor:
        applications.append(dict(row))
    cursor.close()
    return applications

job_sortname = {"position": "type", "company": "company_name", "startdate": "fromdate"}

def get_jobpositions(conn, position, company, fromdate, todate, sortby = None, sorttype = None):
    jobpositions = []
    params = ['OPEN']
    query = "select pid, todate, description, industry, fromdate, company_name, type, size from jobposition INNER JOIN company on com_cid=cid where status=%s"
    if position is not None and position != "":
        query = query + " and lower(type) LIKE %s"
        params.append('%'+position+'%')
    if company != None and company != "":
        query = query + " and lower(company_name) LIKE %s"
        params.append('%'+company+'%')
    if fromdate != None and fromdate != "":
        query = query + " and fromdate >= %s"
        params.append(fromdate)
    if todate != None and todate != "":
        query = query + " and todate <= %s"
        params.append(todate)
    if sortby != None and sortby != "":
        if sortby in job_sortname.keys():
            if sorttype == 'desc':
                query = query + " ORDER BY "+job_sortname[sortby]+" DESC"
            else:
                query = query + " ORDER BY "+job_sortname[sortby]+" ASC"

    cursor = conn.execute(query, tuple(params))
    for row in cursor:
        jobpositions.append(dict(row))
    cursor.close()
    return jobpositions

def get_student_education(userid, conn):
    education = []
    cursor = conn.execute("select * from education where stu_sid=%s ORDER BY fromdate DESC", (userid))
    for row in cursor:
        currentrow = dict(row)
        if currentrow["todate"] is None:
            currentrow["todate"] = "N/A"
        if currentrow["description"] is None:
            currentrow["description"] = "N/A"
        education.append(dict(currentrow))
    cursor.close()
    return education

def delete_education(university, degree, major, fromdate, sid, conn):
    try:
        cursor = conn.execute("delete from education where university = %s AND degree = %s AND major = %s AND fromdate = %s AND stu_sid = %s", (university, degree, major, fromdate, sid))
        cursor.close()
        return True
    except Exception:
        return False

def add_education(university, degree, major, fromdate, todate, description, sid, conn):
    try:
        if todate is None:
            todate = ""
        if description is None:
            description = ""
        cursor = conn.execute("insert into education values(%s,%s,%s,%s,%s,%s,%s)", (university, degree, major, fromdate, todate, description ,sid))
        cursor.close()
        return True
    except Exception:
        return False

def get_student_experience(userid, conn):
    experience = []
    cursor = conn.execute("select * from experience where stu_sid=%s ORDER BY fromdate DESC", (userid))
    for row in cursor:
        currentrow = dict(row)
        if currentrow["todate"] is None:
            currentrow["todate"] = "N/A"
        if currentrow["description"] is None:
            currentrow["description"] = "N/A"
        experience.append(currentrow)
    cursor.close()
    return experience

def delete_experience(company, position, fromdate, sid, conn):
    try:
        cursor = conn.execute("delete from experience where company_name = %s AND position = %s AND fromdate = %s AND stu_sid = %s", (company, position, fromdate, sid))
        cursor.close()
        return True
    except:
        return False

def add_experience(company, position, fromdate, todate, description, sid, conn):
    try:
        if todate is None:
            todate = ""
        if description is None:
            description = ""
        cursor = conn.execute("insert into experience values(%s,%s,%s,%s,%s,%s)", (company, position, fromdate, todate, description ,sid))
        cursor.close()
        return True
    except:
        return False


def get_student_experience(userid, conn):
    experience = []
    cursor = conn.execute("select * from experience where stu_sid=%s ORDER BY fromdate DESC", (userid))
    for row in cursor:
        currentrow = dict(row)
        if currentrow["todate"] is None:
            currentrow["todate"] = "N/A"
        if currentrow["description"] is None:
            currentrow["description"] = "N/A"
        experience.append(currentrow)
    cursor.close()
    return experience

def delete_experience(company, position, fromdate, sid, conn):
    try:
        cursor = conn.execute("delete from experience where company_name = %s AND position = %s AND fromdate = %s AND stu_sid = %s", (company, position, fromdate, sid))
        cursor.close()
        return True
    except:
        return False

def add_experience(company, position, fromdate, todate, description, sid, conn):
    try:
        if todate is None:
            todate = ""
        if description is None:
            description = ""
        cursor = conn.execute("insert into experience values(%s,%s,%s,%s,%s,%s)", (company, position, fromdate, todate, description ,sid))
        cursor.close()
        return True
    except:
        return False

def get_student_skill(userid, conn):
    skills = []
    cursor = conn.execute("select * from skills where stu_sid=%s", (userid))
    for row in cursor:
        currentrow = dict(row)
        skills.append(currentrow)
    cursor.close()
    return skills

def delete_skill(skill, sid, conn):
    try:
        cursor = conn.execute("delete from skills where skill_name = %s AND stu_sid = %s", (skill, sid))
        cursor.close()
        return True
    except:
        return False

def add_skill(skill, proficiency, sid, conn):
    try:
        cursor = conn.execute("insert into skills values(%s,%s,%s)", (skill, proficiency, sid))
        cursor.close()
        return True
    except:
        return False


def insert_application(sid, pid, conn):
    try:
        cursor = conn.execute("insert into application values(%s,%s,%s,%s)", (pid, sid,"https://s3.amazonaws.com/jobhunt-resume/"+sid+"_"+pid+".pdf","PENDING"))
        cursor.close()
        return True
    except:
        return False

def insert_student(first_name, last_name, sex, username, password, sec_question, sec_answer, conn):
    try:
        cursor = conn.execute("insert into student values(DEFAULT,%s,%s,%s,%s,%s,%s,%s)", (first_name, last_name,
                        sex, username, password,sec_question, sec_answer))
        cursor.close()
        return True
    except:
        return False
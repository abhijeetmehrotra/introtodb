
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

    query1 = "select pid, application.status, count(*) from application inner join jobposition using(pid) group by pid,application.status,com_cid having com_cid=%s"
    cursor1 = conn.execute(query1, (cid))
    pos_countinfo = dict()
    for row in cursor1:
        if row["pid"] not in pos_countinfo.keys():
            pos_countinfo[row["pid"]] = dict()
            pos_countinfo[row["pid"]][row["status"]] = row["count"]


    cursor = conn.execute("SELECT hid, (first_name || ' ' || last_name) as name FROM hr WHERE com_cid = %s",(cid))
    for row in cursor:
        hrs.append(dict(row))
    cursor = conn.execute("SELECT pid, hr_hid, type, status, description, fromdate, todate FROM jobposition WHERE com_cid = %s", (cid))
    for row in cursor:
        job = dict(row)
        if (job.get("status") == "OPEN"):
            if job['pid'] in pos_countinfo.keys():
                mydict = pos_countinfo[job['pid']]
                if 'PENDING' in mydict:
                    job['pending'] = mydict['PENDING']
                else:
                    job['pending'] = 0
                if 'ACCEPT' in mydict:
                    job['accept'] = mydict['ACCEPT']
                else:
                    job['accept'] = 0
                if 'REJECT' in mydict:
                    job['reject'] = mydict['REJECT']
                else:
                    job['reject'] = 0
            else:
                job['accept'] = 0
                job['reject'] = 0
                job['pending'] = 0
            job['total'] = job['accept'] + job['reject'] + job['pending']

        jobs.append(job)

    result = {"hr":hrs, "jobs":jobs}
    return result

def change_hr(hid, pid, cid, conn):
    try:
        cursor = conn.execute("UPDATE jobposition SET hr_hid=%s where pid=%s and com_cid=%s",(hid,pid,cid))
    except Exception as err:
        print err
    finally:
        cursor.close()
        return

def firehrfromalljobs(hid, cid, conn):
    try:
        cursor = conn.execute("UPDATE jobposition SET hr_hid=NULL where hr_hid=%s and com_cid=%s",(hid,cid))
    except Exception as err:
        print err
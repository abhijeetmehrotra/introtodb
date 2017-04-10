#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os, json
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, session
from flask_session import Session
from functools import wraps

from studentend import authenticate_student, get_applications, get_jobpositions
from studentend import get_student_education, delete_education, add_education
from studentend import get_student_experience, delete_experience, add_experience
from studentend import get_student_skill, delete_skill, add_skill
from studentend import insert_application,insert_student

from recruiterend import authenticate_recruiter, get_jobs, get_job


from companyend import authenticate_company, get_hr_and_jobs, change_hr

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

db_cred_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_credentials.json')
db_cred = None

aws_cred_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aws_credentials.json')
aws_cred = None

try:
    if not (os.path.exists(db_cred_json) or os.path.isfile(db_cred_json)):
        raise OSError('file does not exist')

    with open(db_cred_json, 'r') as handle:
        db_cred = json.load(handle)
except Exception as err:
    print err

try:
    if not (os.path.exists(aws_cred_json) or os.path.isfile(aws_cred_json)):
        raise OSError('file does not exist')

    with open(aws_cred_json, 'r') as handle:
        aws_cred = json.load(handle)
except Exception as err:
    print err

DATABASEURI = "postgresql://"+db_cred["USERNAME"]+":"+db_cred["PASSWORD"]+"@"+db_cred["HOST"]+"/"+db_cred["DATABASE"]

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            if 'role' in session and role == session['role']:
                return fn(*args, **kwargs)
            elif role == 'student':
                return redirect("/student/login")
            elif role == 'recruiter':
                return redirect("/recruiter/login")
            elif role == 'company':
                return redirect("/company/login")
        return decorated_function
    return wrapper

@app.route('/student/signup', methods=["GET","POST"])
def studentsignup():
    if request.method == "GET":
        return render_template("studentsignup.html")
    elif request.method == "POST":
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        sex = request.form['sex']
        username = request.form['username']
        password = request.form['password']
        sec_question = request.form['secquestion']
        sec_answer = request.form['secanswer']
        result = insert_student(first_name, last_name, sex, username, password, sec_question, sec_answer, g.conn)
        if result:
            return redirect("student/login")
        else:
            return ("<b>User already exits.</b>",200)

@app.route('/student/login', methods=["GET","POST"])
def studentlogin():
  if request.method == "GET":
    return render_template("studentlogin.html")
  elif request.method == "POST":
    print "Authenticating user"
    username = request.form["username"]
    password = request.form["password"]
    auth = authenticate_student(username, password, g.conn)
    if auth[0]:
        """
            Store sid and all other stuff in session info
        """
        session.clear()
        session['sid'] = str(auth[1])
        session['role'] = 'student'
        return redirect("/student/dashboard")
    else:
        return redirect("/student/login")

@app.route('/student/logout', methods=["GET"])
def studentlogout():
    session.clear()
    return redirect("/student/login")

@app.route('/student/dashboard', methods=["GET"])
@login_required(role='student')
def studentdashboard():
  applications = get_applications(session["sid"], g.conn)
  # print applications
  context = dict(data=applications)
  return render_template("studentdashboard.html", **context)

valid_sorting = ["position", "company", "startdate"]

@app.route('/student/profile/education', methods=["GET","POST"])
@login_required(role='student')
def studentprofile():
    if request.method == "GET":
        studenteducation = get_student_education(session["sid"], g.conn)
        context = dict(data=studenteducation)
        return render_template("studenteducation.html", **context)
    elif request.method == "POST":
        university = request.form['university']
        degree = request.form['degree']
        major = request.form['major']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        description = request.form['description']
        add_education(university, degree, major, fromdate, todate, description, session["sid"], g.conn)
        return redirect('/student/profile/education')

@app.route('/student/profile/deleteeducation', methods=["POST"])
@login_required(role='student')
def deleteeducation():
    university = request.json['university']
    degree = request.json['degree']
    major = request.json['major']
    fromdate = request.json['fromdate']
    delete_education(university, degree, major, fromdate, session["sid"], g.conn)
    return ('DELETED', 200)

@app.route('/student/profile/experience', methods=["GET","POST"])
@login_required(role='student')
def studentexperience():
    if request.method == "GET":
        studentexperience = get_student_experience(session["sid"], g.conn)
        context = dict(data=studentexperience)
        return render_template("studentexperience.html", **context)
    elif request.method == "POST":
        company = request.form['company']
        position = request.form['position']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        description = request.form['description']
        add_experience(company, position, fromdate, todate, description, session["sid"], g.conn)
        return redirect('/student/profile/experience')

@app.route('/student/profile/deleteexperience', methods=["POST"])
@login_required(role='student')
def deleteexperience():
    company = request.json['company']
    position = request.json['position']
    fromdate = request.json['fromdate']
    delete_experience(company, position, fromdate, session["sid"], g.conn)
    return ('DELETED', 200)

@app.route('/student/profile/skills', methods=["GET","POST"])
@login_required(role='student')
def studentskills():
    if request.method == "GET":
        studentskills = get_student_skill(session["sid"], g.conn)
        context = dict(data=studentskills)
        return render_template("studentskills.html", **context)
    elif request.method == "POST":
        skill = request.form['skill']
        proficiency = request.form['proficiency']
        add_skill(skill, proficiency, session["sid"], g.conn)
        return redirect('/student/profile/skills')

@app.route('/student/profile/deleteskill', methods=["POST"])
@login_required(role='student')
def deleteskill():
    skill = request.json['skill']
    delete_skill(skill, session["sid"], g.conn)
    return ('DELETED', 200)

@app.route('/student/jobs', methods=["GET"])
@login_required(role='student')
def studentgetopenjobs():
    company=None
    position=None
    fromdate=None
    todate=None
    sorttype = None
    sortby = None
    if 'company' in request.args:
        company = str(request.args["company"]).lower()
    if 'position' in request.args:
        position = str(request.args["position"]).lower()
    if 'fromdate' in request.args:
        fromdate = request.args["fromdate"]
    if 'todate' in request.form:
        todate = request.args["todate"]
    if 'sortby' in request.args:
        sortby = request.args["sortby"]
    if 'sorttype' in request.args:
        sorttype = request.args["sorttype"]


    jobpositions = get_jobpositions(g.conn, position, company, fromdate, todate, sortby, sorttype)
    #jobpositions=[]
    context = dict(data=jobpositions)
    return render_template("studentjobpositions.html", **context)

@app.route('/student/apply', methods=["GET","POST"])
@login_required(role='student')
def studentapply():
    if request.method == "GET":
        pid = request.args.get('pid')
        if pid is not None:
            data = {"pid":int(pid)}
            context = dict(data=data)
            return render_template("studentapply.html", **context)
        else:
            return redirect("jobs")
    elif request.method == "POST":
        if 'resume' in request.files:
            data_file = request.files['resume']
            pid = request.form["pid"]
            submitted = insert_application(session["sid"], pid, g.conn)
            if submitted == True:
                conn = S3Connection(aws_cred["ACCESS_KEY"],aws_cred["SECRET_KEY"])
                bucket = conn.get_bucket(aws_cred["BUCKET_NAME"])
                k = Key(bucket)
                k.key = session["sid"]+"_"+pid+'.pdf'
                # k.set_contents_from_file(data_file)
                k.set_contents_from_string(data_file.read())
                return ('Application Accepted<br/><a href="/student/dashboard">Go back to dashboard</a>', 200)
            else:
                return('Already applied<br/><a href="/student/dashboard">Go back to dashboard</a>', 200)
        else:
            return ('File not uploaded', 400)


"""
Implementation for Recruiter/HR end
"""

@app.route('/recruiter/login', methods=["GET","POST"])
def recruiterlogin():
    if request.method == "GET":
        return render_template("recruiterlogin.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        auth = authenticate_recruiter(username, password, g.conn)
        if auth[0]:
            """
                Store hid and all other stuff in session info
            """
            session.clear()
            session['hid'] = str(auth[1])
            session['role'] = 'recruiter'
            return redirect("/recruiter/viewjobs")
        else:
            return redirect("/recruiter/login")

@app.route('/recruiter/logout', methods=["GET"])
def recruiterlogout():
    session.clear()
    return redirect("/recruiter/login")

@app.route('/recruiter/createjob', methods=["GET","POST"])
@login_required(role='recruiter')
def createjobrender():
    if request.method == "GET":
        return render_template("createapplication.html")
    elif request.method == "POST":
        type = request.form["title"]
        description = request.form["description"]
        fromDate = request.form["fromDate"]
        toDate = request.form["toDate"]
        status = "OPEN"
        hr_hid = session["hid"]
        query = "select com_cid from hr where hid=%s"
        cursor = g.conn.execute(query, (hr_hid))
        com_cid = cursor.fetchone()['com_cid']
        query1 = "insert into jobposition values(DEFAULT, %s, %s, %s, %s, %s, %s, %s)"
        cursor1 = g.conn.execute(query1, (type, status, description, fromDate, toDate, hr_hid, com_cid))
        return redirect("/recruiter/viewjobs", code=302)

@app.route('/recruiter/appaction', methods=["POST"])
@login_required(role='recruiter')
def modify_job():
    pid = request.form["pid"]
    sid = request.form["sid"]
    hid = session["hid"]
    action = request.form["action"]
    query1 = "update application set status =%s where pid=%s and sid=%s and pid in (select pid from jobposition where hr_hid=%s)"
    cursor1 = g.conn.execute(query1, (action, pid, sid, hid))
    return redirect("/recruiter/jobs?pid="+pid)

@app.route('/recruiter/posaction', methods=["POST"])
@login_required(role='recruiter')
def modify_posting():
    pid = request.form["pid"]
    hid = session["hid"]
    query1 = "update jobposition set status ='CLOSED' where pid=%s and pid in (select pid from jobposition where hr_hid=%s)"
    cursor1 = g.conn.execute(query1, (pid, hid))
    return redirect("/recruiter/viewjobs")

@app.route('/recruiter/jobs', methods=["GET"])
@login_required(role='recruiter')
def viewjobs():
    pid = request.args.get('pid')
    hid = session["hid"]
    jobposition = get_job(hid, g.conn, pid)
    context = dict(data=jobposition)
    return render_template("viewjob.html", **context)

@app.route('/recruiter/viewjobs', methods=["GET"])
@login_required(role='recruiter')
def viewapp():
    hid = session["hid"]
    jobpositions = get_jobs(hid, g.conn, 'fromdate')
    context = dict(data=jobpositions)
    return render_template("viewapplication.html", **context)

"""
Implementation for Company end
"""

@app.route('/company/login', methods=["GET","POST"])
def companylogin():
  if request.method == "GET":
    return render_template("companylogin.html")
  elif request.method == "POST":
    print "Authenticating user"
    username = request.form["username"]
    password = request.form["password"]
    auth = authenticate_company(username, password, g.conn)
    if auth[0]:
        """
            Store sid and all other stuff in session info
        """
        session.clear()
        session['cid'] = str(auth[1])
        session['role'] = 'company'
        return redirect("/company/dashboard")
    else:
        return redirect("/company/login")

@app.route('/company/logout', methods=["GET"])
def companylogout():
    session.clear()
    return redirect("/company/login")

@app.route('/company/dashboard', methods=["GET"])
@login_required(role='company')
def companydashboard():
    hr_and_jobs = get_hr_and_jobs(session["cid"], g.conn)
    context = hr_and_jobs
    return render_template("companydashboard.html", **context)

@app.route('/company/changehrforjob', methods=["POST"])
@login_required(role='company')
def companychangehrforjob():
    pid = request.form['pid']
    hid = request.form['hid']
    cid = session['cid']
    change_hr(hid, pid, cid, g.conn)
    return redirect("/company/dashboard")

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """
    app.secret_key = 'dadahatesui'
    app.config['SESSION_TYPE'] = 'filesystem'
    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    sess = Session()
    sess.init_app(app)

    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded, use_reloader=True)


  run()

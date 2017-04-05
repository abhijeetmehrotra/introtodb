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

from studentend import user_authenticate, get_applications, get_jobpositions
from studentend import get_student_education, delete_education, add_education
from studentend import get_student_experience, delete_experience, add_experience
from studentend import get_student_skill, delete_skill, add_skill


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#

db_cred_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_credentials.json')
db_cred = None

try:
    if not (os.path.exists(db_cred_json) or os.path.isfile(db_cred_json)):
        raise OSError('file does not exist')

    with open(db_cred_json, 'r') as handle:
        db_cred = json.load(handle)
except Exception as err:
    print err

DATABASEURI = "postgresql://"+db_cred["USERNAME"]+":"+db_cred["PASSWORD"]+"@"+db_cred["HOST"]+"/"+db_cred["DATABASE"]


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
"""
engine.execute("CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);")
engine.execute("INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');")
"""

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


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  g.conn.execute('INSERT INTO test VALUES (default, %s)', name)
  return redirect('/')


@app.route('/login')
def login():
    pass

@app.route('/student/login', methods=["GET,POST"])
def studentlogin():
  if request.method == "GET":
    return render_template("studentlogin.html")
  elif request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    is_authenticated = user_authenticate(username, password, g.conn)
    return render_template("studentdashboard.html")

@app.route('/student/dashboard', methods=["GET"])
def studentdashboard():
  userid = "1"
  applications = get_applications(userid, g.conn)
  print applications
  context = dict(data=applications)
  return render_template("studentdashboard.html", **context)

valid_sorting = ["position", "company", "startdate"]

@app.route('/student/profile/education', methods=["GET","POST"])
def studentprofile():
    userid = "1"
    if request.method == "GET":
        studenteducation = get_student_education(userid, g.conn)
        context = dict(data=studenteducation)
        return render_template("studenteducation.html", **context)
    elif request.method == "POST":
        university = request.form['university']
        degree = request.form['degree']
        major = request.form['major']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        description = request.form['description']
        sid = "1"
        add_education(university, degree, major, fromdate, todate, description, sid, g.conn)
        return redirect('/student/profile/education')

@app.route('/student/profile/deleteeducation', methods=["POST"])
def deleteeducation():
    university = request.json['university']
    degree = request.json['degree']
    major = request.json['major']
    fromdate = request.json['fromdate']
    sid = request.json['sid']
    delete_education(university, degree, major, fromdate, sid, g.conn)
    return ('DELETED', 200)

@app.route('/student/profile/experience', methods=["GET","POST"])
def studentexperience():
    userid = "1"
    if request.method == "GET":
        studentexperience = get_student_experience(userid, g.conn)
        context = dict(data=studentexperience)
        return render_template("studentexperience.html", **context)
    elif request.method == "POST":
        company = request.form['company']
        position = request.form['position']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        description = request.form['description']
        sid = "1"
        add_education(company, position, fromdate, todate, description, sid, g.conn)
        return redirect('/student/profile/experience')

@app.route('/student/profile/deleteexperience', methods=["POST"])
def deleteexperience():
    company = request.json['company']
    position = request.json['position']
    fromdate = request.json['fromdate']
    sid = request.json['sid']
    delete_experience(company, position, fromdate, sid, g.conn)
    return ('DELETED', 200)

@app.route('/student/profile/skills', methods=["GET","POST"])
def studentskills():
    userid = "1"
    if request.method == "GET":
        studentskills = get_student_skill(userid, g.conn)
        context = dict(data=studentskills)
        return render_template("studentskills.html", **context)
    elif request.method == "POST":
        skill = request.form['skill']
        proficiency = request.form['proficiency']
        sid = "1"
        add_skill(skill, proficiency, sid, g.conn)
        return redirect('/student/profile/skills')

@app.route('/student/profile/deleteskill', methods=["POST"])
def deleteskill():
    skill = request.json['skill']
    sid = request.json['sid']
    delete_skill(skill, sid, g.conn)
    return ('DELETED', 200)

@app.route('/student/jobs', methods=["GET"])
def studentgetopenjobs():
    sortby = request.args.get('sortby')
    sorttype = request.args.get('sorttype')
    print sortby
    if sortby in valid_sorting:
        jobpositions = get_jobpositions(g.conn, sortby, sorttype)
    else:
        jobpositions = get_jobpositions(g.conn)
    print jobpositions
    context = dict(data=jobpositions)
    return render_template("studentjobpositions.html", **context)

@app.route('/student/apply', methods=["GET","POST"])
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
        pass


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

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)

    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded, use_reloader=True)


  run()

"""from flask import Flask
import os, json
from sqlalchemy import *

db_cred_json = "db_credentials"
db_cred = None

try:
    if not (os.path.exists(db_cred_json) or os.path.isfile(db_cred_json)):
        raise OSError('file does not exist')

    with open(db_cred_json, 'r') as handle:
        db_cred = json.load(handle)
except Exception as err:
    print err

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()"""

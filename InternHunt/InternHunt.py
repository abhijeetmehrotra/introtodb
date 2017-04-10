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

from flask.ext.login import *
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

import studentend, recruiterend, utils


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# login_manager = LoginManager()
app = Flask(__name__, template_folder=tmpl_dir)
# login_manager.init_app(app)


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

@app.route('/student/login', methods=["GET"])
def studentlogin():
  return render_template("studentlogin.html")


@app.route('/student/verfify', methods=["POST"])
def verify_student():
  username = request.form["username"]
  password = request.form["password"]
  studentend.authenticate_user(username,password, g.conn)


@app.route('/recruiter/login', methods=["GET"])
def recruiterlogin():
  return render_template("recruiterlogin.html")

@app.route('/recruiter/login', methods=["POST"])
def verify_recruiter():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    recruiterend.authenticate_recruiter(username, password, g.conn)

@app.route('/recruiter/createjob', methods=["GET"])
def createjobrender():
  return render_template("createapplication.html")

@app.route('/recruiter/createjob', methods=["POST"])
def create_job():
      type = request.form["title"]
      description = request.form["description"]
      fromDate = request.form["fromDate"]
      toDate = request.form["toDate"]
      status = "OPEN"
      hr_hid = 1
      com_cid = 2

      query1 = "insert into jobposition values(DEFAULT, %s, %s, %s, %s, %s, %s, %s)"

      cursor1 = g.conn.execute(query1,(type, status, description, fromDate, toDate, hr_hid, com_cid))

      return redirect("/recruiter/viewjobs", code=302)

@app.route('/recruiter/appaction', methods=["POST"])
def modify_job():

    pid = request.form["pid"]
    sid = request.form["sid"]
    action = request.form["action"]
    query1 = "update application set status =%s where pid=%s and sid=%s"
    cursor1 = g.conn.execute(query1, (action, pid, sid))
    return redirect("/recruiter/jobs?pid=1", code=302)

@app.route('/recruiter/jobs', methods=["GET"])
def viewjobs():
    pid = request.args.get('pid')
    jobposition = utils.get_job(g.conn, pid)
    context = dict(data=jobposition)
    return render_template("viewjob.html", **context)

@app.route('/recruiter/viewjobs', methods=["GET"])
def viewapp():
    jobpositions = utils.get_jobs(g.conn, 'fromdate')
    context = dict(data=jobpositions)
    return render_template("viewapplication.html", **context)

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
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded, use_reloader=true)


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

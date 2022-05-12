import os
from flask import Flask, request, session, render_template, send_file, jsonify, Response, flash, redirect, url_for
import threading 
from datetime import datetime
import psutil
from LogsHandler import *
from Scraper import *
from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

mysql = MySQL(app)
   
# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'UAT'
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
mysql.init_app(app)

@app.route('/log')
def content():
    log_file = config.log_file
    def inner():
        file = open(log_file)
        cont = 'data: '.join(readFile(log_file))
        yield "data: " +f"{cont}"+"\n\n"
        loglines = follow(file)
        for line in loglines:
            yield "data: " +f"{line}"+"\n\n"
        file.close()  
    return Response(inner(), mimetype='text/event-stream')

@app.route('/info')
def sysytem_info():
    processes = getListOfProcessSortedByMemory()
    network_usage = net_usage()
    return jsonify({
        "cpu_percent" : psutil.cpu_percent(),
        "virtual_memory" : psutil.virtual_memory().percent,
        "network_download" : network_usage[0],
        "network_upload" : network_usage[1],
        "processes" : len(processes),
        "threads" : sum([ x['threads'] for x in processes])
        })

@app.route('/')
def index():
    if session.get('loggedin'):
        return render_template('index.html')
    else:
        flash("login first!", category="error")
        return redirect(url_for('login'))

@app.route('/logger')
def logger():
    if session.get('loggedin'):
        return render_template('logger.html')
    flash("login first!", category="error")
    return redirect(url_for('login'))

@app.route('/scrape', methods=["POST"])
def scrape_data():
    data = request.get_json()
    client_spent = int(data.get('clientSpend'))
    last_posted = data.get('lastPosted')
    keyword = data.get('keyword')
    project_length = {
        "short": data.get('project-short'),
        "medium": data.get('project-medium'),
        "long": data.get('project-long')
    }
    unspecifiedJobs = data.get('unspecifiedJobs')
    hourlyRateMin = data.get('hourlyRateMin')
    hourlyRateMax = data.get('hourlyRateMax')
    paymentVerified = data.get('paymentVerified')
    paymentUnverified = data.get('paymentUnverified')
    jobExpert = data.get('jobExpert')
    jobIntermediate = data.get('jobIntermediate')
    jobEntry = data.get('jobEntry')
    countries = data.get('countries')

    today = datetime.today().date().isoformat();
    
    # check if user already has scraped data for this keyword
    cur = mysql.connection.cursor()
    sql = f"""SELECT * FROM user_log WHERE keyword = "{keyword}" AND client_spent <= "{client_spent}" AND last_posted >= STR_TO_DATE("{last_posted}", '%Y-%m-%d') AND date_submitted <= STR_TO_DATE("{today}", '%Y-%m-%d')  """
    cur.execute(sql)
    user_log = cur.fetchone()
    jobs_data = []
    # if user_log:
    #     # already have scraped data for this keyword
    #     # TODO: implement countries condition too
    #     sql = f"""SELECT * FROM job WHERE keyword = "{keyword}" AND posted_on >= STR_TO_DATE("{last_posted}", '%Y-%m-%d') AND client_spent >= "{client_spent}" """
    #     cur.execute(sql)
    #     jobs_data = cur.fetchall()
    # else:
    #     jobs_data = scrape_jobs(keyword, client_spent, last_posted, countries)
    #     # update the job database with the new jobs_data
    # # update the user_log database with the new query    
    status = filter_jobs(jobs_data,keyword,project_length,unspecifiedJobs, hourlyRateMin, hourlyRateMax,paymentVerified,paymentUnverified, jobExpert, jobIntermediate, jobEntry, countries, create_file=True)
    return data, status

@app.route('/file/<filename>', methods=["get"])
def download_csv(filename):
    file_path = f"{app.root_path}/static/data/{filename}.csv"
    if os.path.isfile(file_path):
        return send_file(file_path, mimetype="text/csv")
    return file_path, 404

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    email = request.form.get("email")
    password = request.form.get("password")
    cur = mysql.connection.cursor()
    sql = f"""SELECT * FROM user WHERE email = "{email}" AND password = "{password}" """
    cur.execute(sql)
    user = cur.fetchone()
    cur.close()
    print(user)
    if user:
        session['loggedin'] = True
        session['email'] = email
        return redirect(url_for('index'))
    else:
        flash("user/password is wrong or doesn't exists!", category="error")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('email',None)
    flash("You are successfully logged out", category="success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
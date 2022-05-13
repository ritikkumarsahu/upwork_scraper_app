import os
from flask import Flask, request, session, render_template, send_file, jsonify, Response, flash, redirect, url_for
import threading 
from datetime import datetime
from dateutil import parser
import psutil
from LogsHandler import *
from Scraper import *
from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

mysql = MySQL(app)
   
# MySQL configurations
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_PORT'] = config.MYSQL_PORT
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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
    project_length = data.get('projectLength')
    unspecifiedJobs = data.get('unspecifiedJobs')
    hourlyRateMin = data.get('hourlyRateMin')
    hourlyRateMax = data.get('hourlyRateMax')
    paymentVerified = data.get('paymentVerified')
    paymentUnverified = data.get('paymentUnverified')
    jobType = {
        "expert": data.get('jobExpert'),
        "intermediate": data.get('jobIntermediate'),
        "entry": data.get('jobEntry'),
    }
    countries = data.get('countries')

    today = datetime.today().date().isoformat();
    
    # check if user already has scraped data for this keyword
    cur = mysql.connection.cursor()
    sql = """SELECT * FROM user_log WHERE keyword = %s AND client_spent <= %s AND Date(last_posted) <= STR_TO_DATE(%s, '%%Y-%%m-%%d') AND Date(date_submitted) <= STR_TO_DATE(%s, '%%Y-%%m-%%d') """
    cur.execute(sql, (keyword, client_spent, last_posted, today))
    user_log = cur.fetchall()
    flag = False
    jobs_data = []

    if user_log:
        for log in user_log:
            if set(log['countries'].split(',')).issubset(countries):
                flag = True
                break
    if not flag:
        scraped_data = scrape_jobs(keyword, client_spent, last_posted, ','.join(countries))
        # update the job database with the new scraped_data
        sql = """INSERT INTO job (keyword, title, link, posted_on, hourly_budget_min, hourly_budget_max, fixed_budget, currency_code, is_job_fixed, is_payment_verified, job_level, project_length, country, total_jobs_posted, open_jobs, total_reviews, rating, total_hires, client_since, client_spent, skills) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
        for job_data in scraped_data:
            cur.execute(sql, (job_data['keyword'], job_data['title'], job_data['link'], parser.parse(job_data['posted_on']).strftime('%Y-%m-%d %H:%M:%S'), job_data['hourly_budget_min'], job_data['hourly_budget_max'], job_data['fixed_budget'], job_data['currency_code'], job_data['is_job_fixed'], job_data['is_payment_verified'], job_data['job_level'], job_data['project_length'], job_data['country'], job_data['total_jobs_posted'], job_data['open_jobs'], job_data['total_reviews'], job_data['rating'], job_data['total_hires'], parser.parse(job_data['client_since']).strftime('%Y-%m-%d %H:%M:%S'), job_data['client_spent'], job_data['skills']))
        mysql.connection.commit()
        
    sql = """SELECT * FROM job WHERE keyword = %s AND Date(posted_on) >= STR_TO_DATE(%s, '%%Y-%%m-%%d') AND client_spent >= %s """
    cur.execute(sql, (keyword, last_posted, client_spent))
    jobs_data = cur.fetchall()

    # update the user_log database with the new query    
    sql = """INSERT INTO user_log (user, date_submitted, keyword, last_posted, hourly_budget_min, hourly_budget_max, currency_code, unspecified_jobs, payment_verified, payment_unverified, job_expert, job_intermediate, job_entry, project_length_zero, project_length_short, project_length_medium, project_length_long, client_spent, countries) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
    cur.execute(sql, (session.get('user_id'), datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), keyword, last_posted, hourlyRateMin, hourlyRateMax, 'USD', unspecifiedJobs, paymentVerified, paymentUnverified, jobType.get('expert'), jobType.get('intermediate'), jobType.get('entry'), project_length.get('zero'), project_length.get('short'), project_length.get('medium'), project_length.get('long'), client_spent, ','.join(countries)))
    mysql.connection.commit()

    status = filter_jobs(jobs_data,keyword,project_length,unspecifiedJobs, hourlyRateMin, hourlyRateMax,paymentVerified,paymentUnverified, jobType, countries, create_file=True)
    return jsonify({'file':f"/file/{keyword}"}), status

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
    sql = f"""SELECT * FROM user WHERE email = %s AND password = %s """
    cur.execute(sql, (email, password))
    user = cur.fetchone()
    cur.close()
    print(user)
    if user:
        session['loggedin'] = True
        session['email'] = user["email"]
        session['user_id'] = user["id"]
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
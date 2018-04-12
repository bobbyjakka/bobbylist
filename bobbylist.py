from flask import Flask, render_template, request, session, url_for
from flask_triangle import Triangle
from flask_mail import Mail, Message
import hashlib

from os.path import dirname, realpath
from werkzeug.utils import secure_filename, redirect
import os
from pymongo import MongoClient
from multiprocessing import Value
import json


counter = Value('i', 0)

app = Flask(__name__, static_path='/static')
app.secret_key = 'tonystark'
Triangle(app)

app.static_folder = 'static'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME = 'noreply.bobbylist@gmail.com',
    MAIL_PASSWORD = 'BobbylistBobbylistnoreplynoreply'
)

mongo_client = MongoClient(host='127.0.0.1',port=27017, connect=False)
bobbylistdb = mongo_client['bobbylist']

UPLOAD_FOLDER = '/static/imgs/users'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mail = Mail(app)

def send_mail(recipients_list,subject, message):
    msg = mail.send_message(
        subject,
        sender='noreply.bobbylist@gmail.com',
        recipients=recipients_list,
        body=message
    )
    return 'Mail sent'


@app.route('/')
def initiate_launch():
    if session.get('loggedin'):
        if session['loggedin'] == True :
            user_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
            people_list = []
            people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
            if people_list_db is not None:
                if len(people_list_db['people']) > 0:
                    for person in people_list_db['people']:
                        people_dict = {}
                        person_db = bobbylistdb.users.find_one({"email": person}, {"_id": 0})
                        if (person_db is not None):
                            people_dict['img'] = person_db['img']
                            people_dict['username'] = person_db['username']
                            people_dict['email'] = person_db['email']
                            people_list.append(people_dict)
            tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"}, {"_id": 0})
            tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                      {"_id": 0})
            tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                        {"_id": 0})
            return render_template("dashboard.html", newuser=False, user_details=user_db,
                                   tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                                   tasks_completed_details=tasks_completed_db, people_details=people_list)
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if session.get('loggedin'):
            if session['loggedin'] == True:
                user_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
                people_list = []
                people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
                if people_list_db is not None:
                    if len(people_list_db['people']) > 0:
                        for person in people_list_db['people']:
                            people_dict = {}
                            person_db = bobbylistdb.users.find_one({"email": person}, {"_id": 0})
                            if (person_db is not None):
                                people_dict['img'] = person_db['img']
                                people_dict['username'] = person_db['username']
                                people_dict['email'] = person_db['email']
                                people_list.append(people_dict)
                tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"},
                                                        {"_id": 0})
                tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                          {"_id": 0})
                tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                            {"_id": 0})
                return render_template("dashboard.html", newuser=False, user_details=user_db,
                                       tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                                       tasks_completed_details=tasks_completed_db, people_details=people_list)
            else:
                return render_template("index.html")
        else:
            return render_template("index.html")
    if request.method == 'POST':
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        if hashlib.sha256(login_password).hexdigest() == bobbylistdb.users.find_one({"email": login_email}, {"_id": 0})['hashpwd']:
            user_db = bobbylistdb.users.find_one({"email": login_email}, {"_id": 0})
            session['email'] = user_db['email']
            session['img'] = user_db['img']
            session['username'] = user_db['username']
            session['loggedin'] = True
            people_list = []
            people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
            if people_list_db is not None:
                if len(people_list_db['people']) > 0:
                    for person in people_list_db['people']:
                        people_dict = {}
                        person_db = bobbylistdb.users.find_one({"email": person},{"_id": 0})
                        if(person_db is not None):
                            people_dict['img'] = person_db['img']
                            people_dict['username'] = person_db['username']
                            people_dict['email'] = person_db['email']
                            people_list.append(people_dict)
            tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"}, {"_id": 0})
            tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                      {"_id": 0})
            tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                        {"_id": 0})
            return render_template("dashboard.html", newuser=False, user_details=user_db,
                                   tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                                   tasks_completed_details=tasks_completed_db, people_details = people_list)
        return render_template("index.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        signup_email = request.form['signup_email']
        signup_password = request.form['signup_password']
        hashemail = hashlib.sha256(signup_email.encode('utf-8')).hexdigest()
        hashpwd = hashlib.sha256(signup_password.encode('utf-8')).hexdigest()
        verfication_hash_dict = {}
        verfication_hash_dict['email'] = signup_email
        verfication_hash_dict['hashemail'] = hashemail
        verfication_hash_dict['hashpwd'] = hashpwd
        verfication_hash_dict['checked'] = False
        recepients = []
        recepients.append(signup_email)
        send_mail(recepients,'Your activation link', "Please click on this link http://www.bobbylist.com/confirm/"+hashemail)
        print "mail sent"
        if bobbylistdb.email_verification.find_one({"hashemail":hashemail},{"_id":0}) == None:
            bobbylistdb.email_verification.insert(verfication_hash_dict)
        else:
            return render_template("verification.html", again_signup=True)
        return render_template("verification.html", again_signup=False)

@app.route('/confirm/<verify_link>')
def verifylink(verify_link):
    user_verifilist = bobbylistdb.email_verification.find_one({"hashemail":verify_link},{"_id":0})
    if user_verifilist['checked'] == False:
        return render_template("heyitsme.html", user_email= user_verifilist['email'])
    else:
        # user_db = bobbylistdb.users.find_one({"user_email":user_verifilist['email']},{"_id":0})
        return render_template("index.html")

@app.route('/user_creation',  methods=['GET','POST'])
def create_user():
    if request.method == 'GET':
        if session.get('loggedin'):
            if session['loggedin'] == True:
                user_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
                people_list = []
                people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
                if people_list_db is not None:
                    if len(people_list_db['people']) > 0:
                        for person in people_list_db['people']:
                            people_dict = {}
                            person_db = bobbylistdb.users.find_one({"email": person}, {"_id": 0})
                            if (person_db is not None):
                                people_dict['img'] = person_db['img']
                                people_dict['username'] = person_db['username']
                                people_dict['email'] = person_db['email']
                                people_list.append(people_dict)
                tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"},
                                                        {"_id": 0})
                tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                          {"_id": 0})
                tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                            {"_id": 0})
                return render_template("dashboard.html", newuser=False, user_details=user_db,
                                       tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                                       tasks_completed_details=tasks_completed_db, people_details=people_list)
            else:
                return render_template("index.html")
        else:
            return render_template("index.html")
    if request.method == 'POST':
        signup_dict = {}
        signup_dict['firstname'] = request.form['firstnameinput']
        signup_dict['lastname'] = request.form['lastnameinput']
        signup_dict['username'] = request.form['usernameinput']
        signup_dict['email'] = request.form['emailinput']
        people_list = []
        signup_dict['people'] = people_list
        user_verify_table_record = bobbylistdb.email_verification.find_one({"email":signup_dict['email']})
        signup_dict['hashpwd'] = user_verify_table_record['hashpwd']
        signup_dict['checked'] = True
        if 'uploadfile' not in request.files:
            signup_dict['img'] = './static/imgs/bobbylist_user.png'
        else:
            file = request.files['uploadfile']
            if file.filename == "":
                signup_dict['img'] = './static/imgs/bobbylist_user.png'
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(dirname(realpath(__file__))+app.config['UPLOAD_FOLDER'] , signup_dict['username'] + '.jpg'))
                signup_dict['img'] = app.config['UPLOAD_FOLDER'] + '/' + signup_dict['username'] + '.jpg'
        bobbylistdb.users.insert(signup_dict)
        bobbylistdb.email_verification.update({"_id": user_verify_table_record['_id']}, {"$set": {'checked': True}})
        user_db = bobbylistdb.users.find_one({"email": signup_dict['email']}, {"_id": 0})
        session['email'] = signup_dict['email']
        session['username'] = signup_dict['username']
        session['img'] = signup_dict['img']
        session['loggedin'] = True
        people_list = []
        people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
        if people_list_db is not None:
            if len(people_list_db['people']) > 0:
                for person in people_list_db['people']:
                    people_dict = {}
                    person_db = bobbylistdb.users.find_one({"email": person}, {"_id": 0})
                    if (person_db is not None):
                        people_dict['img'] = person_db['img']
                        people_dict['username'] = person_db['username']
                        people_dict['email'] = person_db['email']
                        people_list.append(people_dict)
        tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"}, {"_id": 0})
        tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                  {"_id": 0})
        tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                    {"_id": 0})
        return render_template("dashboard.html", newuser=True, user_details=user_db,
                               tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                               tasks_completed_details=tasks_completed_db, people_details=people_list)

@app.route('/dashboard/create_task',  methods=['GET','POST'])
def create_task():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        with counter.get_lock():
            counter.value += 1
        task_dict = {}
        task_dict['task_id'] = hashlib.sha256(str(counter.value)).hexdigest()
        task_dict['task_title'] = request.form['task_title']
        task_dict['task_assignee'] = request.form['task_assignee']
        assigned_user = bobbylistdb.users.find_one({"email": task_dict['task_assignee']}, {"_id": 0})
        task_dict['task_assignee_img'] = assigned_user['img']
        task_dict['task_assignee_username'] = assigned_user['username']
        task_dict['task_assigned_by'] = request.form['task_assigned_by']
        assigned_by_user = bobbylistdb.users.find_one({"email": task_dict['task_assigned_by']}, {"_id": 0})
        task_dict['task_assigned_by_img'] = assigned_by_user['img']
        task_dict['task_assigned_by_username'] = assigned_by_user['username']
        task_dict['task_desc'] = request.form['task_desc']
        task_dict['task_creation_date'] = request.form['task_creation_date']
        task_dict['task_due_date'] = request.form['task_due_date']
        task_dict['task_milestones'] = request.form.getlist('milestones')
        task_dict['status'] = 'start'
        task_dict['tag'] = ''
        bobbylistdb.tasks.insert(task_dict)
        user_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
        people_list = []
        people_list_db = bobbylistdb.users.find_one({"email": session['email']}, {"_id": 0})
        if people_list_db is not None:
            if len(people_list_db['people']) > 0:
                for person in people_list_db['people']:
                    people_dict = {}
                    person_db = bobbylistdb.users.find_one({"email": person}, {"_id": 0})
                    if (person_db is not None):
                        people_dict['img'] = person_db['img']
                        people_dict['username'] = person_db['username']
                        people_dict['email'] = person_db['email']
                        people_list.append(people_dict)
        tasks_start_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "start"}, {"_id": 0})
        tasks_current_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "current"},
                                                  {"_id": 0})
        tasks_completed_db = bobbylistdb.tasks.find({'task_assignee': session['email'], "status": "completed"},
                                                    {"_id": 0})
        return render_template("dashboard.html", newuser=False, user_details=user_db,
                               tasks_start_details=tasks_start_db, tasks_current_details=tasks_current_db,
                               tasks_completed_details=tasks_completed_db, people_details=people_list)

@app.route('/dashboard/invite_people', methods=['GET', 'POST'])
def invite_people():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        added_people = request.json['add_people_input']
        userdb = bobbylistdb.users.find_one({"email": session['email']})
        if userdb is not None:
            people_list_user = userdb['people']
            if len(people_list_user) > 0:
                if added_people not in people_list_user:
                    people_list_user.append(added_people)
                    bobbylistdb.users.update({"_id": userdb['_id']}, {"$set": {'people': people_list_user}})
            else:
                people_list_user.append(added_people)
                bobbylistdb.users.update({"_id": userdb['_id']}, {"$set": {'people': people_list_user}})
        receipients = []
        receipients.append(added_people)
        send_mail(receipients, session['email'] + ' has added you to his/her bobbylist contacts.', session['email']+' asks you to Join/Login http://www.bobbylist.com to view your pending tasks')
        return ""

@app.route('/dashboard/change_task_status', methods=['GET', 'POST'])
def change_task_status():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        task_id = request.json['task_id']
        task_status = request.json['task_status']
        bobbylistdb.tasks.update({"task_id": task_id}, {"$set": {'status': task_status}})
        return ""

@app.route('/dashboard/change_task_tag', methods=['GET', 'POST'])
def change_task_tag():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        task_id = request.json['task_id']
        task_tag = request.json['task_tag']
        bobbylistdb.tasks.update({"task_id": task_id}, {"$set": {'tag': task_tag}})
        return ""

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('username', None)
    session.pop('img', None)
    return redirect(url_for('initiate_launch'))


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0")
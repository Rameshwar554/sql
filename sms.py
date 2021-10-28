# STUDENT MANAGEMENT SYSTEM
# WITH ORACLE, CRUD operation using REST API

# from functools import wraps
from flask import *
from flask_sqlalchemy import SQLAlchemy, request
from twilio.rest import Client                 # for mobile otp
from random import *                           # for mobile otp and for email also
from flask_mail import Mail, Message           # for email otp
import random
import mysql.connector
import pymysql
# from typing import Callable


sms = Flask(__name__)
mail = Mail(sms)
sms.secret_key = 'otp'


# app.config[url] = value
sms.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Rohit#1234@localhost:3306/student'
# sms.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://system:system@127.0.0.1:1521/xe'
db = SQLAlchemy(sms)


# class MySQLAlchemy(SQLAlchemy):
#     Column: Callable
#     Integer: Callable
#     String: Callable


class Student(db.Model):
    stuid = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    marks = db.Column(db.Integer(), unique=False, nullable=False)

db.create_all()


@sms.route('/')
def home():
    return render_template("student_login.html")


@sms.route('/')
def Welcomepage():
    return render_template("Welcome.html")


# def login_required(test):
#     @wraps(test)
#     def wrap(*args, **kwargs):
#         if 'logged_in' in session:
#             return test(*args, **kwargs)
#         else:
#             return redirect(url_for('home'))
#     return wrap


# ADDING STUDENT
@sms.route("/addstuinfo", methods=['GET', 'POST'])
# @login_required
def stuInfo():
    if request.method == 'POST':
        stuid = request.form.get('stuid')
        name = request.form.get('name')
        marks = request.form.get('marks')

        entry = Student(stuid=stuid, name=name, marks=marks)
        db.session.add(entry)
        db.session.commit()

    return render_template("add_student.html")


# DELETING STUDENT
@sms.route("/delete", methods=['GET', 'POST'])
def deleteinfo():
    if request.method == 'POST':
        stuid = request.form.get('stuid')
        student = Student.query.filter_by(stuid=stuid).first()
        db.session.delete(student)
        db.session.commit()

    return render_template("delete.html")


# DELETING USING REST API
@sms.route("/delete/<int:stuid>", methods=['GET', 'POST'])
def delete_info(stuid):
        student = Student.query.get(stuid)
        db.session.delete(student)
        db.session.commit()

        return "Deleted Successfully Using Rest API"


# UPDATE STUDENT
@sms.route("/update", methods=['GET', 'POST'])
def updateinfo():
    if request.method == 'POST':
        oldstuid = request.form.get('oldstuid')
        newstuid = request.form.get('newstuid')

        oldname = request.form.get('oldname')
        newname = request.form.get('newname')

        oldmarks = request.form.get('oldmarks')
        newmarks = request.form.get('newmarks')

        student = Student.query.filter_by(stuid=oldstuid).first()
        # student = Student.query.filter_by(name=oldname).first()

        student.stuid = newstuid
        student.name = newname
        student.marks = newmarks
        db.session.commit()
        # return redirect("/")

    return render_template("update.html")


# UPDATE USING REST API
@sms.route("/update/<int:stuid>", methods=['GET', 'POST'])
def update_info(stuid):
    student = Student.query.filter_by(stuid=stuid).first()
    if request.method == 'POST':
        if student:
            db.session.delete(student)
            db.session.commit()
            stuid = request.form['stuid']
            name = request.form['name']
            marks = request.form['marks']
            student = Student(stuid=stuid, name=name, marks=marks)
            db.session.add(student)
            db.session.commit()

    return render_template("updaterest.html", student=student)


@sms.route("/logout")
def logout():
    if "user_id2" in session:
        session.pop("user_id2", None)
    return render_template("student_login.html")


################################## DISPLAY ##################################################################

# DISPLAY ALL DATA IN ONE PAGE AND SEARCH A PARTICULAR STUDENT
@sms.route("/display", methods=['GET', 'POST'])
def displaydata():
    students = Student.query.order_by(Student.stuid.asc())
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        students = Student.query.filter(Student.name.like(search))
        return render_template("displayinfo.html", students=students, tag=tag)

    return render_template("displayinfo.html", students=students)
    # students = Student.query.all()
    # return render_template("displayinfo.html", students=students)


# USING PAGINATION AND REST API
@sms.route("/display/<int:page_num>")
def displaydat(page_num):
    students = Student.query.paginate(per_page=5, page=page_num, error_out=True)

    return render_template("displaytest.html", students=students)


################################## MOBILE LOGIN ################################################################


@sms.route('/mobilelogin')
def mobilelogin():
    return render_template("login.html")


@sms.route("/getOTP", methods=['GET', 'POST'])
def getOTP():
    number = request.form['number']
    val = getOTPApi(number)
    if val:
        return render_template("enterotp.html")
    # return render_template("enterotp.html")


@sms.route('/validateOTP', methods=['POST'])
def validateotp():
    otp = request.form['otp']
    if 'response' in session:
        s = session['response']
        session.pop('response', None)
        if s == otp:
            return render_template("Welcome.html")
        else:
            return "You Are Not Authorized Sorry!!!"


def generateOTP():
    return random.randrange(100000, 999999)


def getOTPApi(number):
    account_sid = 'AC1db974f60f7af09f632246b976cdda6e'
    auth_token = 'eba433b3260d9c49ed44d995551e6f8e'
    # auth_token = 'dd112f23765598165d08174e3c43d51a'  #(first token not valid now)
    # auth_token = '7d7cb7e946a27b6b562421fb57b1420f' #(second token not valid now)
    client = Client(account_sid, auth_token)
    otp = generateOTP()
    body = 'Your OTP is ' + str(otp)
    message = client.messages.create(to=number, from_='+16207431805', body=body)
    session['response'] = str(otp)
    if message.sid:
        return True
    else:
        return False


################################## EMAIL LOGIN ###############################################################


sms.config["MAIL_SERVER"] = 'smtp.gmail.com'
sms.config["MAIL_PORT"] = 465
sms.config["MAIL_USERNAME"] = 'dummypass789@gmail.com'
sms.config['MAIL_PASSWORD'] = 'Dummy@00'                    #you have to give your password of gmail account
sms.config['MAIL_USE_TLS'] = False
sms.config['MAIL_USE_SSL'] = True
mail = Mail(sms)
otp = randint(000000, 999999)


@sms.route('/emaillogin')
def emaillogin():
    return render_template("emailindex.html")


@sms.route('/verify', methods=["POST"])
def verify():
    email = request.form['email']
    msg = Message(subject='OTP', sender='dummypass789@gmail.com', recipients=[email])
    msg.body = str(otp)
    mail.send(msg)
    return render_template('emailverify.html')


@sms.route('/validate', methods=['POST'])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return render_template("Welcome.html")
    if 'response' in session:
        s = session['response']
        session.pop('response', None)
    return "<h3>Please Try Again</h3>"


########################################## CHAT BOT #################################################

from Conversation import start_chat


@sms.route('/chatbot', methods=['GET', 'POST'])
def start_page():
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['user_input'].lower()
        bot_response = start_chat(user_input)
        return render_template("home.html", bot_response=bot_response)
    else:
        return render_template("home.html")


if __name__ == "__main__":
    sms.run(debug=True)
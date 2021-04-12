from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'signup_data'

mysql = MySQL(app)


@app.route('/')
@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':

        u = request.form['Email']
        p = request.form['Password']

        '''# Check if account exists using MySQL'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT su.Email, su.Password FROM savesignupdata as su WHERE Email = %s AND Password = %s',
                       (u, p))
        '''# Fetch one record and return result'''
        savesignupdata = cursor.fetchone()

        if savesignupdata:
            '''# Create session data, we can access this data in other routes'''
            session['logged_in'] = True
            session['u'] = savesignupdata['Email']
            session['p'] = savesignupdata['Password']
            '''# Redirect to home page'''
            return 'Logged in successfully!'
        else:
            '''# Account doesnt exist or username/password incorrect'''
            msg = 'Incorrect username/password!'
    '''# Show the login form with message (if any)'''
    return render_template("signin.html", msg=msg)


@app.route("/signup", methods=['GET', 'POST'])
def insert():
    if request.method == "POST":
        n = request.form['name']
        e = request.form['email']
        p = request.form['phone']

        cur = mysql.connection.cursor()
        cur.execute("INSERT  INTO signupdata (Name, Email, Phone, Date) VALUES (%s, %s, %s, %s)",
                    (n, e, p, datetime.now()))

        mysql.connection.commit()
    return render_template("index.html")


app.run(debug=True)

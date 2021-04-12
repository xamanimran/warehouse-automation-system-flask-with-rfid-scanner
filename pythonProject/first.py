from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import serial
import time
from datetime import datetime
import threading

app = Flask(__name__)

''''Defining the secret key'''
app.secret_key = 'super-secret-key'

'''Making database connection'''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

'''Initializing  MySQL'''
mysql = MySQL(app)


@app.route("/pythonlogin/", methods=['GET', 'POST'])
def login():
    """ declaring Message if something goes wrong..."""
    msg = ''
    '''# Check if "username" and "password" POST requests exist (user submitted form)'''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

        '''Making variable for access of get user'''

        get_user = request.form['username']
        get_pass = request.form['password']

        '''Checking in database for the entered user that if it exsist or not'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username, password FROM accounts WHERE username = %s AND password = %s',
                       (get_user, get_pass,))
        '''Fetching the desired result in variable fetch_data'''
        fetch_data = cursor.fetchone()
        ''' If account exists in accounts table in the database'''
        if fetch_data:
            '''creating session for using it in other ways (logout)'''
            session['logged_in'] = True
            session['employee_pass'] = fetch_data['password']
            session['employee_uname'] = fetch_data['username']
            '''# Redirect to home page'''
            return redirect(url_for('home'))
        else:

            ''' if Account doesnt exist or username/password is incorrect'''
            msg = 'Incorrect username/password!'
    '''Showing the login form with message'''
    return render_template('login.html', msg=msg)


''' http://localhost:5000/python/logout - this will be the logout page'''


@app.route('/pythonlogin/logout')
def logout():
    """Removing session data, this will log the user out"""
    session.pop('logged_in', None)
    session.pop('employee_pass', None)
    session.pop('employee_uname', None)
    '''Redirect to the login page'''
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    """Output message if something goes wrong..."""
    msg = ''
    ''' # Check if "username", "password" and "email" POST requests exist (user submitted form)'''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'key' in request.form:
        '''Create variables for easy access'''
        u = request.form['username']
        p = request.form['password']
        e = request.form['email']
        get_key = request.form['key']
        ''' Check if account exists using MySQL'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        '''fetching the supervisor key for registration'''

        cursor.execute('SELECT super_key FROM supervisor WHERE super_key = %s', (get_key,))
        key = cursor.fetchone()
        '''fetching the username from database for already exsistance'''
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (u,))
        account = cursor.fetchone()
        '''If account exists checks'''
        if account:
            msg = 'Account already exists!'
        elif not u or not p or not e:
            msg = 'Please fill out the form!'
        else:
            if key:

                '''Account doesnt exists and the form data is valid, now insert new account into accounts table'''
                cursor.execute('INSERT INTO accounts (username, password, email, date) VALUES (%s, %s, %s,%s)',
                               (u, p, e, datetime.now()))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
            else:
                msg = 'Wrong supervisor key'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


'''# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users'''


@app.route('/pythonlogin/home')
def home():
    """ Checking if user is already logged_in"""
    if 'logged_in' in session:
        ''' User is loggedin show them the home page'''
        return render_template('home.html', user=session['employee_uname'])
    '''# User is not loggedin redirect to login page'''
    return redirect(url_for('login'))


'''# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users'''


@app.route('/pythonlogin/profile')
def profile():
    """Checking if user is already logged_in"""
    if 'logged_in' in session:
        '''getting all the account info for the user for displaying it on the profile page'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['employee_uname'],))
        account = cursor.fetchone()
        '''Showing profile page with account info to the employee'''
        return render_template('profile.html', acc=account)
    '''if User is not logged_in redirect to login page'''
    return redirect(url_for('login'))


@app.route('/pythonlogin/crud')
def crud():
    """ Checking if user is already logged_in"""
    if 'logged_in' in session:
        ''' User is loggedin show them the stock page'''
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM stockdata')
        det = cursor.fetchall()
        cursor.close()

        return render_template('crud.html', fetchget=det, user=session['employee_uname'])
    '''# User is not loggedin redirect to login page'''
    return redirect(url_for('login'))


@app.route('/instock/get', methods=['GET', 'POST'])
def getnum():

    if 'logged_in' in session:
        """Checking if user is already logged_in"""
        getitt = serial.Serial('COM7', baudrate=9600)
        '''while 1:'''
        time.sleep(2)
        while getitt.inWaiting() > 0:
            dat = getitt.readline().decode('ascii')
        return jsonify(result=dat)
    return redirect(url_for('crud'))


@app.route('/crud/instock', methods=['GET', 'POST'])
def instock():
    if 'logged_in' in session:
        """Checking if user is already logged_in"""
        """Output message if something goes wrong..."""
        ''' # Check if "username", "password" and "email" POST requests exist (user submitted form)'''
        if request.method == 'POST' and 'rfidno' in request.form and 'lotno' in request.form and 'color' in request.form and 'Quantity' in request.form:
            '''Create variables for easy access'''
            ba = request.form['barcode']
            rf = request.form['rfidno']
            lot = request.form['lotno']
            co = request.form['color']
            qu = request.form['Quantity']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT rfidno FROM stockdata WHERE rfidno = %s', (rf,))
            get = cursor.fetchone()
            cursor.execute('SELECT stockid FROM stockdata WHERE stockid=%s', (ba,))
            barco = cursor.fetchone()
            if barco and get:
                flash("rfid number and barcode number already exsist")
                return redirect(url_for('crud'))
            elif get:
                flash('rfid is already exsist')
                return redirect(url_for('crud'))
            elif barco:
                flash("barcode number already exsist")
                return redirect(url_for('crud'))
            else:
                cursor.execute(
                    'INSERT INTO stockdata (stockid,rfidno,lotno,color,quantity,DateTime) VALUES (%s, %s, %s, %s, %s,%s)',
                    (ba, rf, lot, co, qu, datetime.now()))
                mysql.connection.commit()
                '''just for knowing that it is working or not'''
                '''getrf()'''
                flash("Stock inserted successfully")
                return redirect(url_for('crud'))
        return redirect(url_for('crud'))
    else:
        return redirect(url_for('login'))


@app.route('/crud/upstock/<string:iddat>', methods=['GET', 'POST'])
def upstock(iddat):
    if 'logged_in' in session:

        """Output message if something goes wrong..."""
        msg = ''
        ''' # Check if "username", "password" and "email" POST requests exist (user submitted form)'''
        if request.method == 'POST':
            '''Create variables for easy access'''
            rf = request.form['rfidno']
            lot = request.form['lotno']
            co = request.form['color']
            qu = request.form['Quantity']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
            
            UPDATE stockdata
            SET lotno=%s,color=%s,quantity=%s
            WHERE rfidno=%s 
            
            """, (lot, co, qu, rf))
            mysql.connection.commit()
            cursor.execute('SELECT stockid FROM stockdata WHERE stockid=%s', (iddat,))
            fetch = cursor.fetchone()
            if fetch:
                cursor.execute("""
                SELECT COUNT(*)+1 as rid
                FROM save_updated_stock
                WHERE id=%s
                
                """, (iddat,))
                get = cursor.fetchone()
                ok = get['rid']
                cursor.execute("""
                INSERT INTO save_updated_stock(id, rfid_no, lot_no, color_, quantity_percen, date_Time, After)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                """, (iddat, rf, lot, co, qu, datetime.now(), ok))
                mysql.connection.commit()
            flash("Stock updated successfully")
            return redirect(url_for('crud'))
    return redirect(url_for('login'))


'''get data from web and delete'''


@app.route('/crud/deletestock/<string:id_data>', methods=['GET', 'POST'])
def deletestock(id_data):
    if 'logged_in' in session:
        """Output message if something goes wrong..."""
        msg = ''
        ''' # Check if "username", "password" and "email" POST requests exist (user submitted form)'''
        '''Create variables for easy access'''
        ''' stid = request.form['stockid']'''

        cursor = mysql.connection.cursor()
        cursor.execute(' DELETE FROM stockdata WHERE stockid=%s ', (id_data,))
        mysql.connection.commit()
        flash("item Deleted successfully")
        return redirect(url_for('crud'))
    return redirect(url_for('login'))


@app.route('/pythonlogin/stockupdatedetail')
def crudupdatedetail():
    """ Checking if user is already logged_in"""
    if 'logged_in' in session:
        ''' User is loggedin show them the stock page'''
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM save_updated_stock')
        det = cursor.fetchall()
        cursor.close()

        return render_template('stockupdatedetail.html', fetchget=det, user=session['employee_uname'])
    '''# User is not loggedin redirect to login page'''
    return redirect(url_for('login'))


@app.route('/pythonlogin/searchstock')
def stocksearch():
    """Checking if user is already logged_in"""
    if 'logged_in' in session:
        return render_template('search_stock.html')
    '''if User is not logged_in redirect to login page'''
    return redirect(url_for('login'))


@app.route('/searchstock', methods=['GET', 'POST'])
def getstock():
    msg = ''
    """Checking if user is already logged_in"""
    if 'logged_in' in session:
        if request.method == 'POST' and 'stoidno' in request.form:
            '''Create variables for easy access'''
            bnum = request.form['stoidno']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT stockid FROM stockdata WHERE stockid=%s', (bnum,))
            fetch = cursor.fetchone()
            if fetch:
                cursor.execute('SELECT * FROM stockdata WHERE stockid=%s', (fetch['stockid'],))
                accountt = cursor.fetchone()
                cursor.close()
                return render_template('dispstock.html', acc=accountt, user=session['employee_uname'])
            else:
                flash("invalid no")
                return redirect(url_for('stocksearch'))
    '''if User is not logged_in redirect to login page'''
    return redirect(url_for('login'))


'''getting the rfid and save to database'''


@app.route('/clickme', methods=['GET', 'POST'])
def getrf():
    """Checking if user is already logged_in"""
    if 'logged_in' in session:
        """Checking if user is already logged_in"""
        getitt = serial.Serial('COM7', baudrate=9600)
        '''while 1:'''
        time.sleep(2)
        while getitt.inWaiting() > 0:
            dat = getitt.readline().decode('ascii')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT rfidno FROM stockdata WHERE rfidno=%s', (dat, ))
        ok = cursor.fetchone()
        if ok and ok['rfidno'] != 0:
            cursor.execute('SELECT * FROM stockdata WHERE rfidno=%s', (dat,))
            accountt = cursor.fetchone()
            cursor.close()
            return render_template('dispstock.html', acc=accountt, user=session['employee_uname'])
        else:
            flash("rfid no doesn't exsist")
            return redirect(url_for('stocksearch'))
    else:
        return redirect(url_for('login'))


app.run(debug=True)

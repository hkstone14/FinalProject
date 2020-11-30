from typing import List, Dict
import simplejson as json
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
# from token import confirm_token, generate_confirmation_token

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app.secret_key = os.urandom(24)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'covidInsight'

mysql.init_app(app)

s = URLSafeTimedSerializer('Thisisasecret!')


@app.route('/')
def index():
    return render_template('login.html')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    cursor = mysql.get_db().cursor()
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    cursor.execute('SELECT * FROM users WHERE username= %s', username)
    user_username = cursor.fetchone()
    cursor.execute('SELECT * FROM users WHERE email= %s', email)
    user_email = cursor.fetchone()
    if user_email:
        flash('Account already exist with given email address!', 'error')
        return render_template('register.html')
    elif user_username:
        flash('Username ' + username + ' is already taken', 'error')
    else:
        cursor.execute('INSERT INTO users (email, username, password) VALUES(%s, %s, %s)', (email, username, password))
        mysql.get_db().commit()
        flash('Your account registered successfully.', 'success')
        return render_template('login.html')


# @app.route('/confirm/<token>')
# def confirm_email(token):
#     try:
#         email = confirm_token(token)
#     except:
#         flash('The confirmation link is invalid or has expired.', 'danger')
#
#     if user.confirmed:
#         flash('Account already confirmed. Please login.', 'success')
#     else:
#         user.confirmed = True
#         user.confirmed_on = datetime.datetime.now()
#         db.session.add(user)
#         db.session.commit()
#         flash('You have confirmed your account. Thanks!', 'success')
#     return redirect(url_for('login'))


@app.route('/home')
def home():
    if 'id' in session:
        username = session['username']
        return render_template('home.html', user=username)
    else:
        return redirect('index')


# User login
@app.route('/login_validation', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE username= %s AND password= %s', (username, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Incorrect username/password', 'error')
            return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You are now logged off.', 'success')
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

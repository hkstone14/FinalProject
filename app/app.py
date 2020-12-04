import datetime

from flask import Flask, render_template, flash, redirect, url_for, session, request
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app.secret_key = os.urandom(24)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'covidInsight'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_USERNAME'] = 'covid19.insightlook@gmail.com'
app.config['MAIL_PASSWORD'] = 'Covid@1999'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'hkstone14@gmail.com'
app.config['SECRET_KEY'] = 'my_precious'
app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
mail = Mail(app)
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
        flash('Username ' + username + ' is already taken!', 'error')
        return render_template('register.html')
    else:
        email_confirm = 'Thanks for signing up for covid-19 insight. Please follow this link to activate your account:'
        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email.html', confirm_url=confirm_url, email_confirm=email_confirm)
        subject = "Please confirm your email"
        send_email(email, subject, html)
        flash('A confirmation email has been sent via email.', 'success')
        cursor.execute('INSERT INTO users (email, username, password) VALUES(%s, %s, %s)', (email, username, password))
        mysql.get_db().commit()
        return redirect(url_for("index"))


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM users WHERE email= %s', email)
    user = cursor.fetchone()
    # user = User.query.filter_by(email=email).first_or_404()
    if user:
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('index'))


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    return render_template("resetPassword.html", token=token)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


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


@app.route('/forgot')
def forgot():
    return render_template("forgotPassword.html")


@app.route('/reset_password', methods=['PUT', 'POST'])
def reset_password():
    cursor = mysql.get_db().cursor()
    email = request.form['email']
    cursor.execute('SELECT * FROM users WHERE email= %s', email)
    user_email = cursor.fetchone()
    if user_email:
        confirmed = 'false'
        reset_pass = 'Please click on the below link to reset your password:'
        token = generate_confirmation_token(email)
        confirm_url = url_for('reset_with_token', token=token, _external=True)
        html = render_template('email.html', confirm_url=confirm_url, reset_pass=reset_pass, confirmed=confirmed)
        subject = "Password reset requested"
        send_email(email, subject, html)
        flash('The password reset link has been sent via email.', 'success')
        return render_template("forgotPassword.html")
    else:
        flash('The email you entered does not exist!', 'error')
        return render_template("forgotPassword.html")


@app.route('/change_password/<token>', methods=['POST'])
def change_password(token):
    try:
        email = confirm_token(token)
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
    cursor = mysql.get_db().cursor()
    password = request.form['password']
    cursor.execute('SELECT * FROM users WHERE email= %s', email)
    user = cursor.fetchone()
    if user['password'] == password:
        flash('Your new password can not be the same as the last one!', 'error')
        return render_template("resetPassword.html", token=token)
    else:
        cursor.execute('UPDATE users SET password = %s WHERE email= %s', (password, email))
        mysql.get_db().commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('index'))


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

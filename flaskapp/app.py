import os
import io
from flask import Flask, render_template, request, redirect, url_for, session 
import mysql.connector
import re
from flask_mysqldb import MySQL
import MySQLdb.cursors
from ocr_core import get_attendence
from werkzeug.utils import secure_filename
import pytesseract
from PIL import ImageFilter
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = 'a'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = '4kGz4X0fxq'
app.config['MYSQL_PASSWORD'] = 'QBNJvgSmVw'
app.config['MYSQL_DB'] = '4kGz4X0fxq'
mysql = MySQL(app)

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# route to index 

@app.route('/')
def index():
    return render_template('index.html')

# route and function to handle the home page
@app.route('/idscanner')
def idscanner():
    return render_template('idscanner.html')


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            userid=  account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('idscanner.html', msg = msg)
            msg = 'Upload ID to get converted into text !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
    msg = 'Upload ID to get converted into text !' 
    


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form  :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  
        address = request.form['address']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, %s)', (username, password, email, address))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html', msg = msg)

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



# route and function to handle the upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    image = request.files['ocrImage']
    text = ''
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = pytesseract.image_to_string(img)
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename)+'.txt','w')
    f.write(text)
    f.close()
    return render_template('upload.html',text=text,filename=f)

if __name__ == '__main__':
    app.run(debug=True)
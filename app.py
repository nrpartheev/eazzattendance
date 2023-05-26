from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import hashlib
import os
import zipfile

app = Flask(__name__)
app.secret_key = 'p0k3m0n' 


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'p0k3m0n'
app.config['MYSQL_PASSWORD'] = 'p0k3m0n'
app.config['MYSQL_DB'] = 'ea'

mysql = MySQL(app)


@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT class_room_id FROM students WHERE username = %s", (username,))
        classrooms = cur.fetchall()
        cur.close()
        classroom_ids = [classroom[0] for classroom in classrooms]
        return render_template('index.html', username=username, classrooms=classroom_ids)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['username'] = user[1] 
            return redirect('/')
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        cur.close()
        
        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        else:
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            
            session['username'] = username 
            return redirect('/')
    
    return render_template('index.html')


@app.route('/createclass', methods=['GET', 'POST'])
def create_classroom():
    if 'username' in session:
        if request.method == 'POST':
            classroom_name = request.form['classroom_name']
            upload_dir = f"upload/{classroom_name}"
            os.makedirs(upload_dir, exist_ok=True)
            zip_file = request.files['zip_file']
            if zip_file and zip_file.filename.endswith('.zip'):
                zip_file.save(f"{upload_dir}/{zip_file.filename}")
                with zipfile.ZipFile(f"{upload_dir}/{zip_file.filename}", 'r') as zip_ref:
                    zip_ref.extractall(upload_dir)
                os.remove(f"{upload_dir}/{zip_file.filename}")
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO students (username, classroom) VALUES (%s, %s)", (username, classroom_name))
            mysql.connection.commit()
            cur.close()
            

    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
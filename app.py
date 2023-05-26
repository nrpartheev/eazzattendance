from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import hashlib
import os
import zipfile
from train import trainmodel
import tensorflow as tf

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
        cur.execute("SELECT classroom FROM classroom WHERE username = %s", (username,))
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
            username = session['username']
            classroom_name = request.form['classroom_name']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM classroom WHERE username = %s and classroom= %s", (username,classroom_name))
            existing_user = cur.fetchone()
            cur.close()
        
            if existing_user:
                error = 'classroom already exists. Please choose a different classroom name.'
                return render_template('signup.html', error=error)
            else:
                upload_dir = f"upload/{username}/{classroom_name}"
                os.makedirs(upload_dir, exist_ok=True)
                zip_file = request.files['zip_file']


                if zip_file and zip_file.filename.endswith('.zip'):
                    zip_file_path = f"{upload_dir}/{zip_file.filename}"
                    zip_file.save(zip_file_path)


                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(upload_dir)

                    os.remove(zip_file_path)
                
                    non_mp4_files = [filename for filename in os.listdir(upload_dir) if not (filename.endswith('.mp4') or filename.endswith('.MOV'))]

                    if non_mp4_files:
                        error_message = "PLEASE UPLOAD A FILE WITH VAILD FORMAT"
                        shutil.rmtree(upload_dir)
                        return render_template('index.html', error=error_message)
            


                    return redirect('/')
            
                else:
                    return render_template('index.html', error='PLEASE UPLOAD ONLY A ZIP FILE')
        
        else:
            return "only post method allowed"
 
    else:
        return render_template('login.html')

@app.route('/classroom')
def classroomeach():
    if 'username' in session:
        username = session['username']
        classroom_name = request.args.get('classroom')
        cur = mysql.connection.cursor()
        cur.execute("SELECT model FROM classroom WHERE username = %s and classroom = %s", (username,classroom_name))
        result = cur.fetchone()
        cur.close()
        if result and result[0] is not None:
            is_trained = 1
        else:
            is_trained = 0

        return render_template('classroom.html',trained=is_trained, classroom=classroom_name)
        
    else:
        return render_template('login.html')




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/train')
def train():
    if 'username' in session:
        username = session['username']
        classroom_name = request.args.get('classroom')

        cur = mysql.connection.cursor()
        cur.execute("SELECT model FROM classroom WHERE username = %s and classroom = %s", (username,classroom_name))
        result = cur.fetchone()
        cur.close()
        if result and result[0] is not None:
            return redirect('/classroom?'+classroom_name)

        trainmodel(username,classroom_name)
        
    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
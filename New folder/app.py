from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import os
import fitz  # PyMuPDF
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import numpy as np
import pickle
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences




app = Flask(__name__)
app.secret_key = 'your_secret_key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fake_job_db'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'user1'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'fake_job_db'

mysql = MySQL(app)

# Load ML model
model = pickle.load(open('model1.pkl', 'rb'))
max_len = 40
voc_size = 5000

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/server')
def home_():
    return render_template('error.html')

# Home route
@app.route('/register')
def refister_page():
    return render_template('register.html')


# Dashboard route
@app.route('/dashboard')
def dashboard_page():
    labels, counts = stats()
    return render_template('home.html', labels=labels, counts=counts)
 


@app.route('/home')
def home_page():
    labels, counts = stats()
    return render_template('home.html', labels=labels, counts=counts)


# Dashboard route
@app.route('/predict')
def predictPage():
    return render_template('predict.html')


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        password = generate_password_hash(request.form['password'])
        cursor = mysql.connection.cursor()
        
      
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Username already exists. Try another one.", "danger")
            return redirect('register')
        
        
        cursor.execute("INSERT INTO users (username, fullname, password_hash) VALUES (%s, %s, %s)",
                       (username, fullname, password))
        mysql.connection.commit()
        cursor.close()
        flash("Registered successfully!", "success")
        return redirect('/')
    return render_template('register.html')


@app.route('/stats')
def stats():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT result, COUNT(*) as count
        FROM job_ads
    """)
    data = cursor.fetchall()
    cursor.close()

    labels = [row[0].capitalize() for row in data]
    counts = [row[1] for row in data]
    return labels, counts

# Login route
from MySQLdb.cursors import DictCursor

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use DictCursor to access fields by name
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            # flash("Login successful!", "success")
            labels, counts = stats()
            # return redirect('/dashboard')
            return render_template('home.html', username=session['username'], labels=labels, counts=counts)
        
        else:
            flash("Invalid username or password", "danger")

    return render_template('index.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

# PDF Upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    
    if 'user_id' not in session:
        return redirect('/login')

    pred = None
    reason = None

    if request.method == 'POST':
        file = request.files.get('pdf')

        if not file or not file.filename.endswith('.pdf'):
            flash("Only PDF files are allowed.", "danger")
            return redirect('/predict')

        # Save the file
        path = os.path.join('static/uploads', file.filename)
        file.save(path)

        # # Extract text and predict
        # text = extract_text_from_pdf(path)
        # pred, reason = predict_job(text)

        text = extract_text_from_pdf(path)
        description, qualifications = split_description_qualifications(text)
        # pred, reason = predict_job(description, qualifications)
        binary_pred, label, reason = predict_job(description, qualifications)

        # Store in DB
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO job_ads (user_id, filename, description, result, reason) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], file.filename, text, label, reason))
        
        cursor.execute("INSERT INTO job_ad (user_id, filename, description, result, reason) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], file.filename, text, label, reason))
       
        mysql.connection.commit()
        cursor.close()
        
        if label == 'fake':
            flash(f"⚠️ Job Classified as: {label.upper()} - Reason: {reason}", "danger")
        else:
            flash(f"✅ Job Classified as: {label.upper()} - Reason: {reason}", "success")

        return redirect('/predict')

    return render_template('predict.html', label=pred, reason=reason)



# User History
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    username = session.get('username', 'User')
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, filename, result, reason 
        FROM job_ads 
        WHERE user_id = %s
        ORDER BY id DESC
    """, (user_id,))
    records = cursor.fetchall()
    cursor.close()

    return render_template('history.html', records=records, username=username)


@app.route('/delete/<filename>')
def delete_file(filename):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Remove file from database
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM job_ads WHERE user_id = %s AND filename = %s", 
                   (session['user_id'], filename))
    mysql.connection.commit()
    cursor.close()

    # Remove file from disk
    path = os.path.join('static/uploads', filename)
    if os.path.exists(path):
        os.remove(path)

    # flash("File deleted successfully!", "success")
    return redirect('/history')



# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# PDF Text Extraction

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 1️⃣ Your split function here
def split_description_qualifications(text):
    parts = text.split('Qualifications:')
    description = parts[0].replace('Description:', '').strip()
    qualifications = parts[1].strip() if len(parts) > 1 else ''
    return description, qualifications



def preprocess(text):
    ps = PorterStemmer()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower().split()
    stop_words = set(stopwords.words('english'))
    text = [ps.stem(word) for word in text if word not in stop_words]
    return ' '.join(text)

# Prediction function
def predict_job(description, qualifications):
    combined_text = (description or "") + " " + (qualifications or "")
    
    if not combined_text.strip():
        return None, "Invalid", "No input provided."

    corpus = preprocess(combined_text)
    if not corpus.strip():
        return None, "Invalid", "Text is empty after preprocessing."

    onehot_repr = [one_hot(corpus, voc_size)]
    padded = pad_sequences(onehot_repr, maxlen=max_len, padding='post')

    pred = model.predict(padded)
    binary_pred = int(np.round(pred[0][0]))
    label = 'fake' if binary_pred == 1 else 'legit'
    reason = "Missing contact info or unrealistic content" if binary_pred == 1 else "Passed normality checks"

    return binary_pred, label, reason
    print(predict_job(description, qualifications))


if __name__ == '__main__':
    app.run(debug=True)

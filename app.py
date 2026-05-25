import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import MySQLdb.cursors
import joblib
import pandas as pd

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import os
import pdfplumber  # Using pdfplumber for PDF extraction
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from tensorflow.keras.preprocessing.text import one_hot
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

model = joblib.load(os.path.join(os.path.dirname(__file__), 'text_classification_model.pkl'))

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

# Register page
@app.route('/register')
def register_page():
    return render_template('register.html')

# Dashboard route
@app.route('/dashboard')
def dashboard_page():
    if 'user_id' not in session:
        return redirect('/login')
    stats_data = stats()
    return render_template('home.html', username=session['username'], **stats_data)

@app.route('/home')
def home_page():
    if 'user_id' not in session:
        return redirect('/login')
    stats_data = stats()
    return render_template('home.html', username=session['username'], **stats_data)

# Predict page
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

# Stats function
def stats():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
        SELECT result, COUNT(*) as count
        FROM job_ads
        WHERE result IN ('fake', 'legit', 'Invalid')
        GROUP BY result
    """)
    data = cursor.fetchall()
    cursor.close()
    
    # Initialize counts
    stats_data = {'fake_count': 0, 'legit_count': 0, 'invalid_count': 0, 'total_jobs': 0}
    labels = []
    counts = []
    
    # Process query results
    for row in data:
        result = row['result'].lower()
        count = row['count']
        if result == 'fake':
            stats_data['fake_count'] = count
        elif result == 'legit':
            stats_data['legit_count'] = count
        elif result == 'Invalid':
            stats_data['invalid_count'] = count
        labels.append(result.capitalize())
        counts.append(count)
    
    # Calculate total jobs
    stats_data['total_jobs'] = stats_data['fake_count'] + stats_data['legit_count'] + stats_data['invalid_count']
    
    # Ensure all categories are represented in the chart
    for result in ['Fake', 'Legit', 'Invalid']:
        if result not in labels:
            labels.append(result)
            counts.append(0)
    
    stats_data['labels'] = labels
    stats_data['counts'] = counts
    return stats_data

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            stats_data = stats()
            return render_template('home.html', username=session['username'], **stats_data)
        else:
            flash("Invalid username or password", "danger")
    return render_template('index.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    stats_data = stats()
    return render_template('dashboard.html', username=session['username'], **stats_data)

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
        path = os.path.join('static/uploads', file.filename)
        file.save(path)
        text = extract_text_from_pdf(path)
        description, qualifications = split_description_qualifications(text)
        binary_pred, label, reason = predict_job(description, qualifications)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO job_ads (user_id, filename, description, result, reason) VALUES (%s, %s, %s, %s, %s)",
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

# Delete file
@app.route('/delete/<filename>')
def delete_file(filename):
    if 'user_id' not in session:
        return redirect('/login')
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM job_ads WHERE user_id = %s AND filename = %s",
                   (session['user_id'], filename))
    mysql.connection.commit()
    cursor.close()
    path = os.path.join('static/uploads', filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect('/history')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# PDF Text Extraction
def extract_text_from_pdf(path):
    try:
        with pdfplumber.open(path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        flash(f"Error reading PDF: {str(e)}", "danger")
        return ""

# Split description and qualifications
def split_description_qualifications(text):
    parts = text.split('Qualifications:')
    description = parts[0].replace('Description:', '').strip()
    qualifications = parts[1].strip() if len(parts) > 1 else ''
    return description, qualifications

# Preprocess text
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

if __name__ == '__main__':
    app.run(debug=False)
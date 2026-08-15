from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import MySQLdb.cursors
import joblib
import nltk
import os
import pdfplumber
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# ✅ MySQL Configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'fraud_detection')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))

# Upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Initialize extensions
mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Load your model
model = joblib.load('text_classification_model.pkl')



# ✅ User class for Flask-Login
class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username
        
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        pdf_text = ""
        # If a PDF file was uploaded, extract its text and prefill the description
        file = request.files.get('pdf_file')
        if file and file.filename and allowed_file(file.filename):
            try:
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                if not pdf_text.strip():
                    flash('Could not extract any text from the PDF. Please fill the form manually.')
                    return render_template('predict.html')
            except Exception as e:
                flash(f'Error reading PDF: {str(e)}. Please fill the form manually.')
                return render_template('predict.html')

        # Get form data (safe getters so unchecked boxes / missing fields don't crash)
        job_post = {
            "location": request.form.get('location', ''),
            "salary_range": request.form.get('salary_range', ''),
            "company_profile": request.form.get('company_profile', ''),
            "description": request.form.get('description', '') or pdf_text[:5000],
            "requirements": request.form.get('requirements', ''),
            "benefits": request.form.get('benefits', ''),
            "telecommuting": int(request.form.get('telecommuting', 0) or 0),
            "has_company_logo": int(request.form.get('has_company_logo', 0) or 0),
            "has_questions": int(request.form.get('has_questions', 0) or 0),
            "employment_type": request.form.get('employment_type', 'Full-time'),
            "required_experience": request.form.get('required_experience', 'Entry level'),
            "required_education": request.form.get('required_education', "Bachelor's"),
            "Industry": request.form.get('Industry', ''),
            "Function": request.form.get('Function', '')
        }

        # The model expects a DataFrame with the same columns it was trained on
        import pandas as pd
        input_data = pd.DataFrame([job_post])

        # Predict
        prediction = model.predict(input_data)[0]

        result = 'FAKE' if prediction == 0 else 'REAL'

        return render_template('predict.html', prediction=result, job_post=job_post, pdf_text=pdf_text[:1000])

    return render_template('predict.html')



@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user['id'], user['username'])
    return None

# ✅ Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/predict_form')
def predict_form():
    return render_template('predict.html')

@app.route('/upload_pdf', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        return redirect(url_for('predict'))
    return render_template('predict.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']  # ✅ New field
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Username already exists. Try another one.')
            return redirect(url_for('register'))

        cur.execute(
            "INSERT INTO users (full_name, username, password) VALUES (%s, %s, %s)",
            (full_name, username, password)
        )
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please log in.')
        return redirect(url_for('index'))  # ✅ more consistent than "/"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user['password'], password_input):
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))  # 🔥 this line is important!

    return render_template('index.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os
import json
import traceback
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
import joblib
import pandas as pd
import pickle
import pdfplumber
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import one_hot

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

PROJECT_ID = "fake-job-detection-343c3"

FIREBASE_INITIALIZED = False
db = None
try:
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    elif os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'):
        cred_dict = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT_KEY'])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
    db = firestore.client()
    FIREBASE_INITIALIZED = True
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase init error: {e}")

model = joblib.load(os.path.join(os.path.dirname(__file__), 'text_classification_model.pkl'))
model = pickle.load(open('model1.pkl', 'rb'))
max_len = 40
voc_size = 5000

def verify_firebase_token(id_token):
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded, None
    except Exception as e:
        return None, str(e)

PERMISSION_NAMES = {
    'view_users': 'View Users',
    'create_users': 'Create Users',
    'edit_users': 'Edit Users',
    'delete_users': 'Delete Users',
    'manage_roles': 'Manage Roles',
    'view_jobs': 'View Job Posts',
    'create_jobs': 'Create Job Posts',
    'edit_jobs': 'Edit Job Posts',
    'delete_jobs': 'Delete Job Posts',
    'approve_jobs': 'Approve Job Posts',
    'view_applications': 'View Applications',
    'manage_applications': 'Manage Applications',
    'export_data': 'Export Data',
    'view_analytics': 'View Analytics',
    'manage_organizations': 'Manage Organizations',
    'manage_settings': 'Manage Settings',
    'manage_integrations': 'Manage Integrations',
    'view_audit_logs': 'View Audit Logs',
    'manage_security': 'Manage Security',
    'super_admin': 'Super Admin Access',
}

ALL_PERMISSIONS = list(PERMISSION_NAMES.keys())

def get_user_permissions(user_id):
    if not db:
        return []
    doc = db.collection('users').document(user_id).get()
    if not doc.exists:
        return []
    d = doc.to_dict()
    if d.get('super_admin'):
        return ALL_PERMISSIONS[:]
    return d.get('permissions', [])

def has_permission(user_id, permission):
    return permission in get_user_permissions(user_id)

def permission_required(permission):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect('/login')
            if not has_permission(session['user_id'], permission):
                flash("Access denied. You do not have the required permission.", "danger")
                return redirect('/home')
            return f(*args, **kwargs)
        return decorated
    return decorator

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_admin():
    uid = session.get('user_id')
    perms = get_user_permissions(uid) if uid else []
    return {
        'is_admin': 'super_admin' in perms or len(perms) > 0,
        'user_permissions': perms,
        'permission_names': PERMISSION_NAMES,
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/server')
def home_():
    return render_template('error.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/reset-password')
def reset_password_page():
    return render_template('reset-password.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    stats_data = stats(user_id=session['user_id'])
    return render_template('home.html', username=session.get('username', 'User'), **stats_data)

@app.route('/home')
@login_required
def home_page():
    stats_data = stats(user_id=session['user_id'])
    return render_template('home.html', username=session.get('username', 'User'), **stats_data)

@app.route('/predict')
@login_required
def predictPage():
    result = request.args.get('result')
    reason = request.args.get('reason')
    return render_template('predict.html', result=result, reason=reason)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not FIREBASE_INITIALIZED:
            flash("Firebase not configured.", "danger")
            return redirect('register')
        id_token = request.form.get('idToken', '')
        fullname = request.form.get('fullname', '')
        username = request.form.get('username', '')
        decoded, error = verify_firebase_token(id_token)
        if error:
            flash("Registration failed: " + error, "danger")
            return redirect('register')
        uid = decoded['sub']
        email = decoded.get('email', '')
        user_ref = db.collection('users').document(uid)
        if user_ref.get().exists:
            flash("User already registered.", "danger")
            return redirect('register')
        is_first = len(list(db.collection('users').limit(2).stream())) <= 1
        user_data = {
            'uid': uid,
            'email': email,
            'fullname': fullname,
            'username': username,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        if is_first:
            user_data['super_admin'] = True
            user_data['permissions'] = ALL_PERMISSIONS[:]
        user_ref.set(user_data)
        session['user_id'] = uid
        session['username'] = username
        role = "super admin" if is_first else "user"
        flash(f"Registered successfully as {role}!", "success")
        return redirect('/home')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not FIREBASE_INITIALIZED:
            flash("Firebase not configured.", "danger")
            return render_template('index.html')
        id_token = request.form.get('idToken', '')
        decoded, error = verify_firebase_token(id_token)
        if error:
            flash("Login failed: " + error, "danger")
            return render_template('index.html')
        uid = decoded['sub']
        email = decoded.get('email', '')
        user_doc = db.collection('users').document(uid).get()
        username = user_doc.get('username') if user_doc.exists else email.split('@')[0]
        if not user_doc.exists:
            db.collection('users').document(uid).set({
                'uid': uid, 'email': email, 'username': username,
                'created_at': firestore.SERVER_TIMESTAMP
            })
        session['user_id'] = uid
        session['username'] = username
        return redirect('/home')
    return render_template('index.html')

@app.route('/lookup-email', methods=['POST'])
def lookup_email():
    username = request.form.get('username', '')
    if not username:
        return {'email': None}, 400
    users = db.collection('users').where('username', '==', username).limit(1).stream()
    for user in users:
        return {'email': user.get('email')}
    return {'email': None}, 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

def stats(user_id=None):
    if not FIREBASE_INITIALIZED:
        return {'fake_count': 0, 'legit_count': 0, 'invalid_count': 0, 'total_jobs': 0, 'labels': ['Fake', 'Legit', 'Invalid'], 'counts': [0, 0, 0]}
    fake = legit = invalid = 0
    collections = ['job_ads', 'url_checks']
    for col in collections:
        docs = db.collection(col)
        if user_id:
            docs = docs.where('user_id', '==', user_id)
        for doc in docs.stream():
            r = doc.to_dict().get('result', '')
            if r == 'fake': fake += 1
            elif r == 'legit': legit += 1
            else: invalid += 1
    total = fake + legit + invalid
    return {
        'fake_count': fake, 'legit_count': legit, 'invalid_count': invalid, 'total_jobs': total,
        'labels': ['Fake', 'Legit', 'Invalid'],
        'counts': [fake, legit, invalid]
    }

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not FIREBASE_INITIALIZED:
        flash("Firebase not configured.", "danger")
        return redirect('/predict')
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
        db.collection('job_ads').add({
            'user_id': session['user_id'],
            'filename': file.filename,
            'description': text,
            'result': label,
            'reason': reason,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return redirect(url_for('predictPage', result=label, reason=reason))
    result = request.args.get('result')
    reason = request.args.get('reason')
    return render_template('predict.html', result=result, reason=reason)

@app.route('/history')
@login_required
def history():
    try:
        if not FIREBASE_INITIALIZED:
            return render_template('history.html', records=[], username=session.get('username', 'User'))
        user_id = session['user_id']
        try:
            all_docs = len(list(db.collection('job_ads').limit(100).stream()))
            print(f"HISTORY: total job_ads docs={all_docs}")
        except Exception as e:
            print(f"HISTORY: error counting all docs: {e}")
        print(f"HISTORY: user_id={user_id}")
        job_docs = list(db.collection('job_ads').where('user_id', '==', user_id).stream())
        print(f"HISTORY: found {len(job_docs)} job_ads docs for user")
        records = []
        for doc in job_docs:
            d = doc.to_dict()
            records.append({'id': doc.id, 'filename': d.get('filename', ''), 'result': d.get('result', ''), 'reason': d.get('reason', ''), 'created_at': str(d.get('created_at', '')), 'type': 'pdf'})
        url_docs = list(db.collection('url_checks').where('user_id', '==', user_id).stream())
        print(f"HISTORY: found {len(url_docs)} url_checks docs for user")
        for doc in url_docs:
            d = doc.to_dict()
            records.append({'id': doc.id, 'filename': d.get('url', ''), 'result': d.get('result', 'Invalid'), 'reason': d.get('reason', ''), 'created_at': str(d.get('created_at', '')), 'type': 'url', 'risk_level': d.get('risk_level', '')})
        records.sort(key=lambda r: r['created_at'], reverse=True)
        return render_template('history.html', records=records, username=session.get('username', 'User'))
    except Exception as e:
        tb = traceback.format_exc()
        print(f"HISTORY ERROR: {e}\n{tb}")
        return render_template('history.html', records=[], username=session.get('username', 'User'), error=str(e))

@app.route('/delete/<doc_type>/<doc_id>')
@login_required
def delete_file(doc_type, doc_id):
    user_id = session['user_id']
    if doc_type == 'pdf':
        doc_ref = db.collection('job_ads').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get('user_id') == user_id:
            filename = doc.to_dict().get('filename', '')
            doc_ref.delete()
            path = os.path.join('static/uploads', filename)
            if os.path.exists(path):
                os.remove(path)
    elif doc_type == 'url':
        doc_ref = db.collection('url_checks').document(doc_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get('user_id') == user_id:
            doc_ref.delete()
    return redirect('/history')

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

TRUSTED_DOMAINS = {
    'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com', 'careerbuilder.com',
    'simplyhired.com', 'ziprecruiter.com', 'dice.com', 'upwork.com', 'freelancer.com',
    'fiverr.com', 'gov', 'go.ke', 'ac.tz', 'or.tz', 'ac.ke', 'or.ke', 'go.tz',
}

SUSPICIOUS_DOMAINS = {
    'bit.ly', 'tinyurl.com', 'tiny.cc', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly',
    'shorturl.at', 'short.link', 'cutt.ly', 'rb.gy', 'bl.ink',
}

SUSPICIOUS_KEYWORDS = ['earn-money-online', 'work-from-home-fast', 'click-here-to-apply-now',
                       'free-money', 'instant-hiring', 'no-experience-required']

def validate_job_url(url):
    from urllib.parse import urlparse
    result = {'trusted': False, 'risk_level': 'high', 'reason': '', 'label': 'fake'}

    if not url or not url.startswith(('http://', 'https://')):
        result['reason'] = 'URL must start with http:// or https://'
        result['label'] = 'Invalid'
        return result

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]

    if parsed.scheme != 'https':
        result['risk_level'] = 'high'
        result['trusted'] = False
        result['reason'] = 'URL does not use HTTPS'
        result['label'] = 'fake'
        return result

    if len(parsed.netloc.split('.')) > 4:
        result['risk_level'] = 'high'
        result['trusted'] = False
        result['reason'] = 'Excessive subdomains — potential phishing'
        result['label'] = 'fake'
        return result

    if any(kw in url.lower() for kw in SUSPICIOUS_KEYWORDS):
        result['risk_level'] = 'high'
        result['trusted'] = False
        result['reason'] = 'URL contains suspicious keywords'
        result['label'] = 'fake'
        return result

    for sd in SUSPICIOUS_DOMAINS:
        if sd in domain:
            result['risk_level'] = 'high'
            result['trusted'] = False
            result['reason'] = f'URL uses known suspicious shortener ({sd})'
            result['label'] = 'fake'
            return result

    base_domain = '.'.join(domain.split('.')[-2:]) if domain.count('.') >= 1 else domain

    import re
    if re.search(r'[0-9]{5,}', domain):
        result['risk_level'] = 'high'
        result['trusted'] = False
        result['reason'] = 'Domain contains long numeric sequence — likely suspicious'
        result['label'] = 'fake'
        return result

    if re.search(r'(xn\-\-|[^a-z0-9\.\-])', domain):
        result['risk_level'] = 'high'
        result['trusted'] = False
        result['reason'] = 'Domain contains punycode or special characters'
        result['label'] = 'fake'
        return result

    for td in TRUSTED_DOMAINS:
        if base_domain == td or domain.endswith('.' + td):
            result['trusted'] = True
            result['risk_level'] = 'low'
            result['reason'] = f'Verified trusted domain ({base_domain})'
            result['label'] = 'legit'
            return result

    result['risk_level'] = 'medium'
    result['trusted'] = False
    result['reason'] = f'Domain "{base_domain}" is not in the trusted list. Verify manually.'
    result['label'] = 'Invalid'
    return result


@app.route('/validate-url', methods=['POST'])
@login_required
def validate_url_route():
    url = request.form.get('url', '')
    vresult = validate_job_url(url)
    db.collection('url_checks').add({
        'user_id': session['user_id'],
        'url': url,
        'result': vresult['label'],
        'risk_level': vresult['risk_level'],
        'reason': vresult['reason'],
        'created_at': firestore.SERVER_TIMESTAMP
    })
    return vresult


@app.route('/admin')
@login_required
@permission_required('view_analytics')
def admin_dashboard():
    total_users = 0
    all_records = []
    fake = legit = invalid = 0
    user_stats = {}
    if db:
        users = list(db.collection('users').stream())
        total_users = len(users)
        user_map = {}
        for u in users:
            d = u.to_dict()
            user_map[u.id] = d.get('username', d.get('email', u.id))

        for doc in db.collection('job_ads').stream():
            d = doc.to_dict()
            r = d.get('result', '')
            if r == 'fake': fake += 1
            elif r == 'legit': legit += 1
            else: invalid += 1
            uid = d.get('user_id', '')
            uname = user_map.get(uid, uid)
            all_records.append({'id': doc.id, 'type': 'pdf', 'filename': d.get('filename', ''), 'result': r, 'reason': d.get('reason', ''), 'created_at': str(d.get('created_at', '')), 'user': uname})
            user_stats[uname] = user_stats.get(uname, {'pdf': 0, 'url': 0, 'fake': 0, 'legit': 0, 'invalid': 0})
            user_stats[uname]['pdf'] += 1
            if r == 'fake': user_stats[uname]['fake'] += 1
            elif r == 'legit': user_stats[uname]['legit'] += 1
            else: user_stats[uname]['invalid'] += 1

        for doc in db.collection('url_checks').stream():
            d = doc.to_dict()
            r = d.get('result', '')
            if r == 'fake': fake += 1
            elif r == 'legit': legit += 1
            else: invalid += 1
            uid = d.get('user_id', '')
            uname = user_map.get(uid, uid)
            all_records.append({'id': doc.id, 'type': 'url', 'filename': d.get('url', ''), 'result': r, 'reason': d.get('reason', ''), 'created_at': str(d.get('created_at', '')), 'user': uname, 'risk_level': d.get('risk_level', '')})
            user_stats[uname] = user_stats.get(uname, {'pdf': 0, 'url': 0, 'fake': 0, 'legit': 0, 'invalid': 0})
            user_stats[uname]['url'] += 1
            if r == 'fake': user_stats[uname]['fake'] += 1
            elif r == 'legit': user_stats[uname]['legit'] += 1
            else: user_stats[uname]['invalid'] += 1

        all_records.sort(key=lambda r: r['created_at'], reverse=True)

    return render_template('admin.html',
        username=session.get('username', 'Admin'),
        total_users=total_users,
        total_records=len(all_records),
        fake_count=fake, legit_count=legit, invalid_count=invalid,
        total=fake+legit+invalid,
        records=all_records,
        user_stats=user_stats
    )


@app.route('/admin/delete/<doc_type>/<doc_id>')
@login_required
@permission_required('delete_jobs')
def admin_delete(doc_type, doc_id):
    if doc_type == 'pdf':
        doc_ref = db.collection('job_ads').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            filename = doc.to_dict().get('filename', '')
            doc_ref.delete()
            path = os.path.join('static/uploads', filename)
            if os.path.exists(path):
                os.remove(path)
    elif doc_type == 'url':
        doc_ref = db.collection('url_checks').document(doc_id)
        if doc_ref.get().exists:
            doc_ref.delete()
    flash("Record deleted.", "success")
    return redirect('/admin')


@app.route('/admin/make-admin', methods=['POST'])
@login_required
@permission_required('manage_roles')
def make_admin():
    target_uid = request.form.get('uid', '')
    if target_uid and db:
        user_ref = db.collection('users').document(target_uid)
        if user_ref.get().exists:
            user_ref.update({'super_admin': True, 'permissions': ALL_PERMISSIONS[:]})
            flash(f"User {target_uid} is now a super admin.", "success")
    return redirect('/admin')


@app.route('/admin/permissions', methods=['GET', 'POST'])
@login_required
@permission_required('manage_roles')
def admin_permissions():
    all_users = list(db.collection('users').stream()) if db else []
    users_data = []
    for u in all_users:
        d = u.to_dict()
        users_data.append({
            'uid': u.id,
            'username': d.get('username', d.get('email', u.id)),
            'email': d.get('email', ''),
            'permissions': d.get('permissions', []),
            'super_admin': d.get('super_admin', False),
        })

    if request.method == 'POST':
        target_uid = request.form.get('uid')
        if target_uid:
            selected = request.form.getlist('perms')
            if request.form.get('super_admin'):
                db.collection('users').document(target_uid).update({
                    'super_admin': True,
                    'permissions': ALL_PERMISSIONS[:]
                })
            else:
                db.collection('users').document(target_uid).update({
                    'super_admin': False,
                    'permissions': selected
                })
            flash("Permissions updated.", "success")
        return redirect('/admin/permissions')

    return render_template('admin_permissions.html',
        users=users_data,
        permission_names=PERMISSION_NAMES,
        all_permissions=ALL_PERMISSIONS,
        username=session.get('username', 'Admin'),
    )


@app.route('/admin/users')
@login_required
@permission_required('view_users')
def admin_users():
    all_users = list(db.collection('users').stream()) if db else []
    users_data = []
    for u in all_users:
        d = u.to_dict()
        users_data.append({
            'uid': u.id,
            'username': d.get('username', ''),
            'email': d.get('email', ''),
            'fullname': d.get('fullname', ''),
            'super_admin': d.get('super_admin', False),
            'permissions': d.get('permissions', []),
            'created_at': str(d.get('created_at', '')),
        })
    return render_template('admin_users.html',
        users=users_data,
        permission_names=PERMISSION_NAMES,
        username=session.get('username', 'Admin'),
    )


@app.route('/admin/delete-user/<uid>')
@login_required
@permission_required('delete_users')
def admin_delete_user(uid):
    if uid == session['user_id']:
        flash("You cannot delete your own account.", "danger")
        return redirect('/admin/users')
    if db:
        for doc in db.collection('job_ads').where('user_id', '==', uid).stream():
            doc.reference.delete()
        for doc in db.collection('url_checks').where('user_id', '==', uid).stream():
            doc.reference.delete()
        db.collection('users').document(uid).delete()
        flash("User and all associated records deleted.", "success")
    return redirect('/admin/users')


@app.route('/admin/jobs')
@login_required
@permission_required('view_jobs')
def admin_jobs():
    all_records = []
    if db:
        users = {u.id: u.to_dict().get('username', u.to_dict().get('email', u.id))
                 for u in db.collection('users').stream()}
        for doc in db.collection('job_ads').stream():
            d = doc.to_dict()
            all_records.append({'id': doc.id, 'type': 'pdf', 'filename': d.get('filename', ''),
                'result': d.get('result', ''), 'reason': d.get('reason', ''),
                'user': users.get(d.get('user_id', ''), d.get('user_id', '')),
                'created_at': str(d.get('created_at', ''))})
        for doc in db.collection('url_checks').stream():
            d = doc.to_dict()
            all_records.append({'id': doc.id, 'type': 'url', 'filename': d.get('url', ''),
                'result': d.get('result', ''), 'reason': d.get('reason', ''),
                'user': users.get(d.get('user_id', ''), d.get('user_id', '')),
                'created_at': str(d.get('created_at', '')), 'risk_level': d.get('risk_level', '')})
        all_records.sort(key=lambda r: r['created_at'], reverse=True)
    return render_template('admin_jobs.html', records=all_records, username=session.get('username', 'Admin'))


@app.route('/admin/export')
@login_required
@permission_required('export_data')
def admin_export():
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'User', 'Filename/URL', 'Result', 'Reason', 'Date'])
    if db:
        users = {u.id: u.to_dict().get('username', u.to_dict().get('email', u.id))
                 for u in db.collection('users').stream()}
        for doc in db.collection('job_ads').stream():
            d = doc.to_dict()
            writer.writerow(['PDF', users.get(d.get('user_id', ''), ''), d.get('filename', ''),
                d.get('result', ''), d.get('reason', ''), str(d.get('created_at', ''))])
        for doc in db.collection('url_checks').stream():
            d = doc.to_dict()
            writer.writerow(['URL', users.get(d.get('user_id', ''), ''), d.get('url', ''),
                d.get('result', ''), d.get('reason', ''), str(d.get('created_at', ''))])
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=job_fraud_export.csv'}
    )


if __name__ == '__main__':
    app.run(debug=False)

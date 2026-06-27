# Job Advertisement Fraud Detection System

## System Documentation

---

## 1. Objective

The primary objective of this system is to **automatically detect fraudulent job advertisements** by analyzing both PDF job postings and job application URLs. The system uses **Machine Learning (NLP)** and **URL reputation analysis** to classify listings as **Fake**, **Legit**, or **Invalid**, helping job seekers and organizations avoid recruitment scams.

### Key Goals
- Reduce exposure to job advertisement fraud and phishing
- Provide real-time, automated validation of job postings
- Centralize per-user validation history with detailed analytics
- Enable administrators to manage users, permissions, and domain rules

---

## 2. Scope

### In Scope
- PDF job advertisement upload and ML-based text classification
- Job application URL validation with multi-layered checks (HTTPS, domain reputation, suspicious patterns)
- Per-user dashboard with aggregated statistics (Fake/Legit/Invalid counts, weekly trend chart)
- Upload and URL check history with search, sort, and delete
- User registration and login via email or username (Firebase Authentication)
- User profile management (edit username, generate API key, download personal data)
- Dark mode toggle with persistent preference (localStorage)
- Bulk URL validation (paste multiple URLs at once)
- Feedback system — users can mark predictions as correct or incorrect
- Admin panel with role-based permissions (20 distinct permissions)
- User management (list, delete users and their records)
- Permission management (assign/revoke permissions, super admin toggle)
- Domain whitelist/blacklist management (admin-configurable domain rules)
- Audit logging (track deletes, profile changes, admin actions)
- API endpoint for URL validation
- Data export (full CSV export for admins, personal CSV for users)
- Responsive design (mobile, tablet, desktop)
- Charts and visualizations (Chart.js bar chart + line chart)

### Out of Scope
- Mobile native application (Flutter/React Native)
- Integration with external threat intelligence APIs (Google Safe Browsing, VirusTotal)
- Multi-language support for non-English job ads
- Real-time email/SMS notifications
- Automated PDF parsing for structured data extraction (salary, location, etc.)

---

## 3. How It Works — System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Browser                                 │
│  (HTML5, CSS3, JavaScript, Chart.js, DataTables, Firebase Auth) │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ├── Firebase Auth (Client SDK)
                   │      │
                   │      ├── Register / Login (email or username)
                   │      ├── Password Reset
                   │      └── ID Token sent to Flask server
                   │
                   └── Flask Web Application (Server-side Python)
                            │
                            ├── /upload ──► PDF ──► pdfplumber ──► NLP ──► TF Model ──► Firestore
                            │
                            ├── /validate-url ──► URL ──► 6 validation layers ──► Firestore
                            │
                            ├── /bulk-validate ──► Multiple URLs ──► batch validation
                            │
                            ├── /api/validate-url ──► API key auth ──► same validation
                            │
                            ├── /home ──► Dashboard ──► stats + charts from Firestore
                            │
                            ├── /history ──► Per-user records with feedback buttons
                            │
                            ├── /profile ──► Edit username, API key, download data
                            │
                            ├── /feedback ──► Mark predictions correct/incorrect
                            │
                            ├── /admin/* ──► Admin panel (permissions, users, domains, logs)
                            │
                            └── Firebase Admin SDK (server-side)
                                     │
                                     ├── Firestore ──► users, job_ads, url_checks,
                                     │                   audit_logs, domain_rules, feedback
                                     │
                                     └── Firebase Auth ──► verify ID tokens
```

### 3.1 Authentication Flow

1. User enters email/password (or username + password) on login page
2. If username is provided, client calls `/lookup-email` to resolve it to an email
3. Client Firebase Auth SDK signs in with email + password, receives an **ID Token**
4. ID Token is sent to Flask server via POST form
5. Flask verifies the token using `firebase_admin.auth.verify_id_token()`
6. Session is created with `user_id` and `username`
7. First registered user is automatically granted **Super Admin** with all permissions

### 3.2 PDF Classification Flow

1. User uploads a PDF file via `/upload`
2. Flask saves the file and extracts text using **pdfplumber**
3. Text is preprocessed:
   - Non-alphabetic characters removed
   - Lowercased and tokenized
   - English stopwords removed
   - Porter Stemming applied
4. Preprocessed text is one-hot encoded (vocab size: 5000) and padded (max length: 40)
5. **TensorFlow/Keras neural network** predicts: **0 = Legit**, **1 = Fake**
6. Result (Fake/Legit/Invalid) + reason is stored in Firestore `job_ads` collection
7. User is redirected to the predict page with the result displayed

### 3.3 URL Validation Flow

1. User submits a URL (single via `/validate-url` or bulk via `/bulk-validate`)
2. Flask performs **6 validation layers** in order:

   | Layer | Check | Outcome |
   |-------|-------|---------|
   | 1 | Starts with http:// or https:// | Invalid if not |
   | 2 | Uses HTTPS | Fake if not |
   | 3 | Excessive subdomains (>4) | Fake (phishing pattern) |
   | 4 | Suspicious keywords in URL | Fake |
   | 5 | Known URL shorteners (bit.ly, tinyurl, etc.) | Fake |
   | 6 | Long numeric sequences in domain | Fake |
   | 7 | Punycode / special characters | Fake |
   | 8 | Trusted domain match (linkedin, .gov, etc.) | Legit |
   | 9 | Admin domain rules (whitelist/blacklist) | Legit or Fake |
   | 10 | Unknown domain (no match) | Invalid |

3. Result (label, risk_level, reason, trusted boolean) is returned as JSON
4. Every check is stored in Firestore `url_checks` collection

### 3.4 Dashboard

- Aggregates counts from both `job_ads` and `url_checks` collections per user
- Displays **Fake**, **Legit**, **Invalid** counts in statistics cards
- Bar chart showing distribution across the three categories
- Line chart showing **weekly trend** of Fake vs Legit over time
- Admin dashboard shows system-wide stats and per-user breakdown

### 3.5 Admin Panel

Access controlled via a **20-permission role system**:

| Permission | Description |
|-----------|-------------|
| `view_users` | View user list |
| `create_users` | Create new users |
| `edit_users` | Edit user details |
| `delete_users` | Delete users |
| `manage_roles` | Assign/revoke permissions |
| `view_jobs` | View all records |
| `create_jobs` | Create job records |
| `edit_jobs` | Edit job records |
| `delete_jobs` | Delete any record |
| `approve_jobs` | Approve job posts |
| `view_applications` | View applications |
| `manage_applications` | Manage applications |
| `export_data` | Export CSV |
| `view_analytics` | View admin dashboard |
| `manage_organizations` | Manage organizations |
| `manage_settings` | Manage domain rules |
| `manage_integrations` | Manage integrations |
| `view_audit_logs` | View audit logs |
| `manage_security` | Manage security settings |
| `super_admin` | Super admin (all permissions) |

### 3.6 Audit Logging

All significant actions are logged to Firestore `audit_logs`:
- User deletions (self and admin)
- Profile changes (username updates)
- Admin record deletions
- Domain rule additions/deletions
- API key generation
- Bulk URL validations
- Feedback submissions

---

## 4. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python Flask 3.x | Web framework, routing, session management |
| **ML Framework** | TensorFlow 2.x / Keras | Neural network for text classification |
| **NLP** | NLTK | Stopwords, Porter Stemmer, tokenization |
| **PDF Extraction** | pdfplumber | Extract text from PDF files |
| **Authentication** | Firebase Admin SDK (server) + Firebase Auth (client) | User registration, login, token verification |
| **Database** | Google Cloud Firestore | NoSQL document store for all records |
| **Frontend** | HTML5, CSS3, Bootstrap 4, jQuery | Responsive UI |
| **Charts** | Chart.js | Dashboard bar and line charts |
| **Tables** | DataTables (jQuery plugin) | Sortable, searchable, paginated tables |
| **File Upload** | Dropify (jQuery plugin) | Styled file input for PDF uploads |
| **WSGI Server** | Gunicorn | Production-ready server for deployment |
| **Deployment** | Render | Cloud hosting with auto-deploy from GitHub |

---

## 5. Data Model (Firestore Collections)

### `users/{uid}`
| Field | Type | Description |
|-------|------|-------------|
| uid | string | Firebase Auth UID |
| email | string | User email |
| username | string | Display name (used for login) |
| fullname | string | Full name (optional) |
| super_admin | boolean | Super admin status |
| permissions | array[string] | List of granted permissions |
| api_key | string | API key for programmatic access |
| created_at | timestamp | Registration time |

### `job_ads/{auto_id}`
| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Owner's Firebase UID |
| filename | string | Original PDF filename |
| description | string | Full extracted text |
| result | string | fake / legit / Invalid |
| reason | string | Human-readable explanation |
| created_at | timestamp | Upload time |

### `url_checks/{auto_id}`
| Field | Type | Description |
|-------|------|-------------|
| user_id | string | Owner's Firebase UID |
| url | string | Validated URL |
| result | string | fake / legit / Invalid |
| risk_level | string | low / medium / high |
| reason | string | Validation explanation |
| api_call | boolean | True if via API endpoint |
| created_at | timestamp | Check time |

### `domain_rules/{auto_id}`
| Field | Type | Description |
|-------|------|-------------|
| domain | string | Domain name (e.g., example.com) |
| action | string | allow (whitelist) / block (blacklist) |
| created_by | string | Admin's Firebase UID |
| created_at | timestamp | Rule creation time |

### `audit_logs/{auto_id}`
| Field | Type | Description |
|-------|------|-------------|
| action | string | Action type (delete, profile_update, etc.) |
| user_id | string | Acting user's UID |
| username | string | Acting user's username |
| details | string | Free-text details |
| timestamp | timestamp | Action time |

### `feedback/{auto_id}`
| Field | Type | Description |
|-------|------|-------------|
| user_id | string | User who submitted feedback |
| doc_type | string | pdf or url |
| doc_id | string | Original document ID |
| original_result | string | Original prediction result |
| marked_correct | boolean | User's feedback |
| timestamp | timestamp | Submission time |

---

## 6. Features Summary

### User Features
- **Registration** — email + username + password; first user gets super admin
- **Login** — by email or username
- **Password Reset** — via Firebase Auth email link
- **Dashboard** — aggregated stats bar chart + weekly trend line chart
- **PDF Upload** — single PDF classification with ML
- **URL Validation** — single URL check with multi-layer rules
- **Bulk URL Check** — paste multiple URLs, validate all at once
- **History** — all past PDFs and URL checks with delete and feedback
- **Profile** — edit username, generate API key, download personal CSV
- **Dark Mode** — toggle in navbar, persists in localStorage
- **Feedback** — ✓/✗ buttons to mark predictions as correct/incorrect

### Admin Features
- **Admin Dashboard** — system-wide stats, per-user breakdown
- **User Management** — list all users, view permissions, delete users
- **Permission Management** — assign/revoke any of 20 permissions
- **All Records** — view and delete any PDF or URL check
- **Domain Rules** — add/remove whitelist and blacklist domains
- **Audit Logs** — view all system actions with DataTables
- **Export** — full CSV download of all records

### API Feature
- **Endpoint**: POST `/api/validate-url` with `X-API-Key` header
- Returns JSON with label, risk_level, reason, trusted
- Results stored in Firestore under the API key owner's account

---

## 7. Security

- **Server-side Firestore** — All database operations use Firebase Admin SDK (service account), bypassing client-side security rules
- **Token-based auth** — Firebase ID tokens verified server-side per request
- **Session-based** — Flask sessions with secret key
- **Permission-gated routes** — Admin routes protected by `@permission_required()` decorator
- **API key authentication** — API endpoint protected by 40-character hex key
- **Password security** — Handled entirely by Firebase Auth (hashed, salted, not stored in app)
- **Credentials in environment** — `serviceAccountKey.json` excluded from git via `.gitignore`; loaded from `FIREBASE_SERVICE_ACCOUNT_KEY` env var in production

---

## 8. Deployment

- **Platform**: Render (https://render.com)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Environment Variables**:
  - `FIREBASE_SERVICE_ACCOUNT_KEY` — Firebase service account JSON (single line)
  - `SECRET_KEY` — Flask session secret
- **Auto-deploy**: Connected to GitHub repo, triggered by push or manual deploy

---

## 9. Trusted Domains (Default)

`linkedin.com`, `indeed.com`, `glassdoor.com`, `monster.com`, `careerbuilder.com`, `simplyhired.com`, `ziprecruiter.com`, `dice.com`, `upwork.com`, `freelancer.com`, `fiverr.com`, and government/education domains (`.gov`, `.go.tz`, `.ac.tz`, `.or.tz`, `.go.ke`, `.ac.ke`, `.or.ke`)

Admins can add more via **Admin → Domains** (whitelist or blacklist).

# An Intelligent Fake Job Advertisement Detection System

## Proposal Document

---

### 1. Executive Summary

This project proposes the development of an **Intelligent Fake Job Advertisement Detection System** — a web-based platform that uses Machine Learning (NLP) and URL validation to automatically detect fraudulent job advertisements. The system analyzes both PDF job postings and job application URLs, classifying them as **Fake**, **Legit**, or **Invalid** to help job seekers and organizations identify recruitment scams. The system is trained on a **bilingual English–Swahili dataset** (independently collected, not machine-translated) and includes a **detection and reporting sub-system** for alerting users and generating admin reports.

---

### 2. Problem Statement

Job advertisement fraud is a growing problem in the digital recruitment space. Fraudsters create fake job postings to:

- Steal personal information from applicants
- Collect application fees under false pretenses
- Lure victims into illegal schemes (money laundering, human trafficking)

Key challenges:
- **No centralized validation** — job seekers have no automated way to verify job ad authenticity
- **URL phishing** — fraudulent recruiters use lookalike domains and URL shorteners to appear legitimate
- **Document forgery** — fake PDF job descriptions contain unrealistic offers and missing contact information
- **Scalability** — manual verification of each job ad is impractical at scale

---

### 3. Proposed Solution

A web-based application with three core capabilities:

#### 3.1 PDF Job Ad Classification
- Users upload a PDF job advertisement
- The system extracts text using **pdfplumber**
- Applies **Natural Language Processing (NLP)** preprocessing (tokenization, stemming, stop-word removal)
- A trained **TensorFlow/Keras neural network** classifies the text as **Fake** or **Legit**
- Results are displayed with a confidence reason

#### 3.2 Job URL Validation
- Users submit a job application URL
- The system performs multi-layered checks:
  - **HTTPS enforcement**
  - **Trusted domain whitelist** (linkedin.com, indeed.com, government domains like .go.tz, educational domains like .ac.tz, etc.)
  - **Suspicious pattern detection** (URL shorteners, excessive subdomains, punycode, numeric sequences, phishing keywords)
  - **Unknown domain flagging** for manual review
- Returns: **Label** (Fake / Legit / Invalid), **Risk Level** (Low / Medium / High), and a human-readable reason

##### 3.3 Detection and Reporting Sub-system
- Flagged fraudulent ads trigger alerts on the user dashboard
- Admin-generated summary reports showing fraud trends, top-flagged domains, and user feedback analytics
- Email notifications (future) for critical detections

#### 3.4 Model Evaluation and Selection
- Multiple classifiers are benchmarked on the bilingual English–Swahili dataset:
  - **Logistic Regression**, **Random Forest**, **Support Vector Machine (SVM)**, **Neural Network (TensorFlow/Keras)**
- Performance metrics: accuracy, precision, recall, F1-score
- The best-performing model is deployed in production

#### 3.5 User Dashboard & History
- **Firebase Authentication** for secure login/registration (email + username)
- **Firestore** database for per-user data storage
- Dashboard displays aggregated statistics (Fake, Legit, Invalid counts with chart)
- History page shows all past PDF uploads and URL checks with delete capability

---

### 4. Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | Python Flask |
| Machine Learning | TensorFlow / Keras, scikit-learn |
| NLP | NLTK (stopwords, PorterStemmer) |
| PDF Extraction | pdfplumber |
| Authentication | Firebase Admin SDK |
| Database | Google Cloud Firestore |
| Frontend | HTML5, CSS3, JavaScript (jQuery, DataTables, Chart.js) |
| Deployment | Gunicorn (production-ready WSGI) |

---

### 5. System Architecture

```
User Browser
     │
     ├── Firebase Auth (Client-side) → Login / Register / Password Reset
     │
     └── Flask Web App (Server-side)
              │
              ├── /upload → PDF extraction → NLP → ML Model → Firestore
              │
              ├── /validate-url → URL parsing → Trusted/Suspicious checks → Firestore
              │
              ├── /home → Dashboard with stats from Firestore
              │
              ├── /history → Per-user upload & validation history
              │
              └── /delete → Remove records from Firestore
```

---

### 6. Machine Learning Pipeline

1. **Data Sources**: Bilingual dataset combining independently collected **English** and **Swahili** job advertisements (not machine-translated)
2. **Text Extraction**: PDF text is extracted using pdfplumber
3. **Preprocessing**:
   - Remove non-alphabetic characters
   - Convert to lowercase
   - Tokenize
   - Remove English and Swahili stopwords
   - Apply Porter Stemming
4. **Feature Encoding**: One-hot encoding with vocabulary size of 5000
5. **Padding**: Sequences padded to a maximum length of 40 tokens
6. **Model Selection**: Multiple classifiers (Logistic Regression, Random Forest, SVM, Neural Network) are evaluated on the bilingual dataset; the best performer is deployed
7. **Classification**: Selected model predicts Fake (1) vs Legit (0)

---

### 7. URL Validation Rules

| Rule | Action |
|------|--------|
| No HTTPS | Fake (High risk) |
| >4 subdomains | Fake (High risk — phishing structure) |
| URL shortener (bit.ly, tinyurl, etc.) | Fake (High risk) |
| Suspicious keywords | Fake (High risk) |
| Long numeric sequences in domain | Fake (High risk) |
| Punycode / special characters | Fake (High risk) |
| Trusted domain match | Legit (Low risk) |
| Unknown domain | Invalid (Medium risk — manual review) |

**Trusted domains include**: linkedin.com, indeed.com, glassdoor.com, .gov, .go.tz, .ac.tz, .or.tz, .go.ke, .ac.ke, and major recruitment platforms.

---

### 8. Data Storage

- **Users**: `users/{uid}` — email, username, fullname, created_at
- **Job Ads**: `job_ads/{auto_id}` — user_id, filename, description, result, reason, created_at
- **URL Checks**: `url_checks/{auto_id}` — user_id, url, result, risk_level, reason, created_at

All data is scoped per user via Firebase Authentication UID.

---

### 9. Expected Outcomes

- Automated, real-time detection of fraudulent job advertisements
- Reduced exposure to recruitment scams for job seekers
- Centralized validation history with search, sort, and filtering
- Scalable architecture capable of handling multiple concurrent users
- URL phishing detection to prevent applicants from visiting malicious sites

---

### 10. Future Enhancements

- Integration with external threat intelligence APIs (Google Safe Browsing, VirusTotal)
- Email notification alerts when suspicious job ads are detected
- Bulk PDF upload and processing
- Mobile application (Flutter/React Native)
- Expansion to additional languages (French, Arabic, Portuguese)
- Real-time SMS alerts for critical fraud detections

---

### 11. Conclusion

This **Intelligent Fake Job Advertisement Detection System** combines **Machine Learning** and **URL reputation analysis** to provide a comprehensive tool against recruitment fraud. By accepting both PDF documents and job URLs, it covers the two primary channels through which fraudulent job ads reach applicants, with all data securely stored per user via Firebase.

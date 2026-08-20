import os
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

class ProposalPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, 'Job Advertisement Fraud Detection System - Proposal', 0, 0, 'C')
            self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, num, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, f'{num}. {title}', 0, 1, 'L')
        self.set_draw_color(0, 123, 255)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(33, 37, 41)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def sub_sub_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 7, title, 0, 1, 'L')
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.set_x(self.l_margin)
        self.cell(5, 5.5, '  -')
        self.set_x(self.l_margin + 12)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5.5, text)

    def table_row(self, cells, bold=False, fill=False):
        style = 'B' if bold else ''
        self.set_font('Helvetica', style, 9)
        w = [50, 80]
        if fill:
            self.set_fill_color(240, 240, 240)
        for i, cell in enumerate(cells):
            self.cell(w[i], 7, cell, 1, 0, 'L', fill)
        self.ln()


def generate_flowchart_pdf_upload():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    boxes = {
        'upload': (4, 5, 'Upload PDF'),
        'extract': (4, 3.8, 'Extract Text\n(pdfplumber)'),
        'preprocess': (4, 2.6, 'NLP Preprocess\n(stemming, stopwords)'),
        'predict': (4, 1.4, 'ML Model\n(TensorFlow)'),
        'result': (4, 0.2, 'Result:\nFake / Legit / Invalid'),
    }

    for key, (x, y, label) in boxes.items():
        bbox = dict(boxstyle='round,pad=0.4', facecolor='#e3f2fd', edgecolor='#1565c0', linewidth=1.5)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold', bbox=bbox)

    arrows = [('upload', 'extract'), ('extract', 'preprocess'), ('preprocess', 'predict'), ('predict', 'result')]
    for src, dst in arrows:
        sx, sy = boxes[src][0], boxes[src][1] - 0.45
        dx, dy = boxes[dst][0], boxes[dst][1] + 0.45
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#1565c0', lw=1.5))

    ax.set_title('PDF Upload Classification Flow', fontsize=13, fontweight='bold', pad=10)
    path = os.path.join(OUTPUT_DIR, 'flow_pdf.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def generate_flowchart_url():
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    boxes = {
        'input': (5, 7.2, 'Submit URL'),
        'https': (5, 5.8, 'HTTPS Check'),
        'patterns': (5, 4.4, 'Suspicious Patterns\n(shorteners, subdomains,\nkeywords, punycode)'),
        'trusted': (3, 2.8, 'Trusted Domain\nCheck'),
        'unknown': (7, 2.8, 'Unknown Domain'),
        'legit': (3, 1.2, 'LEGIT\n(Low Risk)'),
        'fake': (5, 0, 'FAKE\n(High Risk)'),
        'invalid': (7, 1.2, 'INVALID\n(Medium Risk)'),
    }

    colors = {
        'input': '#e3f2fd', 'https': '#fff3e0', 'patterns': '#fff3e0',
        'trusted': '#e8f5e9', 'unknown': '#fce4ec',
        'legit': '#c8e6c9', 'fake': '#ffcdd2', 'invalid': '#fff9c4'
    }
    edge_colors = {
        'input': '#1565c0', 'https': '#e65100', 'patterns': '#e65100',
        'trusted': '#2e7d32', 'unknown': '#c62828',
        'legit': '#1b5e20', 'fake': '#b71c1c', 'invalid': '#f9a825'
    }

    for key, (x, y, label) in boxes.items():
        bbox = dict(boxstyle='round,pad=0.35', facecolor=colors[key], edgecolor=edge_colors[key], linewidth=1.5)
        ax.text(x, y, label, ha='center', va='center', fontsize=8.5, fontweight='bold', bbox=bbox)

    arrows = [
        ('input', 'https'), ('https', 'patterns'),
        ('patterns', 'trusted'), ('patterns', 'unknown'),
        ('trusted', 'legit'), ('unknown', 'invalid'),
    ]
    for src, dst in arrows:
        sx, sy = boxes[src][0], boxes[src][1]
        dx, dy = boxes[dst][0], boxes[dst][1]
        # offset for non-vertical arrows
        if src == 'patterns' and dst == 'trusted':
            sx -= 0.4; sy -= 0.3; dx += 0.4; dy += 0.3
        elif src == 'patterns' and dst == 'unknown':
            sx += 0.4; sy -= 0.3; dx -= 0.4; dy += 0.3
        elif src == 'trusted':
            sy -= 0.5; dy += 0.5
        elif src == 'unknown':
            sy -= 0.5; dy += 0.5
        else:
            sy -= 0.45; dy += 0.45
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.3))

    ax.set_title('Job URL Validation Flow', fontsize=13, fontweight='bold', pad=10)
    path = os.path.join(OUTPUT_DIR, 'flow_url.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def generate_use_case():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # System boundary
    rect = mpatches.FancyBboxPatch((1.5, 0.5), 7, 6, boxstyle="round,pad=0.1",
                                     facecolor='#f8f9fa', edgecolor='#333', linewidth=2)
    ax.add_patch(rect)
    ax.text(5, 6.2, 'Job Fraud Detection System', ha='center', fontsize=11,
            fontweight='bold', style='italic')

    # Actors
    actor_x, actor_y = 5, 0.3
    ax.plot(actor_x, actor_y + 0.5, 'o', markersize=8, color='#333')
    ax.plot([actor_x, actor_x], [actor_y, actor_y + 0.5], color='#333', lw=2)
    ax.plot([actor_x - 0.3, actor_x + 0.3], [actor_y + 0.25, actor_y + 0.25], color='#333', lw=2)
    ax.text(actor_x, actor_y - 0.2, 'User', ha='center', fontsize=10, fontweight='bold')

    # Use cases (ellipses)
    uc = [
        (2.5, 5.2, 'Register\nAccount'),
        (2.5, 3.8, 'Login'),
        (5.5, 5.2, 'Upload PDF\nJob Ad'),
        (5.5, 3.8, 'Validate\nJob URL'),
        (2.5, 2.2, 'View\nDashboard'),
        (5.5, 2.2, 'View Upload\nHistory'),
        (8.5, 5.2, 'Delete\nRecord'),
        (8.5, 3.8, 'Reset\nPassword'),
    ]

    for x, y, label in uc:
        bbox = dict(boxstyle='ellipse,pad=0.4', facecolor='#e3f2fd',
                     edgecolor='#1565c0', linewidth=1.2)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', bbox=bbox)

    # Connections from actor to use cases
    connections = [(2.5, 5.2), (2.5, 3.8), (5.5, 5.2), (5.5, 3.8), (2.5, 2.2), (5.5, 2.2)]
    for cx, cy in connections:
        ax.plot([actor_x, cx], [actor_y + 0.6, cy - 0.35],
                color='#333', lw=1, linestyle='-')

    # Include relationships
    ax.annotate('', xy=(3.8, 4.6), xytext=(4.2, 5.0),
                arrowprops=dict(arrowstyle='->', color='#666', lw=0.8, linestyle='dashed'))
    ax.text(4.0, 4.9, '<<include>>', fontsize=6, color='#666', ha='center')

    plt.title('Use Case Diagram', fontsize=13, fontweight='bold', pad=5)
    path = os.path.join(OUTPUT_DIR, 'use_case.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def generate_architecture():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    layers = [
        (1, 4.5, 3.5, 1.2, 'Browser\n(HTML/JS)', '#bbdefb', '#1565c0'),
        (4.7, 4.5, 3.5, 1.2, 'Firebase Auth\n(Client SDK)', '#c8e6c9', '#2e7d32'),
        (8.4, 4.5, 3.5, 1.2, 'Flask Web App\n(Python)', '#fff9c4', '#f9a825'),
        (1, 2.8, 11, 1.2, 'Firebase Admin SDK\n(Token Verification, Firestore CRUD)', '#f3e5f5', '#7b1fa2'),
        (1, 1.2, 5, 1.2, 'ML Model\n(TensorFlow)', '#ffccbc', '#d84315'),
        (6.4, 1.2, 5.2, 1.2, 'Firestore DB\n(Users, Job Ads, URL Checks)', '#e1f5fe', '#0277bd'),
    ]

    for x, y, w, h, label, fc, ec in layers:
        bbox = dict(boxstyle='round,pad=0.2', facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=9, fontweight='bold', bbox=bbox)

    # Arrows between layers
    ax.annotate('', xy=(4.7, 4.2), xytext=(2.75, 4.5),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))
    ax.annotate('', xy=(8.4, 4.2), xytext=(6.45, 4.5),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))
    ax.annotate('', xy=(6.5, 2.55), xytext=(6.5, 2.8),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))
    ax.annotate('', xy=(3.5, 1.0), xytext=(3.5, 1.2),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.2))
    ax.annotate('', xy=(9, 1.0), xytext=(9, 1.2),
                arrowprops=dict(arrowstyle='<->', color='#333', lw=1.2))

    ax.set_title('System Architecture', fontsize=13, fontweight='bold', pad=8)
    path = os.path.join(OUTPUT_DIR, 'architecture.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return path


def main():
    print("Generating diagrams...")
    flow_pdf = generate_flowchart_pdf_upload()
    flow_url = generate_flowchart_url()
    use_case = generate_use_case()
    arch = generate_architecture()
    print("Diagrams generated.")

    pdf = ProposalPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Title Page ──
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 123, 255)
    pdf.cell(0, 15, 'Job Advertisement', 0, 1, 'C')
    pdf.cell(0, 15, 'Fraud Detection System', 0, 1, 'C')
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Project Proposal', 0, 1, 'C')
    pdf.ln(20)
    pdf.set_draw_color(0, 123, 255)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, 'Prepared by: Development Team', 0, 1, 'C')
    pdf.cell(0, 7, f'Date: May 2026', 0, 1, 'C')
    pdf.cell(0, 7, 'Version: 1.0', 0, 1, 'C')

    # ── Table of Contents ──
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 12, 'Table of Contents', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    toc = [
        '1. Executive Summary',
        '2. Problem Statement',
        '3. Proposed Solution',
        '    3.1 PDF Job Ad Classification',
        '    3.2 Job URL Validation',
        '    3.3 User Dashboard & History',
        '4. Use Case Diagram',
        '5. System Architecture',
        '6. Technology Stack',
        '7. Machine Learning Pipeline',
        '8. URL Validation Rules',
        '9. Data Storage',
        '10. Expected Outcomes',
        '11. Future Enhancements',
        '12. Conclusion',
    ]
    pdf.set_font('Helvetica', '', 11)
    for item in toc:
        pdf.cell(0, 7, item, 0, 1)
        if item.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.')):
            pdf.set_text_color(0, 123, 255)
        else:
            pdf.set_text_color(80, 80, 80)
    pdf.set_text_color(50, 50, 50)

    # ── 1. Executive Summary ──
    pdf.add_page()
    pdf.chapter_title(1, 'Executive Summary')
    pdf.body_text(
        'This project proposes the development of a Job Advertisement Fraud Detection System '
        'a web-based platform that uses Machine Learning (NLP) and URL validation to automatically '
        'detect fraudulent job advertisements. The system analyzes both PDF job postings and job '
        'application URLs, classifying them as Fake, Legit, or Invalid to help job seekers and '
        'organizations identify recruitment scams.'
    )

    # ── 2. Problem Statement ──
    pdf.chapter_title(2, 'Problem Statement')
    pdf.body_text(
        'Job advertisement fraud is a growing problem in the digital recruitment space. '
        'Fraudsters create fake job postings to:'
    )
    pdf.bullet('Steal personal information from applicants')
    pdf.bullet('Collect application fees under false pretenses')
    pdf.bullet('Lure victims into illegal schemes (money laundering, human trafficking)')
    pdf.ln(3)
    pdf.body_text('Key challenges:')
    pdf.bullet('No centralized validation - job seekers have no automated way to verify job ad authenticity')
    pdf.bullet('URL phishing - fraudulent recruiters use lookalike domains and URL shorteners')
    pdf.bullet('Document forgery - fake PDF job descriptions contain unrealistic offers')
    pdf.bullet('Scalability - manual verification of each job ad is impractical at scale')

    # ── 3. Proposed Solution ──
    pdf.chapter_title(3, 'Proposed Solution')
    pdf.body_text(
        'A web-based application with three core capabilities: PDF Job Ad Classification, '
        'Job URL Validation, and a User Dashboard with History.'
    )

    pdf.sub_title('3.1 PDF Job Ad Classification')
    pdf.body_text(
        'Users upload a PDF job advertisement. The system extracts text using pdfplumber, '
        'applies Natural Language Processing (NLP) preprocessing (tokenization, stemming, '
        'stop-word removal), and a trained TensorFlow/Keras neural network classifies the '
        'text as Fake or Legit. Results are displayed with a confidence reason.'
    )
    pdf.image(flow_pdf, x=25, w=160)
    pdf.ln(3)

    pdf.sub_title('3.2 Job URL Validation')
    pdf.body_text(
        'Users submit a job application URL. The system performs multi-layered checks including '
        'HTTPS enforcement, trusted domain whitelist matching, suspicious pattern detection '
        '(URL shorteners, excessive subdomains, punycode, numeric sequences, phishing keywords), '
        'and unknown domain flagging. Returns a label (Fake/Legit/Invalid), risk level, and reason.'
    )
    pdf.image(flow_url, x=25, w=160)
    pdf.ln(3)

    pdf.sub_title('3.3 User Dashboard & History')
    pdf.body_text(
        'Firebase Authentication provides secure login and registration. Firestore stores all '
        'data per user. The Dashboard displays aggregated statistics (Fake, Legit, Invalid counts '
        'with Chart.js bar chart). The History page shows all past PDF uploads and URL checks '
        'with search, sort, and delete capabilities.'
    )

    # ── 4. Use Case Diagram ──
    pdf.chapter_title(4, 'Use Case Diagram')
    pdf.body_text(
        'The following use case diagram illustrates the interactions between the User and the system:'
    )
    pdf.image(use_case, x=20, w=170)
    pdf.ln(3)

    # ── 5. System Architecture ──
    pdf.chapter_title(5, 'System Architecture')
    pdf.body_text(
        'The system follows a client-server architecture with Firebase integration for '
        'authentication and data storage. The diagram below shows the component layering:'
    )
    pdf.image(arch, x=15, w=180)
    pdf.ln(3)

    # ── 6. Technology Stack ──
    pdf.chapter_title(6, 'Technology Stack')
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.table_row(['Component', 'Technology'], bold=True, fill=True)
    pdf.set_font('Helvetica', '', 10)
    stack = [
        ('Backend Framework', 'Python Flask'),
        ('Machine Learning', 'TensorFlow / Keras, scikit-learn'),
        ('NLP', 'NLTK (stopwords, PorterStemmer)'),
        ('PDF Extraction', 'pdfplumber'),
        ('Authentication', 'Firebase Admin SDK'),
        ('Database', 'Google Cloud Firestore'),
        ('Frontend', 'HTML5, CSS3, JavaScript (DataTables, Chart.js)'),
        ('Diagrams', 'Graphviz, Matplotlib'),
        ('Deployment', 'Gunicorn'),
    ]
    for comp, tech in stack:
        pdf.table_row([comp, tech])
    pdf.ln(3)

    # ── 7. ML Pipeline ──
    pdf.chapter_title(7, 'Machine Learning Pipeline')
    pdf.body_text('The ML pipeline processes PDF job ads through the following stages:')
    pdf.ln(1)
    steps = [
        ('1. Text Extraction', 'PDF text is extracted using pdfplumber'),
        ('2. Preprocessing', 'Remove non-alphabetic characters, convert to lowercase, tokenize, remove English stopwords, apply Porter Stemming'),
        ('3. Feature Encoding', 'One-hot encoding with vocabulary size of 5000'),
        ('4. Padding', 'Sequences padded to a maximum length of 40 tokens'),
        ('5. Classification', 'Neural network model predicts Fake (1) vs Legit (0)'),
    ]
    for title, desc in steps:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, title, 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, f'     {desc}', 0, 1)
        pdf.ln(1)

    # ── 8. URL Validation Rules ──
    pdf.chapter_title(8, 'URL Validation Rules')
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.table_row(['Rule', 'Result'], bold=True, fill=True)
    pdf.set_font('Helvetica', '', 10)
    rules = [
        ('No HTTPS', 'Fake (High risk)'),
        ('More than 4 subdomains', 'Fake (High risk)'),
        ('URL shortener (bit.ly, tinyurl)', 'Fake (High risk)'),
        ('Suspicious keywords', 'Fake (High risk)'),
        ('Long numeric sequences', 'Fake (High risk)'),
        ('Punycode / special chars', 'Fake (High risk)'),
        ('Trusted domain match', 'Legit (Low risk)'),
        ('Unknown domain', 'Invalid (Medium risk)'),
    ]
    for rule, result in rules:
        pdf.table_row([rule, result])
    pdf.ln(3)
    pdf.body_text(
        'Trusted domains include: linkedin.com, indeed.com, glassdoor.com, .gov, .go.tz, '
        '.ac.tz, .or.tz, .go.ke, .ac.ke, and major recruitment platforms.'
    )

    # ── 9. Data Storage ──
    pdf.chapter_title(9, 'Data Storage')
    pdf.body_text('All data is stored in Google Cloud Firestore with per-user isolation:')
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.table_row(['Collection', 'Fields'], bold=True, fill=True)
    pdf.set_font('Helvetica', '', 10)
    collections = [
        ('users/{uid}', 'email, username, fullname, created_at'),
        ('job_ads/{auto_id}', 'user_id, filename, description, result, reason, created_at'),
        ('url_checks/{auto_id}', 'user_id, url, result, risk_level, reason, created_at'),
    ]
    for col, fields in collections:
        pdf.table_row([col, fields])
    pdf.ln(2)
    pdf.body_text(
        'Data is scoped per user via Firebase Authentication UID, ensuring that each user '
        'can only access their own uploads and history.'
    )

    # ── 10. Expected Outcomes ──
    pdf.chapter_title(10, 'Expected Outcomes')
    pdf.bullet('Automated, real-time detection of fraudulent job advertisements')
    pdf.bullet('Reduced exposure to recruitment scams for job seekers')
    pdf.bullet('Centralized validation history with search, sort, and filtering')
    pdf.bullet('Scalable architecture capable of handling multiple concurrent users')
    pdf.bullet('URL phishing detection to prevent applicants from visiting malicious sites')

    # ── 11. Future Enhancements ──
    pdf.chapter_title(11, 'Future Enhancements')
    pdf.bullet('Integration with external threat intelligence APIs (Google Safe Browsing, VirusTotal)')
    pdf.bullet('Email notification alerts when suspicious job ads are detected')
    pdf.bullet('Bulk PDF upload and processing')
    pdf.bullet('Mobile application (Flutter / React Native)')
    pdf.bullet('Admin panel for reviewing flagged content')
    pdf.bullet('Multi-language support for non-English job ads')

    # ── 12. Conclusion ──
    pdf.chapter_title(12, 'Conclusion')
    pdf.body_text(
        'This Job Advertisement Fraud Detection System combines Machine Learning and URL '
        'reputation analysis to provide a comprehensive tool against recruitment fraud. By '
        'accepting both PDF documents and job URLs, it covers the two primary channels through '
        'which fraudulent job ads reach applicants, with all data securely stored per user via Firebase.'
    )

    output_path = os.path.join(OUTPUT_DIR, 'Proposal.pdf')
    pdf.output(output_path)
    print(f"Proposal generated: {output_path}")


if __name__ == '__main__':
    main()

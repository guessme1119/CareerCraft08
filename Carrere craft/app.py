import random
import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from dotenv import load_dotenv
from fetch_jobs import JobFetcher

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'skyshotgaming08@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_app_password')  # Use Gmail App Password, not regular password!
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'skyshotgaming08@gmail.com')

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'hr' or 'user'
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    summary = db.Column(db.Text)
    skills = db.Column(db.Text)  # JSON string
    education = db.Column(db.Text)  # JSON string
    experience = db.Column(db.Text)  # JSON string
    projects = db.Column(db.Text)  # JSON string
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200))
    score = db.Column(db.Integer)
    sections_found = db.Column(db.Text)  # JSON string
    skills_found = db.Column(db.Text)  # JSON string
    suggestions = db.Column(db.Text)  # JSON string
    word_count = db.Column(db.Integer)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300))
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    description = db.Column(db.Text)
    redirect_url = db.Column(db.String(500))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def send_otp_email(email, otp):
    """Send OTP via email. If email is not configured, display OTP in console for testing."""
    try:
        # Check if email is properly configured
        if app.config['MAIL_USERNAME'] == 'your_email@gmail.com' or app.config['MAIL_PASSWORD'] == 'your_app_password':
            # Email not configured - show OTP in console for testing
            print("\n" + "="*60)
            print("📧 EMAIL NOT CONFIGURED - SHOWING OTP IN CONSOLE")
            print("="*60)
            print(f"Email: {email}")
            print(f"OTP Code: {otp}")
            print(f"This OTP will expire in 10 minutes")
            print("="*60 + "\n")
            return True
        
        # Email is configured - send actual email
        msg = Message('Your OTP Verification Code',
                      recipients=[email])
        msg.body = f'''Hello,

Your OTP verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Your App Team'''
        mail.send(msg)
        print(f"✅ OTP sent successfully to {email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        # Fallback: Show OTP in console
        print("\n" + "="*60)
        print("⚠️ EMAIL FAILED - SHOWING OTP IN CONSOLE")
        print("="*60)
        print(f"Email: {email}")
        print(f"OTP Code: {otp}")
        print(f"Error: {str(e)}")
        print("="*60 + "\n")
        return True  # Return True so user can still proceed

def generate_otp():
    return str(random.randint(100000, 999999))

def create_otp_record(email):
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Delete old OTPs for this email
    OTP.query.filter_by(email=email, is_used=False).delete()
    
    otp_record = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
    db.session.add(otp_record)
    db.session.commit()
    
    return otp_code

def verify_otp(email, otp_code):
    otp_record = OTP.query.filter_by(
        email=email, 
        otp_code=otp_code, 
        is_used=False
    ).first()
    
    if not otp_record:
        return False
    
    if datetime.utcnow() > otp_record.expires_at:
        return False
    
    otp_record.is_used = True
    db.session.commit()
    return True

# Resume Analysis Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
    return text

def preprocess_text(text):
    """Clean and preprocess extracted text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep important ones
    text = re.sub(r'[^a-zA-Z0-9\s.,@+#-]', '', text)
    return text.strip()

def analyze_resume(text):
    """Analyze resume and return detailed report"""
    text_lower = text.lower()
    
    # Define sections to check
    sections = {
        'Education': ['education', 'academic', 'degree', 'university', 'college', 'bachelor', 'master', 'phd'],
        'Experience': ['experience', 'work history', 'employment', 'worked at', 'position', 'job'],
        'Skills': ['skills', 'technical skills', 'competencies', 'expertise', 'proficient'],
        'Projects': ['projects', 'portfolio', 'work samples', 'achievements'],
        'Contact': ['email', 'phone', 'contact', 'mobile', '@', 'linkedin']
    }
    
    # Define important keywords/skills
    important_skills = [
        'python', 'java', 'javascript', 'sql', 'react', 'angular', 'vue',
        'node', 'flask', 'django', 'spring', 'aws', 'azure', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'html', 'css', 'mongodb',
        'postgresql', 'mysql', 'rest', 'api', 'microservices', 'ci/cd',
        'machine learning', 'data analysis', 'tensorflow', 'pandas', 'numpy'
    ]
    
    # Section Analysis
    sections_found = {}
    section_score = 0
    
    for section, keywords in sections.items():
        found = any(keyword in text_lower for keyword in keywords)
        sections_found[section] = found
        if found:
            section_score += 8  # 8 points per section (5 sections = 40 points)
    
    # Keyword/Skills Analysis
    skills_found = []
    skills_missing = []
    
    for skill in important_skills:
        if skill in text_lower:
            skills_found.append(skill)
        else:
            skills_missing.append(skill)
    
    # Calculate keyword score (max 40 points)
    keyword_score = min(40, len(skills_found) * 2)
    
    # Length and Format Analysis
    word_count = len(text.split())
    format_score = 0
    format_feedback = []
    
    if word_count < 200:
        format_feedback.append("Resume is too short. Aim for 300-800 words.")
        format_score = 5
    elif word_count > 1500:
        format_feedback.append("Resume is too long. Keep it concise (1-2 pages).")
        format_score = 10
    else:
        format_feedback.append("Resume length is appropriate.")
        format_score = 20
    
    # Calculate total score
    total_score = section_score + keyword_score + format_score
    
    # Generate suggestions
    suggestions = []
    
    for section, found in sections_found.items():
        if not found:
            suggestions.append(f"Add a '{section}' section to your resume")
    
    if len(skills_found) < 5:
        suggestions.append(f"Include more relevant skills. Found only {len(skills_found)} skills.")
    
    # Pick top 5 missing skills to suggest
    if len(skills_missing) > 0:
        top_missing = skills_missing[:5]
        suggestions.append(f"Consider adding these skills if applicable: {', '.join(top_missing)}")
    
    # Compile report
    report = {
        'score': total_score,
        'sections': sections_found,
        'skills_found': skills_found[:10],  # Show top 10 skills found
        'skills_count': len(skills_found),
        'word_count': word_count,
        'format_feedback': format_feedback,
        'suggestions': suggestions,
        'section_score': section_score,
        'keyword_score': keyword_score,
        'format_score': format_score
    }
    
    return report

# Routes
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/<role>/login', methods=['GET', 'POST'])
def login(role):
    if role not in ['hr', 'user']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role=role).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Please verify your email first.', 'warning')
                return redirect(url_for('login', role=role))
            
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard', role=role))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', role=role)

@app.route('/<role>/signup', methods=['GET', 'POST'])
def signup(role):
    if role not in ['hr', 'user']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email, role=role).first()
        if existing_user:
            flash('Email already registered for this role.', 'danger')
            return redirect(url_for('signup', role=role))
        
        # Store signup data in session
        session['signup_email'] = email
        session['signup_password'] = generate_password_hash(password)
        session['signup_role'] = role
        
        # Generate and send OTP
        otp_code = create_otp_record(email)
        send_otp_email(email, otp_code)
        
        # Check if email is configured
        if app.config['MAIL_USERNAME'] == 'your_email@gmail.com':
            flash('OTP generated! Check the console/terminal for your OTP code.', 'info')
        else:
            flash('OTP sent to your email. Please check your inbox.', 'success')
        
        return redirect(url_for('verify_otp_route', role=role))
    
    return render_template('signup.html', role=role)

@app.route('/<role>/verify-otp', methods=['GET', 'POST'])
def verify_otp_route(role):
    if role not in ['hr', 'user']:
        return redirect(url_for('index'))
    
    if 'signup_email' not in session:
        flash('Please signup first.', 'warning')
        return redirect(url_for('signup', role=role))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        email = session.get('signup_email')
        
        if verify_otp(email, otp_code):
            # Create user account
            new_user = User(
                email=email,
                password=session.get('signup_password'),
                role=role,
                is_verified=True
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Clear signup session data
            session.pop('signup_email', None)
            session.pop('signup_password', None)
            session.pop('signup_role', None)
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login', role=role))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
    
    return render_template('verify_otp.html', role=role, email=session.get('signup_email'))

@app.route('/<role>/resend-otp', methods=['POST'])
def resend_otp(role):
    if 'signup_email' not in session:
        flash('Session expired. Please signup again.', 'warning')
        return redirect(url_for('signup', role=role))
    
    email = session.get('signup_email')
    otp_code = create_otp_record(email)
    send_otp_email(email, otp_code)
    
    # Check if email is configured
    if app.config['MAIL_USERNAME'] == 'your_email@gmail.com':
        flash('New OTP generated! Check the console/terminal for your OTP code.', 'info')
    else:
        flash('New OTP sent to your email.', 'success')
    
    return redirect(url_for('verify_otp_route', role=role))

@app.route('/<role>/dashboard')
def dashboard(role):
    if 'user_id' not in session or session.get('user_role') != role:
        flash('Please login first.', 'warning')
        return redirect(url_for('login', role=role))
    
    user_id = session.get('user_id')
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    user_name = profile.full_name if profile and profile.full_name else session.get('user_email')
    
    return render_template('user_dashboard.html', role=role, email=session.get('user_email'), user_name=user_name, active_page='dashboard')

@app.route('/<role>/jobs')
def jobs(role):
    if 'user_id' not in session or session.get('user_role') != role:
        flash('Please login first.', 'warning')
        return redirect(url_for('login', role=role))
    
    # Get user's skills to suggest job search
    user_id = session.get('user_id')
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    latest_analysis = ResumeAnalysis.query.filter_by(user_id=user_id).order_by(ResumeAnalysis.analyzed_at.desc()).first()
    
    suggested_search = ""
    user_skills = []
    
    # Get skills from profile or analysis
    if profile and profile.skills:
        try:
            user_skills = json.loads(profile.skills)
        except:
            pass
    
    if not user_skills and latest_analysis and latest_analysis.skills_found:
        try:
            user_skills = json.loads(latest_analysis.skills_found)
        except:
            pass
    
    # Generate suggested search based on top skills
    if user_skills:
        # Pick top 2-3 relevant skills for job search
        top_skills = user_skills[:3]
        suggested_search = " ".join(top_skills)
    
    return render_template('jobs.html', role=role, email=session.get('user_email'), suggested_search=suggested_search, active_page='jobs')

# Job API Routes
def calculate_job_match(user_skills, user_summary, job_title, job_description):
    """Calculate match percentage between user profile and job requirements"""
    if not user_skills or len(user_skills) == 0:
        return 0
    
    # Combine job title and description for analysis
    job_text = f"{job_title} {job_description}".lower()
    
    # Count matching skills
    matched_skills = 0
    total_skills = len(user_skills)
    
    for skill in user_skills:
        skill_lower = str(skill).lower().strip()
        if skill_lower and skill_lower in job_text:
            matched_skills += 1
    
    # Calculate base match from skills (70% weight)
    skills_match = (matched_skills / total_skills * 70) if total_skills > 0 else 0
    
    # Check for keywords in summary (30% weight)
    summary_match = 0
    if user_summary:
        summary_lower = user_summary.lower()
        # Extract key terms from job title
        job_keywords = set(job_title.lower().split())
        common_words = {'and', 'or', 'the', 'a', 'an', 'in', 'at', 'for', 'to', 'of', 'with', 'by', 'on'}
        job_keywords = job_keywords - common_words
        
        matched_keywords = sum(1 for keyword in job_keywords if len(keyword) > 2 and keyword in summary_lower)
        if job_keywords:
            summary_match = (matched_keywords / len(job_keywords)) * 30
    
    # Total match percentage - ensure minimum of 10% if any skills exist
    total_match = max(10, min(100, int(skills_match + summary_match))) if total_skills > 0 else 0
    
    return total_match

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    page = int(request.args.get('page', 1))
    salary_min = request.args.get('salary_min')
    salary_max = request.args.get('salary_max')
    
    fetcher = JobFetcher()
    result = fetcher.fetch_jobs(
        query=query,
        location=location,
        page=page,
        salary_min=salary_min,
        salary_max=salary_max
    )
    
    # Get user profile and resume analysis for match calculation
    user_id = session.get('user_id')
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    latest_analysis = ResumeAnalysis.query.filter_by(user_id=user_id).order_by(ResumeAnalysis.analyzed_at.desc()).first()
    
    user_skills = []
    user_summary = ''
    
    # Get skills from profile first
    if profile:
        if profile.skills:
            try:
                user_skills = json.loads(profile.skills)
            except:
                user_skills = []
        user_summary = profile.summary or ''
    
    # If no skills in profile, get from latest resume analysis
    if not user_skills and latest_analysis:
        if latest_analysis.skills_found:
            try:
                user_skills = json.loads(latest_analysis.skills_found)
            except:
                user_skills = []
    
    # Add formatted salary, days ago, and match percentage for each job
    for job in result.get('jobs', []):
        job['formatted_salary'] = fetcher.format_salary(
            job.get('salary_min'),
            job.get('salary_max'),
            job.get('salary_is_predicted', False)
        )
        job['days_ago'] = fetcher.calculate_days_ago(job.get('created', ''))
        
        # Calculate match percentage
        job['match_percentage'] = calculate_job_match(
            user_skills,
            user_summary,
            job.get('title', ''),
            job.get('description', '')
        )
    
    # Sort jobs by match percentage (highest first)
    if result.get('jobs'):
        result['jobs'] = sorted(result['jobs'], key=lambda x: x.get('match_percentage', 0), reverse=True)
    
    return jsonify(result)

@app.route('/api/jobs/save', methods=['POST'])
def save_job():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    user_id = session.get('user_id')
    
    # Check if already saved
    existing = SavedJob.query.filter_by(user_id=user_id, job_id=data['job_id']).first()
    if existing:
        return jsonify({'message': 'Job already saved', 'already_saved': True}), 200
    
    saved_job = SavedJob(
        user_id=user_id,
        job_id=data['job_id'],
        title=data.get('title'),
        company=data.get('company'),
        location=data.get('location'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        description=data.get('description'),
        redirect_url=data.get('redirect_url')
    )
    db.session.add(saved_job)
    db.session.commit()
    
    return jsonify({'message': 'Job saved successfully', 'already_saved': False}), 201

@app.route('/api/jobs/saved', methods=['GET'])
def get_saved_jobs():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id')
    saved_jobs = SavedJob.query.filter_by(user_id=user_id).order_by(SavedJob.saved_at.desc()).all()
    
    jobs = [{
        'id': job.job_id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'description': job.description,
        'redirect_url': job.redirect_url,
        'saved_at': job.saved_at.isoformat()
    } for job in saved_jobs]
    
    return jsonify({'jobs': jobs})

@app.route('/api/jobs/unsave/<job_id>', methods=['DELETE'])
def unsave_job(job_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id')
    saved_job = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
    
    if saved_job:
        db.session.delete(saved_job)
        db.session.commit()
        return jsonify({'message': 'Job removed'}), 200
    
    return jsonify({'error': 'Job not found'}), 404

@app.route('/<role>/builder')
def builder(role):
    if 'user_id' not in session or session.get('user_role') != role:
        flash('Please login first.', 'warning')
        return redirect(url_for('login', role=role))
    
    return render_template('builder.html', role=role, email=session.get('user_email'), active_page='builder')

def extract_profile_data(text, analysis_report):
    """Extract profile data from resume text"""
    extracted = {
        'skills': analysis_report.get('skills_found', []),
        'summary': ''
    }
    
    # Try to extract summary/objective
    summary_keywords = ['summary', 'objective', 'profile', 'about']
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in summary_keywords):
            # Get next few lines as summary
            summary_lines = []
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip() and not any(k in lines[j].lower() for k in ['experience', 'education', 'skills']):
                    summary_lines.append(lines[j].strip())
            extracted['summary'] = ' '.join(summary_lines)
            break
    
    return extracted

@app.route('/<role>/analyser', methods=['GET', 'POST'])
def analyser(role):
    if 'user_id' not in session or session.get('user_role') != role:
        flash('Please login first.', 'warning')
        return redirect(url_for('login', role=role))
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX allowed'}), 400
        
        try:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Extract text based on file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'pdf':
                text = extract_text_from_pdf(file_path)
            elif file_ext == 'docx':
                text = extract_text_from_docx(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400
            
            # Preprocess text
            cleaned_text = preprocess_text(text)
            
            # Analyze resume
            report = analyze_resume(cleaned_text)
            
            # Save analysis to database
            user_id = session.get('user_id')
            analysis = ResumeAnalysis(
                user_id=user_id,
                filename=filename,
                score=report['score'],
                sections_found=json.dumps(report['sections']),
                skills_found=json.dumps(report.get('skills_found', [])),
                suggestions=json.dumps(report['suggestions']),
                word_count=report.get('word_count', len(cleaned_text.split()))
            )
            db.session.add(analysis)
            
            # Extract and save/update profile data
            extracted_data = extract_profile_data(cleaned_text, report)
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            
            if profile:
                # Update existing profile with extracted data
                if extracted_data.get('skills'):
                    profile.skills = json.dumps(extracted_data['skills'])
                if extracted_data.get('summary'):
                    profile.summary = extracted_data['summary']
                profile.updated_at = datetime.utcnow()
            else:
                # Create new profile
                profile = UserProfile(
                    user_id=user_id,
                    skills=json.dumps(extracted_data.get('skills', [])),
                    summary=extracted_data.get('summary', '')
                )
                db.session.add(profile)
            
            db.session.commit()
            
            # Clean up - delete uploaded file
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify(report)
            
        except Exception as e:
            print(f"Error processing resume: {e}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return render_template('analyser.html', role=role, email=session.get('user_email'), active_page='analyser')

@app.route('/<role>/profile', methods=['GET', 'POST'])
def profile(role):
    if 'user_id' not in session or session.get('user_role') != role:
        flash('Please login first.', 'warning')
        return redirect(url_for('login', role=role))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Save profile data
        try:
            profile_data = UserProfile.query.filter_by(user_id=user_id).first()
            
            if profile_data:
                # Update existing profile
                profile_data.full_name = request.form.get('full_name')
                profile_data.phone = request.form.get('phone')
                profile_data.location = request.form.get('location')
                profile_data.linkedin = request.form.get('linkedin')
                profile_data.summary = request.form.get('summary')
                profile_data.updated_at = datetime.utcnow()
            else:
                # Create new profile
                profile_data = UserProfile(
                    user_id=user_id,
                    full_name=request.form.get('full_name'),
                    phone=request.form.get('phone'),
                    location=request.form.get('location'),
                    linkedin=request.form.get('linkedin'),
                    summary=request.form.get('summary')
                )
                db.session.add(profile_data)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile', role=role))
            
        except Exception as e:
            print(f"Error saving profile: {e}")
            flash('Error saving profile. Please try again.', 'danger')
    
    # GET request - load profile data
    profile_data = UserProfile.query.filter_by(user_id=user_id).first()
    latest_analysis = ResumeAnalysis.query.filter_by(user_id=user_id).order_by(ResumeAnalysis.analyzed_at.desc()).first()
    analysis_history = ResumeAnalysis.query.filter_by(user_id=user_id).order_by(ResumeAnalysis.analyzed_at.desc()).limit(5).all()
    
    # Parse JSON fields
    skills = []
    if profile_data and profile_data.skills:
        try:
            skills = json.loads(profile_data.skills)
        except:
            skills = []
    
    return render_template('profile.html', 
                         role=role, 
                         email=session.get('user_email'), 
                         active_page='profile',
                         profile=profile_data,
                         latest_analysis=latest_analysis,
                         analysis_history=analysis_history,
                         skills=skills)

@app.route('/api/analysis/delete/<int:analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id')
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if analysis:
        db.session.delete(analysis)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Analysis deleted'}), 200
    
    return jsonify({'success': False, 'error': 'Analysis not found'}), 404

@app.route('/api/analysis/delete-all', methods=['DELETE'])
def delete_all_analysis():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id')
    ResumeAnalysis.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'All analysis history deleted'}), 200

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#!/usr/bin/env python3
"""
Day 6: IGCSE Chemistry Assessment Tool - Main Web Application
Flask app with comprehensive performance analysis and AI integration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Add src to path for AI analyzer import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'day6-secret-key-igcse-chemistry')

# Fix database path - create in current directory
db_path = os.path.join(os.path.dirname(__file__), 'day6_assessment.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Import AI analyzer
try:
    from ai_analyzer import AIAnalyzer, create_ai_provider
    AI_AVAILABLE = True
except ImportError:
    print("⚠️  AI analyzer not available - some features will be limited")
    AI_AVAILABLE = False

# Database Models
class Teacher(db.Model):
    """Teacher model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentClass(db.Model):
    """Student class management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    """Student model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    """Assessment management"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    topics = db.Column(db.Text, nullable=False)  # JSON list
    total_questions = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    """Comprehensive quiz results with engagement and attainment"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    
    # Quiz performance
    answers = db.Column(db.Text, nullable=False)  # JSON
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    
    # Day 6 Features: Engagement Rate (1-9)
    engagement_rate = db.Column(db.Integer, nullable=True)
    questioning_evidence = db.Column(db.Boolean, default=False)
    answering_evidence = db.Column(db.Boolean, default=False)
    focus_evidence = db.Column(db.Boolean, default=False)
    activity_evidence = db.Column(db.Boolean, default=False)
    
    # Day 6 Features: Attainment Analysis
    preparation_outcome = db.Column(db.String(20), nullable=True)  # emerging/developing/secure/mastery
    in_class_practice = db.Column(db.String(20), nullable=True)    # emerging/developing/secure/mastery
    
    # AI Analysis Results
    ai_analysis = db.Column(db.Text, nullable=True)  # JSON
    
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize AI analyzer if available
ai_analyzer = None
if AI_AVAILABLE:
    try:
        provider = create_ai_provider("mock")  # Use mock provider for Day 6 demo
        ai_analyzer = AIAnalyzer(provider)
    except Exception as e:
        print(f"⚠️  AI analyzer initialization failed: {e}")

# Routes
@app.route('/')
def index():
    """Day 6 landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Teacher login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        teacher = Teacher.query.filter_by(username=username).first()
        
        if teacher and teacher.check_password(password):
            session['teacher_id'] = teacher.id
            session['teacher_name'] = teacher.username
            flash('✅ Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Teacher registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        school = request.form.get('school', '')
        
        # Check if username exists
        if Teacher.query.filter_by(username=username).first():
            flash('❌ Username already exists!', 'error')
            return render_template('register.html')
        
        # Create new teacher
        teacher = Teacher(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            school=school
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        flash('✅ Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Teacher logout"""
    session.clear()
    flash('✅ Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Day 6 teacher dashboard"""
    if 'teacher_id' not in session:
        return redirect(url_for('login'))
    
    teacher_id = session['teacher_id']
    teacher = Teacher.query.get(teacher_id)
    
    # Get teacher's classes and assessments
    classes = StudentClass.query.filter_by(teacher_id=teacher_id).all()
    assessments = Assessment.query.filter_by(teacher_id=teacher_id)\
                                  .order_by(Assessment.created_at.desc())\
                                  .limit(5).all()
    
    # Calculate statistics
    total_students = sum(len(Student.query.filter_by(class_id=cls.id).all()) for cls in classes)
    total_assessments = len(Assessment.query.filter_by(teacher_id=teacher_id).all())
    recent_results = QuizResult.query.join(Assessment)\
                                    .filter(Assessment.teacher_id == teacher_id)\
                                    .order_by(QuizResult.completed_at.desc())\
                                    .limit(10).all()
    
    return render_template('dashboard.html', 
                         teacher=teacher,
                         classes=classes,
                         assessments=assessments,
                         recent_results=recent_results,
                         total_students=total_students,
                         total_assessments=total_assessments)

@app.route('/enhanced_input_results')
@app.route('/enhanced_input_results/<int:assessment_id>')
def enhanced_input_results(assessment_id=None):
    """Day 6 main feature: Enhanced input results interface"""
    if 'teacher_id' not in session:
        return redirect(url_for('login'))
    
    teacher_id = session['teacher_id']
    
    # Get teacher's classes and assessments
    classes = StudentClass.query.filter_by(teacher_id=teacher_id).all()
    assessments = Assessment.query.filter_by(teacher_id=teacher_id).all()
    
    selected_assessment = None
    students = []
    
    if assessment_id:
        selected_assessment = Assessment.query.get(assessment_id)
        if selected_assessment and selected_assessment.teacher_id == teacher_id:
            students = Student.query.filter_by(class_id=selected_assessment.class_id).all()
    
    return render_template('enhanced_input_results.html',
                         classes=classes,
                         assessments=assessments,
                         selected_assessment=selected_assessment,
                         students=students)

@app.route('/api/submit_comprehensive_assessment', methods=['POST'])
def submit_comprehensive_assessment():
    """API endpoint for submitting comprehensive assessment data"""
    if 'teacher_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Extract assessment data
        student_id = data.get('student_id')
        assessment_id = data.get('assessment_id')
        quiz_answers = data.get('quiz_answers', {})
        engagement_rate = data.get('engagement_rate')
        engagement_evidence = data.get('engagement_evidence', {})
        preparation_outcome = data.get('preparation_outcome')
        in_class_practice = data.get('in_class_practice')
        
        # Calculate score
        total_questions = len(quiz_answers)
        correct_answers = sum(1 for answer in quiz_answers.values() if answer == 'correct')
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Create quiz result record
        quiz_result = QuizResult(
            student_id=student_id,
            assessment_id=assessment_id,
            answers=json.dumps(quiz_answers),
            score=score,
            total_questions=total_questions,
            engagement_rate=engagement_rate,
            questioning_evidence=engagement_evidence.get('questioning', False),
            answering_evidence=engagement_evidence.get('answering', False),
            focus_evidence=engagement_evidence.get('focus', False),
            activity_evidence=engagement_evidence.get('activity', False),
            preparation_outcome=preparation_outcome,
            in_class_practice=in_class_practice
        )
        
        # Generate AI analysis if available
        ai_analysis_result = {}
        if ai_analyzer:
            try:
                # Prepare data for AI analysis
                analysis_data = {
                    'score_percentage': score,
                    'engagement_rate': engagement_rate,
                    'engagement_evidence': engagement_evidence,
                    'preparation_outcome': preparation_outcome,
                    'in_class_practice': in_class_practice,
                    'total_questions': total_questions,
                    'correct_answers': correct_answers
                }
                
                ai_analysis_result = ai_analyzer.analyze_comprehensive_performance(analysis_data)
                quiz_result.ai_analysis = json.dumps(ai_analysis_result)
                
            except Exception as e:
                print(f"AI analysis error: {e}")
                ai_analysis_result = {'error': 'AI analysis failed', 'message': str(e)}
        
        # Save to database
        db.session.add(quiz_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result_id': quiz_result.id,
            'score': score,
            'ai_analysis': ai_analysis_result,
            'message': 'Assessment data saved successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick_demo_data')
def quick_demo_data():
    """Generate quick demo data for Day 6 testing"""
    if 'teacher_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Sample assessment data
    demo_data = {
        'student_name': 'Alex Chen',
        'assessment_title': 'IGCSE Chemistry - Bonding & Structure',
        'quiz_answers': {
            '1': 'correct',
            '2': 'correct', 
            '3': 'incorrect',
            '4': 'correct',
            '5': 'incorrect',
            '6': 'correct',
            '7': 'correct',
            '8': 'incorrect',
            '9': 'correct',
            '10': 'correct'
        },
        'engagement_rate': 7,
        'engagement_evidence': {
            'questioning': True,
            'answering': True,
            'focus': True,
            'activity': False
        },
        'preparation_outcome': 'developing',
        'in_class_practice': 'secure'
    }
    
    return jsonify(demo_data)

# Database initialization
def init_db():
    """Initialize database with Day 6 demo data"""
    try:
        # Create database tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create demo teacher if doesn't exist
        if not Teacher.query.filter_by(username='day6_teacher').first():
            demo_teacher = Teacher(
                username='day6_teacher',
                email='day6@igcse.demo',
                password_hash=generate_password_hash('day6demo'),
                school='Day 6 Demo School'
            )
            db.session.add(demo_teacher)
            db.session.commit()
            
            # Create demo class
            demo_class = StudentClass(
                name='Year 11 Chemistry',
                description='IGCSE Chemistry class for Day 6 demo',
                teacher_id=demo_teacher.id
            )
            db.session.add(demo_class)
            db.session.commit()
            
            # Create demo students
            demo_students = [
                Student(name='Alex Chen', student_id='CHE001', class_id=demo_class.id),
                Student(name='Sarah Johnson', student_id='CHE002', class_id=demo_class.id),
                Student(name='Mohammed Ali', student_id='CHE003', class_id=demo_class.id),
                Student(name='Emma Wilson', student_id='CHE004', class_id=demo_class.id),
                Student(name='James Rodriguez', student_id='CHE005', class_id=demo_class.id)
            ]
            
            for student in demo_students:
                db.session.add(student)
            
            # Create demo assessment
            demo_assessment = Assessment(
                title='Bonding & Structure Assessment',
                description='Day 6 comprehensive assessment covering ionic and covalent bonding',
                topics=json.dumps(['2.4_ionic_bonding', '2.5_covalent_bonding', '2.6_metallic_bonding']),
                total_questions=10,
                teacher_id=demo_teacher.id,
                class_id=demo_class.id
            )
            db.session.add(demo_assessment)
            
            db.session.commit()
            print("✅ Day 6 demo data created successfully!")
        else:
            print("✅ Demo data already exists!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("💡 Try creating database manually or check file permissions")
        return False
    
    return True

if __name__ == '__main__':
    print("🧪 Day 6: IGCSE Chemistry Assessment Tool")
    print("🚀 Starting web application...")
    
    with app.app_context():
        if init_db():
            print("📱 Access at: http://localhost:5000")
            print("👤 Demo login: day6_teacher / day6demo")
            print("🎯 Main feature: http://localhost:5000/enhanced_input_results")
            
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("❌ Database setup failed. Try running without database features.")
            print("💡 You can still test the templates at http://localhost:5000")
            app.run(debug=True, host='0.0.0.0', port=5000)
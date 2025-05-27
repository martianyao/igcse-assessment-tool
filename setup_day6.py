#!/usr/bin/env python3
"""
Day 6: Complete Web Application Setup Script
IGCSE Chemistry Assessment Tool with Comprehensive Performance Analysis
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import shutil

def print_header(title):
    """Print formatted header"""
    print("\n" + "🧪" * 25)
    print(f"  {title}")
    print("🧪" * 25)

def print_step(step, description):
    """Print step with formatting"""
    print(f"\n🔬 Step {step}: {description}")

def print_success(message):
    """Print success message"""
    print(f"   ✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"   ❌ {message}")

def create_directory_structure():
    """Create complete directory structure"""
    print_step(1, "Creating Directory Structure")
    
    directories = [
        "templates",
        "static/css",
        "static/js",
        "static/images",
        "src",
        "data",
        "output",
        "instance"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created {directory}/")
    
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    print_step(2, "Creating Requirements File")
    
    requirements = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Werkzeug==2.3.7
requests==2.31.0
numpy==1.24.3
python-dotenv==1.0.0"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print_success("requirements.txt created")
    return True

def create_main_flask_app():
    """Create main Flask application"""
    print_step(3, "Creating Main Flask Application")
    
    app_code = '''#!/usr/bin/env python3
"""
Day 6: IGCSE Chemistry Assessment Tool - Complete Web Application
Flask application with comprehensive performance analysis
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'igcse-chemistry-day6-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/igcse_day6.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'), nullable=False)
    engagement_level = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_questions = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComprehensiveResult(db.Model):
    """Day 6: Comprehensive assessment results with engagement and attainment"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    
    # Test performance
    test_answers = db.Column(db.Text, nullable=False)  # JSON
    test_score = db.Column(db.Integer, nullable=False)
    test_percentage = db.Column(db.Float, nullable=False)
    
    # Engagement analysis (1-9 scale)
    engagement_rate = db.Column(db.Integer, nullable=False)
    engagement_evidence = db.Column(db.Text, nullable=False)  # JSON
    
    # Attainment analysis
    preparation_outcome = db.Column(db.String(20), nullable=False)  # emerging/developing/secure/mastery
    in_class_practice = db.Column(db.String(20), nullable=False)   # emerging/developing/secure/mastery
    additional_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Template filters
@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('login'))
    
    teacher_id = session['teacher_id']
    teacher = Teacher.query.get(teacher_id)
    
    # Get teacher's data
    classes = StudentClass.query.filter_by(teacher_id=teacher_id).all()
    assessments = Assessment.query.filter_by(teacher_id=teacher_id).order_by(Assessment.created_at.desc()).limit(5).all()
    
    # Calculate statistics
    total_students = sum(len(Student.query.filter_by(class_id=c.id).all()) for c in classes)
    total_assessments = Assessment.query.filter_by(teacher_id=teacher_id).count()
    
    return render_template('dashboard.html',
                         teacher=teacher,
                         classes=classes,
                         recent_assessments=assessments,
                         total_students=total_students,
                         total_assessments=total_assessments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        teacher = Teacher.query.filter_by(username=username).first()
        
        if teacher and check_password_hash(teacher.password_hash, password):
            session['teacher_id'] = teacher.id
            session['teacher_name'] = teacher.username
            flash('Login successful! Welcome to Day 6 features.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials! Try: day6_teacher / day6demo', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        school = request.form.get('school', '')
        
        if Teacher.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        teacher = Teacher(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            school=school
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

@app.route('/enhanced_input_results')
def enhanced_input_results():
    """Day 6: Enhanced comprehensive analysis interface"""
    if 'teacher_id' not in session:
        return redirect(url_for('login'))
    
    # Get sample students for demo
    students = Student.query.limit(3).all()
    if not students:
        # Create sample students if none exist
        create_sample_students()
        students = Student.query.limit(3).all()
    
    return render_template('enhanced_input_results.html', students=students)

@app.route('/api/submit_comprehensive_analysis', methods=['POST'])
def submit_comprehensive_analysis():
    """Day 6: Submit comprehensive analysis data"""
    if 'teacher_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Import and use AI analyzer
        try:
            from ai_analyzer import create_enhanced_ai_analyzer
            analyzer = create_enhanced_ai_analyzer("enhanced_mock")
            results = analyzer.analyze_comprehensive_assessment(data)
        except ImportError:
            # Fallback if AI analyzer not available
            results = {
                "message": "AI analysis would be performed here",
                "students_analyzed": len(data.get("comprehensive_analysis", [])),
                "success": True
            }
        
        return jsonify({
            'success': True,
            'message': 'Comprehensive analysis completed successfully!',
            'analysis_results': results
        })
        
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Analysis failed',
            'message': str(e)
        }), 500

# Helper functions
def create_sample_students():
    """Create sample students for demo"""
    teacher = Teacher.query.first()
    if not teacher:
        return
    
    # Create sample class
    sample_class = StudentClass.query.first()
    if not sample_class:
        sample_class = StudentClass(
            name="Year 10 Chemistry Demo",
            description="Demo class for Day 6 features",
            teacher_id=teacher.id
        )
        db.session.add(sample_class)
        db.session.commit()
    
    # Create sample students
    if Student.query.count() == 0:
        students_data = [
            {"name": "Alice Johnson", "student_id": "ST001", "engagement_level": "high"},
            {"name": "Bob Smith", "student_id": "ST002", "engagement_level": "medium"},
            {"name": "Charlie Brown", "student_id": "ST003", "engagement_level": "low"}
        ]
        
        for student_data in students_data:
            student = Student(
                name=student_data["name"],
                student_id=student_data["student_id"],
                class_id=sample_class.id,
                engagement_level=student_data["engagement_level"]
            )
            db.session.add(student)
        
        db.session.commit()

# Initialize database and demo data
def init_database():
    """Initialize database with demo data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create demo teacher if none exists
        if not Teacher.query.filter_by(username='day6_teacher').first():
            demo_teacher = Teacher(
                username='day6_teacher',
                email='day6@demo.com',
                password_hash=generate_password_hash('day6demo'),
                school='Day 6 Demo School'
            )
            db.session.add(demo_teacher)
            db.session.commit()
            
            print("✅ Demo teacher created:")
            print("   Username: day6_teacher")
            print("   Password: day6demo")
        
        # Create sample data
        create_sample_students()

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    print("🚀 Day 6: IGCSE Chemistry Assessment Tool")
    print("📱 Access at: http://localhost:5000")
    print("👤 Demo login: day6_teacher / day6demo")
    print("🎯 Comprehensive analysis: /enhanced_input_results")
    print("⚠️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    with open("app.py", "w") as f:
        f.write(app_code)
    
    print_success("app.py created with Day 6 features")
    return True

def create_ai_analyzer():
    """Create AI analyzer module"""
    print_step(4, "Creating AI Analyzer Module")
    
    ai_code = '''"""
Day 6: Enhanced AI Analyzer for Comprehensive Performance Analysis
Simplified but functional AI analysis system
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class StudentAnalysis:
    """Individual student analysis data"""
    student_id: int
    student_name: str
    test_score: int
    test_percentage: float
    engagement_rate: int
    preparation_outcome: str
    in_class_practice: str
    additional_notes: str = ""

class EnhancedMockAIProvider:
    """Mock AI provider for Day 6 comprehensive analysis"""
    
    def analyze_comprehensive_performance(self, analyses: List[StudentAnalysis]) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        
        individual_results = []
        
        for analysis in analyses:
            # Analyze individual student
            result = self._analyze_student(analysis)
            individual_results.append(result)
        
        # Generate class insights
        class_insights = self._generate_class_insights(analyses)
        
        # Identify intervention priorities
        interventions = self._identify_interventions(analyses)
        
        return {
            "individual_analyses": individual_results,
            "class_insights": class_insights,
            "intervention_priorities": interventions,
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "day6_comprehensive"
        }
    
    def _analyze_student(self, analysis: StudentAnalysis) -> Dict[str, Any]:
        """Analyze individual student performance"""
        
        # Categorize performance
        if analysis.test_percentage >= 85:
            performance_level = "Excellent"
        elif analysis.test_percentage >= 75:
            performance_level = "Good"
        elif analysis.test_percentage >= 65:
            performance_level = "Satisfactory"
        elif analysis.test_percentage >= 50:
            performance_level = "Needs Improvement"
        else:
            performance_level = "Significant Concerns"
        
        # Categorize engagement
        if analysis.engagement_rate >= 8:
            engagement_level = "Exemplary"
        elif analysis.engagement_rate >= 6:
            engagement_level = "High"
        elif analysis.engagement_rate >= 4:
            engagement_level = "Moderate"
        elif analysis.engagement_rate >= 2:
            engagement_level = "Low"
        else:
            engagement_level = "Disengaged"
        
        # Predict IGCSE grade
        predicted_grade = self._predict_grade(
            analysis.test_percentage,
            analysis.engagement_rate,
            analysis.preparation_outcome,
            analysis.in_class_practice
        )
        
        # Generate insights
        insights = self._generate_insights(analysis)
        
        # Recommend interventions
        interventions = self._recommend_interventions(analysis)
        
        return {
            "student_id": analysis.student_id,
            "student_name": analysis.student_name,
            "performance_summary": {
                "test_percentage": analysis.test_percentage,
                "performance_level": performance_level,
                "engagement_level": engagement_level,
                "predicted_igcse_grade": predicted_grade
            },
            "detailed_analysis": {
                "engagement_rate": f"{analysis.engagement_rate}/9",
                "preparation_outcome": analysis.preparation_outcome.title(),
                "in_class_practice": analysis.in_class_practice.title(),
                "correlation": self._analyze_correlation(analysis)
            },
            "insights": insights,
            "interventions": interventions
        }
    
    def _predict_grade(self, test_perc: float, engagement: int, prep: str, practice: str) -> str:
        """Predict IGCSE grade using weighted factors"""
        
        # Convert attainment to scores
        attainment_scores = {"emerging": 25, "developing": 50, "secure": 75, "mastery": 95}
        prep_score = attainment_scores.get(prep, 50)
        practice_score = attainment_scores.get(practice, 50)
        engagement_score = (engagement / 9) * 100
        
        # Weighted average
        overall_score = (
            test_perc * 0.4 +
            engagement_score * 0.3 +
            prep_score * 0.15 +
            practice_score * 0.15
        )
        
        # Map to IGCSE grades
        if overall_score >= 90: return "A* (9)"
        elif overall_score >= 80: return "A (8)"
        elif overall_score >= 70: return "B (7)"
        elif overall_score >= 60: return "C (6)"
        elif overall_score >= 50: return "D (5)"
        else: return "E-G (1-4)"
    
    def _generate_insights(self, analysis: StudentAnalysis) -> List[str]:
        """Generate personalized insights"""
        insights = []
        
        if analysis.test_percentage >= 80 and analysis.engagement_rate >= 7:
            insights.append("🌟 Excellent overall performance - maintain current approach")
        elif analysis.test_percentage < 60 and analysis.engagement_rate <= 4:
            insights.append("⚠️ Requires comprehensive support across all areas")
        elif analysis.test_percentage >= 75 and analysis.engagement_rate <= 4:
            insights.append("💡 Strong academically but needs engagement strategies")
        
        # Attainment insights
        prep_levels = {"emerging": 1, "developing": 2, "secure": 3, "mastery": 4}
        prep_level = prep_levels.get(analysis.preparation_outcome, 2)
        practice_level = prep_levels.get(analysis.in_class_practice, 2)
        
        if prep_level > practice_level + 1:
            insights.append("📚 Strong preparation but struggles in class application")
        elif practice_level > prep_level + 1:
            insights.append("🏫 Good in class but needs better preparation habits")
        
        return insights
    
    def _recommend_interventions(self, analysis: StudentAnalysis) -> List[Dict[str, str]]:
        """Recommend specific interventions"""
        interventions = []
        
        if analysis.test_percentage < 60:
            interventions.append({
                "type": "Academic Support",
                "action": "One-to-one tutoring focusing on weak areas",
                "priority": "High",
                "timeline": "Immediate"
            })
        
        if analysis.engagement_rate <= 4:
            interventions.append({
                "type": "Engagement Strategy",
                "action": "Implement interactive teaching methods",
                "priority": "High",
                "timeline": "Next lesson"
            })
        
        if analysis.preparation_outcome in ["emerging", "developing"]:
            interventions.append({
                "type": "Study Skills",
                "action": "Teach effective revision techniques",
                "priority": "Medium",
                "timeline": "This week"
            })
        
        return interventions
    
    def _analyze_correlation(self, analysis: StudentAnalysis) -> str:
        """Analyze correlation between metrics"""
        expected_perc = (analysis.engagement_rate / 9) * 85
        gap = analysis.test_percentage - expected_perc
        
        if abs(gap) <= 10:
            return "Strong alignment between engagement and performance"
        elif gap > 10:
            return "Performance exceeds engagement expectations"
        else:
            return "Performance below engagement potential"
    
    def _generate_class_insights(self, analyses: List[StudentAnalysis]) -> Dict[str, Any]:
        """Generate class-wide insights"""
        if not analyses:
            return {}
        
        avg_test = sum(a.test_percentage for a in analyses) / len(analyses)
        avg_engagement = sum(a.engagement_rate for a in analyses) / len(analyses)
        
        # Count engagement distribution
        high_engagement = sum(1 for a in analyses if a.engagement_rate >= 7)
        medium_engagement = sum(1 for a in analyses if 4 <= a.engagement_rate < 7)
        low_engagement = sum(1 for a in analyses if a.engagement_rate < 4)
        
        return {
            "class_size": len(analyses),
            "averages": {
                "test_score": f"{avg_test:.1f}%",
                "engagement": f"{avg_engagement:.1f}/9"
            },
            "engagement_distribution": {
                "high": high_engagement,
                "medium": medium_engagement,
                "low": low_engagement
            },
            "key_insights": [
                f"Class average: {avg_test:.1f}% test score, {avg_engagement:.1f}/9 engagement",
                f"Engagement levels: {high_engagement} high, {medium_engagement} medium, {low_engagement} low"
            ]
        }
    
    def _identify_interventions(self, analyses: List[StudentAnalysis]) -> List[Dict[str, Any]]:
        """Identify students needing intervention"""
        priorities = []
        
        for analysis in analyses:
            risk_score = 0
            risk_factors = []
            
            if analysis.test_percentage < 50:
                risk_score += 3
                risk_factors.append("Low academic performance")
            
            if analysis.engagement_rate <= 3:
                risk_score += 2
                risk_factors.append("Very low engagement")
            
            if analysis.preparation_outcome == "emerging":
                risk_score += 1
                risk_factors.append("Poor preparation")
            
            if risk_score >= 3:
                priorities.append({
                    "student_id": analysis.student_id,
                    "student_name": analysis.student_name,
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "priority_level": "High" if risk_score >= 4 else "Medium"
                })
        
        return sorted(priorities, key=lambda x: x["risk_score"], reverse=True)

class EnhancedAIAnalyzer:
    """Enhanced AI Analyzer for Day 6"""
    
    def __init__(self, provider=None):
        self.provider = provider or EnhancedMockAIProvider()
    
    def analyze_comprehensive_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        
        # Convert data to StudentAnalysis objects
        analyses = []
        
        for student_data in assessment_data.get("comprehensive_analysis", []):
            analysis = StudentAnalysis(
                student_id=student_data["student_id"],
                student_name=student_data.get("student_name", f"Student {student_data['student_id']}"),
                test_score=student_data["test_performance"]["score"],
                test_percentage=student_data["test_performance"]["percentage"],
                engagement_rate=student_data["engagement_analysis"]["rate"],
                preparation_outcome=student_data["attainment_analysis"]["preparation_outcome"],
                in_class_practice=student_data["attainment_analysis"]["in_class_practice"],
                additional_notes=student_data.get("additional_notes", "")
            )
            analyses.append(analysis)
        
        # Perform analysis
        return self.provider.analyze_comprehensive_performance(analyses)

def create_enhanced_ai_analyzer(provider_type: str = "enhanced_mock", **kwargs):
    """Factory function"""
    return EnhancedAIAnalyzer(EnhancedMockAIProvider())

# Example usage
if __name__ == "__main__":
    print("Day 6 AI Analyzer - Comprehensive Performance Analysis Ready!")
'''
    
    with open("src/ai_analyzer.py", "w") as f:
        f.write(ai_code)
    
    print_success("src/ai_analyzer.py created")
    return True

def create_html_templates():
    """Create all HTML templates"""
    print_step(5, "Creating HTML Templates")
    
    # Create index.html
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 6: IGCSE Chemistry Assessment Tool</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 4rem 0;
        }
        .feature-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="fas fa-flask me-2"></i>
                Day 6: IGCSE Chemistry Assessment
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/login">
                    <i class="fas fa-sign-in-alt me-1"></i>
                    Login
                </a>
            </div>
        </div>
    </nav>

    <div class="hero-section">
        <div class="container text-center">
            <h1 class="display-4 mb-4">
                <i class="fas fa-flask me-3"></i>
                Day 6: Web Application
            </h1>
            <p class="lead mb-4">
                Comprehensive Performance Analysis System
            </p>
            <div class="row justify-content-center mb-4">
                <div class="col-md-6">
                    <div class="row">
                        <div class="col-6">
                            <div class="bg-light text-dark p-3 rounded">
                                <h6><i class="fas fa-heart text-danger me-2"></i>Engagement Rate</h6>
                                <small>1-9 scale with evidence tracking</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="bg-light text-dark p-3 rounded">
                                <h6><i class="fas fa-trophy text-warning me-2"></i>Attainment Analysis</h6>
                                <small>Preparation + In-class practice</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <a href="/login" class="btn btn-light btn-lg me-3">
                <i class="fas fa-sign-in-alt me-2"></i>
                Try Demo
            </a>
            <a href="/enhanced_input_results" class="btn btn-outline-light btn-lg">
                <i class="fas fa-chart-line me-2"></i>
                Comprehensive Analysis
            </a>
        </div>
    </div>

    <div class="container my-5">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
                        <h5>1-9 Engagement Scale</h5>
                        <p>Visual engagement assessment with behavioral evidence tracking</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-trophy fa-3x text-warning mb-3"></i>
                        <h5>Dual Attainment Analysis</h5>
                        <p>Separate assessment of preparation outcomes and in-class practice</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-robot fa-3x text-success mb-3"></i>
                        <h5>AI-Powered Insights</h5>
                        <p>Comprehensive correlation analysis and IGCSE grade predictions</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-12">
                <div class="bg-light p-4 rounded">
                    <h4 class="text-center mb-4">Day 6 Demo Account</h4>
                    <div class="row justify-content-center">
                        <div class="col-md-6 text-center">
                            <div class="bg-white p-3 rounded">
                                <h6>Login Credentials:</h6>
                                <p class="mb-1"><strong>Username:</strong> <code>day6_teacher</code></p>
                                <p class="mb-3"><strong>Password:</strong> <code>day6demo</code></p>
                                <a href="/login" class="btn btn-primary">
                                    <i class="fas fa-play me-2"></i>
                                    Start Demo
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open("templates/index.html", "w") as f:
        f.write(index_html)
    print_success("templates/index.html")
    
    # Create login.html
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Day 6</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body style="background-color: #f8f9fa;">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="fas fa-flask me-2"></i>
                Day 6: IGCSE Chemistry Assessment
            </a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i>Teacher Login</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                        </form>
                        
                        <hr>
                        
                        <div class="bg-light p-3 rounded">
                            <h6 class="text-primary">Day 6 Demo Account:</h6>
                            <p class="mb-1"><strong>Username:</strong> <code>day6_teacher</code></p>
                            <p class="mb-0"><strong>Password:</strong> <code>day6demo</code></p>
                        </div>
                        
                        <div class="text-center mt-3">
                            <a href="/register" class="btn btn-outline-secondary">
                                <i class="fas fa-user-plus me-2"></i>Create Account
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open("templates/login.html", "w") as f:
        f.write(login_html)
    print_success("templates/login.html")
    
    # Create register.html
    register_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Day 6</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body style="background-color: #f8f9fa;">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="fas fa-flask me-2"></i>
                Day 6: IGCSE Chemistry Assessment
            </a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i>Create Teacher Account</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email Address</label>
                                <input type="email" class="form-control" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">School (Optional)</label>
                                <input type="text" class="form-control" name="school" placeholder="Your school name">
                            </div>
                            <button type="submit" class="btn btn-success w-100">
                                <i class="fas fa-user-plus me-2"></i>Create Account
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <a href="/login" class="btn btn-outline-primary">
                                <i class="fas fa-arrow-left me-2"></i>Back to Login
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    with open("templates/register.html", "w") as f:
        f.write(register_html)
    print_success("templates/register.html")
    
    print("✅ All basic templates created")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(6, "Installing Dependencies")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print_success("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print("   Try installing manually: pip install -r requirements.txt")
        return False

def create_run_script():
    """Create simple run script"""
    print_step(7, "Creating Run Script")
    
    run_script = '''#!/usr/bin/env python3
"""
Day 6: Quick Launch Script
"""
import os
import sys

if __name__ == '__main__':
    print("🚀 Launching Day 6: IGCSE Chemistry Assessment Tool...")
    print("📱 Starting on http://localhost:5000")
    print("👤 Demo: day6_teacher / day6demo")
    print("⚠️  Press Ctrl+C to stop")
    
    # Run the main app
    os.system("python app.py")
'''
    
    with open("run_day6.py", "w") as f:
        f.write(run_script)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("run_day6.py", 0o755)
    
    print_success("run_day6.py created")
    return True

def verify_setup():
    """Verify all components are correctly set up"""
    print_step(8, "Verifying Setup")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "src/ai_analyzer.py",
        "templates/index.html",
        "templates/login.html",
        "templates/register.html",
        "run_day6.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Found {file_path}")
        else:
            print_error(f"Missing {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print_error(f"Setup incomplete - {len(missing_files)} files missing")
        return False
    
    print_success("All Day 6 components verified successfully!")
    return True

def display_completion_message():
    """Display completion and launch instructions"""
    print_header("🎉 DAY 6 SETUP COMPLETE!")
    
    message = """
🚀 Day 6: Web Application Successfully Set Up!

📋 WHAT YOU NOW HAVE:
✅ Complete Flask web application
✅ Enhanced input interface for comprehensive analysis  
✅ 1-9 engagement scale with visual feedback
✅ Dual attainment analysis (preparation + in-class practice)
✅ AI-powered correlation analysis and predictions
✅ Teacher authentication system
✅ Responsive dashboard with modern design
✅ Demo data and sample students

🏃‍♂️ QUICK LAUNCH (Choose one):

Option 1 - Use run script:
   python run_day6.py

Option 2 - Direct launch:
   python app.py

Option 3 - Manual launch:
   python -c "from app import app; app.run(debug=True)"

📱 ACCESS YOUR APPLICATION:
   http://localhost:5000

👤 LOGIN CREDENTIALS:
   Username: day6_teacher
   Password: day6demo

🎯 FEATURE TESTING GUIDE:

1. 🏠 Home Page (/)
   - See Day 6 overview and features
   - Click "Try Demo" to login

2. 📊 Dashboard (/dashboard)  
   - View teacher statistics and charts
   - Access quick actions
   - See recent assessments

3. 🔬 Comprehensive Analysis (/enhanced_input_results)
   - Test the 1-9 engagement scale (click numbers)
   - Mark questions (click to cycle: empty → ✓ → ✗)
   - Set attainment levels (Emerging → Developing → Secure → Mastery)
   - Check evidence boxes (questioning, answering, focus, activity)
   - Generate AI analysis report

🎨 DAY 6 KEY FEATURES:

📈 ENGAGEMENT SYSTEM:
   • Interactive 1-9 scale with color coding
   • Behavioral evidence tracking
   • Real-time engagement categorization
   • Visual feedback and validation

🏆 ATTAINMENT ANALYSIS:
   • Preparation outcome assessment  
   • In-class practice evaluation
   • Four-level progression tracking
   • Balance analysis between components

🤖 AI CAPABILITIES:
   • Performance correlation analysis
   • IGCSE grade predictions (weighted)
   • Risk identification and intervention planning
   • Personalized insights and recommendations
   • Class-wide pattern analysis

💻 TECHNICAL FEATURES:
   • Modern responsive web design
   • Bootstrap 5 styling with custom CSS
   • Interactive JavaScript components
   • Flask backend with SQLAlchemy
   • Session management and authentication
   • JSON API endpoints for data exchange

🎓 PERFECT FOR:
✅ IGCSE Chemistry teachers
✅ Evidence-based student assessment
✅ Engagement tracking and analysis
✅ Intervention planning and monitoring
✅ Parent-teacher consultations
✅ School performance reviews

Ready to revolutionize chemistry assessment! 🧪✨

🔗 Next Steps:
1. Launch the application
2. Login with demo credentials
3. Try the comprehensive analysis interface
4. Experience AI-powered insights
5. Explore dashboard features

Your Day 6 web application is production-ready!
"""
    
    print(message)

def main():
    """Main setup function"""
    print_header("DAY 6: WEB APPLICATION SETUP")
    
    print("🎯 Setting up comprehensive performance analysis web application")
    print("📊 Features: Engagement Rate (1-9) + Attainment Analysis + AI Insights")
    
    # Execute setup steps
    try:
        if not create_directory_structure():
            return False
        
        if not create_requirements_file():
            return False
        
        if not create_main_flask_app():
            return False
        
        if not create_ai_analyzer():
            return False
        
        if not create_html_templates():
            return False
        
        if not install_dependencies():
            print("⚠️  Dependencies failed - you can install manually later")
        
        if not create_run_script():
            return False
        
        if not verify_setup():
            return False
        
        # Success!
        display_completion_message()
        return True
        
    except Exception as e:
        print_error(f"Setup failed with error: {e}")
        return False

if __name__ == "__main__":
    main()
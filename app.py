#!/usr/bin/env python3
"""
Day 6: IGCSE Chemistry Assessment Tool - Main Web Application
Flask app with comprehensive performance analysis and AI integration
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import random
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'day6-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///day6_assessment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Template filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if value is None:
        return {}
    try:
        return json.loads(value)
    except:
        return {}

# Database Models
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='teacher', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    class_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='student', lazy=True)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Day 6 comprehensive data
    engagement_rate = db.Column(db.Integer)  # 1-9 scale
    engagement_evidence = db.Column(db.Text)  # JSON: questioning, answering, focus, activity
    preparation_outcome = db.Column(db.String(20))  # emerging/developing/secure/mastery
    in_class_practice = db.Column(db.String(20))  # emerging/developing/secure/mastery
    
    # Quiz data
    quiz_answers = db.Column(db.Text)  # JSON: question_id -> correct/incorrect
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    score_percentage = db.Column(db.Float)
    
    # Additional notes
    notes = db.Column(db.Text)
    
    # AI analysis results
    ai_analysis = db.Column(db.Text)  # JSON: comprehensive analysis
    weak_topics = db.Column(db.Text)  # JSON: identified weak areas
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# AI Analysis Functions
def analyze_student_performance(assessment_data):
    """Generate comprehensive AI analysis based on assessment data"""
    
    # Extract data
    engagement_rate = assessment_data.get('engagement_rate', 5)
    quiz_score = assessment_data.get('score_percentage', 0)
    preparation = assessment_data.get('preparation_outcome', 'developing')
    practice = assessment_data.get('in_class_practice', 'developing')
    quiz_answers = assessment_data.get('quiz_answers', {})
    
    # Identify weak topics based on incorrect answers
    weak_topics = []
    topic_map = {
        '1': 'atomic_structure',
        '2': 'chemical_bonding',
        '3': 'stoichiometry',
        '4': 'reaction_kinetics',
        '5': 'equilibrium',
        '6': 'acids_bases',
        '7': 'redox_reactions',
        '8': 'organic_chemistry',
        '9': 'energy_changes',
        '10': 'periodic_table',
        '11': 'states_of_matter',
        '12': 'separation_techniques',
        '13': 'electrochemistry',
        '14': 'chemical_calculations',
        '15': 'environmental_chemistry'
    }
    
    for q_id, result in quiz_answers.items():
        if result == 'incorrect' and q_id in topic_map:
            weak_topics.append(topic_map[q_id])
    
    # Generate analysis
    analysis = {
        'overall_performance': 'excellent' if quiz_score >= 80 else 'good' if quiz_score >= 60 else 'needs_improvement',
        'engagement_level': 'high' if engagement_rate >= 7 else 'moderate' if engagement_rate >= 4 else 'low',
        'preparation_assessment': preparation,
        'practice_assessment': practice,
        'predicted_grade': predict_igcse_grade(quiz_score, engagement_rate, preparation, practice),
        'risk_level': 'low' if quiz_score >= 70 and engagement_rate >= 6 else 'medium' if quiz_score >= 50 else 'high',
        'strengths': identify_strengths(quiz_answers, engagement_rate),
        'weaknesses': weak_topics,
        'recommendations': generate_recommendations(weak_topics, engagement_rate, quiz_score),
        'intervention_needed': quiz_score < 60 or engagement_rate < 4,
        'parent_communication': quiz_score < 50 or engagement_rate < 3
    }
    
    return analysis

def predict_igcse_grade(score, engagement, preparation, practice):
    """Predict IGCSE grade based on multiple factors"""
    # Weight factors
    score_weight = 0.5
    engagement_weight = 0.2
    prep_weight = 0.15
    practice_weight = 0.15
    
    # Convert to numerical values
    level_map = {'emerging': 1, 'developing': 2, 'secure': 3, 'mastery': 4}
    prep_score = level_map.get(preparation, 2) * 25
    practice_score = level_map.get(practice, 2) * 25
    engagement_score = (engagement / 9) * 100
    
    # Calculate weighted score
    total_score = (score * score_weight + 
                  engagement_score * engagement_weight + 
                  prep_score * prep_weight + 
                  practice_score * practice_weight)
    
    # Map to IGCSE grades
    if total_score >= 85:
        return "Grade 8-9 (A*)"
    elif total_score >= 75:
        return "Grade 7 (A)"
    elif total_score >= 65:
        return "Grade 6 (B)"
    elif total_score >= 55:
        return "Grade 5 (C)"
    elif total_score >= 45:
        return "Grade 4 (D)"
    else:
        return "Grade 3 or below"

def identify_strengths(quiz_answers, engagement_rate):
    """Identify student strengths"""
    strengths = []
    
    # Check quiz performance
    correct_topics = []
    topic_map = {
        '1': 'Atomic structure understanding',
        '2': 'Chemical bonding concepts',
        '3': 'Stoichiometry calculations',
        '4': 'Reaction kinetics',
        '5': 'Equilibrium principles',
        '6': 'Acid-base chemistry',
        '7': 'Redox reactions',
        '8': 'Organic chemistry',
        '9': 'Energy changes',
        '10': 'Periodic trends',
        '11': 'States of matter',
        '12': 'Separation techniques',
        '13': 'Electrochemistry',
        '14': 'Chemical calculations',
        '15': 'Environmental chemistry'
    }
    
    for q_id, result in quiz_answers.items():
        if result == 'correct' and q_id in topic_map:
            correct_topics.append(topic_map[q_id])
    
    if len(correct_topics) >= 3:
        strengths.extend(correct_topics[:3])
    
    # Check engagement
    if engagement_rate >= 7:
        strengths.append("Excellent classroom engagement")
    if engagement_rate >= 5:
        strengths.append("Good participation in activities")
    
    return strengths

def generate_recommendations(weak_topics, engagement_rate, score):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Topic-specific recommendations
    topic_recommendations = {
        'chemical_bonding': "Focus on understanding ionic vs covalent bonding differences",
        'stoichiometry': "Practice more mole calculations and balancing equations",
        'reaction_kinetics': "Review rate laws and factors affecting reaction rates",
        'equilibrium': "Study Le Chatelier's principle and equilibrium calculations",
        'acids_bases': "Practice pH calculations and acid-base titrations",
        'redox_reactions': "Review oxidation numbers and balancing redox equations",
        'organic_chemistry': "Learn functional groups and naming conventions",
        'atomic_structure': "Review electron configuration and periodic trends",
        'energy_changes': "Practice enthalpy calculations and Hess's law",
        'periodic_table': "Study periodic trends and element properties",
        'states_of_matter': "Review particle theory and phase changes",
        'separation_techniques': "Practice identifying appropriate separation methods",
        'electrochemistry': "Study electrolysis and electrode reactions",
        'chemical_calculations': "Practice empirical formula and yield calculations",
        'environmental_chemistry': "Review greenhouse gases and pollution effects"
    }
    
    for topic in weak_topics[:3]:  # Top 3 weak areas
        if topic in topic_recommendations:
            recommendations.append(topic_recommendations[topic])
    
    # Engagement recommendations
    if engagement_rate < 4:
        recommendations.append("Increase classroom participation and ask more questions")
    elif engagement_rate < 7:
        recommendations.append("Continue active participation in class discussions")
    
    # Score-based recommendations
    if score < 50:
        recommendations.append("Schedule extra help sessions with teacher")
        recommendations.append("Complete additional practice problems daily")
    elif score < 70:
        recommendations.append("Focus on weak topics with targeted practice")
    
    return recommendations

def generate_quiz_questions():
    """Generate a comprehensive 15-question chemistry quiz"""
    questions = [
        {
            'id': 1,
            'topic': 'atomic_structure',
            'question': 'What is the maximum number of electrons that can occupy the third electron shell?',
            'options': ['8', '18', '32', '2'],
            'correct': '18',
            'explanation': 'The third shell can hold a maximum of 2n² = 2(3)² = 18 electrons.'
        },
        {
            'id': 2,
            'topic': 'chemical_bonding',
            'question': 'Which type of bonding involves the sharing of electrons between atoms?',
            'options': ['Ionic bonding', 'Covalent bonding', 'Metallic bonding', 'Hydrogen bonding'],
            'correct': 'Covalent bonding',
            'explanation': 'Covalent bonding occurs when atoms share electrons to achieve stable electron configurations.'
        },
        {
            'id': 3,
            'topic': 'stoichiometry',
            'question': 'How many moles are in 88g of CO₂? (C=12, O=16)',
            'options': ['1.0 mol', '2.0 mol', '3.0 mol', '4.0 mol'],
            'correct': '2.0 mol',
            'explanation': 'Molar mass of CO₂ = 12 + (16×2) = 44 g/mol. Number of moles = 88g ÷ 44 g/mol = 2.0 mol'
        },
        {
            'id': 4,
            'topic': 'reaction_kinetics',
            'question': 'Which factor does NOT affect the rate of a chemical reaction?',
            'options': ['Temperature', 'Concentration', 'Catalyst', 'Color of reactants'],
            'correct': 'Color of reactants',
            'explanation': 'Color is a physical property that does not affect reaction rate. Temperature, concentration, and catalysts all affect reaction rates.'
        },
        {
            'id': 5,
            'topic': 'equilibrium',
            'question': 'In the reaction N₂ + 3H₂ ⇌ 2NH₃, what happens when pressure is increased?',
            'options': ['Shifts left', 'Shifts right', 'No change', 'Reaction stops'],
            'correct': 'Shifts right',
            'explanation': 'Increasing pressure favors the side with fewer moles of gas (4 moles → 2 moles), shifting equilibrium right.'
        },
        {
            'id': 6,
            'topic': 'acids_bases',
            'question': 'What is the pH of a 0.001 M HCl solution?',
            'options': ['1', '2', '3', '4'],
            'correct': '3',
            'explanation': 'pH = -log[H⁺] = -log(0.001) = -log(10⁻³) = 3'
        },
        {
            'id': 7,
            'topic': 'redox_reactions',
            'question': 'In a redox reaction, the substance that loses electrons is:',
            'options': ['Reduced', 'Oxidized', 'Neutralized', 'Catalyzed'],
            'correct': 'Oxidized',
            'explanation': 'Oxidation is the loss of electrons. Remember: OIL RIG (Oxidation Is Loss, Reduction Is Gain)'
        },
        {
            'id': 8,
            'topic': 'organic_chemistry',
            'question': 'What is the functional group in CH₃CH₂OH?',
            'options': ['Alkene', 'Alcohol', 'Aldehyde', 'Carboxylic acid'],
            'correct': 'Alcohol',
            'explanation': 'The -OH group attached to a carbon chain indicates an alcohol functional group.'
        },
        {
            'id': 9,
            'topic': 'energy_changes',
            'question': 'Which type of reaction releases heat to the surroundings?',
            'options': ['Endothermic', 'Exothermic', 'Isothermic', 'Adiabatic'],
            'correct': 'Exothermic',
            'explanation': 'Exothermic reactions release heat energy to the surroundings, making them feel warm.'
        },
        {
            'id': 10,
            'topic': 'periodic_table',
            'question': 'Which element is in Group 7 (halogens)?',
            'options': ['Sodium', 'Oxygen', 'Chlorine', 'Argon'],
            'correct': 'Chlorine',
            'explanation': 'Chlorine is a halogen in Group 7 of the periodic table.'
        },
        {
            'id': 11,
            'topic': 'states_of_matter',
            'question': 'Which state of matter has particles that vibrate in fixed positions?',
            'options': ['Solid', 'Liquid', 'Gas', 'Plasma'],
            'correct': 'Solid',
            'explanation': 'In solids, particles are closely packed and vibrate in fixed positions.'
        },
        {
            'id': 12,
            'topic': 'separation_techniques',
            'question': 'Which technique is best for separating salt from seawater?',
            'options': ['Filtration', 'Distillation', 'Chromatography', 'Magnetism'],
            'correct': 'Distillation',
            'explanation': 'Distillation separates substances based on different boiling points, perfect for salt and water.'
        },
        {
            'id': 13,
            'topic': 'electrochemistry',
            'question': 'At which electrode does reduction occur in electrolysis?',
            'options': ['Anode', 'Cathode', 'Both', 'Neither'],
            'correct': 'Cathode',
            'explanation': 'Reduction (gain of electrons) always occurs at the cathode in electrolysis.'
        },
        {
            'id': 14,
            'topic': 'chemical_calculations',
            'question': 'What is the empirical formula of a compound with 40% carbon, 6.7% hydrogen, and 53.3% oxygen by mass?',
            'options': ['CHO', 'CH₂O', 'C₂H₄O', 'CH₃O'],
            'correct': 'CH₂O',
            'explanation': 'Converting percentages to moles gives a 1:2:1 ratio of C:H:O, giving empirical formula CH₂O.'
        },
        {
            'id': 15,
            'topic': 'environmental_chemistry',
            'question': 'Which gas is the main contributor to acid rain?',
            'options': ['CO₂', 'SO₂', 'N₂', 'O₂'],
            'correct': 'SO₂',
            'explanation': 'Sulfur dioxide (SO₂) reacts with water in the atmosphere to form sulfuric acid, causing acid rain.'
        }
    ]
    
    return questions

def generate_personalized_questions(weak_topics, num_questions=10):
    """Generate personalized practice questions based on weak areas"""
    
    # Question bank organized by topic
    question_bank = {
        'chemical_bonding': [
            {
                'question': 'Which type of bonding occurs between sodium and chlorine?',
                'options': ['A) Covalent bonding', 'B) Ionic bonding', 'C) Metallic bonding', 'D) Hydrogen bonding'],
                'correct': 'B',
                'explanation': 'Ionic bonding occurs between metals (Na) and non-metals (Cl) through electron transfer.'
            },
            {
                'question': 'What is the electron configuration of a chloride ion (Cl⁻)?',
                'options': ['A) 2,8,7', 'B) 2,8,8', 'C) 2,8,6', 'D) 2,8,1'],
                'correct': 'B',
                'explanation': 'Chlorine gains one electron to achieve a stable octet configuration.'
            }
        ],
        'stoichiometry': [
            {
                'question': 'How many moles are in 44g of CO₂? (C=12, O=16)',
                'options': ['A) 0.5 mol', 'B) 1.0 mol', 'C) 1.5 mol', 'D) 2.0 mol'],
                'correct': 'B',
                'explanation': 'Molar mass of CO₂ = 12 + (16×2) = 44 g/mol. 44g ÷ 44 g/mol = 1 mol'
            },
            {
                'question': 'Balance: __Fe + __O₂ → __Fe₂O₃',
                'options': ['A) 2,3,1', 'B) 4,3,2', 'C) 1,1,1', 'D) 3,2,1'],
                'correct': 'B',
                'explanation': '4Fe + 3O₂ → 2Fe₂O₃ balances all atoms on both sides.'
            }
        ],
        'reaction_kinetics': [
            {
                'question': 'Which factor does NOT affect reaction rate?',
                'options': ['A) Temperature', 'B) Concentration', 'C) Catalyst', 'D) Product amount'],
                'correct': 'D',
                'explanation': 'Product amount does not affect forward reaction rate, only reactant concentration does.'
            },
            {
                'question': 'What happens to reaction rate when temperature increases by 10°C?',
                'options': ['A) Stays same', 'B) Doubles approximately', 'C) Halves', 'D) Triples'],
                'correct': 'B',
                'explanation': 'The general rule is that reaction rate doubles for every 10°C temperature increase.'
            }
        ],
        'equilibrium': [
            {
                'question': 'For N₂ + 3H₂ ⇌ 2NH₃ + heat, what increases NH₃ yield?',
                'options': ['A) Increase temperature', 'B) Decrease pressure', 'C) Increase pressure', 'D) Remove N₂'],
                'correct': 'C',
                'explanation': 'Increasing pressure favors the side with fewer moles of gas (4 → 2).'
            },
            {
                'question': 'What is the equilibrium constant expression for 2SO₂ + O₂ ⇌ 2SO₃?',
                'options': ['A) [SO₃]²/[SO₂]²[O₂]', 'B) [SO₂]²[O₂]/[SO₃]²', 'C) [SO₃]/[SO₂][O₂]', 'D) [SO₃]²/[SO₂][O₂]'],
                'correct': 'A',
                'explanation': 'K = [products]/[reactants] with coefficients as exponents.'
            }
        ],
        'acids_bases': [
            {
                'question': 'What is the pH of 0.001 M HCl solution?',
                'options': ['A) 1', 'B) 2', 'C) 3', 'D) 4'],
                'correct': 'C',
                'explanation': 'pH = -log[H⁺] = -log(0.001) = -log(10⁻³) = 3'
            },
            {
                'question': 'Which is a strong base?',
                'options': ['A) NH₃', 'B) NaOH', 'C) Al(OH)₃', 'D) Cu(OH)₂'],
                'correct': 'B',
                'explanation': 'NaOH is a strong base that completely dissociates in water.'
            }
        ],
        'redox_reactions': [
            {
                'question': 'What is the oxidation state of Mn in KMnO₄?',
                'options': ['A) +4', 'B) +5', 'C) +6', 'D) +7'],
                'correct': 'D',
                'explanation': 'K(+1) + Mn(x) + 4O(-2) = 0, so x = +7'
            },
            {
                'question': 'In the reaction Zn + Cu²⁺ → Zn²⁺ + Cu, what is oxidized?',
                'options': ['A) Zn', 'B) Cu²⁺', 'C) Zn²⁺', 'D) Cu'],
                'correct': 'A',
                'explanation': 'Zn loses electrons (0 → +2) so it is oxidized.'
            }
        ],
        'organic_chemistry': [
            {
                'question': 'What is the functional group in CH₃CH₂OH?',
                'options': ['A) Alkene', 'B) Alcohol', 'C) Aldehyde', 'D) Carboxylic acid'],
                'correct': 'B',
                'explanation': 'The -OH group indicates an alcohol functional group.'
            },
            {
                'question': 'Name the compound CH₃CH₂CH₂CH₃',
                'options': ['A) Propane', 'B) Butane', 'C) Pentane', 'D) Hexane'],
                'correct': 'B',
                'explanation': 'Four carbon atoms in a straight chain = butane.'
            }
        ],
        'atomic_structure': [
            {
                'question': 'How many electrons can the third shell hold maximum?',
                'options': ['A) 2', 'B) 8', 'C) 18', 'D) 32'],
                'correct': 'C',
                'explanation': 'Third shell can hold 2n² = 2(3)² = 18 electrons maximum.'
            },
            {
                'question': 'Which element has electron configuration 2,8,7?',
                'options': ['A) Nitrogen', 'B) Oxygen', 'C) Fluorine', 'D) Chlorine'],
                'correct': 'D',
                'explanation': 'Chlorine (atomic number 17) has configuration 2,8,7.'
            }
        ],
        'energy_changes': [
            {
                'question': 'Which reaction is exothermic?',
                'options': ['A) Photosynthesis', 'B) Combustion', 'C) Thermal decomposition', 'D) Electrolysis'],
                'correct': 'B',
                'explanation': 'Combustion releases heat energy, making it exothermic.'
            },
            {
                'question': 'What is the unit of enthalpy change?',
                'options': ['A) J/mol', 'B) kJ/mol', 'C) kJ/g', 'D) J/K'],
                'correct': 'B',
                'explanation': 'Enthalpy change is measured in kilojoules per mole (kJ/mol).'
            }
        ],
        'periodic_table': [
            {
                'question': 'Which element is most reactive?',
                'options': ['A) Lithium', 'B) Sodium', 'C) Potassium', 'D) Cesium'],
                'correct': 'D',
                'explanation': 'Reactivity increases down Group 1, making cesium most reactive.'
            },
            {
                'question': 'Which has the largest atomic radius?',
                'options': ['A) F', 'B) Cl', 'C) Br', 'D) I'],
                'correct': 'D',
                'explanation': 'Atomic radius increases down a group due to more electron shells.'
            }
        ],
        'states_of_matter': [
            {
                'question': 'In which state do particles have the most kinetic energy?',
                'options': ['A) Solid', 'B) Liquid', 'C) Gas', 'D) All equal'],
                'correct': 'C',
                'explanation': 'Gas particles move fastest and have the highest kinetic energy.'
            },
            {
                'question': 'What happens during sublimation?',
                'options': ['A) Solid to liquid', 'B) Liquid to gas', 'C) Solid to gas', 'D) Gas to liquid'],
                'correct': 'C',
                'explanation': 'Sublimation is the direct transition from solid to gas.'
            }
        ],
        'separation_techniques': [
            {
                'question': 'Which method separates based on different boiling points?',
                'options': ['A) Filtration', 'B) Distillation', 'C) Chromatography', 'D) Crystallization'],
                'correct': 'B',
                'explanation': 'Distillation separates liquids with different boiling points.'
            },
            {
                'question': 'What technique separates insoluble solids from liquids?',
                'options': ['A) Filtration', 'B) Evaporation', 'C) Distillation', 'D) Chromatography'],
                'correct': 'A',
                'explanation': 'Filtration uses a barrier to separate insoluble solids from liquids.'
            }
        ],
        'electrochemistry': [
            {
                'question': 'During electrolysis, positive ions move to the:',
                'options': ['A) Anode', 'B) Cathode', 'C) Both', 'D) Neither'],
                'correct': 'B',
                'explanation': 'Positive ions (cations) are attracted to the negative cathode.'
            },
            {
                'question': 'What happens at the anode during electrolysis?',
                'options': ['A) Reduction', 'B) Oxidation', 'C) Neutralization', 'D) Condensation'],
                'correct': 'B',
                'explanation': 'Oxidation (loss of electrons) occurs at the anode.'
            }
        ],
        'chemical_calculations': [
            {
                'question': 'What is the percentage yield if 20g product is obtained from theoretical 25g?',
                'options': ['A) 60%', 'B) 70%', 'C) 80%', 'D) 90%'],
                'correct': 'C',
                'explanation': 'Percentage yield = (actual/theoretical) × 100 = (20/25) × 100 = 80%'
            },
            {
                'question': 'How many atoms are in 2 moles of helium?',
                'options': ['A) 6.02 × 10²³', 'B) 1.20 × 10²⁴', 'C) 3.01 × 10²³', 'D) 2.41 × 10²⁴'],
                'correct': 'B',
                'explanation': '2 moles × 6.02 × 10²³ atoms/mol = 1.20 × 10²⁴ atoms'
            }
        ],
        'environmental_chemistry': [
            {
                'question': 'Which gas is the main greenhouse gas from human activities?',
                'options': ['A) O₂', 'B) N₂', 'C) CO₂', 'D) H₂'],
                'correct': 'C',
                'explanation': 'Carbon dioxide (CO₂) is the primary greenhouse gas from burning fossil fuels.'
            },
            {
                'question': 'What causes ozone layer depletion?',
                'options': ['A) CO₂', 'B) SO₂', 'C) CFCs', 'D) CH₄'],
                'correct': 'C',
                'explanation': 'Chlorofluorocarbons (CFCs) break down ozone in the stratosphere.'
            }
        ]
    }
    
    # Select questions based on weak topics
    selected_questions = []
    
    # Prioritize weak topics
    if weak_topics:
        questions_per_topic = max(2, num_questions // len(weak_topics))
        
        for topic in weak_topics:
            if topic in question_bank:
                available = question_bank[topic]
                num_to_select = min(questions_per_topic, len(available))
                selected = random.sample(available, num_to_select)
                # Add topic to each selected question
                for q in selected:
                    q_copy = q.copy()  # Make a copy to avoid modifying the original
                    q_copy['topic'] = topic
                    selected_questions.append(q_copy)
    
    # Fill remaining with random questions
    all_topics = list(question_bank.keys())
    while len(selected_questions) < num_questions:
        random_topic = random.choice(all_topics)
        if question_bank[random_topic]:
            question = random.choice(question_bank[random_topic])
            # Check if this question is already selected
            already_selected = False
            for sq in selected_questions:
                if sq.get('question') == question.get('question'):
                    already_selected = True
                    break
            
            if not already_selected:
                q_copy = question.copy()  # Make a copy
                q_copy['topic'] = random_topic
                selected_questions.append(q_copy)
    
    # Number the questions and ensure all have topics
    for i, q in enumerate(selected_questions[:num_questions], 1):
        q['number'] = i
        # If topic is not set (from weak_topics section), try to identify it
        if 'topic' not in q:
            # Try to identify topic based on question content
            for topic, questions in question_bank.items():
                if q in questions:
                    q['topic'] = topic
                    break
            # If still no topic found, set a default
            if 'topic' not in q:
                q['topic'] = 'general_chemistry'
    
    return selected_questions[:num_questions]

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Teacher login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        teacher = Teacher.query.filter_by(username=username).first()
        
        if teacher and check_password_hash(teacher.password_hash, password):
            session['teacher_id'] = teacher.id
            session['username'] = teacher.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Teacher registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if Teacher.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        else:
            teacher = Teacher(
                username=username,
                password_hash=generate_password_hash(password)
            )
            db.session.add(teacher)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Teacher dashboard"""
    # Get recent assessments
    recent_assessments = Assessment.query.filter_by(teacher_id=session['teacher_id']).order_by(Assessment.created_at.desc()).limit(10).all()
    
    # Get student list
    students = Student.query.all()
    
    return render_template('dashboard.html', 
                         assessments=recent_assessments, 
                         students=students)

@app.route('/enhanced_input_results')
@login_required
def enhanced_input_results():
    """Day 6 comprehensive assessment interface"""
    students = Student.query.all()
    return render_template('enhanced_input_results.html', students=students)

@app.route('/quiz_paper')
@login_required
def quiz_paper():
    """Display the 15-question chemistry quiz"""
    questions = generate_quiz_questions()
    return render_template('quiz_paper.html', questions=questions)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student to the database"""
    if request.method == 'POST':
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        class_name = request.form.get('class_name')
        
        # Check if student ID already exists
        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already exists!', 'error')
        else:
            # Add new student
            student = Student(
                name=name,
                student_id=student_id,
                class_name=class_name
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('add_student.html')

@app.route('/api/submit_comprehensive_assessment', methods=['POST'])
@login_required
def submit_comprehensive_assessment():
    """Submit comprehensive assessment data and generate analysis"""
    try:
        data = request.json
        
        # Extract all assessment data
        student_id = data.get('student_id')
        engagement_rate = data.get('engagement_rate', 5)
        engagement_evidence = json.dumps(data.get('engagement_evidence', {}))
        preparation_outcome = data.get('preparation_outcome', 'developing')
        in_class_practice = data.get('in_class_practice', 'developing')
        quiz_answers = data.get('quiz_answers', {})
        notes = data.get('notes', '')
        
        # Calculate quiz score
        correct_count = sum(1 for answer in quiz_answers.values() if answer == 'correct')
        total_questions = len(quiz_answers)
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Prepare assessment data for analysis
        assessment_data = {
            'engagement_rate': engagement_rate,
            'score_percentage': score_percentage,
            'preparation_outcome': preparation_outcome,
            'in_class_practice': in_class_practice,
            'quiz_answers': quiz_answers
        }
        
        # Generate AI analysis
        analysis = analyze_student_performance(assessment_data)
        
        # Create new assessment record
        assessment = Assessment(
            student_id=student_id,
            teacher_id=session['teacher_id'],
            engagement_rate=engagement_rate,
            engagement_evidence=engagement_evidence,
            preparation_outcome=preparation_outcome,
            in_class_practice=in_class_practice,
            quiz_answers=json.dumps(quiz_answers),
            total_questions=total_questions,
            correct_answers=correct_count,
            score_percentage=score_percentage,
            notes=notes,
            ai_analysis=json.dumps(analysis),
            weak_topics=json.dumps(analysis.get('weaknesses', []))
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        # Return success with redirect to personalized report
        return jsonify({
            'success': True,
            'assessment_id': assessment.id,
            'redirect_url': url_for('personalized_report', assessment_id=assessment.id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/personalized_report/<int:assessment_id>')
@login_required
def personalized_report(assessment_id):
    """Show personalized analysis report based on specific assessment"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Check permission
    if assessment.teacher_id != session['teacher_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse JSON data
    ai_analysis = json.loads(assessment.ai_analysis) if assessment.ai_analysis else {}
    weak_topics = json.loads(assessment.weak_topics) if assessment.weak_topics else []
    quiz_answers = json.loads(assessment.quiz_answers) if assessment.quiz_answers else {}
    engagement_evidence = json.loads(assessment.engagement_evidence) if assessment.engagement_evidence else {}
    
    return render_template('personalized_report.html',
                         assessment=assessment,
                         student=assessment.student,
                         ai_analysis=ai_analysis,
                         weak_topics=weak_topics,
                         quiz_answers=quiz_answers,
                         engagement_evidence=engagement_evidence)

@app.route('/generate_personalized_practice/<int:assessment_id>')
@login_required
def generate_personalized_practice(assessment_id):
    """Generate personalized practice paper based on assessment analysis"""
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Check permission
    if assessment.teacher_id != session['teacher_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Get weak topics
    weak_topics = json.loads(assessment.weak_topics) if assessment.weak_topics else []
    
    # Generate personalized questions
    questions = generate_personalized_questions(weak_topics, num_questions=10)
    
    return render_template('personalized_practice.html',
                         assessment=assessment,
                         student=assessment.student,
                         questions=questions,
                         weak_topics=weak_topics)

@app.route('/api/quick_demo_data')
@login_required
def quick_demo_data():
    """Provide quick demo data for testing"""
    # Get first student if exists
    first_student = Student.query.first()
    
    demo_data = {
        'student_name': first_student.name if first_student else 'Demo Student',
        'student_id': first_student.id if first_student else 1,
        'quiz_answers': {
            '1': 'correct',
            '2': 'incorrect',
            '3': 'correct',
            '4': 'incorrect',
            '5': 'correct',
            '6': 'correct',
            '7': 'incorrect',
            '8': 'correct',
            '9': 'correct',
            '10': 'incorrect',
            '11': 'correct',
            '12': 'correct',
            '13': 'incorrect',
            '14': 'correct',
            '15': 'incorrect'
        },
        'engagement_rate': 7,
        'engagement_evidence': {
            'questioning': True,
            'answering': True,
            'focus': True,
            'activity': False
        },
        'preparation_outcome': 'secure',
        'in_class_practice': 'developing'
    }
    
    return jsonify(demo_data)

@app.route('/api/students')
@login_required
def get_students():
    """Get all students"""
    students = Student.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'student_id': s.student_id,
        'class_name': s.class_name
    } for s in students])

# Initialize database
def init_db():
    """Initialize database with demo data"""
    db.create_all()
    
    # Create demo teacher if not exists
    if not Teacher.query.filter_by(username='day6_teacher').first():
        demo_teacher = Teacher(
            username='day6_teacher',
            password_hash=generate_password_hash('day6demo')
        )
        db.session.add(demo_teacher)
    
    # Create demo students if not exist
    if not Student.query.first():
        demo_students = [
            Student(name='Alice Johnson', student_id='ST001', class_name='11A'),
            Student(name='Bob Smith', student_id='ST002', class_name='11A'),
            Student(name='Carol Williams', student_id='ST003', class_name='11B'),
            Student(name='David Brown', student_id='ST004', class_name='11B'),
            Student(name='Emma Davis', student_id='ST005', class_name='11A')
        ]
        for student in demo_students:
            db.session.add(student)
    
    db.session.commit()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Internal server error'), 500

# Main execution
if __name__ == '__main__':
    print("⚠️ AI analyzer not available - some features will be limited")
    print("\n🧪 Day 6: IGCSE Chemistry Assessment Tool")
    print("🚀 Starting web application...")
    
    with app.app_context():
        db.create_all()
        init_db()
        print("✅ Database tables created successfully!")
        print("✅ Demo data created!")
    
    print("\n📱 Access at: http://localhost:5000")
    print("👤 Demo login: day6_teacher / day6demo")
    print("🔥 Day 6 Features: Engagement (1-9) + Attainment + AI Analysis")
    print("📊 New: Personalized reports and practice generation!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
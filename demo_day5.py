#!/usr/bin/env python3
"""
Day 5 Demo Script - IGCSE Assessment Tool with AI
Demonstrates AI-powered question generation, analysis, and personalized learning
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_analyzer import AIAnalyzer, create_ai_provider, MockAIProvider
from src.mapping import TopicMapper
from src.paper_generator import PaperGenerator, PaperConfig


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_status(message, emoji="✅"):
    """Print status message with emoji"""
    print(f"{emoji} {message}")


def demo_ai_question_generation(analyzer):
    """Demonstrate AI question generation"""
    print_header("AI QUESTION GENERATION")
    
    print("📝 Generating questions for selected topics...")
    selected_topics = [
        "1.1_solids_liquids_gases",
        "1.2_changes_of_state", 
        "1.3_kinetic_particle_theory"
    ]
    
    print(f"Topics: {', '.join(selected_topics)}")
    
    # Generate questions
    questions = analyzer.generate_questions_batch(selected_topics, questions_per_topic=3)
    
    print_status(f"Generated {len(questions)} AI questions!")
    
    # Show sample questions
    if questions:
        print("\n📋 Sample Generated Questions:")
        for i, q in enumerate(questions[:2], 1):
            print(f"\n{i}. Topic: {q['topic_id'].replace('_', ' ').title()}")
            print(f"   Question: {q['question']}")
            print(f"   A) {q['options'][0] if isinstance(q['options'], list) else q['options'].get('A', 'Option A')}")
            print(f"   Correct Answer: {q['correct_answer']}")
            print(f"   Difficulty: {q.get('difficulty', 'medium')}")
    
    # Export questions
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    export_path = analyzer.export_ai_questions(str(output_dir / "ai_generated_questions.json"))
    print_status(f"Exported all AI questions to: {export_path}", "💾")
    
    return questions


def demo_performance_analysis(analyzer):
    """Demonstrate AI performance analysis"""
    print_header("AI PERFORMANCE ANALYSIS")
    
    print("📊 Simulating student assessment results...")
    
    # Create mock student results
    student_results = {
        "Q1": True,  # 1.1_solids_liquids_gases
        "Q2": True,  # 1.1_solids_liquids_gases  
        "Q3": False, # 1.1_solids_liquids_gases
        "Q4": False, # 1.2_changes_of_state
        "Q5": False, # 1.2_changes_of_state
        "Q6": True,  # 1.3_kinetic_particle_theory
        "Q7": True,  # 1.3_kinetic_particle_theory
        "Q8": True,  # 2.4_ionic_bonding
        "Q9": False, # 2.4_ionic_bonding
        "Q10": True  # 2.5_covalent_bonding
    }
    
    # Create mock question mappings
    class MockQuestion:
        def __init__(self, topic_id):
            self.topic_id = topic_id
    
    question_mappings = {
        "Q1": MockQuestion("1.1_solids_liquids_gases"),
        "Q2": MockQuestion("1.1_solids_liquids_gases"), 
        "Q3": MockQuestion("1.1_solids_liquids_gases"),
        "Q4": MockQuestion("1.2_changes_of_state"),
        "Q5": MockQuestion("1.2_changes_of_state"),
        "Q6": MockQuestion("1.3_kinetic_particle_theory"),
        "Q7": MockQuestion("1.3_kinetic_particle_theory"),
        "Q8": MockQuestion("2.4_ionic_bonding"),
        "Q9": MockQuestion("2.4_ionic_bonding"),
        "Q10": MockQuestion("2.5_covalent_bonding")
    }
    
    # Analyze performance
    try:
        analysis = analyzer.analyze_student_performance(student_results, question_mappings)
        
        # Display topic performance
        print("📈 Topic Performance Summary:")
        if "topic_performance" in analysis:
            for topic, perf in analysis["topic_performance"].items():
                success_rate = int(perf["success_rate"] * 100)
                print(f"  • {topic}: {success_rate}% ({perf['correct']}/{perf['total']})")
        
        # Display AI analysis
        print("\n🤖 AI Analysis:")
        if "ai_analysis" in analysis:
            # Handle both string and dict formats
            ai_content = analysis["ai_analysis"]
            if isinstance(ai_content, dict):
                ai_content = ai_content.get("content", str(ai_content))
            
            # Truncate long analysis for demo
            if len(ai_content) > 300:
                ai_content = ai_content[:300] + "..."
            print(ai_content)
        
        # Identify weak topics
        weak_topics = analysis.get("weak_topics", [])
        if weak_topics:
            print(f"\n⚠️  Topics needing attention: {', '.join(weak_topics)}")
        
        return weak_topics, analysis
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        print("Make sure all Day 3/4 components are properly set up.")
        return [], {}


def demo_study_plan_generation(analyzer, weak_topics):
    """Demonstrate AI study plan generation"""
    print_header("AI STUDY PLAN GENERATION")
    
    if not weak_topics:
        weak_topics = ["1.2_changes_of_state", "2.4_ionic_bonding"]  # Fallback for demo
        print("📝 Using sample weak topics for demonstration...")
    
    print(f"🎯 Generating personalized study plan for: {', '.join(weak_topics)}")
    
    try:
        study_plan = analyzer.generate_study_plan(weak_topics, time_available=5)
        
        print(f"\n📅 {study_plan['duration_days']}-Day Study Plan Generated!")
        
        # Show daily plans
        daily_plans = study_plan.get("daily_plans", [])
        for day_plan in daily_plans[:3]:  # Show first 3 days
            day_num = day_plan["day"]
            primary_topic = day_plan.get("primary_topic", "Review")
            
            print(f"\n📖 Day {day_num}: {primary_topic.replace('_', ' ').title()}")
            
            # Show activities
            activities = day_plan.get("activities", [])
            for activity in activities[:3]:  # Show first 3 activities
                print(f"   • {activity}")
            
            estimated_time = day_plan.get("estimated_time", "60 minutes")
            print(f"   ⏱️  Estimated time: {estimated_time}")
        
        # Show study tips
        study_tips = study_plan.get("study_tips", [])
        if study_tips:
            print("\n💡 Study Tips:")
            for tip in study_tips[:3]:
                print(f"   • {tip}")
        
        return study_plan
        
    except Exception as e:
        print(f"❌ Error generating study plan: {e}")
        return {}


def demo_topic_explanations(analyzer):
    """Demonstrate AI topic explanations"""
    print_header("AI TOPIC EXPLANATIONS")
    
    sample_topics = [
        "1.1_solids_liquids_gases",
        "2.4_ionic_bonding"
    ]
    
    for topic_id in sample_topics:
        print(f"\n📚 Explaining: {topic_id.replace('_', ' ').title()}")
        
        try:
            explanation = analyzer.get_topic_explanation(topic_id, "medium")
            
            # Truncate for demo display
            if len(explanation) > 200:
                explanation = explanation[:200] + "..."
            
            print(f"💭 {explanation}")
            
        except Exception as e:
            print(f"❌ Error getting explanation: {e}")


def demo_ai_feedback():
    """Demonstrate AI feedback generation"""
    print_header("AI FEEDBACK GENERATION")
    
    # Create a mock provider for feedback demo
    mock_provider = MockAIProvider()
    
    sample_question = {
        "question": "What happens to particles when a solid melts?",
        "options": {
            "A": "Particles move faster and spread out",
            "B": "Particles stop moving",
            "C": "Particles disappear", 
            "D": "Particles get smaller"
        },
        "correct_answer": "A",
        "explanation": "When solids melt, particles gain energy and move more freely."
    }
    
    print("📝 Sample Question: What happens to particles when a solid melts?")
    print("👤 Student Answer: C) Particles disappear")
    print("✅ Correct Answer: A) Particles move faster and spread out")
    
    try:
        feedback = mock_provider.generate_feedback(sample_question, "C", "A")
        print(f"\n🤖 AI Feedback:\n{feedback.content}")
        
    except Exception as e:
        print(f"❌ Error generating feedback: {e}")


def display_system_info(analyzer):
    """Display system information"""
    print("🔄 Initializing AI-powered assessment system...")
    
    # Count available topics
    topic_count = len(analyzer.topic_mapper.topics)
    print_status(f"System initialized with {topic_count} topics")


def main():
    """Main demonstration function"""
    print("🤖" * 30)
    print("  IGCSE ASSESSMENT TOOL - DAY 5")
    print("  AI-Powered Learning Enhancement")
    print("🤖" * 30)
    
    try:
        # Initialize AI provider
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print_status("Using GEMINI API for AI features")
            provider = create_ai_provider("gemini", api_key)
        else:
            print_status("No API key found - using MOCK PROVIDER for demonstration", "⚠️")
            provider = create_ai_provider("mock")
        
        # Initialize topic mapper
        data_dir = Path("data")
        if not data_dir.exists():
            print("❌ Data directory not found. Please run Day 3/4 setup first.")
            return
        
        mapper = TopicMapper(
            str(data_dir / "syllabus_topics.json"),
            str(data_dir / "past_questions_bank.json"), 
            str(data_dir / "manual_mappings.json")
        )
        
        # Map questions if not already done
        if not mapper.topics:
            mapper.map_all_questions()
        
        # Create AI analyzer
        analyzer = AIAnalyzer(provider, mapper)
        
        # Display system info
        display_system_info(analyzer)
        
        # Run demonstrations
        questions = demo_ai_question_generation(analyzer)
        weak_topics, analysis = demo_performance_analysis(analyzer)
        study_plan = demo_study_plan_generation(analyzer, weak_topics)
        demo_topic_explanations(analyzer)
        demo_ai_feedback()
        
        # Final summary
        print_header("AI DEMO COMPLETED")
        print_status(f"Generated {len(questions)} AI questions")
        print_status(f"Analyzed performance across {len(analysis.get('topic_performance', {}))} topics")
        print_status(f"Created {study_plan.get('duration_days', 0)}-day study plan")
        
        print("\n🚀 Next Steps:")
        print("   1. Set up API keys for real AI features")
        print("   2. Run python setup_day5.py for complete setup")
        print("   3. Start building web application (Option B)")
        print("\n💡 Ready for Day 6: Web Application Development!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you have completed Day 3 and Day 4 setup:")
        print("   python demo_day3.py")
        print("   python demo_day4.py")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Check that all required files are present and properly configured.")


if __name__ == "__main__":
    main()
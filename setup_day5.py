#!/usr/bin/env python3
"""
Day 5 Setup Script - IGCSE Assessment Tool with AI
Setup and verification for AI-powered features
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def check_api_setup():
    """Check if API keys are configured"""
    print_header("API KEY SETUP")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if gemini_key:
        print("✅ Gemini API key found")
        print("   Using Google Gemini for AI features")
        return "gemini"
    elif openai_key:
        print("✅ OpenAI API key found")
        print("   Using OpenAI GPT for AI features")
        return "openai"
    else:
        print("⚠️  No API key found")
        print("\nTo use real AI features, you need to set up an API key:")
        print("\n1. For Google Gemini (Recommended - Free tier):")
        print("   • Visit: https://makersuite.google.com/app/apikey")
        print("   • Create a free API key")
        print("   • Set environment variable:")
        print("     export GEMINI_API_KEY='your-api-key-here'")
        print("\n2. For OpenAI GPT:")
        print("   • Visit: https://platform.openai.com/api-keys")
        print("   • Create an API key (requires billing)")
        print("   • Set environment variable:")
        print("     export OPENAI_API_KEY='your-api-key-here'")
        print("\n3. For now, using mock AI provider for testing")
        return "mock"


def install_requirements():
    """Install required packages"""
    print_header("INSTALLING REQUIREMENTS")
    
    requirements = ["requests"]
    
    for package in requirements:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")


def verify_prerequisites():
    """Check Day 3/4 components"""
    print_header("VERIFYING PREREQUISITES")
    
    required_files = [
        ("src/mapping.py", "Day 3: Topic mapping"),
        ("src/paper_generator.py", "Day 4: Paper generation"),
        ("data/syllabus_topics.json", "Syllabus data"),
        ("data/past_questions_bank.json", "Questions bank"),
        ("data/manual_mappings.json", "Manual mappings")
    ]
    
    all_present = True
    for filepath, description in required_files:
        if Path(filepath).exists():
            print(f"✅ {filepath} - {description}")
        else:
            print(f"❌ {filepath} - {description} MISSING")
            all_present = False
    
    if not all_present:
        print("\n❌ Prerequisites missing! Run Day 3/4 setup first.")
        return False
    
    return True


def verify_ai_module():
    """Test AI module imports and basic functionality"""
    print_header("TESTING AI MODULE")
    
    try:
        # Test imports
        sys.path.insert(0, "src")
        from ai_analyzer import AIAnalyzer, AIResponse, create_ai_provider
        print("✅ AI module imports successful")
        
        # Test mock provider
        from ai_analyzer import MockAIProvider
        mock = MockAIProvider()
        response = mock.generate_question({"title": "Test", "keywords": ["test"]}, "easy")
        
        if response.confidence > 0:
            print("✅ Mock AI provider working")
        
        # Test AI response
        ai_response = AIResponse(content="Test", confidence=0.9)
        result = ai_response.to_dict()
        print("✅ AI response objects working")
        
        return True
        
    except Exception as e:
        print(f"❌ AI module error: {e}")
        return False


def run_unit_tests():
    """Run AI analyzer unit tests"""
    print_header("RUNNING UNIT TESTS")
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_ai_analyzer.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse test results
            lines = result.stderr.split('\n')
            for line in lines:
                if "Ran" in line and "tests" in line:
                    print(f"✅ {line.strip()}")
                elif "OK" in line:
                    print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def create_sample_env_file():
    """Create a sample .env file for API keys"""
    print_header("CREATING SAMPLE CONFIGURATION")
    
    env_content = """# IGCSE Assessment Tool - API Configuration
# Uncomment and add your API key for the service you want to use

# Google Gemini API (Recommended - has free tier)
# Get your key at: https://makersuite.google.com/app/apikey
# GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI API
# Get your key at: https://platform.openai.com/api-keys
# OPENAI_API_KEY=your-openai-api-key-here

# Note: Only one API key is needed. Gemini is recommended for the free tier.
"""
    
    env_path = Path(".env.example")
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_path}")
    print("   Copy to .env and add your API key to enable AI features")


def print_next_steps(api_status):
    """Print next steps for the user"""
    print_header("NEXT STEPS")
    
    if api_status == "mock":
        print("\n🔧 To enable real AI features:")
        print("1. Get a free Gemini API key:")
        print("   https://makersuite.google.com/app/apikey")
        print("2. Set the environment variable:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print("3. Re-run this setup")
    
    print("\n🚀 Ready to use AI features!")
    print("\nAvailable commands:")
    print("  python demo_day5.py              # Run AI demonstrations")
    print("  python tests/test_ai_analyzer.py # Run tests")
    print("\nAI Features available:")
    print("  ✅ Automated question generation")
    print("  ✅ Performance analysis with insights")
    print("  ✅ Personalized study plans")
    print("  ✅ Intelligent feedback")
    print("  ✅ AI-enhanced paper generation")
    
    print("\n📚 Sample usage:")
    print("""
from ai_analyzer import AIAnalyzer, create_ai_provider
from mapping import TopicMapper

# Initialize
mapper = TopicMapper("data/syllabus_topics.json", 
                    "data/past_questions_bank.json",
                    "data/manual_mappings.json")
mapper.map_all_questions()

# Create AI analyzer
provider = create_ai_provider("gemini")  # or "openai"
analyzer = AIAnalyzer(provider, mapper)

# Generate questions
questions = analyzer.generate_questions_batch(["1.1_solids_liquids_gases"], 3)

# Analyze performance
analysis = analyzer.analyze_student_performance(results, mappings)
""")


def main():
    """Run Day 5 setup"""
    print("\n🤖 IGCSE Assessment Tool - Day 5 Setup")
    print("AI-Powered Learning Enhancement")
    print("="*60)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Run setup steps
    steps = [
        ("Prerequisites", verify_prerequisites),
        ("Package Installation", install_requirements),
        ("API Configuration", check_api_setup),
        ("AI Module", verify_ai_module),
        ("Unit Tests", run_unit_tests),
        ("Sample Config", create_sample_env_file)
    ]
    
    results = {}
    for step_name, step_func in steps:
        print(f"\n🔄 Running: {step_name}")
        try:
            if step_name == "API Configuration":
                results[step_name] = step_func()  # Returns API type
            else:
                results[step_name] = step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results[step_name] = False
    
    # Summary
    print_header("SETUP SUMMARY")
    
    passed = sum(1 for k, v in results.items() 
                 if k != "API Configuration" and v)
    total = len(results) - 1  # Exclude API config from count
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📋 Total: {total}")
    
    api_status = results.get("API Configuration", "mock")
    print(f"\n🤖 AI Provider: {api_status}")
    
    if passed == total:
        print("\n🎉 Day 5 AI features ready to use!")
        print_next_steps(api_status)
    else:
        print("\n⚠️  Some components need attention")
        print("Fix the issues above and re-run setup")


if __name__ == "__main__":
    main()
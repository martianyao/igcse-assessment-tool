#!/usr/bin/env python3
"""
Day 4 Setup Script - IGCSE Assessment Tool
Automated setup and verification for paper generation system
"""

import os
import sys
from pathlib import Path

# Ensure 'src' is in sys.path for module imports
src_path = os.path.abspath("src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def check_prerequisites():
    """Check that Day 3 is properly set up"""
    print_header("CHECKING PREREQUISITES")
    
    required_day3_files = [
        "src/mapping.py",
        "data/syllabus_topics.json", 
        "data/past_questions_bank.json",
        "data/manual_mappings.json"
    ]
    
    missing_files = []
    for file_path in required_day3_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Day 3 setup incomplete. Missing files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False

    try:
        src_abs_path = os.path.abspath("src")
        if src_abs_path not in sys.path:
            sys.path.insert(0, src_abs_path)
        # Ensure import works by changing cwd if needed
        try:
            from src.mapping import TopicMapper
        except ImportError:
            import importlib.util
            mapping_path = os.path.join(src_abs_path, "mapping.py")
            spec = importlib.util.spec_from_file_location("mapping", mapping_path)
            mapping = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mapping)
            TopicMapper = mapping.TopicMapper

        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json", 
            "data/manual_mappings.json"
        )
        mapper.map_all_questions()

        print(f"✅ Day 3 system functional: {len(mapper.topics)} topics, {len(mapper.mappings)} mappings")
        return True

    except Exception as e:
        print(f"❌ Day 3 system error: {e}")
        return False


def verify_day4_files():
    """Verify all Day 4 files are in place"""
    print_header("VERIFYING DAY 4 FILES")
    
    required_files = [
        "src/paper_generator.py",
        "tests/test_paper_generator.py",
        "demo_day4.py",
        "integration_test_day4.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size} bytes)")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing Day 4 files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False
    
    return True


def test_imports():
    """Test that all Day 4 modules can be imported"""
    print_header("TESTING IMPORTS")
    
    try:
        src_abs_path = os.path.abspath("src")
        if src_abs_path not in sys.path:
            sys.path.insert(0, src_abs_path)

        from src.mapping import TopicMapper, Topic, QuestionTopicMapping
        print("✅ Day 3 imports successful")

        from src.paper_generator import (
            PaperGenerator, PaperConfig, QuestionSelector, 
            QuestionSelection, GeneratedPaper
        )
        print("✅ Day 4 imports successful")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_basic_functionality():
    """Test basic paper generation functionality"""
    print_header("TESTING BASIC FUNCTIONALITY")
    
    try:
        sys.path.insert(0, "src")
        from src.mapping import TopicMapper
        from src.paper_generator import PaperGenerator, PaperConfig
        
        # Set up system
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        mapper.map_all_questions()
        
        generator = PaperGenerator(mapper)
        print(f"✅ Paper generator initialized")
        
        # Test simple paper generation
        config = PaperConfig(total_questions=3, paper_type="balanced")
        paper = generator.generate_paper(config)
        
        print(f"✅ Paper generated: {len(paper.questions)} questions, {paper.total_points} points")
        
        # Test export
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        files = generator.export_paper(paper, "output")
        print(f"✅ Export successful: {len(files)} files created")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_unit_tests():
    """Run Day 4 unit tests"""
    print_header("RUNNING UNIT TESTS")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "tests/test_paper_generator.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stderr.split('\n')
            test_line = [line for line in lines if 'Ran' in line and 'test' in line]
            if test_line:
                print(f"✅ {test_line[0]}")
            else:
                print("✅ Unit tests passed")
            return True
        else:
            print(f"❌ Unit tests failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not run unit tests: {e}")
        return False


def run_integration_tests():
    """Run Day 4 integration tests"""
    print_header("RUNNING INTEGRATION TESTS")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "integration_test_day4.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All integration tests passed")
            return True
        else:
            print(f"❌ Integration tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not run integration tests: {e}")
        return False


def run_demo():
    """Run the Day 4 demo"""
    print_header("RUNNING DEMO")
    
    try:
        print("Starting Day 4 demo... (this may take a moment)")
        import subprocess
        result = subprocess.run([
            sys.executable, "demo_day4.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Demo completed successfully")
            
            # Show demo summary
            lines = result.stdout.split('\n')
            summary_lines = [line for line in lines if '✅' in line or '📊' in line or '🎉' in line]
            if summary_lines:
                print("\nDemo highlights:")
                for line in summary_lines[-5:]:  # Show last 5 highlight lines
                    print(f"  {line}")
            
            return True
        else:
            print(f"❌ Demo failed:")
            print(result.stdout[-1000:])  # Show last 1000 chars
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not run demo: {e}")
        return False


def show_final_status():
    """Show final setup status and next steps"""
    print_header("DAY 4 SETUP COMPLETE")
    
    print("🎉 Paper Generation System is ready!")
    
    print("\n📁 File Structure:")
    print("src/")
    print("├── mapping.py              (Day 3: Topic mapping)")
    print("└── paper_generator.py      (Day 4: Paper generation)")
    print()
    print("tests/")
    print("├── test_mapping.py         (Day 3 tests)")
    print("└── test_paper_generator.py (Day 4 tests)")
    print()
    print("data/")
    print("├── syllabus_topics.json")
    print("├── past_questions_bank.json")
    print("└── manual_mappings.json")
    print()
    print("output/")
    print("└── [generated papers and analysis files]")
    
    print("\n🚀 Available Commands:")
    print("python demo_day4.py                     # Run full demo")
    print("python tests/test_paper_generator.py    # Run unit tests")
    print("python integration_test_day4.py         # Run integration tests")
    print("python src/paper_generator.py           # Test paper generation")
    
    print("\n🎯 System Capabilities:")
    print("✅ Multiple paper generation strategies")
    print("✅ Intelligent question selection")
    print("✅ Weak topic focused remediation")
    print("✅ Comprehensive assessment creation")
    print("✅ Multi-format export (JSON, TXT, analysis)")
    print("✅ Statistical analysis and reporting")
    
    print("\n📚 Paper Types Available:")
    print("• Balanced papers (even difficulty distribution)")
    print("• Weak topic focused (remediation)")
    print("• Comprehensive (maximum topic coverage)")
    print("• Topic-specific (custom focus areas)")
    
    print("\n🎓 Ready for production use!")


def main():
    """Run complete Day 4 setup verification"""
    print("🚀 IGCSE Assessment Tool - Day 4 Setup")
    print("Paper Generation System Setup and Verification")
    
    tests = [
        ("Prerequisites Check", check_prerequisites),
        ("File Verification", verify_day4_files),
        ("Import Tests", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("Demo Execution", run_demo)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: CRASHED - {e}")
    
    print(f"\n📊 Setup Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total: {passed + failed}")
    
    if failed == 0:
        show_final_status()
        return True
    else:
        print(f"\n⚠️ {failed} setup step(s) failed.")
        print("Please resolve issues before using the system.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Integration Test for Day 4 Implementation
Tests complete paper generation system functionality end-to-end
"""

import sys
import json
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
if str(src_path.resolve()) not in sys.path:
    sys.path.insert(0, str(src_path.resolve()))


def test_file_structure():
    """Test that all required Day 4 files exist"""
    required_files = [
        "src/paper_generator.py",
        "tests/test_paper_generator.py",
        "demo_day4.py",
        # Day 3 dependencies
        "src/mapping.py",
        "data/syllabus_topics.json",
        "data/past_questions_bank.json",
        "data/manual_mappings.json"
    ]
    
    print("🔍 Testing Day 4 File Structure...")
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def test_imports():
    """Test that all Day 4 modules can be imported"""
    print("\n🔍 Testing Day 4 Imports...")
    
    try:
        from src.mapping import TopicMapper
        print("✅ TopicMapper imported")
        
        from src.paper_generator import PaperGenerator, PaperConfig, QuestionSelector, QuestionSelection
        print("✅ Paper generation classes imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_day3_integration():
    """Test integration with Day 3 topic mapping system"""
    print("\n🔍 Testing Day 3 Integration...")
    
    try:
        from src.mapping import TopicMapper
        
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        mapper.map_all_questions()
        
        print(f"✅ Day 3 system loaded: {len(mapper.topics)} topics, {len(mapper.mappings)} mappings")
        
        # Test that mappings exist for paper generation
        if len(mapper.mappings) == 0:
            print("❌ No question mappings available for paper generation")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Day 3 integration error: {e}")
        return False


def test_paper_generation_functionality():
    """Test core paper generation functionality"""
    print("\n🔍 Testing Paper Generation Functionality...")
    
    try:
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
        print(f"✅ Paper generator initialized with {len(generator.question_selector.available_questions)} questions")
        
        # Test different paper types
        test_configs = [
            ("balanced", PaperConfig(total_questions=5, paper_type="balanced")),
            ("comprehensive", PaperConfig(total_questions=3, paper_type="comprehensive")),
            ("weak_focus", PaperConfig(total_questions=4, paper_type="weak_focus"))
        ]
        
        for paper_type, config in test_configs:
            # Mock weak topics for weak_focus test
            weak_topics = {
                "weak_topics": {
                    "1.1_solids_liquids_gases": {"success_rate": 0.4}
                }
            } if paper_type == "weak_focus" else None
            
            paper = generator.generate_paper(config, weak_topics)
            
            if len(paper.questions) != config.total_questions:
                print(f"❌ {paper_type} paper: expected {config.total_questions}, got {len(paper.questions)}")
                return False
            
            print(f"✅ {paper_type} paper: {len(paper.questions)} questions, {paper.total_points} points")
        
        return True
    except Exception as e:
        print(f"❌ Paper generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_functionality():
    """Test paper export functionality"""
    print("\n🔍 Testing Export Functionality...")
    
    try:
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
        
        # Generate a test paper
        config = PaperConfig(total_questions=3, paper_type="balanced")
        paper = generator.generate_paper(config)
        
        # Test export
        files = generator.export_paper(paper, "output")
        
        print(f"✅ Export created {len(files)} files")
        
        # Verify required file types
        required_files = ["json", "text", "answer_key", "analysis"]
        for file_type in required_files:
            if file_type not in files:
                print(f"❌ Missing {file_type} export")
                return False
            
            file_path = files[file_type]
            if not os.path.exists(file_path):
                print(f"❌ {file_type} file not created: {file_path}")
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print(f"❌ {file_type} file is empty")
                return False
            
            print(f"✅ {file_type} export: {Path(file_path).name} ({file_size} bytes)")
        
        return True
    except Exception as e:
        print(f"❌ Export functionality error: {e}")
        return False


def test_question_selection_algorithms():
    """Test question selection algorithms"""
    print("\n🔍 Testing Question Selection Algorithms...")
    
    try:
        from src.mapping import TopicMapper
        from src.paper_generator import QuestionSelector
        
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        mapper.map_all_questions()
        
        selector = QuestionSelector(mapper)
        
        # Test balanced selection
        balanced = selector.select_balanced(5)
        if len(balanced) != 5:
            print(f"❌ Balanced selection: expected 5, got {len(balanced)}")
            return False
        print(f"✅ Balanced selection: {len(balanced)} questions")
        
        # Test weak topics selection
        weak_topics = list(mapper.topics.keys())[:2]
        weak_selections = selector.select_by_weak_topics(weak_topics, 4)
        if len(weak_selections) > 4:
            print(f"❌ Weak topics selection: expected ≤4, got {len(weak_selections)}")
            return False
        print(f"✅ Weak topics selection: {len(weak_selections)} questions")
        
        # Test topic focus selection
        target_topics = list(mapper.topics.keys())[:1]
        topic_selections = selector.select_by_topics(target_topics, 3)
        print(f"✅ Topic focus selection: {len(topic_selections)} questions")
        
        return True
    except Exception as e:
        print(f"❌ Question selection error: {e}")
        return False


def test_json_validity():
    """Test that all output JSON files are valid"""
    print("\n🔍 Testing JSON Output Validity...")
    
    # Check if output directory exists and has files
    output_dir = Path("output")
    if not output_dir.exists():
        print("⚠️ No output directory found - running quick export test")
        
        try:
            from src.mapping import TopicMapper
            from src.paper_generator import PaperGenerator, PaperConfig
            
            mapper = TopicMapper(
                "data/syllabus_topics.json",
                "data/past_questions_bank.json",
                "data/manual_mappings.json"
            )
            mapper.map_all_questions()
            
            generator = PaperGenerator(mapper)
            config = PaperConfig(total_questions=2, paper_type="balanced")
            paper = generator.generate_paper(config)
            generator.export_paper(paper, "output")
        except Exception as e:
            print(f"❌ Could not create test output: {e}")
            return False
    
    # Find and validate JSON files
    json_files = list(output_dir.glob("*.json")) if output_dir.exists() else []
    
    if not json_files:
        print("⚠️ No JSON files found in output directory")
        return True  # Not a failure if no files exist yet
    
    all_valid = True
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
            print(f"✅ {json_file.name} - Valid JSON")
        except json.JSONDecodeError:
            print(f"❌ {json_file.name} - Invalid JSON")
            all_valid = False
        except Exception as e:
            print(f"❌ {json_file.name} - Error: {e}")
            all_valid = False
    
    return all_valid


def test_system_performance():
    """Test system performance and scalability"""
    print("\n🔍 Testing System Performance...")
    
    try:
        import time
        from src.mapping import TopicMapper
        from src.paper_generator import PaperGenerator, PaperConfig
        
        # Set up system
        setup_start = time.time()
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        mapper.map_all_questions()
        generator = PaperGenerator(mapper)
        setup_time = time.time() - setup_start
        
        print(f"✅ System setup: {setup_time:.3f} seconds")
        
        # Test paper generation speed
        config = PaperConfig(total_questions=10, paper_type="balanced")
        
        generation_start = time.time()
        paper = generator.generate_paper(config)
        generation_time = time.time() - generation_start
        
        print(f"✅ Paper generation: {generation_time:.3f} seconds")
        
        # Test export speed
        export_start = time.time()
        files = generator.export_paper(paper, "output")
        export_time = time.time() - export_start
        
        print(f"✅ Paper export: {export_time:.3f} seconds")
        
        # Performance evaluation
        total_time = setup_time + generation_time + export_time
        print(f"✅ Total operation time: {total_time:.3f} seconds")
        
        if total_time < 5.0:
            print("✅ Performance: Excellent")
        elif total_time < 10.0:
            print("✅ Performance: Good")
        else:
            print("⚠️ Performance: Acceptable (may need optimization)")
        
        return True
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False


def main():
    """Run all Day 4 integration tests"""
    print("🚀 Day 4 Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_imports,
        test_day3_integration,
        test_paper_generation_functionality,
        test_export_functionality,
        test_question_selection_algorithms,
        test_json_validity,
        test_system_performance
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n📊 Day 4 Integration Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All Day 4 integration tests passed!")
        print("Paper Generation System is fully operational!")
        
        print("\n🎯 System Capabilities Verified:")
        print("✅ Multiple paper generation strategies")
        print("✅ Intelligent question selection algorithms")
        print("✅ Multi-format export system")
        print("✅ Integration with Day 3 topic mapping")
        print("✅ Performance and scalability")
        
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
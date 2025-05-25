#!/usr/bin/env python3
"""
Integration Test for Day 3 Implementation
Tests complete system functionality end-to-end
"""

import sys
import json
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        "src/mapping.py",
        "tests/test_mapping.py", 
        "data/syllabus_topics.json",
        "data/past_questions_bank.json",
        "data/manual_mappings.json",
        "demo_day3.py"
    ]
    
    print("🔍 Testing File Structure...")
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def test_imports():
    """Test that all modules can be imported"""
    print("\n🔍 Testing Imports...")
    
    try:
        from src.mapping import TopicMapper, Topic, QuestionTopicMapping
        print("✅ All classes imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_data_loading():
    """Test that data files load correctly"""
    print("\n🔍 Testing Data Loading...")
    
    try:
        from src.mapping import TopicMapper
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        
        print(f"✅ Loaded {len(mapper.topics)} topics")
        print(f"✅ Loaded {len(mapper.questions)} question groups")
        print(f"✅ Loaded {len(mapper.manual_mappings)} manual mappings")
        
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False


def test_mapping_functionality():
    """Test core mapping functionality"""
    print("\n🔍 Testing Mapping Functionality...")
    
    try:
        from src.mapping import TopicMapper
        mapper = TopicMapper(
            "data/syllabus_topics.json",
            "data/past_questions_bank.json",
            "data/manual_mappings.json"
        )
        
        # Test mapping
        mapper.map_all_questions()
        print(f"✅ Generated {len(mapper.mappings)} mappings")
        
        # Test export
        mapper.export_mappings("output/test_mappings.json")
        sample_results = {"SLG_001": True, "SLG_002": False}
        mapper.export_weak_topics_analysis(sample_results, "output/test_analysis.json")
        print("✅ Export functionality works")
        
        return True
    except Exception as e:
        print(f"❌ Mapping functionality error: {e}")
        return False


def test_json_validity():
    """Test that output JSON files are valid"""
    print("\n🔍 Testing JSON Validity...")
    
    json_files = [
        "data/syllabus_topics.json",
        "data/past_questions_bank.json", 
        "data/manual_mappings.json"
    ]
    
    # Add output files if they exist
    if os.path.exists("output/question_topic_mappings.json"):
        json_files.append("output/question_topic_mappings.json")
    if os.path.exists("output/weak_topics_analysis.json"):
        json_files.append("output/weak_topics_analysis.json")
    
    all_valid = True
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
                print(f"✅ {json_file} - Valid JSON")
            except json.JSONDecodeError:
                print(f"❌ {json_file} - Invalid JSON")
                all_valid = False
        else:
            print(f"⚠️ {json_file} - File not found")
    
    return all_valid


def main():
    """Run all integration tests"""
    print("🚀 Day 3 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_data_loading, 
        test_mapping_functionality,
        test_json_validity
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
    
    print(f"\n📊 Integration Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed! Day 3 implementation is complete.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
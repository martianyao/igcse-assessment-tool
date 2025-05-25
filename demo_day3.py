#!/usr/bin/env python3
"""
Day 3 Demo Script - IGCSE Assessment Tool
Demonstrates all features of the topic mapping system
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mapping import TopicMapper, QuestionTopicMapping


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_subheader(title):
    """Print formatted subsection header"""
    print(f"\n--- {title} ---")


def demo_topic_loading():
    """Demonstrate topic loading functionality"""
    print_header("TOPIC LOADING DEMO")
    
    try:
        mapper = TopicMapper(
            syllabus_path="data/syllabus_topics.json",
            questions_path="data/past_questions_bank.json", 
            manual_mappings_path="data/manual_mappings.json"
        )
        
        print(f"✅ Successfully loaded {len(mapper.topics)} topics")
        print(f"✅ Successfully loaded {sum(len(q['questions']) for q in mapper.questions.values())} questions")
        print(f"✅ Successfully loaded {len(mapper.manual_mappings)} manual mappings")
        
        print_subheader("Sample Topics Loaded")
        for i, (topic_id, topic) in enumerate(list(mapper.topics.items())[:5]):
            print(f"{i+1}. {topic_id}: {topic.title}")
            print(f"   Level: {topic.level}, Keywords: {topic.keywords[:3]}...")
        
        return mapper
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def demo_confidence_calculation(mapper):
    """Demonstrate confidence score calculation"""
    print_header("CONFIDENCE CALCULATION DEMO")
    
    test_cases = [
        {
            "text": "Which statement about solid particles is correct? Particles are close together in fixed positions",
            "expected_topic": "1.1_solids_liquids_gases"
        },
        {
            "text": "What happens during melting? Temperature remains constant while state changes",
            "expected_topic": "1.2_changes_of_state"
        },
        {
            "text": "Which element forms an acidic oxide? Sulfur forms SO2 which is acidic",
            "expected_topic": "7.5_oxides_classification"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print_subheader(f"Test Case {i}")
        print(f"Text: {test_case['text'][:50]}...")
        
        if test_case['expected_topic'] in mapper.topics:
            topic = mapper.topics[test_case['expected_topic']]
            confidence = mapper.calculate_topic_confidence(test_case['text'], topic)
            
            print(f"Expected Topic: {topic.title}")
            print(f"Confidence Score: {confidence:.3f}")
            print(f"Result: {'✅ Good match' if confidence > 0.3 else '⚠️ Low match'}")
        else:
            print(f"⚠️ Topic {test_case['expected_topic']} not found in dataset")


def demo_all_questions_mapping(mapper):
    """Demonstrate mapping all questions at once"""
    print_header("BULK MAPPING DEMO")
    
    print("Mapping all questions to topics...")
    mapper.map_all_questions()
    
    print(f"✅ Successfully mapped {len(mapper.mappings)} question-topic associations")
    
    # Show mapping statistics
    unique_questions = len(set(m.question_id for m in mapper.mappings))
    unique_topics = len(set(m.topic_id for m in mapper.mappings))
    avg_confidence = sum(m.confidence for m in mapper.mappings) / len(mapper.mappings)
    
    print_subheader("Mapping Statistics")
    print(f"Unique Questions Mapped: {unique_questions}")
    print(f"Topics Covered: {unique_topics}")
    print(f"Average Confidence: {avg_confidence:.3f}")
    
    # Show confidence distribution
    high_conf = sum(1 for m in mapper.mappings if m.confidence > 0.7)
    med_conf = sum(1 for m in mapper.mappings if 0.3 <= m.confidence <= 0.7)
    low_conf = sum(1 for m in mapper.mappings if m.confidence < 0.3)
    
    print_subheader("Confidence Distribution")
    print(f"High Confidence (>0.7): {high_conf}")
    print(f"Medium Confidence (0.3-0.7): {med_conf}")
    print(f"Low Confidence (<0.3): {low_conf}")


def demo_export_functionality(mapper):
    """Demonstrate export functionality"""
    print_header("EXPORT FUNCTIONALITY DEMO")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print("Exporting mapping results...")
    
    # Export mappings
    mappings_path = "output/question_topic_mappings.json"
    mapper.export_mappings(mappings_path)
    print(f"✅ Exported mappings to: {mappings_path}")
    
    # Export weak topics analysis
    sample_results = {m.question_id: hash(m.question_id) % 3 == 0 for m in mapper.mappings[:20]}
    analysis_path = "output/weak_topics_analysis.json"
    mapper.export_weak_topics_analysis(sample_results, analysis_path)
    print(f"✅ Exported analysis to: {analysis_path}")
    
    # Show file contents preview
    print_subheader("Export File Preview")
    
    try:
        with open(mappings_path, 'r') as f:
            mappings_data = json.load(f)
        print(f"Mappings file contains {len(mappings_data['mappings'])} mappings")
        print(f"Summary: {mappings_data['summary']}")
        
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
        print(f"Analysis file contains {len(analysis_data['weak_topics'])} weak topics")
        print(f"Summary: {analysis_data['summary']}")
        
    except Exception as e:
        print(f"⚠️ Could not preview files: {e}")


def main():
    """Run complete demo of Day 3 functionality"""
    print_header("IGCSE ASSESSMENT TOOL - DAY 3 DEMO")
    print("Demonstrating Topic Mapping System Features")
    
    # Step 1: Load data
    mapper = demo_topic_loading()
    if not mapper:
        print("❌ Cannot continue demo without data. Please check file paths.")
        return
    
    # Step 2: Show confidence calculation
    demo_confidence_calculation(mapper)
    
    # Step 3: Show bulk mapping
    demo_all_questions_mapping(mapper)
    
    # Step 4: Show export functionality
    demo_export_functionality(mapper)
    
    # Final summary
    print_header("DEMO COMPLETE")
    print("✅ All Day 3 features demonstrated successfully!")
    print("\nFiles created/updated:")
    print("- src/mapping.py (Topic mapping engine)")
    print("- tests/test_mapping.py (Comprehensive test suite)")
    print("- data/syllabus_topics.json (Enhanced syllabus)")
    print("- data/manual_mappings.json (Manual overrides)")
    print("- output/question_topic_mappings.json (Generated mappings)")
    print("- output/weak_topics_analysis.json (Analysis results)")
    
    print("\n🚀 Ready for Day 4: Paper Generation System!")


if __name__ == "__main__":
    main()
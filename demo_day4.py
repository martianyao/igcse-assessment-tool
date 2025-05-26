#!/usr/bin/env python3
"""
Day 4 Demo Script - IGCSE Assessment Tool
Demonstrates paper generation system with different strategies and configurations
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mapping import TopicMapper
from src.paper_generator import PaperGenerator, PaperConfig


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subheader(title):
    """Print formatted subsection header"""
    print(f"\n--- {title} ---")


def demo_paper_generation_setup():
    """Demonstrate setup of paper generation system"""
    print_header("PAPER GENERATION SYSTEM SETUP")
    
    try:
        # Load Day 3 topic mapping system
        print("Loading topic mapping system from Day 3...")
        mapper = TopicMapper(
            syllabus_path="data/syllabus_topics.json",
            questions_path="data/past_questions_bank.json", 
            manual_mappings_path="data/manual_mappings.json"
        )
        mapper.map_all_questions()
        
        print(f"✅ Loaded {len(mapper.topics)} topics")
        print(f"✅ Loaded {len(mapper.mappings)} question-topic mappings")
        
        # Initialize paper generator
        generator = PaperGenerator(mapper)
        question_pool_size = len(generator.question_selector.available_questions)
        
        print(f"✅ Paper generator initialized")
        print(f"✅ Question pool: {question_pool_size} questions available")
        
        return generator, mapper
        
    except Exception as e:
        print(f"❌ Error setting up paper generation: {e}")
        return None, None


def demo_balanced_paper_generation(generator):
    """Demonstrate balanced paper generation"""
    print_header("BALANCED PAPER GENERATION")
    
    print("Generating a balanced assessment paper...")
    
    config = PaperConfig(
        total_questions=12,
        paper_type="balanced",
        time_limit_minutes=75,
        difficulty_distribution={"easy": 0.4, "medium": 0.4, "hard": 0.2}
    )
    
    paper = generator.generate_paper(config)
    
    print_subheader("Paper Details")
    print(f"Title: {paper.title}")
    print(f"Paper ID: {paper.paper_id}")
    print(f"Total Questions: {len(paper.questions)}")
    print(f"Total Points: {paper.total_points}")
    print(f"Average Points per Question: {paper.total_points / len(paper.questions):.1f}")
    
    print_subheader("Difficulty Distribution")
    difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
    for q in paper.questions:
        difficulty_count[q.difficulty] += 1
    
    for diff, count in difficulty_count.items():
        percentage = (count / len(paper.questions)) * 100
        print(f"{diff.title()}: {count} questions ({percentage:.1f}%)")
    
    print_subheader("Topic Coverage")
    for topic, count in paper.topic_coverage.items():
        print(f"• {topic}: {count} questions")
    
    return paper


def demo_weak_focus_paper_generation(generator):
    """Demonstrate weak topic focused paper generation"""
    print_header("WEAK TOPIC FOCUSED PAPER GENERATION")
    
    print("Simulating student weak topics analysis...")
    
    # Simulate weak topics from Day 3 analysis
    mock_weak_topics = {
        "weak_topics": {
            "1.1_solids_liquids_gases": {
                "success_rate": 0.35,
                "total_questions": 3,
                "wrong_questions": ["SLG_001", "SLG_002"]
            },
            "2.4_ionic_bonding": {
                "success_rate": 0.40,
                "total_questions": 3,
                "wrong_questions": ["ION_001", "ION_003"]
            },
            "7.5_oxides_classification": {
                "success_rate": 0.25,
                "total_questions": 3,
                "wrong_questions": ["OX_001", "OX_002", "OX_003"]
            }
        }
    }
    
    print("Identified weak topics:")
    for topic_id, stats in mock_weak_topics["weak_topics"].items():
        topic_title = generator.topic_mapper.topics[topic_id].title
        print(f"• {topic_title}: {stats['success_rate']*100:.0f}% success rate")
    
    print("\nGenerating focused review paper...")
    
    config = PaperConfig(
        total_questions=10,
        paper_type="weak_focus",
        time_limit_minutes=60
    )
    
    paper = generator.generate_paper(config, mock_weak_topics)
    
    print_subheader("Focused Paper Details")
    print(f"Title: {paper.title}")
    print(f"Generation Strategy: Weak topic focus (70% weak, 30% balanced)")
    print(f"Total Questions: {len(paper.questions)}")
    print(f"Total Points: {paper.total_points}")
    
    print_subheader("Selection Reasons")
    reason_count = {}
    for q in paper.questions:
        reason_type = q.selection_reason.split(":")[0]
        reason_count[reason_type] = reason_count.get(reason_type, 0) + 1
    
    for reason, count in reason_count.items():
        print(f"• {reason}: {count} questions")
    
    return paper


def demo_comprehensive_paper_generation(generator):
    """Demonstrate comprehensive paper generation"""
    print_header("COMPREHENSIVE PAPER GENERATION")
    
    print("Generating comprehensive assessment covering all topics...")
    
    config = PaperConfig(
        total_questions=15,
        paper_type="comprehensive",
        time_limit_minutes=90,
        difficulty_distribution={"easy": 0.3, "medium": 0.5, "hard": 0.2}
    )
    
    paper = generator.generate_paper(config)
    
    print_subheader("Comprehensive Paper Details")
    print(f"Title: {paper.title}")
    print(f"Strategy: Maximum topic coverage")
    print(f"Total Questions: {len(paper.questions)}")
    print(f"Total Points: {paper.total_points}")
    
    print_subheader("Topic Coverage Analysis")
    total_topics = len(generator.topic_mapper.topics)
    covered_topics = len(paper.topic_coverage)
    coverage_percentage = (covered_topics / total_topics) * 100
    
    print(f"Topics covered: {covered_topics}/{total_topics} ({coverage_percentage:.1f}%)")
    print("Coverage breakdown:")
    for topic, count in sorted(paper.topic_coverage.items()):
        print(f"• {topic}: {count} questions")
    
    return paper


def demo_topic_specific_paper_generation(generator):
    """Demonstrate topic-specific paper generation"""
    print_header("TOPIC-SPECIFIC PAPER GENERATION")
    
    # Focus on specific chemistry areas
    target_topics = ["1.1_solids_liquids_gases", "1.2_changes_of_state", "2.4_ionic_bonding"]
    
    print("Generating paper focused on specific topics:")
    for topic_id in target_topics:
        topic_title = generator.topic_mapper.topics[topic_id].title
        print(f"• {topic_title}")
    
    config = PaperConfig(
        total_questions=9,
        paper_type="balanced",  # Use balanced selection within chosen topics
        topic_focus=target_topics,
        time_limit_minutes=45
    )
    
    paper = generator.generate_paper(config)
    
    print_subheader("Topic-Specific Paper Details")
    print(f"Title: {paper.title}")
    print(f"Focus Strategy: Selected topics only")
    print(f"Total Questions: {len(paper.questions)}")
    print(f"Total Points: {paper.total_points}")
    
    print_subheader("Topic Distribution")
    for topic, count in paper.topic_coverage.items():
        print(f"• {topic}: {count} questions")
    
    return paper


def demo_paper_export_functionality(generator, papers):
    """Demonstrate paper export functionality"""
    print_header("PAPER EXPORT FUNCTIONALITY")
    
    print("Exporting generated papers in multiple formats...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    all_files_created = []
    
    for i, paper in enumerate(papers, 1):
        print(f"\nExporting Paper {i}: {paper.config.paper_type}")
        
        files = generator.export_paper(paper, "output")
        all_files_created.extend(files.values())
        
        print(f"✅ Generated {len(files)} files:")
        for file_type, file_path in files.items():
            file_size = Path(file_path).stat().st_size
            print(f"   • {file_type}: {Path(file_path).name} ({file_size} bytes)")
    
    print_subheader("Export Summary")
    print(f"Total files created: {len(all_files_created)}")
    print("File types generated:")
    print("• JSON format (machine-readable)")
    print("• Text format (human-readable)")
    print("• Answer keys (for educators)")
    print("• Analysis reports (statistics)")
    
    # Show sample content
    if papers:
        sample_paper = papers[0]
        sample_files = generator.export_paper(sample_paper, "output")
        
        print_subheader("Sample Paper Content Preview")
        
        # Show text format preview
        if "text" in sample_files:
            with open(sample_files["text"], 'r') as f:
                content = f.read()
                lines = content.split('\n')
                preview_lines = lines[:15]  # Show first 15 lines
                print("Text format preview:")
                for line in preview_lines:
                    print(f"  {line}")
                if len(lines) > 15:
                    print(f"  ... ({len(lines) - 15} more lines)")
    
    return all_files_created


def demo_paper_analysis_features(generator, papers):
    """Demonstrate paper analysis features"""
    print_header("PAPER ANALYSIS FEATURES")
    
    if not papers:
        print("No papers available for analysis.")
        return
    
    print("Analyzing generated papers...")
    
    for i, paper in enumerate(papers, 1):
        print_subheader(f"Paper {i} Analysis: {paper.config.paper_type.title()}")
        
        # Basic statistics
        total_questions = len(paper.questions)
        total_points = paper.total_points
        avg_points = total_points / total_questions if total_questions > 0 else 0
        
        print(f"Questions: {total_questions}")
        print(f"Total Points: {total_points}")
        print(f"Average Points per Question: {avg_points:.1f}")
        
        # Difficulty analysis
        difficulty_analysis = generator._analyze_difficulty(paper.questions)
        print("Difficulty distribution:")
        for diff, percentage in difficulty_analysis["percentage_by_count"].items():
            count = difficulty_analysis["count_distribution"][diff]
            print(f"• {diff.title()}: {count} questions ({percentage:.1f}%)")
        
        # Selection strategy analysis
        selection_analysis = generator._analyze_selection_reasons(paper.questions)
        print("Selection strategy breakdown:")
        for reason, count in selection_analysis.items():
            percentage = (count / total_questions) * 100
            print(f"• {reason}: {count} questions ({percentage:.1f}%)")
    
    print_subheader("Cross-Paper Comparison")
    
    if len(papers) > 1:
        print("Comparing different paper generation strategies:")
        
        for i, paper in enumerate(papers, 1):
            strategy = paper.config.paper_type
            questions = len(paper.questions)
            points = paper.total_points
            topics = len(paper.topic_coverage)
            
            print(f"Paper {i} ({strategy}): {questions}Q, {points}pts, {topics} topics")
        
        # Find most comprehensive
        most_comprehensive = max(papers, key=lambda p: len(p.topic_coverage))
        print(f"\nMost comprehensive: {most_comprehensive.config.paper_type} "
              f"({len(most_comprehensive.topic_coverage)} topics covered)")
        
        # Find most focused
        most_focused = min(papers, key=lambda p: len(p.topic_coverage))
        print(f"Most focused: {most_focused.config.paper_type} "
              f"({len(most_focused.topic_coverage)} topics covered)")


def main():
    """Run complete Day 4 demonstration"""
    print_header("IGCSE ASSESSMENT TOOL - DAY 4 DEMO")
    print("Paper Generation System - Creating Custom Assessment Papers")
    
    # Setup
    generator, mapper = demo_paper_generation_setup()
    if not generator:
        print("❌ Cannot continue demo without paper generator.")
        return
    
    papers = []
    
    # Demo different paper generation strategies
    print("\n🎯 Demonstrating different paper generation strategies...")
    
    # 1. Balanced paper
    balanced_paper = demo_balanced_paper_generation(generator)
    papers.append(balanced_paper)
    
    # 2. Weak topic focused paper
    weak_focus_paper = demo_weak_focus_paper_generation(generator)
    papers.append(weak_focus_paper)
    
    # 3. Comprehensive paper
    comprehensive_paper = demo_comprehensive_paper_generation(generator)
    papers.append(comprehensive_paper)
    
    # 4. Topic-specific paper
    topic_specific_paper = demo_topic_specific_paper_generation(generator)
    papers.append(topic_specific_paper)
    
    # Demo export functionality
    exported_files = demo_paper_export_functionality(generator, papers)
    
    # Demo analysis features
    demo_paper_analysis_features(generator, papers)
    
    # Final summary
    print_header("DAY 4 DEMO COMPLETE")
    print("🎉 Paper Generation System successfully demonstrated!")
    
    print(f"\n📊 Summary of achievements:")
    print(f"✅ Generated {len(papers)} different types of assessment papers")
    print(f"✅ Demonstrated {len(set(p.config.paper_type for p in papers))} generation strategies")
    print(f"✅ Created {len(exported_files)} output files")
    print(f"✅ Covered {len(set().union(*(p.topic_coverage.keys() for p in papers)))} unique topics")
    
    total_questions = sum(len(p.questions) for p in papers)
    total_points = sum(p.total_points for p in papers)
    print(f"✅ Generated {total_questions} total questions worth {total_points} points")
    
    print("\n📁 Files created:")
    print("• Paper files (JSON, TXT formats)")
    print("• Answer keys for educators")  
    print("• Statistical analysis reports")
    print("• Topic coverage reports")
    
    print("\n🚀 System Capabilities Demonstrated:")
    print("• Intelligent question selection algorithms")
    print("• Multiple paper generation strategies")
    print("• Difficulty and topic balancing")
    print("• Weak topic focused remediation")
    print("• Comprehensive assessment creation")
    print("• Multi-format export system")
    print("• Statistical analysis and reporting")
    
    print("\n🎓 Ready for real-world assessment creation!")
    print("The system can now generate custom papers based on:")
    print("• Student performance analysis from Day 3")
    print("• Specific curriculum requirements")
    print("• Teacher preferences and constraints")
    print("• Exam board specifications")


if __name__ == "__main__":
    main()
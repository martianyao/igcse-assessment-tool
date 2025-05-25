"""
Test suite for diagnostics module.
Tests item analysis, student profiling, and weakness identification.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.diagnostics import (
    WeaknessAnalyzer, 
    ItemStatistics, 
    StudentWeaknessProfile
)
from src.ingestion import DataIngestion, ClassData, StudentRecord


class TestItemStatistics:
    """Test ItemStatistics dataclass."""
    
    def test_difficulty_categorization(self):
        """Test difficulty level categorization."""
        # Easy item
        easy_item = ItemStatistics(
            question_id="q1",
            p_value=0.8,
            discrimination=0.3,
            num_correct=24,
            num_attempts=30
        )
        assert easy_item.difficulty_level == "Easy"
        
        # Medium item
        medium_item = ItemStatistics(
            question_id="q2",
            p_value=0.5,
            discrimination=0.35,
            num_correct=15,
            num_attempts=30
        )
        assert medium_item.difficulty_level == "Medium"
        
        # Hard item
        hard_item = ItemStatistics(
            question_id="q3",
            p_value=0.2,
            discrimination=0.4,
            num_correct=6,
            num_attempts=30
        )
        assert hard_item.difficulty_level == "Hard"
    
    def test_discrimination_quality(self):
        """Test discrimination quality categorization."""
        # Excellent
        excellent = ItemStatistics(
            question_id="q1",
            p_value=0.5,
            discrimination=0.5,
            num_correct=15,
            num_attempts=30
        )
        assert excellent.discrimination_quality == "Excellent"
        
        # Good
        good = ItemStatistics(
            question_id="q2",
            p_value=0.5,
            discrimination=0.35,
            num_correct=15,
            num_attempts=30
        )
        assert good.discrimination_quality == "Good"
        
        # Fair
        fair = ItemStatistics(
            question_id="q3",
            p_value=0.5,
            discrimination=0.25,
            num_correct=15,
            num_attempts=30
        )
        assert fair.discrimination_quality == "Fair"
        
        # Poor
        poor = ItemStatistics(
            question_id="q4",
            p_value=0.5,
            discrimination=0.1,
            num_correct=15,
            num_attempts=30
        )
        assert poor.discrimination_quality == "Poor"


class TestStudentWeaknessProfile:
    """Test StudentWeaknessProfile dataclass."""
    
    def test_get_priority_questions(self):
        """Test priority question selection."""
        profile = StudentWeaknessProfile(
            student_id="S001",
            weak_questions=["q1", "q2", "q3", "q4", "q5", "q6"],
            performance_by_difficulty={"Easy": 80.0, "Medium": 60.0, "Hard": 30.0},
            overall_mcq_percentage=70.0,
            relative_performance=0.95,
            suggested_focus_areas=["q1", "q2", "q3"]
        )
        
        # Test default (5 questions)
        priority = profile.get_priority_questions()
        assert len(priority) == 5
        assert priority == ["q1", "q2", "q3", "q4", "q5"]
        
        # Test custom number
        priority_3 = profile.get_priority_questions(3)
        assert len(priority_3) == 3
        assert priority_3 == ["q1", "q2", "q3"]


class TestWeaknessAnalyzer:
    """Test WeaknessAnalyzer class."""
    
    def create_sample_class_data(self) -> ClassData:
        """Create sample class data for testing."""
        class_data = ClassData()
        class_data.mcq_questions = ["q1", "q2", "q3", "q4", "q5"]
        
        # Create diverse student responses
        students = {
            "S001": {"q1": 1, "q2": 1, "q3": 1, "q4": 0, "q5": 0},  # Good student
            "S002": {"q1": 1, "q2": 1, "q3": 0, "q4": 0, "q5": 0},  # Average student
            "S003": {"q1": 1, "q2": 0, "q3": 0, "q4": 0, "q5": 0},  # Weak student
            "S004": {"q1": 1, "q2": 1, "q3": 1, "q4": 1, "q5": 0},  # Very good student
            "S005": {"q1": 0, "q2": 0, "q3": 0, "q4": 0, "q5": 0},  # Very weak student
        }
        
        for sid, responses in students.items():
            student = StudentRecord(
                student_id=sid,
                mcq_responses=responses,
                mcq_total=float(sum(responses.values())),
                assignments={"a1": 80.0},
                assignment_total=80.0,
                participation={"week_1": 4.0},
                participation_avg=4.0
            )
            class_data.students[sid] = student
        
        return class_data
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        
        assert analyzer.class_data == class_data
        assert len(analyzer.item_stats) == 0
        assert len(analyzer.student_profiles) == 0
        assert analyzer._response_matrix is None
    
    def test_build_response_matrix(self):
        """Test response matrix building."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        
        matrix = analyzer._build_response_matrix()
        
        # Check shape
        assert matrix.shape[0] == 5  # 5 students
        assert matrix.shape[1] == 6  # 5 questions + total_score
        
        # Check content
        assert matrix.loc["S001", "q1"] == 1
        assert matrix.loc["S001", "q4"] == 0
        assert matrix.loc["S001", "total_score"] == 3
    
    def test_calculate_item_statistics(self):
        """Test item statistics calculation."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        
        item_stats = analyzer.calculate_item_statistics()
        
        # Check all questions analyzed
        assert len(item_stats) == 5
        
        # Check q1 (easiest - 4/5 correct)
        q1_stats = item_stats["q1"]
        assert q1_stats.p_value == 0.8
        assert q1_stats.num_correct == 4
        assert q1_stats.num_attempts == 5
        
        # Check q5 (hardest - 0/5 correct)
        q5_stats = item_stats["q5"]
        assert q5_stats.p_value == 0.0
        assert q5_stats.num_correct == 0
        assert q5_stats.num_attempts == 5
    
    def test_create_student_profiles(self):
        """Test student profile creation."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        
        profiles = analyzer.create_student_profiles()
        
        # Check all students profiled
        assert len(profiles) == 5
        
        # Check S001 (good student)
        s001_profile = profiles["S001"]
        assert s001_profile.overall_mcq_percentage == 60.0  # 3/5 = 60%
        assert len(s001_profile.weak_questions) == 2  # q4, q5
        
        # Check S005 (very weak student)
        s005_profile = profiles["S005"]
        assert s005_profile.overall_mcq_percentage == 0.0
        assert len(s005_profile.weak_questions) == 5  # All questions
    
    def test_identify_weak_items(self):
        """Test weak item identification."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        analyzer.calculate_item_statistics()
        
        # With default threshold (0.5)
        weak_items = analyzer.identify_weak_items()
        assert "q5" in weak_items  # 0% correct
        assert "q4" in weak_items  # 20% correct
        assert "q1" not in weak_items  # 80% correct
    
    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        
        # Run full analysis
        analyzer.analyze()
        
        # Check all components completed
        assert len(analyzer.item_stats) == 5
        assert len(analyzer.student_profiles) == 5
        assert analyzer._response_matrix is not None
    
    def test_class_summary(self):
        """Test class summary generation."""
        class_data = self.create_sample_class_data()
        analyzer = WeaknessAnalyzer(class_data)
        analyzer.analyze()
        
        summary = analyzer.get_class_summary()
        
        # Check summary content
        assert summary["num_students"] == 5
        assert summary["num_questions"] == 5
        assert "avg_score" in summary
        assert "hardest_questions" in summary
        assert "easiest_questions" in summary
        
        # Check ordering
        assert summary["hardest_questions"][0] == "q5"  # 0% correct
        assert summary["easiest_questions"][0] == "q1"  # 80% correct


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
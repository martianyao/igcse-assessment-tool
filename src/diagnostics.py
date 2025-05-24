"""
Diagnostic engine for IGCSE Assessment Tool.

Analyzes MCQ responses to identify student weaknesses using:
- Item difficulty (p-values)
- Item discrimination (point-biserial correlation)
- Topic-level performance aggregation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
from scipy import stats

from src.ingestion import ClassData, StudentRecord

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ItemStatistics:
    """Statistics for a single MCQ item/question."""
    question_id: str
    p_value: float  # Difficulty index (0-1, lower = harder)
    discrimination: float  # Point-biserial correlation
    num_correct: int
    num_attempts: int
    distractor_analysis: Optional[Dict[str, int]] = None
    
    @property
    def difficulty_level(self) -> str:
        """Categorize difficulty: Easy (>0.7), Medium (0.3-0.7), Hard (<0.3)"""
        if self.p_value > 0.7:
            return "Easy"
        elif self.p_value < 0.3:
            return "Hard"
        return "Medium"
    
    @property
    def discrimination_quality(self) -> str:
        """Categorize discrimination: Excellent (>0.4), Good (0.3-0.4), Fair (0.2-0.3), Poor (<0.2)"""
        if self.discrimination > 0.4:
            return "Excellent"
        elif self.discrimination > 0.3:
            return "Good"
        elif self.discrimination > 0.2:
            return "Fair"
        return "Poor"


@dataclass
class StudentWeaknessProfile:
    """Individual student's weakness analysis."""
    student_id: str
    weak_questions: List[str]  # Questions answered incorrectly
    performance_by_difficulty: Dict[str, float]  # Easy/Medium/Hard -> % correct
    overall_mcq_percentage: float
    relative_performance: float  # Compared to class average
    suggested_focus_areas: List[str]  # Top 3-5 weak areas
    
    def get_priority_questions(self, n: int = 5) -> List[str]:
        """Return top n questions to focus on."""
        return self.weak_questions[:n]


class WeaknessAnalyzer:
    """Analyzes student performance to identify weaknesses."""
    
    def __init__(self, class_data: ClassData):
        """
        Initialize analyzer with class data.
        
        Args:
            class_data: ClassData object from ingestion module
        """
        self.class_data = class_data
        self.item_stats: Dict[str, ItemStatistics] = {}
        self.student_profiles: Dict[str, StudentWeaknessProfile] = {}
        self._response_matrix: Optional[pd.DataFrame] = None
        
    def analyze(self) -> None:
        """Run full analysis pipeline."""
        logger.info("Starting weakness analysis...")
        
        # Build response matrix
        self._build_response_matrix()
        
        # Calculate item statistics
        self.calculate_item_statistics()
        
        # Create student profiles
        self.create_student_profiles()
        
        logger.info(f"Analysis complete for {len(self.student_profiles)} students")
    
    def _build_response_matrix(self) -> pd.DataFrame:
        """Build matrix of student responses (rows=students, cols=questions)."""
        data = []
        student_ids = []
        
        for student_id, student in self.class_data.students.items():
            student_ids.append(student_id)
            row = [student.mcq_responses.get(q, 0) for q in self.class_data.mcq_questions]
            data.append(row)
        
        self._response_matrix = pd.DataFrame(
            data, 
            index=student_ids,
            columns=self.class_data.mcq_questions
        )
        
        # Add total score column
        self._response_matrix['total_score'] = self._response_matrix.sum(axis=1)
        
        return self._response_matrix
    
    def calculate_item_statistics(self) -> Dict[str, ItemStatistics]:
        """Calculate difficulty and discrimination for each question."""
        if self._response_matrix is None:
            self._build_response_matrix()
        
        for question in self.class_data.mcq_questions:
            # Calculate p-value (difficulty)
            responses = self._response_matrix[question]
            num_correct = responses.sum()
            num_attempts = len(responses)
            p_value = num_correct / num_attempts if num_attempts > 0 else 0
            
            # Calculate point-biserial correlation (discrimination)
            # Correlation between item score and total score
            total_scores = self._response_matrix['total_score']
            
            # Remove the current item from total to avoid part-whole correlation
            adjusted_total = total_scores - responses
            
            if len(set(responses)) > 1:  # Need variance in responses
                correlation, _ = stats.pointbiserialr(responses, adjusted_total)
            else:
                correlation = 0.0
            
            self.item_stats[question] = ItemStatistics(
                question_id=question,
                p_value=p_value,
                discrimination=correlation,
                num_correct=int(num_correct),
                num_attempts=num_attempts
            )
        
        return self.item_stats
    
    def create_student_profiles(self) -> Dict[str, StudentWeaknessProfile]:
        """Create weakness profile for each student."""
        if not self.item_stats:
            self.calculate_item_statistics()
        
        class_avg = self._response_matrix['total_score'].mean()
        
        for student_id, student in self.class_data.students.items():
            # Find questions answered incorrectly
            weak_questions = [
                q for q, score in student.mcq_responses.items() 
                if score == 0
            ]
            
            # Sort by item difficulty (focus on easier questions first)
            weak_questions.sort(
                key=lambda q: self.item_stats[q].p_value, 
                reverse=True
            )
            
            # Calculate performance by difficulty level
            perf_by_diff = self._calculate_performance_by_difficulty(student)
            
            # Calculate overall percentage
            overall_pct = (student.mcq_total / len(self.class_data.mcq_questions)) * 100
            
            # Calculate relative performance
            relative_perf = student.mcq_total / class_avg if class_avg > 0 else 1.0
            
            # Identify focus areas (questions with high p-value that student missed)
            focus_areas = [
                q for q in weak_questions 
                if self.item_stats[q].p_value > 0.5  # Focus on easier questions first
            ][:5]
            
            self.student_profiles[student_id] = StudentWeaknessProfile(
                student_id=student_id,
                weak_questions=weak_questions,
                performance_by_difficulty=perf_by_diff,
                overall_mcq_percentage=overall_pct,
                relative_performance=relative_perf,
                suggested_focus_areas=focus_areas
            )
        
        return self.student_profiles
    
    def _calculate_performance_by_difficulty(self, student: StudentRecord) -> Dict[str, float]:
        """Calculate student's performance on Easy/Medium/Hard questions."""
        performance = {"Easy": [], "Medium": [], "Hard": []}
        
        for q, score in student.mcq_responses.items():
            if q in self.item_stats:
                difficulty = self.item_stats[q].difficulty_level
                performance[difficulty].append(score)
        
        # Calculate percentages
        result = {}
        for level, scores in performance.items():
            if scores:
                result[level] = (sum(scores) / len(scores)) * 100
            else:
                result[level] = 0.0
        
        return result
    
    def identify_weak_items(self, threshold: float = 0.5) -> List[str]:
        """Identify questions where class performance is below threshold."""
        if not self.item_stats:
            self.calculate_item_statistics()
        
        weak_items = [
            q for q, stats in self.item_stats.items()
            if stats.p_value < threshold
        ]
        
        # Sort by p-value (hardest first)
        weak_items.sort(key=lambda q: self.item_stats[q].p_value)
        
        return weak_items
    
    def get_class_summary(self) -> Dict[str, any]:
        """Get summary statistics for the entire class."""
        if self._response_matrix is None:
            self._build_response_matrix()
        
        summary = {
            "num_students": len(self.class_data.students),
            "num_questions": len(self.class_data.mcq_questions),
            "avg_score": self._response_matrix['total_score'].mean(),
            "std_score": self._response_matrix['total_score'].std(),
            "min_score": self._response_matrix['total_score'].min(),
            "max_score": self._response_matrix['total_score'].max(),
            "hardest_questions": self.identify_weak_items()[:5],
            "easiest_questions": sorted(
                self.item_stats.keys(),
                key=lambda q: self.item_stats[q].p_value,
                reverse=True
            )[:5]
        }
        
        return summary
    
    def export_item_analysis(self, output_path: Path) -> None:
        """Export item statistics to CSV."""
        if not self.item_stats:
            self.calculate_item_statistics()
        
        data = []
        for q, stats in self.item_stats.items():
            data.append({
                "Question": q,
                "P-Value": round(stats.p_value, 3),
                "Discrimination": round(stats.discrimination, 3),
                "Difficulty": stats.difficulty_level,
                "Quality": stats.discrimination_quality,
                "Correct": stats.num_correct,
                "Total": stats.num_attempts
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        logger.info(f"Item analysis exported to {output_path}")


if __name__ == "__main__":
    # Test with sample data
    from src.ingestion import DataIngestion
    
    # Load sample data
    data_dir = Path("data")
    if not data_dir.exists():
        print("Please run generate_sample_data.py first!")
    else:
        # Rename sample files if needed
        for old_name, new_name in [
            ("sample_mcq_results.csv", "mcq_results.csv"),
            ("sample_assignments.csv", "assignments.csv"),
            ("sample_participation.csv", "participation.csv")
        ]:
            old_path = data_dir / old_name
            new_path = data_dir / new_name
            if old_path.exists() and not new_path.exists():
                old_path.rename(new_path)
        
        # Load and analyze
        ingestion = DataIngestion(data_dir)
        class_data = ingestion.merge_all_data()
        
        analyzer = WeaknessAnalyzer(class_data)
        analyzer.analyze()
        
        # Show class summary
        summary = analyzer.get_class_summary()
        print("\n📊 Class Summary:")
        print(f"   Students: {summary['num_students']}")
        print(f"   Questions: {summary['num_questions']}")
        print(f"   Average Score: {summary['avg_score']:.1f}")
        print(f"   Std Dev: {summary['std_score']:.1f}")
        print(f"   Range: {summary['min_score']:.0f} - {summary['max_score']:.0f}")
        
        print(f"\n🔴 Hardest Questions: {summary['hardest_questions'][:3]}")
        print(f"🟢 Easiest Questions: {summary['easiest_questions'][:3]}")
        
        # Show sample student profile
        if analyzer.student_profiles:
            sample_id = list(analyzer.student_profiles.keys())[0]
            profile = analyzer.student_profiles[sample_id]
            print(f"\n👤 Sample Student Profile ({sample_id}):")
            print(f"   Overall: {profile.overall_mcq_percentage:.1f}%")
            print(f"   Relative Performance: {profile.relative_performance:.2f}x class avg")
            print(f"   Performance by Difficulty:")
            for level, pct in profile.performance_by_difficulty.items():
                print(f"     - {level}: {pct:.1f}%")
            print(f"   Focus Areas: {profile.suggested_focus_areas}")
        
        # Export item analysis
        analyzer.export_item_analysis(Path("output/item_analysis.csv"))
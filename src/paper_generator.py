"""
Paper Generation System for IGCSE Chemistry Assessment Tool
Creates custom assessment papers based on student performance and topic analysis
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import sys

# Import our topic mapping system
sys.path.append(str(Path(__file__).parent))
from mapping import TopicMapper, Topic


@dataclass
class QuestionSelection:
    """Represents a selected question with metadata"""
    question_id: str
    topic_id: str
    difficulty: str
    points: int
    selection_reason: str
    confidence_score: float


@dataclass
class PaperConfig:
    """Configuration for paper generation"""
    total_questions: int = 20
    total_points: int = 100
    difficulty_distribution: Dict[str, float] = None
    topic_focus: List[str] = None
    paper_type: str = "balanced"  # balanced, weak_focus, comprehensive
    include_answer_key: bool = True
    time_limit_minutes: int = 90
    
    def __post_init__(self):
        if self.difficulty_distribution is None:
            self.difficulty_distribution = {"easy": 0.4, "medium": 0.4, "hard": 0.2}


@dataclass
class GeneratedPaper:
    """Represents a complete generated paper"""
    paper_id: str
    title: str
    questions: List[QuestionSelection]
    config: PaperConfig
    metadata: Dict
    generated_at: str
    total_points: int
    topic_coverage: Dict[str, int]


class QuestionSelector:
    """Handles intelligent question selection algorithms"""
    
    def __init__(self, topic_mapper: TopicMapper):
        self.topic_mapper = topic_mapper
        self.available_questions = self._build_question_pool()
    
    def _build_question_pool(self) -> Dict[str, Dict]:
        """Build a searchable pool of all available questions"""
        question_pool = {}
        
        for topic_id, topic_data in self.topic_mapper.questions.items():
            if isinstance(topic_data, dict) and "questions" in topic_data:
                for question in topic_data["questions"]:
                    question_id = question.get("id")
                    if question_id:
                        # Get topic info
                        mapped_topic = None
                        for mapping in self.topic_mapper.mappings:
                            if mapping.question_id == question_id:
                                mapped_topic = mapping.topic_id
                                break
                        
                        if mapped_topic and mapped_topic in self.topic_mapper.topics:
                            topic_obj = self.topic_mapper.topics[mapped_topic]
                            question_pool[question_id] = {
                                "question_data": question,
                                "topic_id": mapped_topic,
                                "topic_title": topic_obj.title,
                                "difficulty": topic_obj.level,
                                "weight": topic_obj.weight,
                                "keywords": topic_obj.keywords
                            }
        
        return question_pool
    
    def select_by_weak_topics(self, weak_topics: List[str], num_questions: int) -> List[QuestionSelection]:
        """Select questions focusing on weak topics"""
        selections = []
        questions_per_topic = max(1, num_questions // len(weak_topics)) if weak_topics else 0
        
        for topic_id in weak_topics:
            topic_questions = [
                qid for qid, qdata in self.available_questions.items()
                if qdata["topic_id"] == topic_id
            ]
            
            # Select questions from this topic
            selected = random.sample(
                topic_questions, 
                min(questions_per_topic, len(topic_questions))
            )
            
            for qid in selected:
                qdata = self.available_questions[qid]
                selections.append(QuestionSelection(
                    question_id=qid,
                    topic_id=topic_id,
                    difficulty=qdata["difficulty"],
                    points=self._calculate_points(qdata["difficulty"]),
                    selection_reason=f"Weak topic focus: {qdata['topic_title']}",
                    confidence_score=qdata["weight"]
                ))
        
        # Fill remaining slots with balanced selection
        remaining = num_questions - len(selections)
        if remaining > 0:
            excluded_ids = {s.question_id for s in selections}
            balanced_selections = self.select_balanced(remaining, excluded_ids)
            selections.extend(balanced_selections)
        
        return selections[:num_questions]
    
    def select_balanced(self, num_questions: int, excluded_ids: set = None) -> List[QuestionSelection]:
        """Select questions with balanced topic and difficulty distribution"""
        if excluded_ids is None:
            excluded_ids = set()
        
        available = [
            qid for qid in self.available_questions.keys()
            if qid not in excluded_ids
        ]
        
        if len(available) < num_questions:
            available = list(self.available_questions.keys())
        
        # Group by difficulty
        by_difficulty = {"easy": [], "medium": [], "hard": []}
        for qid in available:
            difficulty = self.available_questions[qid]["difficulty"]
            by_difficulty[difficulty].append(qid)
        
        selections = []
        target_easy = int(num_questions * 0.4)
        target_medium = int(num_questions * 0.4)
        target_hard = num_questions - target_easy - target_medium
        
        # Select by difficulty targets
        for difficulty, target in [("easy", target_easy), ("medium", target_medium), ("hard", target_hard)]:
            available_for_difficulty = by_difficulty[difficulty]
            selected_count = min(target, len(available_for_difficulty))
            selected = random.sample(available_for_difficulty, selected_count)
            
            for qid in selected:
                qdata = self.available_questions[qid]
                selections.append(QuestionSelection(
                    question_id=qid,
                    topic_id=qdata["topic_id"],
                    difficulty=difficulty,
                    points=self._calculate_points(difficulty),
                    selection_reason=f"Balanced selection ({difficulty})",
                    confidence_score=qdata["weight"]
                ))
        
        return selections
    
    def select_by_topics(self, target_topics: List[str], num_questions: int) -> List[QuestionSelection]:
        """Select questions from specific topics"""
        selections = []
        questions_per_topic = max(1, num_questions // len(target_topics))
        
        for topic_id in target_topics:
            topic_questions = [
                qid for qid, qdata in self.available_questions.items()
                if qdata["topic_id"] == topic_id
            ]
            
            selected_count = min(questions_per_topic, len(topic_questions))
            if selected_count > 0:
                selected = random.sample(topic_questions, selected_count)
                
                for qid in selected:
                    qdata = self.available_questions[qid]
                    selections.append(QuestionSelection(
                        question_id=qid,
                        topic_id=topic_id,
                        difficulty=qdata["difficulty"],
                        points=self._calculate_points(qdata["difficulty"]),
                        selection_reason=f"Topic focus: {qdata['topic_title']}",
                        confidence_score=qdata["weight"]
                    ))
        
        return selections[:num_questions]
    
    def _calculate_points(self, difficulty: str) -> int:
        """Calculate points based on difficulty"""
        point_mapping = {"easy": 3, "medium": 5, "hard": 7}
        return point_mapping.get(difficulty, 5)


class PaperGenerator:
    """Main paper generation system"""
    
    def __init__(self, topic_mapper: TopicMapper):
        self.topic_mapper = topic_mapper
        self.question_selector = QuestionSelector(topic_mapper)
    
    def generate_paper(self, config: PaperConfig, weak_topics_analysis: Dict = None) -> GeneratedPaper:
        """Generate a complete assessment paper"""
        
        # Determine paper generation strategy
        if config.paper_type == "weak_focus" and weak_topics_analysis:
            questions = self._generate_weak_focus_paper(config, weak_topics_analysis)
        elif config.paper_type == "comprehensive":
            questions = self._generate_comprehensive_paper(config)
        elif config.topic_focus:
            questions = self._generate_topic_focus_paper(config)
        else:
            questions = self._generate_balanced_paper(config)
        
        # Generate paper metadata
        paper_id = f"PAPER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate topic coverage
        topic_coverage = {}
        for q in questions:
            topic_title = self.topic_mapper.topics[q.topic_id].title
            topic_coverage[topic_title] = topic_coverage.get(topic_title, 0) + 1
        
        # Calculate actual total points
        total_points = sum(q.points for q in questions)
        
        paper = GeneratedPaper(
            paper_id=paper_id,
            title=self._generate_title(config),
            questions=questions,
            config=config,
            metadata={
                "generation_strategy": config.paper_type,
                "algorithm_version": "1.0",
                "topic_mapper_version": "day3",
                "question_pool_size": len(self.question_selector.available_questions)
            },
            generated_at=datetime.now().isoformat(),
            total_points=total_points,
            topic_coverage=topic_coverage
        )
        
        return paper
    
    def _generate_weak_focus_paper(self, config: PaperConfig, weak_topics_analysis: Dict) -> List[QuestionSelection]:
        """Generate paper focusing on weak topics"""
        weak_topics = list(weak_topics_analysis.get("weak_topics", {}).keys())
        
        if not weak_topics:
            return self._generate_balanced_paper(config)
        
        # Allocate 70% to weak topics, 30% to balanced
        weak_focus_count = int(config.total_questions * 0.7)
        balanced_count = config.total_questions - weak_focus_count
        
        questions = []
        questions.extend(self.question_selector.select_by_weak_topics(weak_topics, weak_focus_count))
        
        if balanced_count > 0:
            excluded_ids = {q.question_id for q in questions}
            questions.extend(self.question_selector.select_balanced(balanced_count, excluded_ids))
        
        return questions
    
    def _generate_comprehensive_paper(self, config: PaperConfig) -> List[QuestionSelection]:
        """Generate comprehensive paper covering all topics"""
        all_topics = list(self.topic_mapper.topics.keys())
        return self.question_selector.select_by_topics(all_topics, config.total_questions)
    
    def _generate_topic_focus_paper(self, config: PaperConfig) -> List[QuestionSelection]:
        """Generate paper focusing on specific topics"""
        return self.question_selector.select_by_topics(config.topic_focus, config.total_questions)
    
    def _generate_balanced_paper(self, config: PaperConfig) -> List[QuestionSelection]:
        """Generate balanced paper with even distribution"""
        return self.question_selector.select_balanced(config.total_questions)
    
    def _generate_title(self, config: PaperConfig) -> str:
        """Generate appropriate title for the paper"""
        titles = {
            "balanced": "IGCSE Chemistry Practice Paper",
            "weak_focus": "IGCSE Chemistry Focused Review Paper",
            "comprehensive": "IGCSE Chemistry Comprehensive Assessment",
        }
        
        base_title = titles.get(config.paper_type, "IGCSE Chemistry Assessment Paper")
        
        if config.topic_focus:
            topic_names = [self.topic_mapper.topics[tid].title for tid in config.topic_focus if tid in self.topic_mapper.topics]
            if topic_names:
                base_title += f" - {', '.join(topic_names[:2])}"
                if len(topic_names) > 2:
                    base_title += f" and {len(topic_names) - 2} more topics"
        
        return base_title
    
    def export_paper(self, paper: GeneratedPaper, output_dir: str = "output") -> Dict[str, str]:
        """Export paper in multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Export as JSON
        json_file = output_path / f"{paper.paper_id}.json"
        self._export_json(paper, json_file)
        files_created["json"] = str(json_file)
        
        # Export as formatted text
        text_file = output_path / f"{paper.paper_id}.txt"
        self._export_text(paper, text_file)
        files_created["text"] = str(text_file)
        
        # Export answer key if requested
        if paper.config.include_answer_key:
            key_file = output_path / f"{paper.paper_id}_answers.txt"
            self._export_answer_key(paper, key_file)
            files_created["answer_key"] = str(key_file)
        
        # Export paper analysis
        analysis_file = output_path / f"{paper.paper_id}_analysis.json"
        self._export_analysis(paper, analysis_file)
        files_created["analysis"] = str(analysis_file)
        
        return files_created
    
    def _export_json(self, paper: GeneratedPaper, file_path: Path):
        """Export paper as JSON"""
        # Convert to dictionary for JSON serialization
        paper_dict = {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "questions": [asdict(q) for q in paper.questions],
            "config": asdict(paper.config),
            "metadata": paper.metadata,
            "generated_at": paper.generated_at,
            "total_points": paper.total_points,
            "topic_coverage": paper.topic_coverage
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(paper_dict, f, indent=2, ensure_ascii=False)
    
    def _export_text(self, paper: GeneratedPaper, file_path: Path):
        """Export paper as formatted text"""
        content = []
        content.append(f"{paper.title}")
        content.append("=" * len(paper.title))
        content.append(f"Paper ID: {paper.paper_id}")
        content.append(f"Generated: {paper.generated_at}")
        content.append(f"Time Limit: {paper.config.time_limit_minutes} minutes")
        content.append(f"Total Points: {paper.total_points}")
        content.append("")
        
        content.append("INSTRUCTIONS:")
        content.append("- Answer ALL questions")
        content.append("- Write clearly and show your working")
        content.append("- Points for each question are shown in brackets")
        content.append("")
        
        for i, question_sel in enumerate(paper.questions, 1):
            # Get the actual question data
            question_data = None
            for topic_data in self.topic_mapper.questions.values():
                if isinstance(topic_data, dict) and "questions" in topic_data:
                    for q in topic_data["questions"]:
                        if q.get("id") == question_sel.question_id:
                            question_data = q
                            break
                if question_data:
                    break
            
            if question_data:
                content.append(f"Question {i}: [{question_sel.points} marks]")
                content.append(f"{question_data['question']}")
                content.append("")
                
                if "options" in question_data:
                    for option_key, option_text in question_data["options"].items():
                        content.append(f"   {option_key}) {option_text}")
                    content.append("")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def _export_answer_key(self, paper: GeneratedPaper, file_path: Path):
        """Export answer key"""
        content = []
        content.append(f"ANSWER KEY - {paper.title}")
        content.append("=" * (len(paper.title) + 13))
        content.append(f"Paper ID: {paper.paper_id}")
        content.append("")
        
        for i, question_sel in enumerate(paper.questions, 1):
            # Get the actual question data
            question_data = None
            for topic_data in self.topic_mapper.questions.values():
                if isinstance(topic_data, dict) and "questions" in topic_data:
                    for q in topic_data["questions"]:
                        if q.get("id") == question_sel.question_id:
                            question_data = q
                            break
                if question_data:
                    break
            
            if question_data and "correct_answer" in question_data:
                topic_title = self.topic_mapper.topics[question_sel.topic_id].title
                content.append(f"Question {i}: {question_data['correct_answer']} [{question_sel.points} marks]")
                content.append(f"Topic: {topic_title}")
                content.append(f"Difficulty: {question_sel.difficulty}")
                content.append("")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def _export_analysis(self, paper: GeneratedPaper, file_path: Path):
        """Export paper analysis"""
        analysis = {
            "paper_summary": {
                "total_questions": len(paper.questions),
                "total_points": paper.total_points,
                "average_points_per_question": paper.total_points / len(paper.questions) if paper.questions else 0
            },
            "difficulty_breakdown": self._analyze_difficulty(paper.questions),
            "topic_coverage": paper.topic_coverage,
            "selection_reasons": self._analyze_selection_reasons(paper.questions),
            "paper_statistics": {
                "generation_strategy": paper.config.paper_type,
                "config_used": asdict(paper.config),
                "metadata": paper.metadata
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    def _analyze_difficulty(self, questions: List[QuestionSelection]) -> Dict:
        """Analyze difficulty distribution"""
        difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
        difficulty_points = {"easy": 0, "medium": 0, "hard": 0}
        
        for q in questions:
            difficulty_count[q.difficulty] += 1
            difficulty_points[q.difficulty] += q.points
        
        total_questions = len(questions)
        total_points = sum(q.points for q in questions)
        
        return {
            "count_distribution": difficulty_count,
            "points_distribution": difficulty_points,
            "percentage_by_count": {
                diff: (count / total_questions * 100) if total_questions > 0 else 0
                for diff, count in difficulty_count.items()
            },
            "percentage_by_points": {
                diff: (points / total_points * 100) if total_points > 0 else 0
                for diff, points in difficulty_points.items()
            }
        }
    
    def _analyze_selection_reasons(self, questions: List[QuestionSelection]) -> Dict:
        """Analyze why questions were selected"""
        reasons = {}
        for q in questions:
            reason_category = q.selection_reason.split(":")[0]
            reasons[reason_category] = reasons.get(reason_category, 0) + 1
        
        return reasons


# Example usage and testing
if __name__ == "__main__":
    print("Paper Generation System - Test Run")
    
    try:
        # Load topic mapper from Day 3
        from mapping import TopicMapper
        
        mapper = TopicMapper(
            syllabus_path="../data/syllabus_topics.json",
            questions_path="../data/past_questions_bank.json",
            manual_mappings_path="../data/manual_mappings.json"
        )
        mapper.map_all_questions()
        
        # Create paper generator
        generator = PaperGenerator(mapper)
        
        # Test different paper types
        configs = [
            PaperConfig(total_questions=10, paper_type="balanced"),
            PaperConfig(total_questions=8, paper_type="comprehensive"),
            PaperConfig(total_questions=12, paper_type="weak_focus")
        ]
        
        for i, config in enumerate(configs, 1):
            print(f"\nGenerating paper {i}: {config.paper_type}")
            
            # Mock weak topics for testing
            mock_weak_topics = {
                "weak_topics": {
                    "1.1_solids_liquids_gases": {"success_rate": 0.4},
                    "2.4_ionic_bonding": {"success_rate": 0.3}
                }
            }
            
            paper = generator.generate_paper(config, mock_weak_topics)
            files = generator.export_paper(paper)
            
            print(f"✅ Generated '{paper.title}'")
            print(f"   Questions: {len(paper.questions)}")
            print(f"   Points: {paper.total_points}")
            print(f"   Files: {list(files.keys())}")
        
        print(f"\n🎉 Paper generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
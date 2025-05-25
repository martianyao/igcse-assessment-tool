"""
Topic Mapping Engine for IGCSE Chemistry Assessment Tool
Maps questions to syllabus topics automatically with confidence scoring
"""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Topic:
    """Represents a syllabus topic with mapping keywords"""
    id: str
    title: str
    level: str
    keywords: List[str]
    weight: float = 1.0


class QuestionTopicMapping:
    """Maps individual questions to topics with confidence scores"""
    
    def __init__(self, question_id: str, topic_id: str, confidence: float, method: str = "auto"):
        self.question_id = question_id
        self.topic_id = topic_id
        self.confidence = confidence  # 0.0 to 1.0
        self.method = method  # "auto" or "manual"
        
    def to_dict(self):
        return {
            "question_id": self.question_id,
            "topic_id": self.topic_id, 
            "confidence": self.confidence,
            "method": self.method
        }


class TopicMapper:
    """Main class for mapping questions to syllabus topics"""
    
    def __init__(self, syllabus_path: str, questions_path: str, manual_mappings_path: str = None):
        self.topics = self._load_topics(syllabus_path)
        self.questions = self._load_questions(questions_path)
        self.manual_mappings = self._load_manual_mappings(manual_mappings_path)
        self.mappings: List[QuestionTopicMapping] = []
    
    def _load_topics(self, path: str) -> Dict[str, Topic]:
        """Load syllabus topics with keywords"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topics = {}
        
        # Handle different possible structures
        if "chemistry_topics" in data:
            topics_data = data["chemistry_topics"]
        elif "topics" in data:
            topics_data = data["topics"]
        elif "syllabus_topics" in data:
            topics_data = data["syllabus_topics"]
        else:
            # If none of the expected keys, assume the data itself is the topics
            topics_data = data
        
        for topic_id, topic_data in topics_data.items():
            # Handle cases where topic_data might be a string or dict
            if isinstance(topic_data, str):
                topics[topic_id] = Topic(
                    id=topic_id,
                    title=topic_data,
                    level="medium",
                    keywords=[],
                    weight=1.0
                )
            else:
                topics[topic_id] = Topic(
                    id=topic_id,
                    title=topic_data.get("title", topic_data.get("name", topic_id)),
                    level=topic_data.get("level", topic_data.get("difficulty", "medium")),
                    keywords=topic_data.get("keywords", []),
                    weight=topic_data.get("weight", 1.0)
                )
        return topics
    
    def _load_questions(self, path: str) -> Dict:
        """Load questions bank"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different possible structures
        if "chemistry_questions_bank" in data:
            return data["chemistry_questions_bank"]
        elif "questions_bank" in data:
            return data["questions_bank"]
        elif "questions" in data:
            return data["questions"]
        else:
            # If none of the expected keys, assume the data itself is the questions
            return data
    
    def _load_manual_mappings(self, path: str) -> Dict:
        """Load manual topic mappings if available"""
        if not path or not Path(path).exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("manual_topic_mappings", data)
    
    def calculate_topic_confidence(self, question_text: str, topic: Topic) -> float:
        """Calculate confidence score for question-topic mapping"""
        text_lower = question_text.lower()
        
        # Count keyword matches
        matches = 0
        for keyword in topic.keywords:
            if keyword.lower() in text_lower:
                matches += 1
        
        if not topic.keywords:
            # If no keywords, try to match against topic title
            title_words = topic.title.lower().split()
            for word in title_words:
                if len(word) > 3 and word in text_lower:
                    matches += 1
            return min(matches * 0.2, 1.0) if matches > 0 else 0.1
            
        # Base confidence from keyword matches
        confidence = matches / len(topic.keywords)
        
        # Boost confidence for topic title words
        title_words = topic.title.lower().split()
        for word in title_words:
            if word in text_lower and len(word) > 3:  # Ignore short words
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def map_question_to_topics(self, question_id: str, question_data: Dict) -> List[QuestionTopicMapping]:
        """Map a single question to most relevant topics"""
        # Handle different question structures
        if isinstance(question_data, dict):
            if "question" in question_data:
                question_text = question_data["question"]
                if "options" in question_data:
                    question_text += " " + " ".join(question_data["options"].values())
            else:
                question_text = str(question_data)
        else:
            question_text = str(question_data)
        
        # Check for manual mapping first
        if question_id in self.manual_mappings:
            manual_topic = self.manual_mappings[question_id]
            return [QuestionTopicMapping(question_id, manual_topic, 1.0, "manual")]
        
        # Calculate confidence for each topic
        topic_scores = []
        for topic_id, topic in self.topics.items():
            confidence = self.calculate_topic_confidence(question_text, topic)
            if confidence > 0.0:  # Include all non-zero matches
                topic_scores.append((topic_id, confidence))
        
        # Sort by confidence and return mappings
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        
        mappings = []
        for topic_id, confidence in topic_scores:
            mappings.append(QuestionTopicMapping(question_id, topic_id, confidence, "auto"))
        
        return mappings
    
    def map_all_questions(self) -> None:
        """Map all questions to topics"""
        self.mappings = []
        
        for topic_id, topic_questions in self.questions.items():
            # Handle different question structures
            if isinstance(topic_questions, dict) and "questions" in topic_questions:
                questions_list = topic_questions["questions"]
            elif isinstance(topic_questions, list):
                questions_list = topic_questions
            else:
                continue
                
            for question in questions_list:
                if isinstance(question, dict) and "id" in question:
                    question_id = question["id"]
                    mappings = self.map_question_to_topics(question_id, question)
                    self.mappings.extend(mappings)
    
    def aggregate_weak_questions(self, student_results: Dict[str, bool]) -> Dict[str, Dict]:
        """Aggregate weak questions by topic"""
        topic_stats = {}
        
        # Initialize topic stats
        for topic_id in self.topics.keys():
            topic_stats[topic_id] = {
                "title": self.topics[topic_id].title,
                "total_questions": 0,
                "correct_answers": 0,
                "wrong_questions": [],
                "success_rate": 0.0,
                "confidence_sum": 0.0
            }
        
        # Aggregate question results by topic
        for mapping in self.mappings:
            if mapping.confidence > 0.3:  # Only consider high-confidence mappings
                topic_id = mapping.topic_id
                question_id = mapping.question_id
                
                topic_stats[topic_id]["total_questions"] += 1
                topic_stats[topic_id]["confidence_sum"] += mapping.confidence
                
                if student_results.get(question_id, False):
                    topic_stats[topic_id]["correct_answers"] += 1
                else:
                    topic_stats[topic_id]["wrong_questions"].append(question_id)
        
        # Calculate success rates
        for topic_id, stats in topic_stats.items():
            if stats["total_questions"] > 0:
                stats["success_rate"] = stats["correct_answers"] / stats["total_questions"]
                stats["avg_confidence"] = stats["confidence_sum"] / stats["total_questions"]
            else:
                stats["success_rate"] = 0.0
                stats["avg_confidence"] = 0.0
        
        return topic_stats
    
    def export_mappings(self, output_path: str) -> None:
        """Export question-topic mappings to JSON"""
        mappings_data = {
            "mappings": [mapping.to_dict() for mapping in self.mappings],
            "summary": {
                "total_mappings": len(self.mappings),
                "unique_questions": len(set(m.question_id for m in self.mappings)),
                "topics_covered": len(set(m.topic_id for m in self.mappings)),
                "avg_confidence": sum(m.confidence for m in self.mappings) / len(self.mappings) if self.mappings else 0
            }
        }
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings_data, f, indent=2, ensure_ascii=False)
    
    def export_weak_topics_analysis(self, student_results: Dict[str, bool], output_path: str) -> None:
        """Export weak topics analysis"""
        topic_stats = self.aggregate_weak_questions(student_results)
        
        # Identify weak topics (success rate < 60%)
        weak_topics = {
            topic_id: stats for topic_id, stats in topic_stats.items() 
            if stats["success_rate"] < 0.6 and stats["total_questions"] > 0
        }
        
        analysis_data = {
            "weak_topics": weak_topics,
            "all_topics": topic_stats,
            "summary": {
                "total_topics_analyzed": len([t for t in topic_stats.values() if t["total_questions"] > 0]),
                "weak_topics_count": len(weak_topics),
                "overall_success_rate": sum(t["success_rate"] for t in topic_stats.values() if t["total_questions"] > 0) / max(1, len([t for t in topic_stats.values() if t["total_questions"] > 0])),
                "questions_analyzed": sum(len(student_results) for _ in [1])
            }
        }
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)


# Example usage for testing
if __name__ == "__main__":
    print("Topic Mapping Engine - Test Run")
    
    try:
        # Note: Actual file paths would be used in real implementation
        mapper = TopicMapper(
            syllabus_path="data/syllabus_topics.json",
            questions_path="data/past_questions_bank.json",
            manual_mappings_path="data/manual_mappings.json"
        )
        
        # Map all questions
        mapper.map_all_questions()
        print(f"Mapped {len(mapper.mappings)} question-topic associations")
        
        # Sample student results for testing
        sample_results = {
            "SLG_001": True, "SLG_002": False, "SLG_003": True,
            "COS_001": False, "COS_002": True, "COS_003": False,
            "ECM_001": True, "ECM_002": False, "ECM_003": True
        }
        
        # Export results
        mapper.export_mappings("output/question_topic_mappings.json")
        mapper.export_weak_topics_analysis(sample_results, "output/weak_topics_analysis.json")
        
        print("Mapping completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your data file structure.")
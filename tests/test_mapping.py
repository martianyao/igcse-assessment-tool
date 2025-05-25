import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Import from mapping module in src directory
from src.mapping import TopicMapper, Topic, QuestionTopicMapping


class TestTopicMapping(unittest.TestCase):
    """Test cases for topic mapping functionality"""
    
    def setUp(self):
        """Set up test data and temporary files"""
        # Sample syllabus data
        self.test_syllabus = {
            "chemistry_topics": {
                "1.1_solids_liquids_gases": {
                    "title": "Properties and Structure of Solids, Liquids and Gases",
                    "level": "easy",
                    "weight": 1.0,
                    "keywords": ["solid", "liquid", "gas", "particle", "arrangement"]
                },
                "2.4_ionic_bonding": {
                    "title": "Ions and Ionic Bonds", 
                    "level": "medium",
                    "weight": 1.2,
                    "keywords": ["ion", "ionic", "bond", "electron", "charge"]
                }
            }
        }
        
        # Sample questions data
        self.test_questions = {
            "chemistry_questions_bank": {
                "1.1_solids_liquids_gases": {
                    "questions": [
                        {
                            "id": "TEST_001",
                            "question": "Which statement about solid particles is correct?",
                            "options": {
                                "A": "Particles are far apart",
                                "B": "Particles are close together in fixed positions", 
                                "C": "Particles move freely",
                                "D": "Particles have no arrangement"
                            },
                            "correct_answer": "B"
                        }
                    ]
                },
                "2.4_ionic_bonding": {
                    "questions": [
                        {
                            "id": "TEST_002", 
                            "question": "What happens when sodium forms an ionic bond?",
                            "options": {
                                "A": "Gains an electron",
                                "B": "Loses an electron",
                                "C": "Shares electrons", 
                                "D": "No change"
                            },
                            "correct_answer": "B"
                        }
                    ]
                }
            }
        }
        
        # Sample manual mappings
        self.test_manual_mappings = {
            "manual_topic_mappings": {
                "TEST_001": "1.1_solids_liquids_gases"
            }
        }
        
        # Create temporary files
        self.temp_dir = tempfile.mkdtemp()
        
        self.syllabus_path = os.path.join(self.temp_dir, "syllabus.json")
        with open(self.syllabus_path, 'w') as f:
            json.dump(self.test_syllabus, f)
            
        self.questions_path = os.path.join(self.temp_dir, "questions.json") 
        with open(self.questions_path, 'w') as f:
            json.dump(self.test_questions, f)
            
        self.manual_path = os.path.join(self.temp_dir, "manual.json")
        with open(self.manual_path, 'w') as f:
            json.dump(self.test_manual_mappings, f)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_topic_loading(self):
        """Test that topics are loaded correctly"""
        mapper = TopicMapper(self.syllabus_path, self.questions_path)
        
        self.assertEqual(len(mapper.topics), 2)
        self.assertIn("1.1_solids_liquids_gases", mapper.topics)
        self.assertIn("2.4_ionic_bonding", mapper.topics)
        
        topic = mapper.topics["1.1_solids_liquids_gases"]
        self.assertEqual(topic.title, "Properties and Structure of Solids, Liquids and Gases")
        self.assertEqual(topic.level, "easy")
        self.assertIn("solid", topic.keywords)
    
    def test_questions_loading(self):
        """Test that questions are loaded correctly"""
        mapper = TopicMapper(self.syllabus_path, self.questions_path)
        
        self.assertEqual(len(mapper.questions), 2)
        self.assertIn("1.1_solids_liquids_gases", mapper.questions)
        
        questions = mapper.questions["1.1_solids_liquids_gases"]["questions"]
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["id"], "TEST_001")
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        mapper = TopicMapper(self.syllabus_path, self.questions_path)
        topic = mapper.topics["1.1_solids_liquids_gases"]
        
        # Test high confidence match
        high_conf_text = "solid particles are arranged in fixed positions"
        confidence = mapper.calculate_topic_confidence(high_conf_text, topic)
        self.assertGreater(confidence, 0.3)
        
        # Test low confidence match
        low_conf_text = "chemical reaction produces energy"
        confidence = mapper.calculate_topic_confidence(low_conf_text, topic)
        self.assertLess(confidence, 0.3)
    
    def test_question_mapping(self):
        """Test individual question mapping"""
        mapper = TopicMapper(self.syllabus_path, self.questions_path)
        
        question_data = {
            "question": "Which statement about solid particles is correct?",
            "options": {
                "A": "Particles are far apart",
                "B": "Particles are close together in fixed positions"
            }
        }
        
        mappings = mapper.map_question_to_topics("TEST_001", question_data)
        
        self.assertGreater(len(mappings), 0)
        self.assertIsInstance(mappings[0], QuestionTopicMapping)
        self.assertEqual(mappings[0].question_id, "TEST_001")
    
    def test_manual_mapping_override(self):
        """Test that manual mappings override automatic ones"""
        mapper = TopicMapper(self.syllabus_path, self.questions_path, self.manual_path)
        
        question_data = {
            "question": "Test question",
            "options": {"A": "Option A"}
        }
        
        mappings = mapper.map_question_to_topics("TEST_001", question_data)
        
        self.assertEqual(len(mappings), 1)
        self.assertEqual(mappings[0].method, "manual")
        self.assertEqual(mappings[0].confidence, 1.0)
        self.assertEqual(mappings[0].topic_id, "1.1_solids_liquids_gases")


class TestQuestionTopicMapping(unittest.TestCase):
    """Test cases for QuestionTopicMapping class"""
    
    def test_mapping_creation(self):
        """Test creating question-topic mappings"""
        mapping = QuestionTopicMapping("Q001", "topic_1", 0.85, "auto")
        
        self.assertEqual(mapping.question_id, "Q001")
        self.assertEqual(mapping.topic_id, "topic_1")
        self.assertEqual(mapping.confidence, 0.85)
        self.assertEqual(mapping.method, "auto")
    
    def test_mapping_to_dict(self):
        """Test converting mapping to dictionary"""
        mapping = QuestionTopicMapping("Q001", "topic_1", 0.85, "manual")
        mapping_dict = mapping.to_dict()
        
        expected = {
            "question_id": "Q001",
            "topic_id": "topic_1", 
            "confidence": 0.85,
            "method": "manual"
        }
        
        self.assertEqual(mapping_dict, expected)


class TestTopic(unittest.TestCase):
    """Test cases for Topic class"""
    
    def test_topic_creation(self):
        """Test creating topic objects"""
        topic = Topic(
            id="test_topic",
            title="Test Topic",
            level="medium", 
            keywords=["test", "keyword"],
            weight=1.5
        )
        
        self.assertEqual(topic.id, "test_topic")
        self.assertEqual(topic.title, "Test Topic")
        self.assertEqual(topic.level, "medium")
        self.assertEqual(topic.keywords, ["test", "keyword"])
        self.assertEqual(topic.weight, 1.5)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
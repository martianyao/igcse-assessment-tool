"""
Test suite for Paper Generation System
Tests paper generation, question selection, and export functionality
"""

import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Simple path setup
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from paper_generator import PaperGenerator, PaperConfig, QuestionSelector, QuestionSelection
from mapping import TopicMapper, Topic


class TestPaperGenerator(unittest.TestCase):
    """Test cases for paper generation functionality"""
    
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
                    "title": "Ionic Bonding", 
                    "level": "medium",
                    "weight": 1.2,
                    "keywords": ["ion", "ionic", "bond", "electron", "charge"]
                },
                "7.5_oxides_classification": {
                    "title": "Classification of Oxides",
                    "level": "hard",
                    "weight": 1.5,
                    "keywords": ["oxide", "acidic", "basic", "neutral"]
                }
            }
        }
        
        # Sample questions data
        self.test_questions = {
            "chemistry_questions_bank": {
                "1.1_solids_liquids_gases": {
                    "questions": [
                        {
                            "id": "SLG_001",
                            "question": "Which statement about solid particles is correct?",
                            "options": {
                                "A": "Particles are far apart",
                                "B": "Particles are close together in fixed positions", 
                                "C": "Particles move freely",
                                "D": "Particles have no arrangement"
                            },
                            "correct_answer": "B"
                        },
                        {
                            "id": "SLG_002",
                            "question": "What happens to particle arrangement in liquids?",
                            "options": {
                                "A": "Fixed positions",
                                "B": "Random movement", 
                                "C": "Close but mobile",
                                "D": "Far apart"
                            },
                            "correct_answer": "C"
                        }
                    ]
                },
                "2.4_ionic_bonding": {
                    "questions": [
                        {
                            "id": "ION_001", 
                            "question": "What happens when sodium forms an ionic bond?",
                            "options": {
                                "A": "Gains an electron",
                                "B": "Loses an electron",
                                "C": "Shares electrons", 
                                "D": "No change"
                            },
                            "correct_answer": "B"
                        },
                        {
                            "id": "ION_002", 
                            "question": "Which particles are present in ionic compounds?",
                            "options": {
                                "A": "Atoms only",
                                "B": "Molecules only",
                                "C": "Ions only", 
                                "D": "Electrons only"
                            },
                            "correct_answer": "C"
                        }
                    ]
                },
                "7.5_oxides_classification": {
                    "questions": [
                        {
                            "id": "OX_001", 
                            "question": "Which oxide is acidic?",
                            "options": {
                                "A": "CaO",
                                "B": "SO2",
                                "C": "MgO", 
                                "D": "Na2O"
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
                "SLG_001": "1.1_solids_liquids_gases",
                "SLG_002": "1.1_solids_liquids_gases",
                "ION_001": "2.4_ionic_bonding",
                "ION_002": "2.4_ionic_bonding",
                "OX_001": "7.5_oxides_classification"
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
        
        # Create topic mapper and paper generator
        self.mapper = TopicMapper(self.syllabus_path, self.questions_path, self.manual_path)
        self.mapper.map_all_questions()
        self.generator = PaperGenerator(self.mapper)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_paper_config_creation(self):
        """Test paper configuration creation"""
        config = PaperConfig(total_questions=15, paper_type="balanced")
        
        self.assertEqual(config.total_questions, 15)
        self.assertEqual(config.paper_type, "balanced")
        self.assertEqual(config.total_points, 100)
        self.assertTrue(config.include_answer_key)
        self.assertIsNotNone(config.difficulty_distribution)
    
    def test_question_pool_building(self):
        """Test question pool is built correctly"""
        selector = QuestionSelector(self.mapper)
        
        self.assertGreater(len(selector.available_questions), 0)
        
        # Check that questions have required fields
        for qid, qdata in selector.available_questions.items():
            self.assertIn("question_data", qdata)
            self.assertIn("topic_id", qdata)
            self.assertIn("difficulty", qdata)
            self.assertIn("weight", qdata)
    
    def test_balanced_question_selection(self):
        """Test balanced question selection"""
        selector = QuestionSelector(self.mapper)
        selections = selector.select_balanced(3)
        
        self.assertEqual(len(selections), 3)
        
        for selection in selections:
            self.assertIsInstance(selection, QuestionSelection)
            self.assertIsNotNone(selection.question_id)
            self.assertIsNotNone(selection.topic_id)
            self.assertIn(selection.difficulty, ["easy", "medium", "hard"])
            self.assertGreater(selection.points, 0)
    
    def test_weak_topics_selection(self):
        """Test weak topic focused selection"""
        selector = QuestionSelector(self.mapper)
        weak_topics = ["1.1_solids_liquids_gases", "2.4_ionic_bonding"]
        selections = selector.select_by_weak_topics(weak_topics, 3)
        
        self.assertLessEqual(len(selections), 3)
        
        # Check that selections focus on weak topics
        selected_topics = {s.topic_id for s in selections}
        self.assertTrue(selected_topics.intersection(set(weak_topics)))
    
    def test_topic_focus_selection(self):
        """Test topic-focused selection"""
        selector = QuestionSelector(self.mapper)
        target_topics = ["2.4_ionic_bonding"]
        selections = selector.select_by_topics(target_topics, 2)
        
        # All selections should be from target topics
        for selection in selections:
            self.assertIn(selection.topic_id, target_topics)
    
    def test_balanced_paper_generation(self):
        """Test balanced paper generation"""
        config = PaperConfig(total_questions=5, paper_type="balanced")
        paper = self.generator.generate_paper(config)
        
        self.assertEqual(len(paper.questions), 5)
        self.assertGreater(paper.total_points, 0)
        self.assertIsNotNone(paper.paper_id)
        self.assertIn("IGCSE Chemistry", paper.title)
        self.assertEqual(paper.config.paper_type, "balanced")
    
    def test_weak_focus_paper_generation(self):
        """Test weak topic focused paper generation"""
        config = PaperConfig(total_questions=3, paper_type="weak_focus")
        weak_analysis = {
            "weak_topics": {
                "1.1_solids_liquids_gases": {"success_rate": 0.4},
                "2.4_ionic_bonding": {"success_rate": 0.3}
            }
        }
        
        paper = self.generator.generate_paper(config, weak_analysis)
        
        # Test should pass with 3 or fewer questions
        self.assertLessEqual(len(paper.questions), 3)
        self.assertGreater(len(paper.questions), 0)
        self.assertEqual(paper.config.paper_type, "weak_focus")
        
        # Check that weak topics are represented
        selected_topics = {q.topic_id for q in paper.questions}
        weak_topics = set(weak_analysis["weak_topics"].keys())
        self.assertTrue(selected_topics.intersection(weak_topics))
    
    def test_comprehensive_paper_generation(self):
        """Test comprehensive paper generation"""
        config = PaperConfig(total_questions=3, paper_type="comprehensive")
        paper = self.generator.generate_paper(config)
        
        self.assertEqual(len(paper.questions), 3)
        self.assertEqual(paper.config.paper_type, "comprehensive")
    
    def test_topic_coverage_calculation(self):
        """Test topic coverage calculation"""
        config = PaperConfig(total_questions=3, paper_type="balanced")
        paper = self.generator.generate_paper(config)
        
        self.assertIsInstance(paper.topic_coverage, dict)
        
        # Check that coverage adds up to total questions
        total_coverage = sum(paper.topic_coverage.values())
        self.assertEqual(total_coverage, len(paper.questions))
    
    def test_paper_export_json(self):
        """Test JSON export functionality"""
        config = PaperConfig(total_questions=2, paper_type="balanced")
        paper = self.generator.generate_paper(config)
        
        output_dir = tempfile.mkdtemp()
        files = self.generator.export_paper(paper, output_dir)
        
        self.assertIn("json", files)
        
        # Verify JSON file exists and is valid
        json_file = files["json"]
        self.assertTrue(os.path.exists(json_file))
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["paper_id"], paper.paper_id)
        self.assertEqual(len(data["questions"]), len(paper.questions))
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
    
    def test_paper_export_text(self):
        """Test text export functionality"""
        config = PaperConfig(total_questions=2, paper_type="balanced")
        paper = self.generator.generate_paper(config)
        
        output_dir = tempfile.mkdtemp()
        files = self.generator.export_paper(paper, output_dir)
        
        self.assertIn("text", files)
        
        # Verify text file exists and has content
        text_file = files["text"]
        self.assertTrue(os.path.exists(text_file))
        
        with open(text_file, 'r') as f:
            content = f.read()
        
        self.assertIn(paper.title, content)
        self.assertIn("Question 1", content)
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
    
    def test_answer_key_export(self):
        """Test answer key export"""
        config = PaperConfig(total_questions=2, include_answer_key=True)
        paper = self.generator.generate_paper(config)
        
        output_dir = tempfile.mkdtemp()
        files = self.generator.export_paper(paper, output_dir)
        
        self.assertIn("answer_key", files)
        
        # Verify answer key file exists
        key_file = files["answer_key"]
        self.assertTrue(os.path.exists(key_file))
        
        with open(key_file, 'r') as f:
            content = f.read()
        
        self.assertIn("ANSWER KEY", content)
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)


class TestPaperConfiguration(unittest.TestCase):
    """Test cases for paper configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = PaperConfig()
        
        self.assertEqual(config.total_questions, 20)
        self.assertEqual(config.total_points, 100)
        self.assertEqual(config.paper_type, "balanced")
        self.assertTrue(config.include_answer_key)
        self.assertEqual(config.time_limit_minutes, 90)
        self.assertIsNotNone(config.difficulty_distribution)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = PaperConfig(
            total_questions=15,
            paper_type="weak_focus",
            difficulty_distribution={"easy": 0.6, "medium": 0.3, "hard": 0.1}
        )
        
        self.assertEqual(config.total_questions, 15)
        self.assertEqual(config.paper_type, "weak_focus")
        self.assertEqual(config.difficulty_distribution["easy"], 0.6)
    
    def test_config_with_topic_focus(self):
        """Test configuration with topic focus"""
        config = PaperConfig(
            total_questions=10,
            topic_focus=["1.1_solids_liquids_gases", "2.4_ionic_bonding"]
        )
        
        self.assertEqual(len(config.topic_focus), 2)
        self.assertIn("1.1_solids_liquids_gases", config.topic_focus)


class TestQuestionSelection(unittest.TestCase):
    """Test cases for question selection data structure"""
    
    def test_question_selection_creation(self):
        """Test creating question selection objects"""
        selection = QuestionSelection(
            question_id="TEST_001",
            topic_id="1.1_test_topic",
            difficulty="medium",
            points=5,
            selection_reason="Test selection",
            confidence_score=0.8
        )
        
        self.assertEqual(selection.question_id, "TEST_001")
        self.assertEqual(selection.topic_id, "1.1_test_topic")
        self.assertEqual(selection.difficulty, "medium")
        self.assertEqual(selection.points, 5)
        self.assertEqual(selection.selection_reason, "Test selection")
        self.assertEqual(selection.confidence_score, 0.8)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
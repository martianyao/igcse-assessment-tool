"""
Test suite for AI-Powered Analysis Engine
Tests AI integration, question generation, and analysis functionality
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_analyzer import AIAnalyzer, AIResponse, GeminiProvider, create_ai_provider
from mapping import TopicMapper, Topic


class MockAIProvider:
    """Mock AI provider for testing"""
    
    def generate_question(self, topic: dict, difficulty: str) -> AIResponse:
        """Generate mock question"""
        question_data = {
            "question": f"Mock question about {topic['title']}?",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "Mock explanation"
        }
        return AIResponse(
            content=json.dumps(question_data),
            confidence=0.9,
            metadata={"mock": True}
        )
    
    def analyze_performance(self, student_results: dict) -> AIResponse:
        """Generate mock analysis"""
        analysis = "Mock analysis: Student shows good understanding overall."
        return AIResponse(content=analysis, confidence=0.85)
    
    def generate_feedback(self, question: dict, student_answer: str, correct_answer: str) -> AIResponse:
        """Generate mock feedback"""
        if student_answer == correct_answer:
            feedback = "Correct! Well done."
        else:
            feedback = f"Not quite. The correct answer is {correct_answer}."
        return AIResponse(content=feedback, confidence=0.9)
    
    def explain_topic(self, topic: dict, student_level: str) -> AIResponse:
        """Generate mock explanation"""
        explanation = f"Mock explanation for {topic['title']}"
        return AIResponse(content=explanation, confidence=0.85)


class TestAIResponse(unittest.TestCase):
    """Test AIResponse class"""
    
    def test_ai_response_creation(self):
        """Test creating AI response"""
        response = AIResponse(
            content="Test content",
            confidence=0.95,
            metadata={"test": True}
        )
        
        self.assertEqual(response.content, "Test content")
        self.assertEqual(response.confidence, 0.95)
        self.assertEqual(response.metadata["test"], True)
    
    def test_ai_response_to_dict(self):
        """Test converting response to dictionary"""
        response = AIResponse(content="Test", confidence=0.9)
        result = response.to_dict()
        
        self.assertIn("content", result)
        self.assertIn("confidence", result)
        self.assertIn("generated_at", result)
        self.assertEqual(result["content"], "Test")
        self.assertEqual(result["confidence"], 0.9)


class TestAIAnalyzer(unittest.TestCase):
    """Test AI Analyzer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create mock topic mapper
        self.mock_mapper = Mock()
        self.mock_mapper.topics = {
            "1.1_solids_liquids_gases": Mock(
                id="1.1_solids_liquids_gases",
                title="Properties of Solids, Liquids and Gases",
                keywords=["solid", "liquid", "gas"],
                __dict__={
                    "id": "1.1_solids_liquids_gases",
                    "title": "Properties of Solids, Liquids and Gases",
                    "keywords": ["solid", "liquid", "gas"]
                }
            ),
            "2.4_ionic_bonding": Mock(
                id="2.4_ionic_bonding",
                title="Ionic Bonding",
                keywords=["ionic", "bond", "electron"],
                __dict__={
                    "id": "2.4_ionic_bonding",
                    "title": "Ionic Bonding",
                    "keywords": ["ionic", "bond", "electron"]
                }
            )
        }
        
        # Create analyzer with mock provider
        self.mock_provider = MockAIProvider()
        self.analyzer = AIAnalyzer(self.mock_provider, self.mock_mapper)
    
    def test_analyzer_creation(self):
        """Test creating AI analyzer"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.provider, self.mock_provider)
        self.assertEqual(self.analyzer.topic_mapper, self.mock_mapper)
        self.assertEqual(len(self.analyzer.generated_questions), 0)
    
    def test_generate_questions_batch(self):
        """Test generating multiple questions"""
        topics = ["1.1_solids_liquids_gases", "2.4_ionic_bonding"]
        questions = self.analyzer.generate_questions_batch(topics, questions_per_topic=2)
        
        self.assertEqual(len(questions), 4)  # 2 topics × 2 questions
        
        # Check first question
        q1 = questions[0]
        self.assertIn("id", q1)
        self.assertIn("question", q1)
        self.assertIn("options", q1)
        self.assertIn("correct_answer", q1)
        self.assertEqual(q1["topic_id"], "1.1_solids_liquids_gases")
        self.assertTrue(q1["ai_generated"])
    
    def test_analyze_student_performance(self):
        """Test performance analysis"""
        results = {
            "Q1": True,
            "Q2": False,
            "Q3": True,
            "Q4": False
        }
        
        question_mappings = {
            "Q1": Mock(topic_id="1.1_solids_liquids_gases"),
            "Q2": Mock(topic_id="1.1_solids_liquids_gases"),
            "Q3": Mock(topic_id="2.4_ionic_bonding"),
            "Q4": Mock(topic_id="2.4_ionic_bonding")
        }
        
        analysis = self.analyzer.analyze_student_performance(results, question_mappings)
        
        self.assertIn("topic_performance", analysis)
        self.assertIn("ai_analysis", analysis)
        self.assertIn("timestamp", analysis)
        
        # Check topic performance calculations
        perf = analysis["topic_performance"]
        self.assertEqual(perf["1.1_solids_liquids_gases"]["success_rate"], 0.5)
        self.assertEqual(perf["2.4_ionic_bonding"]["success_rate"], 0.5)
    
    def test_generate_study_plan(self):
        """Test study plan generation"""
        weak_topics = ["1.1_solids_liquids_gases", "2.4_ionic_bonding"]
        study_plan = self.analyzer.generate_study_plan(weak_topics, time_available=3)
        
        self.assertEqual(study_plan["duration_days"], 3)
        self.assertIn("daily_plans", study_plan)
        self.assertGreater(len(study_plan["daily_plans"]), 0)
        
        # Check first day plan
        day1 = study_plan["daily_plans"][0]
        self.assertEqual(day1["day"], 1)
        self.assertIn("topics", day1)
        self.assertIn("explanations", day1)
        self.assertIn("practice_time", day1)
    
    def test_export_ai_questions(self):
        """Test exporting generated questions"""
        # Generate some questions first
        self.analyzer.generate_questions_batch(["1.1_solids_liquids_gases"], 2)
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        result_path = self.analyzer.export_ai_questions(filepath)
        
        # Check file exists and contains data
        self.assertTrue(os.path.exists(result_path))
        
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("generated_questions", data)
        self.assertIn("metadata", data)
        self.assertEqual(len(data["generated_questions"]), 2)
        
        # Cleanup
        os.unlink(filepath)


class TestAIProviders(unittest.TestCase):
    """Test AI provider implementations"""
    
    @patch('requests.post')
    def test_gemini_provider_request(self, mock_post):
        """Test Gemini API provider"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '{"question": "Test?", "options": {"A": "A"}, "correct_answer": "A"}'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        provider = GeminiProvider("test_api_key")
        topic = {"title": "Test Topic", "keywords": ["test"]}
        response = provider.generate_question(topic, "easy")
        
        self.assertIsInstance(response, AIResponse)
        self.assertGreater(response.confidence, 0)
        mock_post.assert_called_once()
    
    def test_create_ai_provider_factory(self):
        """Test AI provider factory function"""
        # Test with environment variable
        os.environ["GEMINI_API_KEY"] = "test_key"
        provider = create_ai_provider("gemini")
        self.assertIsInstance(provider, GeminiProvider)
        
        # Test with explicit key
        provider2 = create_ai_provider("gemini", "explicit_key")
        self.assertIsInstance(provider2, GeminiProvider)
        
        # Test invalid provider
        with self.assertRaises(ValueError):
            create_ai_provider("invalid_provider")


class TestIntegration(unittest.TestCase):
    """Integration tests with topic mapper"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data files
        syllabus_data = {
            "chemistry_topics": {
                "1.1_solids_liquids_gases": {
                    "title": "Properties of Solids, Liquids and Gases",
                    "level": "easy",
                    "weight": 1.0,
                    "keywords": ["solid", "liquid", "gas"]
                }
            }
        }
        
        questions_data = {
            "chemistry_questions_bank": {
                "1.1_solids_liquids_gases": {
                    "questions": [{
                        "id": "SLG_001",
                        "question": "Test question?",
                        "options": {"A": "A", "B": "B", "C": "C", "D": "D"},
                        "correct_answer": "A"
                    }]
                }
            }
        }
        
        manual_data = {"manual_topic_mappings": {"SLG_001": "1.1_solids_liquids_gases"}}
        
        # Write test files
        self.syllabus_path = os.path.join(self.temp_dir, "syllabus.json")
        self.questions_path = os.path.join(self.temp_dir, "questions.json")
        self.manual_path = os.path.join(self.temp_dir, "manual.json")
        
        with open(self.syllabus_path, 'w') as f:
            json.dump(syllabus_data, f)
        with open(self.questions_path, 'w') as f:
            json.dump(questions_data, f)
        with open(self.manual_path, 'w') as f:
            json.dump(manual_data, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ai_analyzer_with_topic_mapper(self):
        """Test AI analyzer integrated with topic mapper"""
        # Create real topic mapper
        mapper = TopicMapper(self.syllabus_path, self.questions_path, self.manual_path)
        mapper.map_all_questions()
        
        # Create analyzer with mock provider
        mock_provider = MockAIProvider()
        analyzer = AIAnalyzer(mock_provider, mapper)
        
        # Test question generation
        questions = analyzer.generate_questions_batch(["1.1_solids_liquids_gases"], 1)
        
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["topic_id"], "1.1_solids_liquids_gases")
        self.assertTrue(questions[0]["ai_generated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
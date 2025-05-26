"""
AI-Powered Analysis Engine for IGCSE Chemistry Assessment Tool
Integrates with various AI APIs for intelligent analysis and content generation
"""

import json
import os
import sys
import requests
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AIResponse:
    """Standardized response from AI providers"""
    content: str
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "content": self.content,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "generated_at": self.generated_at
        }


class BaseAIProvider:
    """Base class for AI providers"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.name = "base"
        
    def generate_question(self, topic: Dict[str, Any], difficulty: str = "medium") -> AIResponse:
        """Generate a question for the given topic"""
        raise NotImplementedError
        
    def analyze_performance(self, student_results: Dict[str, Any]) -> AIResponse:
        """Analyze student performance and provide insights"""
        raise NotImplementedError
        
    def generate_feedback(self, question: Dict[str, Any], student_answer: str, correct_answer: str) -> AIResponse:
        """Generate personalized feedback for a student answer"""
        raise NotImplementedError
        
    def explain_topic(self, topic: Dict[str, Any], student_level: str = "medium") -> AIResponse:
        """Generate topic explanation for student level"""
        raise NotImplementedError


class MockAIProvider(BaseAIProvider):
    """Mock AI provider for testing and demonstration purposes"""
    
    def __init__(self):
        super().__init__()
        self.name = "mock"
        self.model = "mock-model"
    
    def generate_question(self, topic: Dict[str, Any], difficulty: str = "medium") -> AIResponse:
        """Generate mock question for testing"""
        topic_title = topic.get("title", "Unknown Topic")
        topic_id = topic.get("id", "unknown")
        
        question_data = {
            "question": f"What are the key properties of {topic_title.lower()}?",
            "options": {
                "A": f"Property A related to {topic_title}",
                "B": f"Property B related to {topic_title}",
                "C": f"Property C related to {topic_title}",
                "D": f"Property D related to {topic_title}"
            },
            "correct_answer": "A",
            "explanation": f"This is a mock explanation for {topic_title}. The correct answer demonstrates understanding of the fundamental concepts."
        }
        
        return AIResponse(
            content=json.dumps(question_data),
            confidence=0.9,
            metadata={"topic_id": topic_id, "difficulty": difficulty, "mock": True}
        )
    
    def analyze_performance(self, student_results: Dict[str, Any]) -> AIResponse:
        """Generate mock performance analysis"""
        total_correct = sum(1 for result in student_results.values() if result)
        total_questions = len(student_results)
        percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        analysis = f"""Mock Performance Analysis:
        
Score: {total_correct}/{total_questions} ({percentage:.1f}%)

Strengths:
- Shows good understanding of basic concepts
- Consistent performance across topics

Areas for Improvement:
- Practice more complex problem-solving
- Review fundamental principles
- Focus on application questions

Recommendations:
- Spend 30 minutes daily on weak topics
- Use active recall techniques
- Practice past paper questions
"""
        
        return AIResponse(
            content=analysis,
            confidence=0.85,
            metadata={"total_questions": total_questions, "score": percentage}
        )
    
    def generate_feedback(self, question: Dict[str, Any], student_answer: str, correct_answer: str) -> AIResponse:
        """Generate mock feedback"""
        if student_answer.upper() == correct_answer.upper():
            feedback = "Excellent! You've demonstrated a clear understanding of this concept. Well done!"
        else:
            feedback = f"Not quite right. The correct answer is {correct_answer}. This concept relates to the fundamental principles we've studied. Try reviewing the key points and attempt similar questions."
        
        return AIResponse(
            content=feedback,
            confidence=0.9,
            metadata={"student_answer": student_answer, "correct_answer": correct_answer}
        )
    
    def explain_topic(self, topic: Dict[str, Any], student_level: str = "medium") -> AIResponse:
        """Generate mock topic explanation"""
        topic_title = topic.get("title", "Unknown Topic")
        
        explanations = {
            "easy": f"Basic Overview of {topic_title}:\n\n{topic_title} is a fundamental concept in chemistry. It involves understanding the basic properties and behaviors that are essential for further study.",
            "medium": f"Understanding {topic_title}:\n\n{topic_title} represents an important principle in chemistry. This concept builds on basic knowledge and introduces more complex relationships between different chemical properties and processes.",
            "hard": f"Advanced Analysis of {topic_title}:\n\n{topic_title} is a sophisticated topic that requires deep understanding of underlying chemical principles. It involves complex interactions and advanced applications in real-world scenarios."
        }
        
        explanation = explanations.get(student_level, explanations["medium"])
        explanation += "\n\n(This is a mock explanation for demonstration purposes.)"
        
        return AIResponse(
            content=explanation,
            confidence=0.85,
            metadata={"topic": topic_title, "level": student_level}
        )
    
    def generate_questions(self, topic_id: str, num_questions: int = 5) -> List[Dict]:
        """Generate multiple mock questions for batch processing"""
        mock_questions = []
        
        sample_templates = [
            {
                "template": "What are the properties of {topic}?",
                "options": ["Strong properties", "Weak properties", "Variable properties", "No properties"],
                "correct": 0,
                "explanation": "This demonstrates the key characteristics."
            },
            {
                "template": "How does {topic} relate to chemical bonding?",
                "options": ["Direct relationship", "Inverse relationship", "No relationship", "Complex relationship"],
                "correct": 1,
                "explanation": "The relationship depends on molecular structure."
            },
            {
                "template": "Which statement about {topic} is most accurate?",
                "options": ["Statement A", "Statement B", "Statement C", "Statement D"],
                "correct": 2,
                "explanation": "This statement correctly describes the concept."
            }
        ]
        
        topic_display = topic_id.replace('_', ' ').title()
        
        for i in range(min(num_questions, len(sample_templates) * 2)):
            template = sample_templates[i % len(sample_templates)]
            
            question = {
                "id": f"mock_{topic_id}_{i+1}",
                "question": template["template"].format(topic=topic_display),
                "options": template["options"],
                "correct_answer": chr(65 + template["correct"]),  # A, B, C, D
                "explanation": template["explanation"],
                "difficulty": ["easy", "medium", "hard"][i % 3],
                "topic_id": topic_id,
                "ai_generated": True
            }
            mock_questions.append(question)
        
        return mock_questions
    
    def analyze_student_performance(self, student_results: List[Dict], question_mappings: Dict) -> Dict:
        """Generate comprehensive mock performance analysis"""
        # Calculate basic statistics
        total_questions = len(student_results)
        if total_questions == 0:
            return {"error": "No results to analyze"}
        
        correct_answers = sum(1 for result in student_results if result.get('correct', False))
        overall_score = (correct_answers / total_questions) * 100
        
        # Analyze by topic
        topic_performance = {}
        for result in student_results:
            topic = result.get('topic_id', 'unknown')
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0, 'questions': []}
            
            topic_performance[topic]['total'] += 1
            topic_performance[topic]['questions'].append(result)
            if result.get('correct', False):
                topic_performance[topic]['correct'] += 1
        
        # Calculate success rates
        for topic in topic_performance:
            perf = topic_performance[topic]
            perf['success_rate'] = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
        
        # Identify weak and strong topics
        weak_topics = [topic for topic, perf in topic_performance.items() 
                      if perf['success_rate'] < 0.6]
        strong_topics = [topic for topic, perf in topic_performance.items() 
                        if perf['success_rate'] > 0.8]
        
        return {
            "overall_score": round(overall_score, 1),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "topic_performance": {topic: {
                'correct': perf['correct'],
                'total': perf['total'], 
                'success_rate': round(perf['success_rate'], 2)
            } for topic, perf in topic_performance.items()},
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "recommendations": [
                "Focus on weak topics for improvement",
                "Practice more questions in challenging areas",
                "Review fundamental concepts",
                "Use active learning techniques"
            ],
            "analysis_type": "mock_analysis",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_study_plan(self, weak_topics: List[str], days: int = 7) -> Dict:
        """Generate comprehensive mock study plan"""
        daily_plans = []
        
        for day in range(1, days + 1):
            if weak_topics:
                # Rotate through weak topics
                primary_topic = weak_topics[(day - 1) % len(weak_topics)]
                secondary_topics = [t for t in weak_topics if t != primary_topic][:2]
                
                daily_plan = {
                    "day": day,
                    "primary_topic": primary_topic,
                    "secondary_topics": secondary_topics,
                    "activities": [
                        f"Deep dive into {primary_topic.replace('_', ' ')}",
                        f"Practice 8-10 questions on {primary_topic.replace('_', ' ')}",
                        "Review previous day's material",
                        "Create concept maps or summaries"
                    ],
                    "estimated_time": "60-75 minutes",
                    "focus_areas": [
                        "Understanding core concepts",
                        "Practicing problem-solving",
                        "Making connections between topics"
                    ]
                }
            else:
                daily_plan = {
                    "day": day,
                    "primary_topic": "general_review",
                    "secondary_topics": [],
                    "activities": [
                        "Review mixed topics",
                        "Practice past paper questions",
                        "Consolidate knowledge"
                    ],
                    "estimated_time": "45-60 minutes",
                    "focus_areas": ["Comprehensive review"]
                }
            
            daily_plans.append(daily_plan)
        
        return {
            "total_days": days,
            "weak_topics": weak_topics,
            "daily_plans": daily_plans,
            "study_tips": [
                "Set specific daily goals",
                "Use active recall and spaced repetition",
                "Practice with timer for exam conditions",
                "Review mistakes immediately",
                "Connect new learning to existing knowledge"
            ],
            "success_metrics": [
                "Complete daily activities",
                "Improve accuracy on weak topics",
                "Reduce time per question",
                "Increase confidence levels"
            ],
            "plan_type": "mock_comprehensive_plan",
            "generated_at": datetime.now().isoformat()
        }


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "gemini"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.headers = {"Content-Type": "application/json"}
    
    def _make_request(self, prompt: str) -> AIResponse:
        """Make request to Gemini API"""
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                
                return AIResponse(
                    content=content,
                    confidence=0.85,
                    metadata={"provider": "gemini", "status": "success"}
                )
            else:
                return AIResponse(
                    content=f"API Error: {response.status_code}",
                    confidence=0.0,
                    metadata={"provider": "gemini", "status": "error", "error": response.text}
                )
                
        except Exception as e:
            return AIResponse(
                content=f"Request failed: {str(e)}",
                confidence=0.0,
                metadata={"provider": "gemini", "status": "error", "error": str(e)}
            )
    
    def generate_question(self, topic: Dict[str, Any], difficulty: str = "medium") -> AIResponse:
        """Generate question using Gemini"""
        topic_title = topic.get("title", "Unknown Topic")
        keywords = ", ".join(topic.get("keywords", []))
        
        prompt = f"""
Generate a multiple choice question for IGCSE Chemistry on the topic: {topic_title}

Topic keywords: {keywords}
Difficulty level: {difficulty}

Please provide the response in this exact JSON format:
{{
    "question": "Your question here?",
    "options": {{
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
}}

Make sure the question is appropriate for IGCSE level and tests understanding of the concept.
"""
        
        return self._make_request(prompt)
    
    def analyze_performance(self, student_results: Dict[str, Any]) -> AIResponse:
        """Analyze performance using Gemini"""
        prompt = f"""
Analyze this student's performance on an IGCSE Chemistry assessment:

Results: {json.dumps(student_results, indent=2)}

Please provide:
1. Overall performance summary
2. Strengths identified
3. Areas needing improvement
4. Specific study recommendations
5. Next steps for improvement

Keep the analysis constructive and actionable for a student preparing for IGCSE Chemistry.
"""
        
        return self._make_request(prompt)
    
    def generate_feedback(self, question: Dict[str, Any], student_answer: str, correct_answer: str) -> AIResponse:
        """Generate feedback using Gemini"""
        prompt = f"""
A student answered a question incorrectly. Please provide helpful feedback.

Question: {question.get('question', 'N/A')}
Student's answer: {student_answer}
Correct answer: {correct_answer}
Explanation: {question.get('explanation', 'N/A')}

Provide encouraging, specific feedback that:
1. Acknowledges their attempt
2. Explains why their answer was incorrect (if applicable)
3. Clarifies the correct concept
4. Suggests how to approach similar questions

Keep it supportive and educational for an IGCSE student.
"""
        
        return self._make_request(prompt)
    
    def explain_topic(self, topic: Dict[str, Any], student_level: str = "medium") -> AIResponse:
        """Generate topic explanation using Gemini"""
        topic_title = topic.get("title", "Unknown Topic")
        keywords = ", ".join(topic.get("keywords", []))
        
        prompt = f"""
Explain the IGCSE Chemistry topic: {topic_title}

Key concepts: {keywords}
Student level: {student_level}

Please provide a clear, comprehensive explanation that:
1. Introduces the topic with simple terms
2. Explains key concepts and principles
3. Provides relevant examples
4. Connects to other chemistry topics where appropriate
5. Includes practical applications

Tailor the complexity to {student_level} level understanding.
"""
        
        return self._make_request(prompt)


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider (placeholder implementation)"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "openai"
        # Implementation would go here
        # For now, fall back to mock behavior
        self.mock_provider = MockAIProvider()
    
    def generate_question(self, topic: Dict[str, Any], difficulty: str = "medium") -> AIResponse:
        """Generate question using OpenAI (placeholder)"""
        # Placeholder - would implement OpenAI API calls here
        return self.mock_provider.generate_question(topic, difficulty)
    
    def analyze_performance(self, student_results: Dict[str, Any]) -> AIResponse:
        """Analyze performance using OpenAI (placeholder)"""
        return self.mock_provider.analyze_performance(student_results)
    
    def generate_feedback(self, question: Dict[str, Any], student_answer: str, correct_answer: str) -> AIResponse:
        """Generate feedback using OpenAI (placeholder)"""
        return self.mock_provider.generate_feedback(question, student_answer, correct_answer)
    
    def explain_topic(self, topic: Dict[str, Any], student_level: str = "medium") -> AIResponse:
        """Generate topic explanation using OpenAI (placeholder)"""
        return self.mock_provider.explain_topic(topic, student_level)


class AIAnalyzer:
    """Main AI-powered analysis engine"""
    
    def __init__(self, provider: BaseAIProvider, topic_mapper):
        self.provider = provider
        self.topic_mapper = topic_mapper
        self.generated_questions = []
        self.analysis_history = []
    
    def generate_questions_batch(self, topic_ids: List[str], questions_per_topic: int = 5) -> List[Dict[str, Any]]:
        """Generate multiple questions for given topics"""
        all_questions = []
        
        for topic_id in topic_ids:
            if topic_id in self.topic_mapper.topics:
                topic = self.topic_mapper.topics[topic_id]
                topic_dict = {
                    "id": topic_id,
                    "title": topic.title if hasattr(topic, 'title') else str(topic),
                    "keywords": getattr(topic, 'keywords', [])
                }
                
                # Use mock provider's batch method if available
                if hasattr(self.provider, 'generate_questions'):
                    questions = self.provider.generate_questions(topic_id, questions_per_topic)
                    all_questions.extend(questions)
                else:
                    # Generate one by one
                    for i in range(questions_per_topic):
                        try:
                            response = self.provider.generate_question(topic_dict)
                            if response.content and response.confidence > 0:
                                try:
                                    question_data = json.loads(response.content)
                                    question_data.update({
                                        "id": f"ai_{topic_id}_{i+1}_{uuid.uuid4().hex[:8]}",
                                        "topic_id": topic_id,
                                        "ai_generated": True,
                                        "confidence": response.confidence,
                                        "generated_at": response.generated_at
                                    })
                                    all_questions.append(question_data)
                                except json.JSONDecodeError:
                                    print(f"Failed to parse AI response for {topic_id}")
                        except Exception as e:
                            print(f"Error generating question for {topic_id}: {e}")
        
        # Store generated questions
        self.generated_questions.extend(all_questions)
        return all_questions
    
    def analyze_student_performance(self, student_results: Dict[str, Any], question_mappings: Dict) -> Dict[str, Any]:
        """Analyze student performance with AI insights"""
        
        # Use provider's analysis method if available
        if hasattr(self.provider, 'analyze_student_performance'):
            # Convert to format expected by mock provider
            results_list = []
            for question_id, correct in student_results.items():
                if question_id in question_mappings:
                    topic_id = getattr(question_mappings[question_id], 'topic_id', 'unknown')
                    results_list.append({
                        'question_id': question_id,
                        'correct': correct,
                        'topic_id': topic_id
                    })
            
            analysis = self.provider.analyze_student_performance(results_list, question_mappings)
            if isinstance(analysis, dict):
                analysis["ai_analysis"] = "Generated using AI provider"
                analysis["timestamp"] = datetime.now().isoformat()
                self.analysis_history.append(analysis)
                return analysis
        
        # Fallback to basic analysis
        total_questions = len(student_results)
        correct_answers = sum(1 for result in student_results.values() if result)
        
        # Calculate topic performance
        topic_performance = {}
        for question_id, correct in student_results.items():
            if question_id in question_mappings:
                topic_id = getattr(question_mappings[question_id], 'topic_id', 'unknown')
                if topic_id not in topic_performance:
                    topic_performance[topic_id] = {"correct": 0, "total": 0}
                
                topic_performance[topic_id]["total"] += 1
                if correct:
                    topic_performance[topic_id]["correct"] += 1
        
        # Calculate success rates
        for topic_id in topic_performance:
            perf = topic_performance[topic_id]
            perf["success_rate"] = perf["correct"] / perf["total"] if perf["total"] > 0 else 0
        
        # Get AI analysis
        ai_response = self.provider.analyze_performance(student_results)
        
        analysis = {
            "overall_score": round((correct_answers / total_questions) * 100, 1) if total_questions > 0 else 0,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "topic_performance": topic_performance,
            "ai_analysis": ai_response.content,
            "confidence": ai_response.confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    def generate_study_plan(self, weak_topics: List[str], time_available: int = 7) -> Dict[str, Any]:
        """Generate personalized study plan"""
        if hasattr(self.provider, 'generate_study_plan'):
            return self.provider.generate_study_plan(weak_topics, time_available)
        
        # Basic study plan generation
        daily_plans = []
        topics_per_day = max(1, len(weak_topics) // time_available) if weak_topics else 1
        
        for day in range(1, time_available + 1):
            if weak_topics:
                start_idx = (day - 1) * topics_per_day
                end_idx = min(start_idx + topics_per_day, len(weak_topics))
                day_topics = weak_topics[start_idx:end_idx]
                
                # Get AI explanations for topics
                explanations = {}
                for topic_id in day_topics:
                    if topic_id in self.topic_mapper.topics:
                        topic = self.topic_mapper.topics[topic_id]
                        topic_dict = {
                            "title": getattr(topic, 'title', topic_id),
                            "keywords": getattr(topic, 'keywords', [])
                        }
                        explanation = self.provider.explain_topic(topic_dict, "medium")
                        explanations[topic_id] = explanation.content
                
                daily_plans.append({
                    "day": day,
                    "topics": day_topics,
                    "explanations": explanations,
                    "practice_time": "45-60 minutes",
                    "activities": [
                        "Read topic explanations",
                        "Practice 5-8 questions per topic",
                        "Review incorrect answers",
                        "Create summary notes"
                    ]
                })
        
        return {
            "duration_days": time_available,
            "total_days": time_available,  # Add both keys for compatibility
            "weak_topics": weak_topics,
            "daily_plans": daily_plans,
            "overall_strategy": "Focus on understanding concepts before memorization",
            "generated_at": datetime.now().isoformat()
        }
    
    def export_ai_questions(self, filepath: str) -> str:
        """Export generated questions to file"""
        export_data = {
            "generated_questions": self.generated_questions,
            "total_questions": len(self.generated_questions),
            "metadata": {
                "provider": self.provider.name,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # Ensure .json extension
        if not filepath.endswith('.json'):
            filepath += '.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_topic_explanation(self, topic_id: str, student_level: str = "medium") -> str:
        """Get AI explanation for a specific topic"""
        if topic_id in self.topic_mapper.topics:
            topic = self.topic_mapper.topics[topic_id]
            topic_dict = {
                "title": getattr(topic, 'title', topic_id),
                "keywords": getattr(topic, 'keywords', [])
            }
            
            response = self.provider.explain_topic(topic_dict, student_level)
            return response.content
        
        return f"Topic {topic_id} not found in topic mapper."


def create_ai_provider(provider_type: str = "mock", api_key: str = None, **kwargs) -> BaseAIProvider:
    """Factory function to create AI provider instances"""
    
    if provider_type.lower() == "mock":
        return MockAIProvider()
    
    elif provider_type.lower() == "gemini":
        api_key = api_key or kwargs.get('api_key') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Warning: No Gemini API key found. Using mock provider instead.")
            return MockAIProvider()
        
        try:
            return GeminiProvider(api_key)
        except Exception as e:
            print(f"Error setting up Gemini provider: {e}. Using mock provider instead.")
            return MockAIProvider()
    
    elif provider_type.lower() == "openai":
        api_key = api_key or kwargs.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: No OpenAI API key found. Using mock provider instead.")
            return MockAIProvider()
        
        try:
            return OpenAIProvider(api_key)
        except Exception as e:
            print(f"Error setting up OpenAI provider: {e}. Using mock provider instead.")
            return MockAIProvider()
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Supported types: mock, gemini, openai")


# Utility functions
def validate_api_key(provider_type: str, api_key: str) -> bool:
    """Validate API key for given provider"""
    if provider_type.lower() == "mock":
        return True
    
    if not api_key:
        return False
    
    # Basic validation (real validation would test actual API calls)
    if provider_type.lower() == "gemini":
        return api_key.startswith("AIza") and len(api_key) > 20
    elif provider_type.lower() == "openai":
        return api_key.startswith("sk-") and len(api_key) > 40
    
    return False


def get_available_providers() -> List[str]:
    """Get list of available AI providers"""
    return ["mock", "gemini", "openai"]


# Example usage and testing
if __name__ == "__main__":
    # Test with mock provider
    print("Testing AI Analyzer with Mock Provider...")
    
    mock_provider = create_ai_provider("mock")
    print(f"Created provider: {mock_provider.name}")
    
    # Test question generation
    test_topic = {
        "id": "1.1_solids_liquids_gases",
        "title": "Properties of Solids, Liquids and Gases",
        "keywords": ["solid", "liquid", "gas", "particle", "movement"]
    }
    
    response = mock_provider.generate_question(test_topic)
    print(f"Generated question: {response.content[:100]}...")
    
    # Test performance analysis
    test_results = {"Q1": True, "Q2": False, "Q3": True, "Q4": True}
    analysis = mock_provider.analyze_performance(test_results)
    print(f"Performance analysis: {analysis.content[:100]}...")
    
    print("AI Analyzer testing completed successfully!")
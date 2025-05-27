"""
Day 6: Enhanced AI Analyzer for Comprehensive Performance Analysis
Simplified but functional AI analysis system
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class StudentAnalysis:
    """Individual student analysis data"""
    student_id: int
    student_name: str
    test_score: int
    test_percentage: float
    engagement_rate: int
    preparation_outcome: str
    in_class_practice: str
    additional_notes: str = ""

class EnhancedMockAIProvider:
    """Mock AI provider for Day 6 comprehensive analysis"""
    
    def analyze_comprehensive_performance(self, analyses: List[StudentAnalysis]) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        
        individual_results = []
        
        for analysis in analyses:
            # Analyze individual student
            result = self._analyze_student(analysis)
            individual_results.append(result)
        
        # Generate class insights
        class_insights = self._generate_class_insights(analyses)
        
        # Identify intervention priorities
        interventions = self._identify_interventions(analyses)
        
        return {
            "individual_analyses": individual_results,
            "class_insights": class_insights,
            "intervention_priorities": interventions,
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "day6_comprehensive"
        }
    
    def _analyze_student(self, analysis: StudentAnalysis) -> Dict[str, Any]:
        """Analyze individual student performance"""
        
        # Categorize performance
        if analysis.test_percentage >= 85:
            performance_level = "Excellent"
        elif analysis.test_percentage >= 75:
            performance_level = "Good"
        elif analysis.test_percentage >= 65:
            performance_level = "Satisfactory"
        elif analysis.test_percentage >= 50:
            performance_level = "Needs Improvement"
        else:
            performance_level = "Significant Concerns"
        
        # Categorize engagement
        if analysis.engagement_rate >= 8:
            engagement_level = "Exemplary"
        elif analysis.engagement_rate >= 6:
            engagement_level = "High"
        elif analysis.engagement_rate >= 4:
            engagement_level = "Moderate"
        elif analysis.engagement_rate >= 2:
            engagement_level = "Low"
        else:
            engagement_level = "Disengaged"
        
        # Predict IGCSE grade
        predicted_grade = self._predict_grade(
            analysis.test_percentage,
            analysis.engagement_rate,
            analysis.preparation_outcome,
            analysis.in_class_practice
        )
        
        # Generate insights
        insights = self._generate_insights(analysis)
        
        # Recommend interventions
        interventions = self._recommend_interventions(analysis)
        
        return {
            "student_id": analysis.student_id,
            "student_name": analysis.student_name,
            "performance_summary": {
                "test_percentage": analysis.test_percentage,
                "performance_level": performance_level,
                "engagement_level": engagement_level,
                "predicted_igcse_grade": predicted_grade
            },
            "detailed_analysis": {
                "engagement_rate": f"{analysis.engagement_rate}/9",
                "preparation_outcome": analysis.preparation_outcome.title(),
                "in_class_practice": analysis.in_class_practice.title(),
                "correlation": self._analyze_correlation(analysis)
            },
            "insights": insights,
            "interventions": interventions
        }
    
    def _predict_grade(self, test_perc: float, engagement: int, prep: str, practice: str) -> str:
        """Predict IGCSE grade using weighted factors"""
        
        # Convert attainment to scores
        attainment_scores = {"emerging": 25, "developing": 50, "secure": 75, "mastery": 95}
        prep_score = attainment_scores.get(prep, 50)
        practice_score = attainment_scores.get(practice, 50)
        engagement_score = (engagement / 9) * 100
        
        # Weighted average
        overall_score = (
            test_perc * 0.4 +
            engagement_score * 0.3 +
            prep_score * 0.15 +
            practice_score * 0.15
        )
        
        # Map to IGCSE grades
        if overall_score >= 90: return "A* (9)"
        elif overall_score >= 80: return "A (8)"
        elif overall_score >= 70: return "B (7)"
        elif overall_score >= 60: return "C (6)"
        elif overall_score >= 50: return "D (5)"
        else: return "E-G (1-4)"
    
    def _generate_insights(self, analysis: StudentAnalysis) -> List[str]:
        """Generate personalized insights"""
        insights = []
        
        if analysis.test_percentage >= 80 and analysis.engagement_rate >= 7:
            insights.append("🌟 Excellent overall performance - maintain current approach")
        elif analysis.test_percentage < 60 and analysis.engagement_rate <= 4:
            insights.append("⚠️ Requires comprehensive support across all areas")
        elif analysis.test_percentage >= 75 and analysis.engagement_rate <= 4:
            insights.append("💡 Strong academically but needs engagement strategies")
        
        # Attainment insights
        prep_levels = {"emerging": 1, "developing": 2, "secure": 3, "mastery": 4}
        prep_level = prep_levels.get(analysis.preparation_outcome, 2)
        practice_level = prep_levels.get(analysis.in_class_practice, 2)
        
        if prep_level > practice_level + 1:
            insights.append("📚 Strong preparation but struggles in class application")
        elif practice_level > prep_level + 1:
            insights.append("🏫 Good in class but needs better preparation habits")
        
        return insights
    
    def _recommend_interventions(self, analysis: StudentAnalysis) -> List[Dict[str, str]]:
        """Recommend specific interventions"""
        interventions = []
        
        if analysis.test_percentage < 60:
            interventions.append({
                "type": "Academic Support",
                "action": "One-to-one tutoring focusing on weak areas",
                "priority": "High",
                "timeline": "Immediate"
            })
        
        if analysis.engagement_rate <= 4:
            interventions.append({
                "type": "Engagement Strategy",
                "action": "Implement interactive teaching methods",
                "priority": "High",
                "timeline": "Next lesson"
            })
        
        if analysis.preparation_outcome in ["emerging", "developing"]:
            interventions.append({
                "type": "Study Skills",
                "action": "Teach effective revision techniques",
                "priority": "Medium",
                "timeline": "This week"
            })
        
        return interventions
    
    def _analyze_correlation(self, analysis: StudentAnalysis) -> str:
        """Analyze correlation between metrics"""
        expected_perc = (analysis.engagement_rate / 9) * 85
        gap = analysis.test_percentage - expected_perc
        
        if abs(gap) <= 10:
            return "Strong alignment between engagement and performance"
        elif gap > 10:
            return "Performance exceeds engagement expectations"
        else:
            return "Performance below engagement potential"
    
    def _generate_class_insights(self, analyses: List[StudentAnalysis]) -> Dict[str, Any]:
        """Generate class-wide insights"""
        if not analyses:
            return {}
        
        avg_test = sum(a.test_percentage for a in analyses) / len(analyses)
        avg_engagement = sum(a.engagement_rate for a in analyses) / len(analyses)
        
        # Count engagement distribution
        high_engagement = sum(1 for a in analyses if a.engagement_rate >= 7)
        medium_engagement = sum(1 for a in analyses if 4 <= a.engagement_rate < 7)
        low_engagement = sum(1 for a in analyses if a.engagement_rate < 4)
        
        return {
            "class_size": len(analyses),
            "averages": {
                "test_score": f"{avg_test:.1f}%",
                "engagement": f"{avg_engagement:.1f}/9"
            },
            "engagement_distribution": {
                "high": high_engagement,
                "medium": medium_engagement,
                "low": low_engagement
            },
            "key_insights": [
                f"Class average: {avg_test:.1f}% test score, {avg_engagement:.1f}/9 engagement",
                f"Engagement levels: {high_engagement} high, {medium_engagement} medium, {low_engagement} low"
            ]
        }
    
    def _identify_interventions(self, analyses: List[StudentAnalysis]) -> List[Dict[str, Any]]:
        """Identify students needing intervention"""
        priorities = []
        
        for analysis in analyses:
            risk_score = 0
            risk_factors = []
            
            if analysis.test_percentage < 50:
                risk_score += 3
                risk_factors.append("Low academic performance")
            
            if analysis.engagement_rate <= 3:
                risk_score += 2
                risk_factors.append("Very low engagement")
            
            if analysis.preparation_outcome == "emerging":
                risk_score += 1
                risk_factors.append("Poor preparation")
            
            if risk_score >= 3:
                priorities.append({
                    "student_id": analysis.student_id,
                    "student_name": analysis.student_name,
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "priority_level": "High" if risk_score >= 4 else "Medium"
                })
        
        return sorted(priorities, key=lambda x: x["risk_score"], reverse=True)

class EnhancedAIAnalyzer:
    """Enhanced AI Analyzer for Day 6"""
    
    def __init__(self, provider=None):
        self.provider = provider or EnhancedMockAIProvider()
    
    def analyze_comprehensive_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        
        # Convert data to StudentAnalysis objects
        analyses = []
        
        for student_data in assessment_data.get("comprehensive_analysis", []):
            analysis = StudentAnalysis(
                student_id=student_data["student_id"],
                student_name=student_data.get("student_name", f"Student {student_data['student_id']}"),
                test_score=student_data["test_performance"]["score"],
                test_percentage=student_data["test_performance"]["percentage"],
                engagement_rate=student_data["engagement_analysis"]["rate"],
                preparation_outcome=student_data["attainment_analysis"]["preparation_outcome"],
                in_class_practice=student_data["attainment_analysis"]["in_class_practice"],
                additional_notes=student_data.get("additional_notes", "")
            )
            analyses.append(analysis)
        
        # Perform analysis
        return self.provider.analyze_comprehensive_performance(analyses)

def create_enhanced_ai_analyzer(provider_type: str = "enhanced_mock", **kwargs):
    """Factory function"""
    return EnhancedAIAnalyzer(EnhancedMockAIProvider())

# Example usage
if __name__ == "__main__":
    print("Day 6 AI Analyzer - Comprehensive Performance Analysis Ready!")

"""
Performance tests using Locust for load testing
"""
from locust import HttpUser, task, between
import json
import random


class WebsiteUser(HttpUser):
    """Simulate user behavior for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when user starts - login"""
        self.login()
    
    def login(self):
        """Login with demo credentials"""
        response = self.client.post("/login", data={
            "username": "day6_teacher",
            "password": "day6demo"
        })
        if response.status_code != 302:  # Should redirect on success
            print(f"Login failed: {response.status_code}")
    
    @task(3)
    def view_dashboard(self):
        """Most common task - view dashboard"""
        self.client.get("/dashboard")
    
    @task(2)
    def view_enhanced_input(self):
        """Second most common - view assessment interface"""
        self.client.get("/enhanced_input_results")
    
    @task(1)
    def get_demo_data(self):
        """Occasionally get demo data"""
        self.client.get("/api/quick_demo_data")
    
    @task(1)
    def submit_assessment(self):
        """Simulate submitting assessment data"""
        demo_data = {
            "student_id": random.randint(1, 5),
            "assessment_id": 1,
            "quiz_answers": {str(i): random.choice(['correct', 'incorrect']) 
                            for i in range(1, 11)},
            "engagement_rate": random.randint(1, 9),
            "engagement_evidence": {
                "questioning": random.choice([True, False]),
                "answering": random.choice([True, False]),
                "focus": random.choice([True, False]),
                "activity": random.choice([True, False])
            },
            "preparation_outcome": random.choice(['emerging', 'developing', 'secure', 'mastery']),
            "in_class_practice": random.choice(['emerging', 'developing', 'secure', 'mastery'])
        }
        
        self.client.post("/api/submit_comprehensive_assessment", 
                        json=demo_data,
                        headers={"Content-Type": "application/json"})
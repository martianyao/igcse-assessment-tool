# Copy this content into verify_mappings.py
import json
import os

def verify_question_mappings():
    """Verify that all questions have corresponding manual mappings"""
    
    print("🔍 Verifying Question ID Mappings...")
    print("=" * 50)
    
    # Check if files exist
    questions_file = 'data/past_questions_bank.json'
    mappings_file = 'data/manual_mappings.json'
    
    if not os.path.exists(questions_file):
        print(f"❌ Error: {questions_file} not found!")
        return False
        
    if not os.path.exists(mappings_file):
        print(f"❌ Error: {mappings_file} not found!")
        return False
    
    try:
        # Load questions bank
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        # Load manual mappings
        with open(mappings_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        
        # Extract all question IDs from questions bank
        question_ids = []
        for topic, data in questions['chemistry_questions_bank'].items():
            for q in data['questions']:
                question_ids.append(q['id'])
        
        # Get manual mapping IDs
        manual_mapping_ids = list(mappings['manual_topic_mappings'].keys())
        
        print(f"📊 Questions in bank: {len(question_ids)}")
        print(f"📊 Manual mappings: {len(manual_mapping_ids)}")
        
        # Check for missing mappings
        missing = [qid for qid in question_ids if qid not in manual_mapping_ids]
        extra = [qid for qid in manual_mapping_ids if qid not in question_ids]
        
        if missing:
            print(f"\n❌ Missing mappings for questions:")
            for qid in missing:
                print(f"   - {qid}")
        
        if extra:
            print(f"\n⚠️  Extra mappings (not in question bank):")
            for qid in extra:
                print(f"   - {qid}")
        
        if not missing and not extra:
            print("\n✅ Perfect match! All questions have manual mappings")
            return True
        else:
            print(f"\n❌ Mismatch found!")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verify_question_mappings()
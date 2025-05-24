#!/usr/bin/env python3
"""
Script to generate sample data files for testing the IGCSE Assessment Tool.
Run this to create sample CSV files in the data/ directory.
"""

from pathlib import Path
import sys

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion import generate_sample_data


def main():
    """Generate sample data files"""
    print("Generating sample data files...")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate sample data
    try:
        generate_sample_data(
            output_dir=data_dir,
            num_students=30,
            num_questions=50
        )
        print("\n✅ Sample data files generated successfully!")
        print("\nCreated files:")
        print("  - data/sample_mcq_results.csv (30 students, 50 questions)")
        print("  - data/sample_assignments.csv (30 students, 3 assignments)")
        print("  - data/sample_participation.csv (30 students, 12 weeks)")
        
    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
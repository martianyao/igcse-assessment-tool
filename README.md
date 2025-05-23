# IGCSE Assessment Tool

A lightweight assessment tool for Cambridge IGCSE teachers to diagnose student weaknesses in multiple-choice tests and automatically generate personalized practice papers.

## Features

- 📊 Multi-stream data integration: Combines MCQ results, assignment marks, and classroom participation
- 🔍 Intelligent weakness detection: Uses item response analysis to identify knowledge gaps  
- 🎯 Topic mapping: Maps weaknesses to Cambridge IGCSE syllabus topics
- 📝 Personalized papers: Automatically assembles custom practice papers from past CIE questions
- 📈 Visual reports: Generates heatmaps and teacher summaries

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run example
python src/ingestion.py
```

## Project Structure

```
igcse-assessment-tool/
├── src/               # Source code
├── tests/             # Test files
├── data/              # Sample data
├── output/            # Generated reports
└── demo.ipynb         # Demo notebook
```

#!/usr/bin/env python3
"""
Day 2 Demo Script - Shows all diagnostic features
Run this to see everything working together!
"""

from pathlib import Path
from src.ingestion import DataIngestion
from src.diagnostics import WeaknessAnalyzer
from src.visualization import DiagnosticVisualizer


def main():
    """Run complete diagnostic demo."""
    print("="*60)
    print("IGCSE Assessment Tool - Day 2 Diagnostic Demo")
    print("="*60)
    
    # Step 1: Load data
    print("\n1️⃣ Loading data...")
    data_dir = Path("data")
    ingestion = DataIngestion(data_dir)
    class_data = ingestion.merge_all_data()
    print(f"   ✅ Loaded {class_data.num_students} students")
    
    # Step 2: Run diagnostics
    print("\n2️⃣ Running diagnostic analysis...")
    analyzer = WeaknessAnalyzer(class_data)
    analyzer.analyze()
    print("   ✅ Analysis complete")
    
    # Step 3: Show class summary
    summary = analyzer.get_class_summary()
    print("\n3️⃣ Class Summary:")
    print(f"   📊 Average Score: {summary['avg_score']:.1f} / {summary['num_questions']}")
    print(f"   📈 Score Range: {summary['min_score']:.0f} - {summary['max_score']:.0f}")
    print(f"   🔴 Hardest Questions: {', '.join(summary['hardest_questions'][:3])}")
    print(f"   🟢 Easiest Questions: {', '.join(summary['easiest_questions'][:3])}")
    
    # Step 4: Show item analysis
    print("\n4️⃣ Item Analysis (Top 5 Questions):")
    print("   Question | P-Value | Discrimination | Quality")
    print("   ---------|---------|----------------|----------")
    for i, (q, stats) in enumerate(analyzer.item_stats.items()):
        if i >= 5:
            break
        print(f"   {q:<8} | {stats.p_value:>7.3f} | {stats.discrimination:>14.3f} | {stats.discrimination_quality}")
    
    # Step 5: Show sample student profiles
    print("\n5️⃣ Sample Student Profiles:")
    for i, (sid, profile) in enumerate(analyzer.student_profiles.items()):
        if i >= 3:
            break
        print(f"\n   Student {sid}:")
        print(f"   - Overall: {profile.overall_mcq_percentage:.1f}%")
        print(f"   - Performance: {profile.relative_performance:.2f}x class average")
        print(f"   - Focus Areas: {', '.join(profile.suggested_focus_areas[:3])}")
    
    # Step 6: Export results
    print("\n6️⃣ Exporting results...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Export item analysis
    analyzer.export_item_analysis(output_dir / "item_analysis.csv")
    print(f"   ✅ Item analysis exported to output/item_analysis.csv")
    
    # Step 7: Create visualizations
    print("\n7️⃣ Creating visualizations...")
    visualizer = DiagnosticVisualizer(analyzer)
    visualizer.create_all_visualizations()
    print(f"   ✅ All charts saved to output/visualizations/")
    
    print("\n" + "="*60)
    print("✨ Day 2 Demo Complete! Check the output folder for results.")
    print("="*60)


if __name__ == "__main__":
    main()
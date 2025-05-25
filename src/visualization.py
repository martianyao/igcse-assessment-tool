"""
Visualization module for IGCSE Assessment Tool.

Creates charts and visualizations for diagnostic results:
- Item difficulty bar charts
- Student performance distributions
- Class-wide weakness heatmaps
- Individual student profiles
"""
import sys
from pathlib import Path
# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

from src.diagnostics import WeaknessAnalyzer, ItemStatistics, StudentWeaknessProfile

# Configure plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagnosticVisualizer:
    """Creates visualizations for diagnostic analysis results."""
    
    def __init__(self, analyzer: WeaknessAnalyzer):
        """
        Initialize visualizer with analyzer results.
        
        Args:
            analyzer: WeaknessAnalyzer instance with completed analysis
        """
        self.analyzer = analyzer
        self.output_dir = Path("output/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_all_visualizations(self) -> None:
        """Generate all standard visualizations."""
        logger.info("Creating visualizations...")
        
        self.plot_item_difficulty_chart()
        self.plot_discrimination_analysis()
        self.plot_student_distribution()
        self.plot_class_heatmap()
        self.plot_difficulty_performance()
        
        logger.info(f"Visualizations saved to {self.output_dir}")
    
    def plot_item_difficulty_chart(self, save_path: Optional[Path] = None) -> None:
        """Create bar chart of item difficulties (p-values)."""
        if save_path is None:
            save_path = self.output_dir / "item_difficulty.png"
        
        # Prepare data
        items = []
        p_values = []
        colors = []
        
        for q in sorted(self.analyzer.item_stats.keys()):
            stats = self.analyzer.item_stats[q]
            items.append(q)
            p_values.append(stats.p_value)
            
            # Color by difficulty
            if stats.p_value > 0.7:
                colors.append('green')
            elif stats.p_value < 0.3:
                colors.append('red')
            else:
                colors.append('orange')
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(items, p_values, color=colors, alpha=0.7)
        
        # Add threshold lines
        ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='Easy (>0.7)')
        ax.axhline(y=0.3, color='red', linestyle='--', alpha=0.5, label='Hard (<0.3)')
        
        # Formatting
        ax.set_xlabel('Question ID', fontsize=12)
        ax.set_ylabel('P-Value (Proportion Correct)', fontsize=12)
        ax.set_title('Item Difficulty Analysis', fontsize=16, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right')
        
        # Rotate x labels if many questions
        if len(items) > 20:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Item difficulty chart saved to {save_path}")
    
    def plot_discrimination_analysis(self, save_path: Optional[Path] = None) -> None:
        """Create scatter plot of p-value vs discrimination."""
        if save_path is None:
            save_path = self.output_dir / "discrimination_analysis.png"
        
        # Prepare data
        p_values = []
        discriminations = []
        labels = []
        
        for q, stats in self.analyzer.item_stats.items():
            p_values.append(stats.p_value)
            discriminations.append(stats.discrimination)
            labels.append(q)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        scatter = ax.scatter(p_values, discriminations, 
                           c=discriminations, cmap='RdYlGn', 
                           s=100, alpha=0.6, edgecolors='black')
        
        # Add quadrant lines
        ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=0.3, color='gray', linestyle='--', alpha=0.5)
        
        # Add labels for interesting points
        for i, (p, d, label) in enumerate(zip(p_values, discriminations, labels)):
            if d < 0.2 or d > 0.5 or p < 0.2 or p > 0.8:
                ax.annotate(label, (p, d), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        # Formatting
        ax.set_xlabel('P-Value (Difficulty)', fontsize=12)
        ax.set_ylabel('Discrimination (Point-Biserial r)', fontsize=12)
        ax.set_title('Item Quality Analysis', fontsize=16, fontweight='bold')
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.1, 0.8)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Discrimination', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Discrimination analysis saved to {save_path}")
    
    def plot_student_distribution(self, save_path: Optional[Path] = None) -> None:
        """Create histogram of student scores."""
        if save_path is None:
            save_path = self.output_dir / "student_distribution.png"
        
        # Get student scores
        scores = [student.mcq_total for student in self.analyzer.class_data.students.values()]
        max_score = len(self.analyzer.class_data.mcq_questions)
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram
        n, bins, patches = ax1.hist(scores, bins=min(20, max_score), 
                                   edgecolor='black', alpha=0.7)
        
        # Color bars by performance
        for i, patch in enumerate(patches):
            if bins[i] < max_score * 0.4:
                patch.set_facecolor('red')
            elif bins[i] < max_score * 0.7:
                patch.set_facecolor('orange')
            else:
                patch.set_facecolor('green')
        
        # Add statistics
        mean_score = np.mean(scores)
        ax1.axvline(mean_score, color='blue', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.1f}')
        
        ax1.set_xlabel('Total Score', fontsize=12)
        ax1.set_ylabel('Number of Students', fontsize=12)
        ax1.set_title('Score Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        
        # Box plot
        ax2.boxplot(scores, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightblue'),
                   medianprops=dict(color='red', linewidth=2))
        ax2.set_ylabel('Total Score', fontsize=12)
        ax2.set_title('Score Summary', fontsize=14, fontweight='bold')
        
        plt.suptitle('Student Performance Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Student distribution saved to {save_path}")
    
    def plot_class_heatmap(self, save_path: Optional[Path] = None) -> None:
        """Create heatmap of class performance by question."""
        if save_path is None:
            save_path = self.output_dir / "class_heatmap.png"
        
        # Get response matrix
        matrix = self.analyzer._response_matrix.drop('total_score', axis=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create heatmap
        sns.heatmap(matrix, cmap='RdYlGn', center=0.5, 
                   cbar_kws={'label': 'Correct (1) / Incorrect (0)'},
                   xticklabels=True, yticklabels=True,
                   linewidths=0.5, linecolor='gray')
        
        # Formatting
        ax.set_xlabel('Question ID', fontsize=12)
        ax.set_ylabel('Student ID', fontsize=12)
        ax.set_title('Class Performance Heatmap', fontsize=16, fontweight='bold')
        
        # Rotate labels
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Class heatmap saved to {save_path}")
    
    def plot_difficulty_performance(self, save_path: Optional[Path] = None) -> None:
        """Create chart showing performance by question difficulty."""
        if save_path is None:
            save_path = self.output_dir / "difficulty_performance.png"
        
        # Aggregate performance by difficulty level
        difficulty_data = {'Easy': [], 'Medium': [], 'Hard': []}
        
        for student in self.analyzer.student_profiles.values():
            for level, pct in student.performance_by_difficulty.items():
                difficulty_data[level].append(pct)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create violin plot
        positions = [1, 2, 3]
        parts = ax.violinplot([difficulty_data['Easy'], 
                             difficulty_data['Medium'], 
                             difficulty_data['Hard']], 
                            positions=positions, showmeans=True)
        
        # Customize colors
        colors = ['green', 'orange', 'red']
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        # Add box plot overlay
        bp = ax.boxplot([difficulty_data['Easy'], 
                        difficulty_data['Medium'], 
                        difficulty_data['Hard']], 
                       positions=positions, widths=0.1,
                       patch_artist=True, boxprops=dict(facecolor='white'))
        
        # Formatting
        ax.set_xticks(positions)
        ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
        ax.set_xlabel('Question Difficulty', fontsize=12)
        ax.set_ylabel('Student Performance (%)', fontsize=12)
        ax.set_title('Performance by Question Difficulty', fontsize=16, fontweight='bold')
        ax.set_ylim(0, 105)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Difficulty performance chart saved to {save_path}")


if __name__ == "__main__":
    # Test visualization
    from src.ingestion import DataIngestion
    from src.diagnostics import WeaknessAnalyzer
    
    # Load data and run analysis
    data_dir = Path("data")
    ingestion = DataIngestion(data_dir)
    class_data = ingestion.merge_all_data()
    
    analyzer = WeaknessAnalyzer(class_data)
    analyzer.analyze()
    
    # Create visualizations
    visualizer = DiagnosticVisualizer(analyzer)
    visualizer.create_all_visualizations()
    
    print("\n✅ All visualizations created successfully!")
    print(f"📁 Check the output/visualizations/ folder for charts")
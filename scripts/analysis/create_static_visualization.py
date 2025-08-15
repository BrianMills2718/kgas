#!/usr/bin/env python3
"""
Create static image visualizations of the Kunst-Carter analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
import numpy as np
from pathlib import Path

# Load the visualization data
viz_dir = Path("/home/brian/projects/Digimons/kunst_carter_analysis")
viz_file = list(viz_dir.glob("carter_kunst_visualization_*.json"))[0]
with open(viz_file, 'r') as f:
    viz_data = json.load(f)

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))
fig.suptitle('Kunst Theory Analysis of Carter Speech - Visual Summary', fontsize=20, fontweight='bold')

# 1. Risk Gauge (top left)
ax1 = plt.subplot(3, 3, 1)
risk_score = viz_data['risk_assessment']['risk_score']
risk_level = viz_data['risk_assessment']['risk_level']

# Create gauge
theta = np.linspace(0, np.pi, 100)
r_inner, r_outer = 0.7, 1.0

# Color zones
colors = ['green', 'yellow', 'red']
boundaries = [0, 0.3, 0.7, 1.0]

for i, color in enumerate(colors):
    theta_start = boundaries[i] * np.pi
    theta_end = boundaries[i+1] * np.pi
    theta_zone = np.linspace(theta_start, theta_end, 50)
    
    x_outer = r_outer * np.cos(theta_zone)
    y_outer = r_outer * np.sin(theta_zone)
    x_inner = r_inner * np.cos(theta_zone[::-1])
    y_inner = r_inner * np.sin(theta_zone[::-1])
    
    x = np.concatenate([x_outer, x_inner])
    y = np.concatenate([y_outer, y_inner])
    
    ax1.fill(x, y, color=color, alpha=0.3)

# Add needle
needle_angle = (1 - risk_score) * np.pi
needle_x = 0.9 * np.cos(needle_angle)
needle_y = 0.9 * np.sin(needle_angle)
ax1.plot([0, needle_x], [0, needle_y], 'k-', linewidth=3)
ax1.plot(0, 0, 'ko', markersize=10)

ax1.text(0, -0.3, f'{risk_score:.1%}', fontsize=24, ha='center', fontweight='bold')
ax1.text(0, -0.5, risk_level.upper(), fontsize=16, ha='center')
ax1.set_xlim(-1.2, 1.2)
ax1.set_ylim(-0.6, 1.2)
ax1.axis('off')
ax1.set_title('Conspiracy Risk Score', fontsize=14, fontweight='bold')

# 2. Psychological Factors Radar (top middle)
ax2 = plt.subplot(3, 3, 2, projection='polar')
factors = list(viz_data['factor_presence_scores'].keys())
scores = [viz_data['factor_presence_scores'][f] for f in factors]
scores.append(scores[0])  # Complete the circle

angles = np.linspace(0, 2 * np.pi, len(factors), endpoint=False).tolist()
angles.append(angles[0])

ax2.plot(angles, scores, 'b-', linewidth=2)
ax2.fill(angles, scores, 'b', alpha=0.25)
ax2.plot(angles, [0.5] * len(angles), 'k--', alpha=0.5)  # 50% reference line

ax2.set_xticks(angles[:-1])
ax2.set_xticklabels([f.replace('_', ' ').title() for f in factors], fontsize=10)
ax2.set_ylim(0, 1)
ax2.set_title('Psychological Factors', fontsize=14, fontweight='bold', pad=20)

# 3. Theme Balance (top right)
ax3 = plt.subplot(3, 3, 3)
themes = ['Transparency\nvs Secrecy', 'Unity\nvs Division', 'Trust\nvs Distrust']
positive = [
    viz_data['word_frequency']['transparency_words'],
    viz_data['word_frequency']['unity_indicators'],
    8  # From the full analysis data
]
negative = [
    viz_data['word_frequency']['secrecy_words'],
    viz_data['word_frequency']['division_indicators'],
    1  # From the full analysis data
]

x = np.arange(len(themes))
width = 0.35

ax3.bar(x - width/2, positive, width, label='Positive', color='lightgreen')
ax3.bar(x + width/2, negative, width, label='Negative', color='lightcoral')

ax3.set_xticks(x)
ax3.set_xticklabels(themes)
ax3.set_ylabel('Count')
ax3.set_title('Thematic Balance', fontsize=14, fontweight='bold')
ax3.legend()

# 4. Protective vs Risk Pie (middle left)
ax4 = plt.subplot(3, 3, 4)
protective = viz_data['risk_assessment']['protective_score']
risk = viz_data['risk_assessment']['risk_score']

sizes = [protective, risk]
labels = ['Protective\nFactors', 'Risk\nFactors']
colors = ['lightgreen', 'lightcoral']

wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                    startangle=90, textprops={'fontsize': 12})
ax4.set_title('Factor Distribution', fontsize=14, fontweight='bold')

# 5. Key Metrics Display (middle center)
ax5 = plt.subplot(3, 3, 5)
ax5.axis('off')

metrics_text = f"""Key Metrics:
━━━━━━━━━━━━━━━━━━━━
Total Words: 3,455
Risk Score: 42.6%
Risk Level: MODERATE
Unity Ratio: 91.6%
Transparency: 2:1
━━━━━━━━━━━━━━━━━━━━"""

ax5.text(0.5, 0.5, metrics_text, fontsize=14, ha='center', va='center',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.3))
ax5.set_title('Summary Statistics', fontsize=14, fontweight='bold')

# 6. Word Categories Bar (middle right)
ax6 = plt.subplot(3, 3, 6)
categories = ['Transparency', 'Secrecy', 'Unity', 'Division']
values = [
    viz_data['word_frequency']['transparency_words'],
    viz_data['word_frequency']['secrecy_words'],
    viz_data['word_frequency']['unity_indicators'],
    viz_data['word_frequency']['division_indicators']
]
colors_bar = ['lightblue', 'gray', 'lightgreen', 'lightcoral']

bars = ax6.bar(categories, values, color=colors_bar)
ax6.set_ylabel('Frequency')
ax6.set_title('Word Category Analysis', fontsize=14, fontweight='bold')

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(value)}', ha='center', va='bottom')

# 7. Discourse Patterns (bottom)
ax7 = plt.subplot(3, 1, 3)
patterns = viz_data['discourse_pattern_counts']
sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)

pattern_names = [p[0].replace('_', ' ').title() for p in sorted_patterns]
pattern_values = [p[1] for p in sorted_patterns]

y_pos = np.arange(len(pattern_names))
ax7.barh(y_pos, pattern_values, color='skyblue')
ax7.set_yticks(y_pos)
ax7.set_yticklabels(pattern_names)
ax7.set_xlabel('Count')
ax7.set_title('Discourse Pattern Frequency', fontsize=14, fontweight='bold')

# Add value labels
for i, v in enumerate(pattern_values):
    ax7.text(v + 0.1, i, str(v), va='center')

plt.tight_layout()
plt.savefig('/home/brian/projects/Digimons/kunst_carter_analysis_summary.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/brian/projects/Digimons/kunst_carter_analysis_summary.pdf', bbox_inches='tight')

print("✅ Static visualizations saved:")
print("   📊 kunst_carter_analysis_summary.png")
print("   📄 kunst_carter_analysis_summary.pdf")
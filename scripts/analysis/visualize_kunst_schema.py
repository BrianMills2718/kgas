#!/usr/bin/env python3
"""
Visualize the Kunst theory schema structure
"""

import yaml
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Load the schema
schema_path = Path("/home/brian/projects/Digimons/schemas/kunst_conspiracy_theory/kunst_ai_conspiracy_theory_schema.yml")
with open(schema_path, 'r') as f:
    schema = yaml.safe_load(f)

# Create network graph
G = nx.DiGraph()

# Node type colors
node_colors = {
    'psychological_trait': '#ff9999',
    'psychological_disposition': '#ff6666',
    'cognitive_vulnerability': '#ffcc99',
    'cognitive_bias': '#ffaa66',
    'social_position': '#99ccff',
    'political_orientation': '#6699ff',
    'behavioral_outcome': '#99ff99',
    'behavioral_manifestation': '#66ff66',
    'contextual_event': '#ffff99',
    'information_environment': '#ffff66',
    'demographic_variable': '#cc99ff'
}

# Add nodes
for node in schema['nodes']:
    node_type = node['type']
    color = node_colors.get(node_type, '#cccccc')
    G.add_node(node['id'], 
              label=node['label'],
              type=node_type,
              color=color)

# Add edges
edge_colors = {
    'predicts': 'red',
    'manifests_as': 'green',
    'creates': 'blue',
    'facilitates': 'orange'
}

for conn in schema['connections']:
    edge_type = conn['type']
    color = edge_colors.get(edge_type, 'gray')
    strength = conn['properties'].get('strength', 'unknown')
    G.add_edge(conn['source'], conn['target'],
              type=edge_type,
              color=color,
              strength=strength)

# Create visualization
plt.figure(figsize=(20, 16))

# Layout
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

# Draw nodes
for node_type, color in node_colors.items():
    nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
    if nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                             node_color=color, 
                             node_size=3000,
                             alpha=0.8)

# Draw edges
for edge_type, color in edge_colors.items():
    edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
    if edges:
        nx.draw_networkx_edges(G, pos, edgelist=edges,
                             edge_color=color,
                             width=2,
                             alpha=0.6,
                             arrows=True,
                             arrowsize=20,
                             connectionstyle="arc3,rad=0.1")

# Draw labels
labels = nx.get_node_attributes(G, 'label')
# Adjust label positions slightly above nodes
label_pos = {k: (v[0], v[1] + 0.05) for k, v in pos.items()}
nx.draw_networkx_labels(G, label_pos, labels, font_size=10, font_weight='bold')

# Create legend
node_patches = []
for node_type, color in node_colors.items():
    if any(d.get('type') == node_type for n, d in G.nodes(data=True)):
        patch = mpatches.Patch(color=color, label=node_type.replace('_', ' ').title())
        node_patches.append(patch)

edge_patches = []
for edge_type, color in edge_colors.items():
    if any(d.get('type') == edge_type for u, v, d in G.edges(data=True)):
        patch = mpatches.Patch(color=color, label=edge_type.replace('_', ' ').title())
        edge_patches.append(patch)

# Position legends
plt.legend(handles=node_patches, loc='upper left', title='Node Types', bbox_to_anchor=(0, 1))
plt.legend(handles=edge_patches, loc='upper right', title='Connection Types', bbox_to_anchor=(1, 1))

plt.title('Kunst et al. (2024) AI-Psychological Conspiracy Theory Support Model\nMeta-Schema v10 Network Visualization', 
          fontsize=18, fontweight='bold', pad=20)
plt.axis('off')
plt.tight_layout()

# Save
output_path = Path("/home/brian/projects/Digimons/kunst_theory_schema_network.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')

print(f"✅ Schema visualization saved:")
print(f"   📊 {output_path}")
print(f"   📄 {output_path.with_suffix('.pdf')}")

# Create a simple summary
print("\n📋 Schema Summary:")
print(f"   Model Type: {schema['model_type']}")
print(f"   Theory: {schema['theory_name']}")
print(f"   Nodes: {len(schema['nodes'])}")
print(f"   Connections: {len(schema['connections'])}")
print(f"   Node Types: {len(set(n['type'] for n in schema['nodes']))}")
print(f"   Connection Types: {len(set(c['type'] for c in schema['connections']))}")
#!/usr/bin/env python3
"""
VERSION 1.0: KNOWLEDGE GRAPH UPDATER AND PYVIS VISUALIZATION
This script receives a user instruction, sends it to the Anthropic LLM with a system prompt that instructs the model to intelligently add, remove, merge, or edit nodes and edges (and their properties) of a knowledge graph, and then displays the resulting graph interactively using pyvis.
"""

import os
import json
import anthropic  # Ensure you have the 'anthropic' package installed
from pyvis.network import Network

import streamlit as st
import streamlit.components.v1 as components

import networkx as nx
import plotly.graph_objects as go

# --- Function to update the knowledge graph using the Anthropic API call ---
def update_knowledge_graph(user_input, current_graph):
    # Instantiate the Anthropomorphic client with your API key
    client = anthropic.Anthropic(
        api_key="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"  # REPLACE WITH YOUR VALID API KEY
    )
    
    # Prepare a system prompt that instructs the LLM to update the graph.
    # The prompt is strict: it must return valid JSON with exactly two keys: "nodes" and "edges".
    system_prompt = (
        f"You are an expert knowledge graph curator. Given the current knowledge graph (under the key 'graph') and the user instruction (under the key 'input'), "
        "update the graph by intelligently adding, removing, merging, or editing nodes and edges, including their properties. "
        "Return the updated knowledge graph as valid JSON with exactly two keys: 'nodes' and 'edges'. "
        "Nodes must be a list of objects with at least the keys 'id' and 'label'. "
        "Edges must be a list of objects with the keys 'source' and 'target', and optionally 'label'. "
        "Do not include any commentary or additional text. "
        "\n\nEXAMPLES:\n"
        "<goal>Create a network representing von Neumann architecture</goal>\n"
        "<context>This network should include components such as CPU, Memory, ALU, and Control Unit.</context>\n"
        "<instructions>Update the graph by adding nodes for each component (with keys 'id' and 'label') and connect them with edges representing data flow.</instructions>\n"
        f"\nCURRENT GRAPH: {json.dumps(current_graph)}"
        f"\nUSER INPUT: {user_input}"
    )
    
    # Make the API call using the provided correct syntax.
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input
                    }
                ]
            }
        ]
    )
    
    # Get the text content from the first message
    response_text = message.content[0].text.strip()
    
    try:
        updated_graph = json.loads(response_text)
    except json.JSONDecodeError as e:
        # If the LLM's response cannot be parsed, output an error and return the original graph.
        print("Error parsing JSON response from LLM:", e)
        print("Raw response:", response_text)
        return current_graph
    
    return updated_graph

# --- Function to build and display the interactive pyvis graph ---
def build_pyvis_graph(graph_data, disable_physics=True, spring_length=200, spring_constant=0.04, avoid_overlap=1.0, output_filename="graph.html"):
    # Create a directed network with pyvis, incorporating visualization settings
    net = Network(height="750px", width="100%", directed=True, notebook=False)
    
    # Set visualization options for physics and spacing
    options = {
        "physics": {
            "enabled": not disable_physics,
            "barnesHut": {
                "springLength": spring_length,
                "springConstant": spring_constant,
                "avoidOverlap": avoid_overlap
            }
        },
        "layout": {
            "improvedLayout": True
        }
    }
    net.set_options(json.dumps(options))
    
    # Add nodes with hover-enabled detailed information (all node properties)
    for node in graph_data.get("nodes", []):
        node_id = node.get("id")
        label = node.get("label", node_id)
        # The hover (title) displays the full node properties in formatted JSON
        title = json.dumps(node, indent=2)
        net.add_node(node_id, label=label, title=title)
    
    # Add edges with hover-enabled detailed information (all edge properties)
    for edge in graph_data.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        label = edge.get("label", "")
        title = json.dumps(edge, indent=2)
        net.add_edge(source, target, label=label, title=title)
    
    # Generate the network graph's HTML
    html = net.generate_html(notebook=False)
    return html

def build_network_graph_3d(graph_data):
    """
    Build a 3D network visualization using NetworkX for layout and Plotly for rendering.
    """
    # Build the networkx graph from the current graph data:
    G = nx.DiGraph()
    for node in graph_data.get("nodes", []):
        G.add_node(node["id"], label=node.get("label", node["id"]))

    for edge in graph_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], label=edge.get("label", ""))

    # Compute 3D layout using a spring layout
    pos = nx.spring_layout(G, dim=3, seed=42)

    # Build edge traces
    edge_x = []
    edge_y = []
    edge_z = []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Build node traces
    node_x = []
    node_y = []
    node_z = []
    node_text = []
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(G.nodes[node]["label"])

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=node_text,
        marker=dict(
            size=10,
            color=[],
            colorscale='YlGnBu',
            reversescale=True,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left'
            ),
            line_width=2
        )
    )

    # Color the nodes based on their number of connections
    node_adjacencies = []
    for node in G.nodes():
        node_adjacencies.append(len(list(G.neighbors(node))))
    node_trace.marker.color = node_adjacencies

    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(
                           text='3D Network Graph Visualization',
                           font=dict(size=16)
                       ),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       scene=dict(
                           xaxis=dict(showbackground=False),
                           yaxis=dict(showbackground=False),
                           zaxis=dict(showbackground=False)
                       )
                   ))
    return fig

def parse_obsidian_links(markdown_text):
    """Extract Obsidian-style links from markdown text."""
    import re
    # Match both [[wiki-style]] and [[display|target]] links
    wiki_pattern = r'\[\[(.*?)\]\]'
    links = []
    
    for match in re.finditer(wiki_pattern, markdown_text):
        link = match.group(1)
        # Handle display|target style links
        if '|' in link:
            display, target = link.split('|', 1)
            links.append((display.strip(), target.strip()))
        else:
            links.append((link.strip(), link.strip()))
    
    return links

def read_obsidian_vault(vault_path):
    """Read all markdown files from Obsidian vault and build initial graph."""
    import glob
    import os
    
    nodes = {}  # Dictionary to store unique nodes
    edges = []  # List to store edges
    
    # Add logging
    st.write(f"Reading files from: {vault_path}")
    
    # Recursively find all .md files in the vault
    md_files = glob.glob(os.path.join(vault_path, "**/*.md"), recursive=True)
    
    # Log number of files found
    st.write(f"Found {len(md_files)} markdown files")
    
    for file_path in md_files:
        # Create node for the current file
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        nodes[file_name] = {"id": file_name, "label": file_name, "type": "note"}
        
        # Read file content and extract links
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract links from content
        links = parse_obsidian_links(content)
        
        # Log links found in each file
        if links:
            st.write(f"Found {len(links)} links in {file_name}")
        
        # Add edges for each link
        for display, target in links:
            # Add target node if it doesn't exist
            if target not in nodes:
                nodes[target] = {"id": target, "label": target, "type": "note"}
            
            # Add edge
            edges.append({
                "source": file_name,
                "target": target,
                "label": "references"
            })
    
    result = {"nodes": list(nodes.values()), "edges": edges}
    st.write(f"Created graph with {len(result['nodes'])} nodes and {len(result['edges'])} edges")
    return result

def export_to_obsidian(graph_data, vault_path):
    """Export graph connections as markdown files in Obsidian vault."""
    import os
    
    # Create a directory for exported files if it doesn't exist
    export_dir = os.path.join(vault_path, "graph_exports")
    os.makedirs(export_dir, exist_ok=True)
    
    export_file = os.path.join(export_dir, "graph_summary.md")
    st.write(f"Exporting to: {export_file}")
    
    # Create a markdown file summarizing the graph
    with open(export_file, 'w', encoding='utf-8') as f:
        f.write("# Knowledge Graph Summary\n\n")
        
        # Write nodes section
        f.write("## Nodes\n\n")
        for node in graph_data["nodes"]:
            f.write(f"- [[{node['label']}]]\n")
        
        # Write connections section
        f.write("\n## Connections\n\n")
        for edge in graph_data["edges"]:
            f.write(f"- [[{edge['source']}]] {edge.get('label', 'connects to')} [[{edge['target']}]]\n")
    
    st.write(f"Exported {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")

# --- Main Execution Flow (Streamlit App) ---
st.title("Iterative Knowledge Graph Updater")

# Initialize current graph in session state if not already present
if "current_graph" not in st.session_state:
    st.session_state.current_graph = {"nodes": [], "edges": []}

# Sidebar options for 2D Visualization Settings
st.sidebar.header("2D Visualization Settings")
disable_physics = st.sidebar.checkbox("Disable Physics", value=True)
spring_length = st.sidebar.slider("Spring Length", min_value=50, max_value=300, value=200)
spring_constant = st.sidebar.slider("Spring Constant", min_value=0.01, max_value=0.1, value=0.04, step=0.01)
avoid_overlap = st.sidebar.slider("Avoid Overlap Factor", min_value=0.0, max_value=5.0, value=1.0)

# Text input for the update instruction
user_instruction = st.text_input("Enter your graph update instruction:")

# Update the graph when the button is clicked
if st.button("Update Graph") and user_instruction.strip():
    # Store the previous graph state
    previous_graph = st.session_state.current_graph.copy()
    
    # Update the graph
    updated_graph = update_knowledge_graph(user_instruction, previous_graph)
    
    # Only update if we got a valid result
    if updated_graph and "nodes" in updated_graph and "edges" in updated_graph:
        st.session_state.current_graph = updated_graph

# Display the current knowledge graph JSON (optional)
st.subheader("Current Knowledge Graph (JSON)")
st.json(st.session_state.current_graph)

# Build the 2D pyvis graph using updated sidebar parameters and embed it into the Streamlit app
html = build_pyvis_graph(
    st.session_state.current_graph,
    disable_physics=disable_physics,
    spring_length=spring_length,
    spring_constant=spring_constant,
    avoid_overlap=avoid_overlap
)
st.subheader("2D Graph Visualization")
components.html(html, height=750, width=900)

# Build and display the 3D network graph visualization
st.subheader("3D Graph Visualization")
fig = build_network_graph_3d(st.session_state.current_graph)
st.plotly_chart(fig)

# Add Obsidian integration settings to sidebar
st.sidebar.header("Obsidian Integration")
obsidian_vault_path = st.sidebar.text_input("Obsidian Vault Path", "")

# Add buttons for Obsidian operations
if obsidian_vault_path:
    st.sidebar.write(f"Using vault at: {obsidian_vault_path}")
    
    if st.sidebar.button("Import from Obsidian"):
        try:
            st.write("Starting import...")
            imported_graph = read_obsidian_vault(obsidian_vault_path)
            
            # Show the before/after node counts
            old_count = len(st.session_state.current_graph.get("nodes", []))
            new_count = len(imported_graph.get("nodes", []))
            st.write(f"Nodes before: {old_count}, Nodes after: {new_count}")
            
            # Update the session state
            st.session_state.current_graph = imported_graph
            st.success("Successfully imported graph from Obsidian vault!")
            
            # Use the current rerun method
            st.rerun()
            
        except Exception as e:
            st.error(f"Error importing from Obsidian: {str(e)}")
            st.error(f"Full error: {repr(e)}")
    
    if st.sidebar.button("Export to Obsidian"):
        try:
            export_to_obsidian(st.session_state.current_graph, obsidian_vault_path)
            st.success(f"Successfully exported graph to {os.path.join(obsidian_vault_path, 'graph_exports')}")
        except Exception as e:
            st.error(f"Error exporting to Obsidian: {str(e)}")
            st.error(f"Full error: {repr(e)}")

# declare graphbuilder class
from yfiles_jupyter_graphs import GraphWidget
from ipywidgets import Layout

class GraphBuilder:
    def __init__(self):
        self.graph_data = {"nodes": {}, "edges": []}
        self.default_node_properties = {
            "fontSize": 12,
            "width": 30,
            "height": 30,
            "labelColor": "#000000",
            "labelBackgroundColor": "",
            "labelPosition": "center",
            "shape": "ellipse",  # Default shape
            "color": "#000000",  # Default color
            "image": None,  # No image by default
        }
        self.edge_styles = {}

    def add_node(
        self,
        node_id,
        label=None,
        color=None,
        shape=None,
        image=None,
        parent=None,
        properties=None,
    ):
        """Add a new node to the graph with optional shape, color, and parent."""
        if parent and parent not in self.graph_data["nodes"]:
            self.add_node(parent, label=f"Parent {parent}")
        label = label or node_id.replace("_", " ")
        node = {
            "id": node_id,
            "label": label,
            "parent": parent,
            **self.default_node_properties,
        }
        if color:
            node["color"] = color
        if shape:
            node["shape"] = shape
        if image:
            node["image"] = image
        if properties:
            node.update(properties)
        self.graph_data["nodes"][node_id] = node

    def add_children(self, parent, children, color=None, shape=None, properties=None):
        """Add multiple child nodes to a given parent."""
        if parent not in self.graph_data["nodes"]:
            raise ValueError(f"Parent node '{parent}' does not exist.")
        for child in children:
            label = child.replace("_", " ")
            child_properties = properties.copy() if properties else {}
            if color:
                child_properties["color"] = color
            if shape:
                child_properties["shape"] = shape
            self.add_node(
                node_id=child, label=label, parent=parent, properties=child_properties
            )

    def add_edge(
        self,
        start,
        end,
        label="",
        color="#000000",
        thickness=1.0,
        directed=False,
        properties=None,
    ):
        """Add an edge between two nodes with customizable properties."""
        edge = {
            "start": start,
            "end": end,
            "label": label,
            "color": color,
            "thickness": thickness,
            "fontSize": 12,
            "labelColor": "#000000",
            "labelBackgroundColor": "",
            "directed": directed,
        }
        if properties:
            edge.update(properties)
        start_parent = self.graph_data["nodes"][start].get("parent")
        end_parent = self.graph_data["nodes"][end].get("parent")
        if start_parent and end_parent:
            parent_pair = (start_parent, end_parent)
            if parent_pair in self.edge_styles:
                edge.update(self.edge_styles[parent_pair])
        self.graph_data["edges"].append(edge)

    def change_node_parent(self, node_id, new_parent_id=None):
        """Change the parent of an existing node."""
        if node_id not in self.graph_data["nodes"]:
            raise ValueError(f"Node {node_id} does not exist.")
        if new_parent_id not in self.graph_data["nodes"]:
            raise ValueError(f"New parent node {new_parent_id} does not exist.")
        # Update the parent of the node
        self.graph_data["nodes"][node_id]["parent"] = new_parent_id

    def set_node_group_style(self, node_filter, properties):
        """
        Apply styles to a group of nodes based on a filter.
        :param node_filter: A function that returns True if a node should be styled.
        :param properties: A dictionary of properties to apply to the filtered nodes.
        """
        for node_id, node in self.graph_data["nodes"].items():
            if node_filter(node):  # Apply filter function to select nodes
                node.update(properties)

    def set_edge_group_style(self, edge_filter, properties):
        """
        Apply styles to a group of edges based on a filter.
        :param edge_filter: A function that returns True if an edge should be styled.
        :param properties: A dictionary of properties to apply to the filtered edges.
        """
        for edge in self.graph_data["edges"]:
            if edge_filter(edge):  # Apply filter function to select edges
                edge.update(properties)

    def create_graph(self):
        """
        Create the graph visualization using the stored graph data.
        """
        nodes = []
        edges = []
        # Process nodes and add them to the list
        for node_id, node in self.graph_data["nodes"].items():
            nodes.append(
                {
                    "id": node_id,
                    "properties": node.copy(),  # Copy all node properties
                    "parent": node.get("parent"),  # Add parent if exists
                }
            )
        # Process edges and add them to the list
        edge_set = set()
        for edge in self.graph_data["edges"]:
            start = edge["start"]
            end = edge["end"]
            edge_id = f"{start}_{end}"
            if edge_id not in edge_set:
                edges.append(
                    {
                        "id": edge_id,
                        "start": start,
                        "end": end,
                        "properties": edge.copy(),  # Copy all edge properties
                    }
                )
                edge_set.add(edge_id)
        
        # Create and configure the graph widget
        # Define the layout with a specific height and width
        widget_layout = Layout(height="1500px", width="100%")

        # Create the GraphWidget with the specified layout
        w = GraphWidget(widget_layout=widget_layout)
        #w = GraphWidget()
        w.nodes = nodes
        w.edges = edges
        # Mapping for node styles (shape, color, and image)
        w.set_node_styles_mapping(
            lambda node: {
                "shape": node["properties"].get("shape", "ellipse"),
                "color": node["properties"].get("color", "#000000"),
                "image": node["properties"].get("image", None),
            }
        )
        # Mapping for node sizes and labels
        w.set_node_size_mapping(
            lambda node: (
                node["properties"].get("width", 30),
                node["properties"].get("height", 30),
            )
        )
        w.set_node_label_mapping(
            lambda node: {
                "text": node["properties"].get("label", ""),
                "fontSize": node["properties"].get("fontSize", 12),
                "textFill": node["properties"].get("labelColor", "#000000"),
                "backgroundFill": node["properties"].get("labelBackgroundColor", ""),
                "placement": node["properties"].get("labelPosition", "center"),
            }
        )
        # Mapping for edge properties
        w.set_edge_color_mapping(
            lambda edge: edge["properties"].get("color", "#000000")
        )
        w.set_edge_thickness_factor_mapping(
            lambda edge: edge["properties"].get("thickness", 1.0)
        )
        w.set_edge_label_mapping(
            lambda edge: {
                "text": edge["properties"].get("label", ""),
                "fontSize": edge["properties"].get("fontSize", 12),
                "textFill": edge["properties"].get("labelColor", "#000000"),
                "backgroundFill": edge["properties"].get("labelBackgroundColor", ""),
            }
        )
        w.set_directed_mapping(lambda edge: edge["properties"].get("directed", False))
        # Ensure correct parent-child relationships
        w.set_node_parent_mapping(lambda node: node.get("parent", None))
        # Use hierarchical layout for parent-child relationships
        w.hierarchic_layout()
        return w

    def display(self):
        """Display the graph using the GraphWidget."""
        graph_widget = self.create_graph()
        display(graph_widget)


import pandas as pd
import os
import colorsys
import numpy as np


def get_hex_color(hue, saturation=0.7, lightness=0.5):
    """
    Convert HSL to hex color.

    Args:
        hue (float): Hue value (0-1)
        saturation (float): Saturation value (0-1)
        lightness (float): Lightness value (0-1)

    Returns:
        str: Hex color code
    """
    # Convert HSL to RGB
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)

    # Convert RGB to hex
    hex_color = "#{:02x}{:02x}{:02x}".format(
        int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
    )
    return hex_color


def generate_color_scheme(num_levels):
    """
    Generate a color scheme with evenly distributed colors based on number of levels.

    Args:
        num_levels (int): Number of hierarchy levels

    Returns:
        dict: Dictionary mapping levels to colors
    """
    colors = {}

    # Calculate hue step size to distribute colors evenly
    hue_step = 1.0 / num_levels

    for level in range(num_levels):
        # Generate color with varying hue
        hue = level * hue_step
        colors[level] = get_hex_color(hue)

    return colors


def calculate_node_degrees(relationships_df):
    """
    Calculate the degree (number of connections) for each node.

    Args:
        relationships_df (DataFrame): DataFrame containing relationships

    Returns:
        dict: Dictionary mapping node IDs to their degrees
    """
    # Count occurrences as both source and target
    source_counts = relationships_df["source_id"].value_counts()
    target_counts = relationships_df["target_id"].value_counts()

    # Combine the counts
    total_degrees = (source_counts.add(target_counts, fill_value=0)).to_dict()

    return total_degrees


def scale_node_size(degree):
    """
    10x linear scaling where:
    - degree 1 = size 10
    - degree 93 = size 930

    Args:
        degree (float): Node degree

    Returns:
        float: Scaled node size
    """
    return degree * 10


def preprocess_relationships(nodes_df, relationships_df):
    """
    Preprocess relationships by mapping source and target names to IDs in nodes_df.

    Args:
        nodes_df (DataFrame): DataFrame containing node information.
        relationships_df (DataFrame): DataFrame containing relationship information.

    Returns:
        DataFrame: Updated relationships DataFrame with source and target mapped to IDs.
    """
    # Create a mapping from title to ID
    title_to_id = nodes_df.set_index("title")["id"].to_dict()

    # Map source and target to IDs
    relationships_df["source_id"] = relationships_df["source"].map(title_to_id)
    relationships_df["target_id"] = relationships_df["target"].map(title_to_id)

    # Drop rows with unmapped source or target IDs
    relationships_df = relationships_df.dropna(subset=["source_id", "target_id"])

    # Convert IDs to string to ensure consistency
    relationships_df["source_id"] = relationships_df["source_id"].astype(str)
    relationships_df["target_id"] = relationships_df["target_id"].astype(str)

    return relationships_df


def visualize_focus_hierarchy(
    nodes_df, relationships_df, community_reports_df, focus_community
):
    """
    Visualize the focus community, its hierarchical children, and entities with relationships strictly in the hierarchy.

    Args:
        nodes_df (DataFrame): DataFrame of nodes (entities).
        relationships_df (DataFrame): DataFrame of relationships.
        community_reports_df (DataFrame): DataFrame of community reports.
        focus_community (str): ID of the focus community.
    """
    # Instantiate GraphBuilder
    graph_builder = GraphBuilder()

    # Calculate node degrees
    node_degrees = calculate_node_degrees(relationships_df)

    # Find the maximum degree for proper scaling
    max_degree = max(node_degrees.values()) if node_degrees else 1
    print(f"Maximum degree in network: {max_degree}")  # Debug print

    # Calculate community degrees (for reference only)
    community_degrees = {}

    def calculate_community_degree(comm_id):
        entities = nodes_df[nodes_df["community"].astype(str) == str(comm_id)]
        total_degree = sum(
            node_degrees.get(str(entity_id), 0) for entity_id in entities["id"]
        )
        return total_degree

    for comm in community_reports_df["community"]:
        community_degrees[str(comm)] = calculate_community_degree(comm)

    # Get the maximum level from community_reports
    max_level = community_reports_df["level"].max()

    # Generate color scheme based on number of levels
    COMMUNITY_COLORS = generate_color_scheme(max_level + 1)

    # Entity color
    ENTITY_COLOR = "#FFE66D"  # Soft Yellow

    def get_community_title(comm):
        """Get the title for a community."""
        title_data = community_reports_df[
            community_reports_df["community"] == str(comm)
        ]
        return (
            title_data.iloc[0]["title"] if not title_data.empty else f"Community {comm}"
        )

    def get_community_entities(comm):
        """Get all entities belonging to a specific community."""
        return nodes_df[nodes_df["community"].astype(str) == str(comm)]

    def get_child_communities(current_level):
        """Get all child communities from the next level."""
        return community_reports_df[community_reports_df["level"] == current_level + 1]

    def get_community_color(level):
        """Get color for community based on its level."""
        return COMMUNITY_COLORS[level]

    # Add the focus community as the root node
    focus_title = get_community_title(focus_community)

    # Get root community report data
    root_report = (
        community_reports_df[community_reports_df["community"] == focus_community].iloc[
            0
        ]
        if not community_reports_df[
            community_reports_df["community"] == focus_community
        ].empty
        else None
    )

    # Create root properties dictionary
    root_properties = {
        "type": "community",
        "degree": community_degrees.get(focus_community, 0),
    }

    if root_report is not None:
        root_properties.update(
            {
                "community_summary": root_report.get("summary", "No summary available"),
                "community_size": root_report.get("size", 0),
                "community_density": root_report.get("density", 0),
                "community_modularity": root_report.get("modularity", 0),
                "topic_keywords": root_report.get("keywords", []),
                "key_entities": root_report.get("key_entities", []),
                "level": 0,
            }
        )


    root_degree = community_degrees.get(focus_community, 0)
    root_properties["fontSize"] = root_degree + 11
    
    graph_builder.add_node(
        "root",
        label=focus_title,
        color=get_community_color(0),
        shape="rectangle",
        properties=root_properties
    )

    # Track all relevant entities in the focus community hierarchy
    focus_entity_ids = set()

    def add_community_hierarchy(current_level, parent_node, community_id):
        """Recursively add a community and its entities/children to the graph."""
        nonlocal focus_entity_ids

        # Add entities belonging to this specific community
        entities = get_community_entities(community_id)

        for _, entity in entities.iterrows():
            entity_id = str(entity["id"])
            entity_title = entity["title"]
            entity_description = entity.get("description", "No description available")

            # Scale based on relative degree
            entity_degree = node_degrees.get(entity_id, 0)
            entity_size = scale_node_size(entity_degree)

            print(
                f"Entity: {entity_title}, Degree: {entity_degree}, Size: {entity_size}"
            )  # Debug print

            entity_properties = {
                "description": entity_description,
                "community": community_id,
                "type": "entity",
                "degree": entity_degree,
                "width": entity_size,
                "height": entity_size,
                "fontSize": entity_degree + 11,
            }

            graph_builder.add_node(
                entity_id,
                label=entity_title,
                parent=parent_node,
                color=ENTITY_COLOR,
                properties=entity_properties,
            )
            focus_entity_ids.add(entity_id)

        # Add child communities
        child_communities = get_child_communities(current_level)
        for _, child in child_communities.iterrows():
            child_comm = str(child["community"])
            child_title = child["title"]
            child_level = child.get("level", current_level + 1)

            # Create properties dictionary
            node_properties = {
                "parent_label": focus_title,
                "children_labels": get_child_communities(current_level + 1)[
                    "title"
                ].tolist(),
                "actual_entity_count": len(get_community_entities(child_comm)),
                "level": child_level,
                "type": "community",
                "degree": community_degrees.get(child_comm, 0),
            }

            # Get community report summary
            community_report = (
                community_reports_df[
                    community_reports_df["community"] == child_comm
                ].iloc[0]
                if not community_reports_df[
                    community_reports_df["community"] == child_comm
                ].empty
                else None
            )

            if community_report is not None:
                node_properties.update(
                    {
                        "community_summary": community_report.get(
                            "summary", "No summary available"
                        ),
                        "community_size": community_report.get("size", 0),
                        "community_density": community_report.get("density", 0),
                        "community_modularity": community_report.get("modularity", 0),
                        "topic_keywords": community_report.get("keywords", []),
                        "key_entities": community_report.get("key_entities", []),
                    }
                )



            child_node_id = f"community_{child_comm}"
            community_degree = community_degrees.get(child_comm, 0)
            node_properties["fontSize"] = community_degree + 11
            
            graph_builder.add_node(
                child_node_id,
                label=child_title,
                parent=parent_node,
                color=get_community_color(child_level),
                shape="rectangle",
                properties=node_properties
            )


            # Recurse into child community
            add_community_hierarchy(current_level + 1, child_node_id, child_comm)

    # Start recursion from the focus community
    add_community_hierarchy(0, "root", focus_community)

    # Add relationships
    related_relationships = relationships_df[
        (relationships_df["source_id"].isin(focus_entity_ids))
        | (relationships_df["target_id"].isin(focus_entity_ids))
    ]

    # Add edges and external nodes
    for _, rel in related_relationships.iterrows():
        source_id = rel["source_id"]
        target_id = rel["target_id"]

        if source_id not in focus_entity_ids and target_id not in focus_entity_ids:
            continue

        # Add external nodes if needed
        if source_id not in graph_builder.graph_data["nodes"]:
            source_label = nodes_df.loc[nodes_df["id"] == source_id, "title"].values
            source_label = source_label[0] if len(source_label) > 0 else "External Node"
            source_description = nodes_df.loc[
                nodes_df["id"] == source_id, "description"
            ].values
            source_description = (
                source_description[0]
                if len(source_description) > 0
                else "No description available"
            )
            source_degree = node_degrees.get(source_id, 0)
            source_size = scale_node_size(source_degree)

            graph_builder.add_node(
                source_id,
                label=source_label,
                color="#D3D3D3",
                shape="ellipse",
                properties={
                    "description": source_description,
                    "type": "external",
                    "degree": source_degree,
                    "width": source_size,
                    "height": source_size,
                    "fontSize": source_degree + 11,
                },
            )

        if target_id not in graph_builder.graph_data["nodes"]:
            target_label = nodes_df.loc[nodes_df["id"] == target_id, "title"].values
            target_label = target_label[0] if len(target_label) > 0 else "External Node"
            target_description = nodes_df.loc[
                nodes_df["id"] == target_id, "description"
            ].values
            target_description = (
                target_description[0]
                if len(target_description) > 0
                else "No description available"
            )
            target_degree = node_degrees.get(target_id, 0)
            target_size = scale_node_size(target_degree)

            graph_builder.add_node(
                target_id,
                label=target_label,
                color="#D3D3D3",
                shape="ellipse",
                properties={
                    "description": target_description,
                    "type": "external",
                    "degree": target_degree,
                    "width": target_size,
                    "height": target_size,
                    "fontSize": target_degree + 11,
                },
            )

        # Add the edge
        edge_description = rel.get("description", "No description available")
        graph_builder.add_edge(
            source_id,
            target_id,
            color="#FF6347",
            properties={
                "description": edge_description,
                "weight": rel.get("weight", "N/A"),
                "type": rel.get("type", "Relationship"),
            },
        )

    # Display the graph
    graph_builder.display()



# declare graphbuilder class
from yfiles_jupyter_graphs import GraphWidget


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
        w = GraphWidget()
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
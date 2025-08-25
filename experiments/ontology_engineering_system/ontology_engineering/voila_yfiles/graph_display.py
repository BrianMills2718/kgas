from graphbuilder import GraphBuilder

class GraphDisplay:
    def __init__(self):
        self.graph = GraphBuilder()
        
    def build_ontology_graph(self):
        """Build and configure the graph visualization"""
        self.graph.default_node_style = {
            "shape": "rectangle",
            "color": "#4287f5",
            "properties": {
                "fontSize": 14,
                "height": 40,
                "width": 120
            }
        }
        
        self.graph.default_edge_style = {
            "color": "#666666",
            "thickness": 2.0,
            "directed": True
        }
        
    def add_class(self, class_id, label):
        """Add an ontology class to the graph"""
        self.graph.add_node(
            class_id,
            label=label,
            shape="rectangle",
            color="#4287f5",
            properties={"fontSize": 14}
        )
        
    def add_property(self, prop_id, source_class, target_class, label):
        """Add a property relationship between classes"""
        self.graph.add_edge(
            source_class,
            target_class,
            label=label,
            color="#666666",
            thickness=2.0,
            directed=True
        )
        
    def display_graph(self):
        """Display the graph using yfiles"""
        return self.graph.display()
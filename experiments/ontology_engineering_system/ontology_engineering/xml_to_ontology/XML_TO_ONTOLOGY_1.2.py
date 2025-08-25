import xml.etree.ElementTree as ET
from pyvis.network import Network
import re

def create_ontology_visualization(xsd_file_path, output_file='ontology.html'):
    # Initialize pyvis network with notebook=False for standalone HTML
    net = Network(height='750px', width='100%', bgcolor='#ffffff', font_color='#333333', notebook=False)
    
    # Parse the XSD file
    tree = ET.parse(xsd_file_path)
    root = tree.getroot()
    
    print(f"Root tag: {root.tag}")  # Debugging
    
    # Track nodes to avoid duplicates
    added_nodes = set()
    
    # Register all namespaces
    namespaces = dict([node for _, node in ET.iterparse(xsd_file_path, events=['start-ns'])])
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    # Helper function to get clean element name
    def get_clean_name(tag):
        # Remove namespace from tag
        return tag.split('}')[-1] if '}' in tag else tag
    
    def add_element_to_graph(element, parent_name=None, level=0):
        # Get element name without namespace
        element_name = get_clean_name(element.tag)
        print(f"{'  ' * level}Processing element: {element_name}")  # Debugging
        
        # Add node if not already added
        if element_name not in added_nodes:
            # Different colors for different types of nodes
            if element_name == 'element':
                color = "#97C2FC"  # Light blue
            elif element_name in ['complexType', 'simpleType']:
                color = "#FB7E81"  # Light red
            elif element_name in ['sequence', 'choice']:
                color = "#7BE141"  # Light green
            else:
                color = "#FFA807"  # Light orange
                
            net.add_node(element_name, 
                        label=element_name, 
                        title=element_name,
                        color=color)
            added_nodes.add(element_name)
            print(f"{'  ' * level}Added node: {element_name}")
        
        # Add edge if there's a parent
        if parent_name:
            net.add_edge(parent_name, element_name)
            print(f"{'  ' * level}Added edge: {parent_name} -> {element_name}")  # Debugging
        
        # Process attributes
        for attr_name, attr_value in element.attrib.items():
            clean_attr_name = get_clean_name(attr_name)
            attr_label = f"{element_name}_{clean_attr_name}"
            if attr_label not in added_nodes:
                net.add_node(attr_label, label=clean_attr_name, 
                           title=f"Attribute: {clean_attr_name}\nValue: {attr_value}")
                added_nodes.add(attr_label)
                net.add_edge(element_name, attr_label, dashes=True)
                print(f"{'  ' * level}Added attribute: {attr_label}")  # Debugging
        
        # Process child elements including xsd:element, xsd:complexType, etc.
        for child in element:
            add_element_to_graph(child, element_name, level + 1)
            
        # Special handling for XSD specific elements
        if element_name == 'element' and 'name' in element.attrib:
            elem_name = element.attrib['name']
            if elem_name not in added_nodes:
                net.add_node(elem_name, label=elem_name, title=f"XSD Element: {elem_name}")
                added_nodes.add(elem_name)
                net.add_edge(element_name, elem_name)
                print(f"{'  ' * level}Added XSD element: {elem_name}")  # Debugging
    
    # Start processing from root
    add_element_to_graph(root)
    
    print(f"Total nodes added: {len(added_nodes)}")  # Debugging
    
    # Configure network options
    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])
    net.set_options("""
    {
        "nodes": {
            "shape": "box",
            "size": 25,
            "font": {
                "size": 16,
                "face": "arial",
                "bold": true
            },
            "color": {
                "border": "#2B7CE9",
                "background": "#D2E5FF"
            }
        },
        "edges": {
            "color": {
                "color": "#2B7CE9",
                "inherit": false
            },
            "smooth": {
                "type": "continuous",
                "forceDirection": "none"
            },
            "length": 250
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -2000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04,
                "damping": 0.09,
                "avoidOverlap": 1
            },
            "minVelocity": 0.75
        }
    }
    """)
    
    # Save the visualization
    net.write_html(output_file)
    print(f"Visualization saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    xsd_file_path = "DM2Foundation_v2.02.xsd"  # Replace with your XSD file path
    create_ontology_visualization(xsd_file_path)

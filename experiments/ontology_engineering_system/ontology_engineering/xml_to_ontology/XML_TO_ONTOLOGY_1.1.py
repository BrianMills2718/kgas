#XML_TO_ONTOLOGY_1.1.py
import xml.etree.ElementTree as ET
from pyvis.network import Network
from IPython.display import IFrame, display, HTML
import sys
import traceback

def extract_enhanced_ontology(xml_file):
    """Extract ontology with relationship mapping"""
    try:
        print("\n=== Starting Ontology Extraction ===")
        
        # Define namespaces
        ns = {
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'dm2': 'http://www.ideasgroup.org/dm2'
        }
        
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        nodes = {}
        edges = set()  # Using set to avoid duplicate edges
        
        def add_node(node_id, label, node_type, details=""):
            """Helper function to add nodes"""
            if node_id not in nodes:
                nodes[node_id] = {
                    'label': label,
                    'type': node_type,
                    'details': details
                }
                print(f"Added node: {label} ({node_type})")
                return True
            return False

        def add_edge(source, target, edge_type=""):
            """Helper function to add edges"""
            if source and target and source in nodes and target in nodes:
                edge = (source, target, edge_type)
                if edge not in edges:
                    edges.add(edge)
                    print(f"Added edge: {nodes[source]['label']} -> {nodes[target]['label']} ({edge_type})")

        def process_complex_type(complex_type, parent_id=None):
            """Process complex type definitions"""
            name = complex_type.get('name', '')
            if name:
                type_id = f"complexType_{name}"
                if add_node(type_id, name, 'complexType'):
                    if parent_id:
                        add_edge(parent_id, type_id, 'defines')

                    # Process extensions
                    for extension in complex_type.findall('.//xs:extension', ns):
                        base = extension.get('base', '')
                        if base:
                            # Remove namespace prefix if present
                            if ':' in base:
                                base = base.split(':')[1]
                            base_id = f"complexType_{base}"
                            add_node(base_id, base, 'complexType')
                            add_edge(type_id, base_id, 'extends')

                    # Process sequence elements
                    for sequence in complex_type.findall('.//xs:sequence', ns):
                        for elem in sequence.findall('.//xs:element', ns):
                            elem_name = elem.get('name', elem.get('ref', ''))
                            if elem_name:
                                elem_id = f"element_{elem_name}"
                                add_node(elem_id, elem_name, 'element')
                                add_edge(type_id, elem_id, 'contains')

                    # Process choice elements
                    for choice in complex_type.findall('.//xs:choice', ns):
                        for elem in choice.findall('.//xs:element', ns):
                            elem_name = elem.get('name', elem.get('ref', ''))
                            if elem_name:
                                elem_id = f"element_{elem_name}"
                                add_node(elem_id, elem_name, 'element')
                                add_edge(type_id, elem_id, 'choice')

                    # Process attributes
                    for attr in complex_type.findall('.//xs:attribute', ns):
                        attr_name = attr.get('name', '')
                        if attr_name:
                            attr_id = f"attribute_{attr_name}"
                            add_node(attr_id, attr_name, 'attribute')
                            add_edge(type_id, attr_id, 'has_attribute')

        def process_element(element, parent_id=None):
            """Process elements and their relationships"""
            name = element.get('name', element.get('ref', ''))
            if name:
                elem_id = f"element_{name}"
                add_node(elem_id, name, 'element')
                
                if parent_id:
                    add_edge(parent_id, elem_id, 'contains')

                # Handle type reference
                type_name = element.get('type', '')
                if type_name:
                    if ':' in type_name:
                        type_name = type_name.split(':')[1]
                    type_id = f"complexType_{type_name}"
                    add_node(type_id, type_name, 'complexType')
                    add_edge(elem_id, type_id, 'hasType')

                # Process annotations
                for annotation in element.findall('.//xs:annotation/xs:documentation', ns):
                    if annotation.text:
                        nodes[elem_id]['details'] = annotation.text.strip()

                # Process nested complex types
                for complex_type in element.findall('.//xs:complexType', ns):
                    process_complex_type(complex_type, elem_id)

                # Handle base types through extension
                for extension in element.findall('.//xs:extension', ns):
                    base = extension.get('base', '')
                    if base:
                        if ':' in base:
                            base = base.split(':')[1]
                        base_id = f"complexType_{base}"
                        add_node(base_id, base, 'complexType')
                        add_edge(elem_id, base_id, 'extends')

        # Process global elements
        for element in root.findall('.//xs:element', ns):
            process_element(element)

        # Process global complex types
        for complex_type in root.findall('.//xs:complexType', ns):
            process_complex_type(complex_type)

        # Process global simple types
        for simple_type in root.findall('.//xs:simpleType', ns):
            name = simple_type.get('name', '')
            if name:
                type_id = f"simpleType_{name}"
                add_node(type_id, name, 'simpleType')

        print(f"Processed {len(nodes)} nodes and {len(edges)} edges")
        return nodes, edges
        
    except Exception as e:
        print(f"Error in extract_enhanced_ontology: {str(e)}")
        traceback.print_exc()
        return {}, set()

def visualize_enhanced_ontology(xml_file, output_file='schema_ontology.html'):
    """Visualize ontology with improved styling"""
    try:
        print("\n=== Starting Visualization ===")
        
        nodes, edges = extract_enhanced_ontology(xml_file)
        
        if not nodes:
            print("No nodes extracted, visualization cannot proceed")
            return
            
        print(f"\nCreating visualization with {len(nodes)} nodes and {len(edges)} edges")
        
        # Create network with improved settings
        net = Network(
            height='900px',
            width='100%',
            bgcolor='#ffffff',
            font_color='#000000',
            directed=True,
            notebook=True
        )

        # Enhanced color scheme with better contrast
        colors = {
            'element': '#2ECC71',     # Emerald Green
            'complexType': '#3498DB',  # Bright Blue
            'simpleType': '#9B59B6',   # Amethyst Purple
            'attribute': '#E67E22'     # Carrot Orange
        }
        
        # Enhanced node styling
        for node_id, info in nodes.items():
            label = f"{info['label']}\n({info['type']})"  # Include type in label
            title = f"Type: {info['type']}\nDetails: {info.get('details', 'No details available')}"
            
            net.add_node(
                node_id,
                label=label,
                title=title,
                color=colors.get(info['type'], '#95A5A6'),  # Default gray for unknown types
                size=30 if info['type'] == 'complexType' else 25,
                font={'size': 14},
                shape='box' if info['type'] == 'complexType' else 'dot'
            )
        
        # Enhanced edge styling with visible labels
        edge_colors = {
            'extends': '#E74C3C',      # Red
            'contains': '#27AE60',      # Green
            'hasType': '#3498DB',       # Blue
            'choice': '#F1C40F',        # Yellow
            'has_attribute': '#9B59B6'  # Purple
        }
        
        for source, target, edge_type in edges:
            net.add_edge(
                source, 
                target,
                label=edge_type,
                title=f"Relationship: {edge_type}",
                color=edge_colors.get(edge_type, '#95A5A6'),
                width=2,
                font={'size': 10, 'color': '#2C3E50'},
                arrows={
                    'to': {
                        'enabled': True,
                        'type': 'arrow'
                    }
                },
                smooth={'type': 'curvedCW', 'roundness': 0.2}
            )
        
        # Configure physics for better layout
        net.set_options("""
        const options = {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {
                    "enabled": true,
                    "iterations": 1000
                }
            },
            "edges": {
                "smooth": {
                    "type": "curvedCW",
                    "roundness": 0.2
                }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": true
            }
        }
        """)
        
        # Add legend
        legend_html = """
        <div style="position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border: 1px solid #ccc;">
            <h3>Legend</h3>
            <p><span style="color: #2ECC71;">●</span> Element</p>
            <p><span style="color: #3498DB;">■</span> Complex Type</p>
            <p><span style="color: #9B59B6;">●</span> Simple Type</p>
            <p><span style="color: #E67E22;">●</span> Attribute</p>
            <hr>
            <p><span style="color: #E74C3C;">→</span> Extends</p>
            <p><span style="color: #27AE60;">→</span> Contains</p>
            <p><span style="color: #3498DB;">→</span> Has Type</p>
            <p><span style="color: #F1C40F;">→</span> Choice</p>
            <p><span style="color: #9B59B6;">→</span> Has Attribute</p>
        </div>
        """
        
        # Save visualization with legend
        net.save_graph(output_file)
        
        # Add legend to the saved file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(output_file, 'w', encoding='utf-8') as f:
            content = content.replace('</body>', f'{legend_html}</body>')
            f.write(content)
            
        print(f"Visualization saved as {output_file}")
        
        # Display in notebook
        display(HTML(filename=output_file))
            
    except Exception as e:
        print(f"Error in visualization: {str(e)}")
        traceback.print_exc()

# Run visualization
xml_file = r"C:\Users\bmills\Downloads\DoDAF-digitized-master\DoDAF-digitized-master\DM2Foundation_v2.02.xsd"
visualize_enhanced_ontology(xml_file)
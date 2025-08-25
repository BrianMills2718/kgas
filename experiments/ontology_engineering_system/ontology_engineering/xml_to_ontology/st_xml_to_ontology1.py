import streamlit as st
import json
import xml.etree.ElementTree as ET
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
import io
from xml.dom import minidom

# Define a class representation
@dataclass
class Company:
    name: str
    description: str
    industry: str
    employees: int
    locations: list
    products: list

def text_to_structures(text, company_name="Example Corp"):
    """Convert input text to various data structures"""
    # Basic company info for demonstration
    company_info = {
        "name": company_name,
        "description": text,
        "industry": "Technology",
        "employees": 500,
        "locations": ["New York", "San Francisco"],
        "products": ["Product A", "Product B"]
    }
    
    return company_info

def create_class_representation(company_info):
    # Format each field on a new line
    return (
        f"Company(\n"
        f"    name: {company_info['name']},\n"
        f"    description: {company_info['description']},\n"
        f"    industry: {company_info['industry']},\n"
        f"    employees: {company_info['employees']},\n"
        f"    locations: {company_info['locations']},\n"
        f"    products: {company_info['products']}\n"
        f")"
    )

def create_json_representation(company_info):
    return json.dumps(company_info, indent=2)

def create_xml_representation(company_info):
    root = ET.Element("company")
    for key, value in company_info.items():
        if isinstance(value, list):
            container = ET.SubElement(root, key)
            for item in value:
                ET.SubElement(container, "item").text = str(item)
        else:
            ET.SubElement(root, key).text = str(value)
    
    # Convert to string with proper indentation
    rough_string = ET.tostring(root, encoding='unicode', method='xml')
    # Parse the string and pretty print it
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="    ")

def create_csv_representation(company_info):
    # Flatten the nested structure
    flat_data = {
        key: '\n'.join(map(str, value)) if isinstance(value, list) else value
        for key, value in company_info.items()
    }
    df = pd.DataFrame([flat_data])
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()

def create_relational_tables(company_info):
    # Create multiple related tables
    companies_df = pd.DataFrame({
        'name': [company_info['name']],
        'description': [company_info['description']],
        'industry': [company_info['industry']],
        'employees': [company_info['employees']]
    })
    
    locations_df = pd.DataFrame({
        'company_name': [company_info['name']] * len(company_info['locations']),
        'location': company_info['locations']
    })
    
    products_df = pd.DataFrame({
        'company_name': [company_info['name']] * len(company_info['products']),
        'product': company_info['products']
    })
    
    return companies_df, locations_df, products_df

def create_network_visualization(company_info):
    G = nx.Graph()
    
    # Add company node
    G.add_node(company_info['name'], node_type='company')
    
    # Add and connect locations
    for loc in company_info['locations']:
        G.add_node(loc, node_type='location')
        G.add_edge(company_info['name'], loc)
    
    # Add and connect products
    for prod in company_info['products']:
        G.add_node(prod, node_type='product')
        G.add_edge(company_info['name'], prod)
    
    return G

def main():
    st.title("Data Structure Visualizer")
    
    # Input text area
    text_input = st.text_area(
        "Enter company description:",
        "A technology company specializing in AI solutions and cloud computing services."
    )
    company_name = st.text_input("Company name:", "Example Corp")
    
    if text_input:
        company_info = text_to_structures(text_input, company_name)
        
        # Class representation
        st.header("Class Representation")
        company_class = create_class_representation(company_info)
        st.code(company_class)
        
        # JSON representation
        st.header("JSON Representation")
        json_repr = create_json_representation(company_info)
        st.code(json_repr, language='json')
        
        # XML representation
        st.header("XML Representation")
        xml_repr = create_xml_representation(company_info)
        st.code(xml_repr, language='xml')
        
        # CSV representation
        st.header("CSV Representation")
        csv_repr = create_csv_representation(company_info)
        st.code(csv_repr)
        
        # Relational tables
        st.header("Relational Tables")
        companies_df, locations_df, products_df = create_relational_tables(company_info)
        
        st.subheader("Companies Table")
        st.dataframe(companies_df)
        
        st.subheader("Locations Table")
        st.dataframe(locations_df)
        
        st.subheader("Products Table")
        st.dataframe(products_df)
        
        # Network visualization
        st.header("Network Representation")
        G = create_network_visualization(company_info)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        pos = nx.spring_layout(G)
        
        # Draw nodes with different colors based on type
        node_colors = ['lightblue' if G.nodes[node]['node_type'] == 'company'
                      else 'lightgreen' if G.nodes[node]['node_type'] == 'location'
                      else 'lightcoral' for node in G.nodes()]
        
        nx.draw(G, pos, with_labels=True, node_color=node_colors,
                node_size=2000, font_size=8, font_weight='bold')
        
        st.pyplot(fig)
        
        st.markdown("""
        ### Notes on Data Structure Representations:
        
        1. **Class**: Provides encapsulation and method integration
        2. **JSON**: Hierarchical, readable, widely used in APIs
        3. **XML**: Tree structure, good for document-like data
        4. **CSV**: Flat structure, good for tabular data
        5. **Relational Tables**: Normalized, good for complex queries
        6. **Network/Graph**: Shows relationships and connections
        
        Regarding hypergraphs: They can indeed represent any other data structure, as they allow edges to connect multiple nodes (unlike regular graphs). This makes them particularly suitable for representing:
        - Hierarchical relationships (like XML)
        - Many-to-many relationships (like relational tables)
        - Nested structures (like JSON)
        - Class hierarchies
        """)

if __name__ == "__main__":
    main()
"""
VERSION 1.2: THIS CODE TAKES TEXT INPUT, INVOKES A LANGCHAIN LLM TO PRODUCE AN RST HYPERGRAPH REPRESENTATION,
AND THEN VISUALIZES IT AS A BIPARTITE GRAPH WITH REIFIED HYPEREDGES.
"""

import json
import networkx as nx
import matplotlib.pyplot as plt

# Import necessary LangChain modules
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# VERSION 1.0: FUNCTION TO INVOKE LLM WITH A DETAILED PROMPT FOR RST HYPERGRAPH CONVERSION
def get_rst_hypergraph(text: str) -> dict:
    # This prompt instructs the LLM to convert raw text directly into a recursive hypergraph,
    # in accordance with Rhetorical Structure Theory (RST), without producing an intermediate binary parse tree.
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
You are an expert in computational linguistics and discourse analysis. Your task is to convert a given text into a recursive hypergraph representation of its discourse structure following Rhetorical Structure Theory (RST).

INSTRUCTIONS:
1. Do not generate an intermediate binary parse tree. Convert the text directly into a hypergraph.
2. Each node corresponds to an Elementary Discourse Unit (EDU) or a higher-level discourse unit.
3. Each hyperedge denotes a discourse relation (e.g., "Elaboration", "Joint", "Condition") connecting multiple nodes. Reify each hyperedge by outputting it as an independent object.
4. Output the hypergraph as JSON with two keys: "nodes" and "hyperedges".
   - "nodes": a list of objects, each with a unique "id" (integer) and "text" (the EDU or aggregated discourse unit).
   - "hyperedges": a list of objects, each with a unique "id" (integer), a "relation" (discourse relation type), and "node_ids" (list of node ids that it connects).
5. Provide a concise example:
   Example Input: "John went to the store. He bought milk."
   Example Output:
   {
     "nodes": [
       {"id": 1, "text": "John went to the store."},
       {"id": 2, "text": "He bought milk."}
     ],
     "hyperedges": [
       {"id": 1, "relation": "Elaboration", "node_ids": [1, 2]}
     ]
   }

Now, process the following text:
{text}
"""
    )
    
    # Using OpenAI via LangChain with zero temperature for deterministic output.
    llm = OpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(text=text)
    
    # The response is expected to be a valid JSON string.
    try:
        hypergraph = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError("The LLM response could not be parsed as JSON. Please check the prompt or output format.") from e
    return hypergraph

# VERSION 1.1: FUNCTION TO CONSTRUCT A BIPARTITE GRAPH FROM THE HYPERGRAPH
def build_bipartite_graph(hypergraph: dict) -> nx.Graph:
    # We construct a bipartite graph where one set contains EDU nodes and the other contains reified hyperedge nodes.
    B = nx.Graph()
    # Add EDU nodes with attribute "bipartite" = 0.
    for node in hypergraph.get("nodes", []):
        B.add_node(f"edu_{node['id']}", label=node["text"], bipartite=0)
    # Add hyperedge nodes with attribute "bipartite" = 1 and connect them to the corresponding EDU nodes.
    for hedge in hypergraph.get("hyperedges", []):
        B.add_node(f"he_{hedge['id']}", label=hedge["relation"], bipartite=1)
        for nid in hedge.get("node_ids", []):
            B.add_edge(f"he_{hedge['id']}", f"edu_{nid}")
    return B

# VERSION 1.2: FUNCTION TO VISUALIZE THE BIPARTITE GRAPH (RST HYPERGRAPH)
def visualize_hypergraph(B: nx.Graph):
    # Separate nodes by their bipartite attribute.
    edu_nodes = [n for n, d in B.nodes(data=True) if d["bipartite"] == 0]
    he_nodes = [n for n, d in B.nodes(data=True) if d["bipartite"] == 1]
    
    pos = nx.spring_layout(B, seed=42)  # Deterministic layout for reproducibility.
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(B, pos, nodelist=edu_nodes, node_color="skyblue", node_size=500, label="EDU Nodes")
    nx.draw_networkx_nodes(B, pos, nodelist=he_nodes, node_color="lightgreen", node_shape="s", node_size=700, label="Hyperedge Nodes")
    nx.draw_networkx_edges(B, pos)
    
    # Create labels from the node attribute "label".
    labels = {n: B.nodes[n]["label"] for n in B.nodes()}
    nx.draw_networkx_labels(B, pos, labels, font_size=8)
    
    plt.title("RST Hypergraph Visualization with Reified Hyperedges")
    plt.axis("off")
    plt.legend(scatterpoints=1)
    plt.show()

# MAIN EXECUTION BLOCK
if __name__ == "__main__":
    # Sample input text (replace with any text as needed)
    sample_text = (
        "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work. "
        "And the only way to do great is to love what you do. If you haven’t found it yet, keep looking. Don’t settle."
    )
    
    # Step 1: Convert text to RST hypergraph using the LLM.
    hypergraph = get_rst_hypergraph(sample_text)
    
    # Step 2: Build the bipartite graph with reified hyperedges.
    B = build_bipartite_graph(hypergraph)
    
    # Step 3: Visualize the resulting hypergraph.
    visualize_hypergraph(B)

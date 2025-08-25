"""
T68 PageRank Integration
Adds PageRank calculation to the pipeline
"""

import networkx as nx
from neo4j import GraphDatabase
from typing import Dict

class T68PageRankIntegration:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def calculate_and_store_pagerank(self) -> Dict[str, float]:
        """
        Calculate PageRank and store scores in Neo4j
        """
        # Load graph from Neo4j
        G = nx.DiGraph()
        
        with self.driver.session() as session:
            # Get all nodes
            nodes = session.run("MATCH (n:Entity) RETURN n.entity_id as id, n.canonical_name as name")
            for node in nodes:
                node_id = node['id']
                node_name = node['name']
                if node_id and node_name:  # Only add nodes with valid IDs
                    G.add_node(node_id, name=node_name)
            
            # Get all edges - use undirected relationships
            edges = session.run("""
                MATCH (n:Entity)-[r]-(m:Entity) 
                WHERE n.entity_id IS NOT NULL AND m.entity_id IS NOT NULL
                RETURN n.entity_id as source, m.entity_id as target, r.weight as weight
            """)
            for edge in edges:
                source = edge['source']
                target = edge['target']
                if source and target and source != target:  # Valid edges only
                    G.add_edge(source, target, weight=edge.get('weight', 1.0))
        
        # Calculate PageRank
        if G.number_of_nodes() > 0:
            pagerank = nx.pagerank(G, alpha=0.85)
            
            # Store scores back to Neo4j
            with self.driver.session() as session:
                for node_id, score in pagerank.items():
                    session.run("""
                        MATCH (n:Entity {entity_id: $id})
                        SET n.pagerank_score = $score
                        RETURN n
                    """, id=node_id, score=score)
            
            return pagerank
        
        return {}
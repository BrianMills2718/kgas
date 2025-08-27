#!/usr/bin/env python3
"""
CrossModal Service - Handles graph↔table conversions
Hypergraph approach: edges as rows, properties as columns
"""

import pandas as pd
from neo4j import GraphDatabase
import sqlite3
from typing import List, Dict, Any

class CrossModalService:
    """Convert between graph and tabular representations"""
    
    def __init__(self, neo4j_driver, sqlite_path: str):
        self.neo4j = neo4j_driver
        self.sqlite_path = sqlite_path
    
    def graph_to_table(self, entity_ids: List[str]) -> pd.DataFrame:
        """
        Export graph to relational tables for statistical analysis
        
        Creates:
        1. vs_entity_metrics: node properties and graph metrics  
        2. vs_relationships: edges as rows with properties
        """
        with self.neo4j.session() as session:
            # Get entities with metrics
            entity_query = """
            MATCH (e:VSEntity)
            WHERE e.entity_id IN $entity_ids
            OPTIONAL MATCH (e)-[r]-()
            RETURN e.entity_id as id,
                   e.canonical_name as name,
                   e.entity_type as type,
                   count(DISTINCT r) as degree,
                   properties(e) as properties
            """
            entities = session.run(entity_query, entity_ids=entity_ids).data()
            
            # Get relationships (hypergraph as table)
            relationship_query = """
            MATCH (s:VSEntity)-[r]->(t:VSEntity)
            WHERE s.entity_id IN $entity_ids
            RETURN s.entity_id as source,
                   t.entity_id as target,
                   type(r) as relationship_type,
                   properties(r) as properties
            """
            relationships = session.run(relationship_query, entity_ids=entity_ids).data()
        
        # Write to SQLite
        conn = sqlite3.connect(self.sqlite_path)
        
        # Entity metrics table - serialize properties as JSON
        entity_df = pd.DataFrame(entities)
        if 'properties' in entity_df.columns:
            import json
            entity_df['properties'] = entity_df['properties'].apply(json.dumps)
        entity_df.to_sql('vs_entity_metrics', conn, if_exists='replace', index=False)
        
        # Relationships table - serialize properties as JSON
        rel_df = pd.DataFrame(relationships)
        if 'properties' in rel_df.columns:
            import json
            rel_df['properties'] = rel_df['properties'].apply(json.dumps)
        rel_df.to_sql('vs_relationships', conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"✅ Exported {len(entities)} entities and {len(relationships)} relationships")
        return entity_df
    
    def table_to_graph(self, relationships_df: pd.DataFrame) -> Dict:
        """
        Convert relational table to graph
        Each row becomes an edge with properties
        """
        created_edges = 0
        
        with self.neo4j.session() as session:
            for _, row in relationships_df.iterrows():
                query = """
                MATCH (s:VSEntity {entity_id: $source})
                MATCH (t:VSEntity {entity_id: $target})
                CREATE (s)-[r:VS_RELATION {type: $rel_type}]->(t)
                SET r += $properties
                """
                session.run(
                    query,
                    source=row['source'],
                    target=row['target'],
                    rel_type=row.get('relationship_type', 'RELATED'),
                    properties=row.get('properties', {})
                )
                created_edges += 1
        
        return {"edges_created": created_edges}
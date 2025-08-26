#!/usr/bin/env python3
"""
Neo4j Graph Builder - Real graph creation in Neo4j
NO MOCKS - This uses actual Neo4j database
"""

import os
from typing import Dict, Any, List
from neo4j import GraphDatabase
from datetime import datetime

class Neo4jGraphBuilder:
    """
    Build knowledge graph in Neo4j from extracted entities.
    Real implementation, no mocks.
    """
    
    def __init__(self):
        self.tool_id = "Neo4jGraphBuilder"
        self.name = "Neo4j Graph Builder"
        self.input_type = "entities"  # Will be mapped to DataType.ENTITIES
        self.output_type = "graph"  # Will be mapped to DataType.GRAPH
        
        # Neo4j connection parameters
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'devpassword')
        
        # Create driver
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
        # Test connection
        try:
            self.driver.verify_connectivity()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Neo4j: {e}")
    
    def process(self, entities_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create graph nodes and relationships in Neo4j
        
        Args:
            entities_data: Dict with 'entities' key containing list of entities
            
        Returns:
            Dict with graph creation results and statistics
        """
        try:
            # Extract entities list
            if isinstance(entities_data, dict):
                entities = entities_data.get('entities', [])
            elif isinstance(entities_data, list):
                entities = entities_data
            else:
                entities = []
            
            if not entities:
                return {
                    'success': False,
                    'nodes_created': 0,
                    'relationships_created': 0,
                    'error': 'No entities provided'
                }
            
            nodes_created = 0
            relationships_created = 0
            
            with self.driver.session() as session:
                # Mark nodes from this framework run
                created_by = 'framework_poc'
                created_at = datetime.now().isoformat()
                
                # Create nodes for each entity
                for entity in entities:
                    if isinstance(entity, dict):
                        entity_text = entity.get('text', '')
                        entity_type = entity.get('type', 'UNKNOWN')
                        confidence = entity.get('confidence', 0.5)
                        
                        if entity_text:
                            # Create node with framework marker
                            result = session.run("""
                                MERGE (e:Entity {name: $name})
                                SET e.type = $type,
                                    e.confidence = $confidence,
                                    e.created_by = $created_by,
                                    e.created_at = $created_at,
                                    e.framework_tool = $tool_id
                                RETURN e
                            """, 
                            name=entity_text,
                            type=entity_type,
                            confidence=confidence,
                            created_by=created_by,
                            created_at=created_at,
                            tool_id=self.tool_id)
                            
                            if result.single():
                                nodes_created += 1
                
                # Create relationships between co-occurring entities
                # (Simple approach: connect entities from same extraction)
                if len(entities) > 1:
                    for i, entity1 in enumerate(entities[:-1]):
                        if not isinstance(entity1, dict):
                            continue
                        for entity2 in entities[i+1:]:
                            if not isinstance(entity2, dict):
                                continue
                                
                            name1 = entity1.get('text', '')
                            name2 = entity2.get('text', '')
                            
                            if name1 and name2:
                                result = session.run("""
                                    MATCH (e1:Entity {name: $name1})
                                    MATCH (e2:Entity {name: $name2})
                                    MERGE (e1)-[r:CO_OCCURS]->(e2)
                                    SET r.created_by = $created_by,
                                        r.created_at = $created_at
                                    RETURN r
                                """,
                                name1=name1,
                                name2=name2,
                                created_by=created_by,
                                created_at=created_at)
                                
                                if result.single():
                                    relationships_created += 1
                
                # Get total count for verification
                count_result = session.run("""
                    MATCH (n:Entity {created_by: $created_by})
                    RETURN count(n) as count
                """, created_by=created_by)
                
                total_framework_nodes = count_result.single()['count']
            
            return {
                'success': True,
                'nodes_created': nodes_created,
                'relationships_created': relationships_created,
                'total_framework_nodes': total_framework_nodes,
                'neo4j_uri': self.uri,
                'created_by': created_by,
                'timestamp': created_at
            }
            
        except Exception as e:
            return {
                'success': False,
                'nodes_created': 0,
                'relationships_created': 0,
                'error': str(e)
            }
    
    def cleanup(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
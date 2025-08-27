#!/usr/bin/env python3
"""
Simplified IdentityService for MVP
Just handles basic entity deduplication
"""

from typing import List, Dict
from neo4j import GraphDatabase

class IdentityServiceV3:
    """
    Simplified for MVP - just handles entity deduplication
    The bug fix (creating Entity nodes) is handled in GraphPersister
    """
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def find_similar_entities(self, name: str, threshold: float = 0.8) -> List[Dict]:
        """
        Find entities with similar names (for deduplication)
        MVP: Simple string matching, can add embeddings later
        """
        with self.driver.session() as session:
            query = """
            MATCH (e:VSEntity)
            WHERE toLower(e.canonical_name) CONTAINS toLower($name)
            RETURN e.entity_id as id, e.canonical_name as name
            LIMIT 10
            """
            result = session.run(query, name=name)
            return [dict(record) for record in result]
    
    def merge_entities(self, entity_id1: str, entity_id2: str) -> str:
        """
        Merge two entities that refer to the same real-world entity
        Not critical for MVP - can be manual process initially
        """
        with self.driver.session() as session:
            # Move all relationships to entity1
            merge_query = """
            MATCH (e1:VSEntity {entity_id: $id1})
            MATCH (e2:VSEntity {entity_id: $id2})
            OPTIONAL MATCH (e2)-[r]->(target)
            CREATE (e1)-[r2:VS_MERGED]->(target)
            SET r2 = properties(r)
            DELETE r
            DELETE e2
            RETURN e1.entity_id as merged_id
            """
            result = session.run(merge_query, id1=entity_id1, id2=entity_id2)
            return result.single()['merged_id']
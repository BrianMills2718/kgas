#!/usr/bin/env python3
"""Graph persistence to Neo4j with uncertainty tracking"""

import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any
from neo4j import GraphDatabase

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.identity_service_v3 import IdentityServiceV3
from services.crossmodal_service import CrossModalService

class GraphPersister:
    """Persist knowledge graph to Neo4j"""
    
    def __init__(self, neo4j_driver, identity_service=None, crossmodal_service=None):
        self.tool_id = "GraphPersister"
        self.neo4j = neo4j_driver
        self.identity = identity_service
        self.crossmodal = crossmodal_service
    
    def process(self, kg_data: Dict) -> Dict[str, Any]:
        """
        Persist knowledge graph to Neo4j
        
        Args:
            kg_data: Dict with 'entities' and 'relationships' lists
            
        Returns:
            Dict with success status, created counts, uncertainty, and reasoning
        """
        if not kg_data or 'entities' not in kg_data:
            return {
                'success': False,
                'error': 'Invalid knowledge graph data',
                'uncertainty': 1.0,
                'reasoning': 'No entities provided for persistence'
            }
        
        entities = kg_data.get('entities', [])
        relationships = kg_data.get('relationships', [])
        
        # Create entities in Neo4j (FIXES THE IDENTITYSERVICE BUG!)
        entity_map = {}  # Map from extraction IDs to Neo4j IDs
        entities_created = 0
        entities_failed = 0
        
        for entity in entities:
            try:
                neo4j_id = self._create_or_merge_entity(entity)
                if neo4j_id:
                    entity_map[entity.get('id', '')] = neo4j_id
                    entities_created += 1
                else:
                    entities_failed += 1
            except Exception as e:
                print(f"Failed to create entity {entity.get('name')}: {e}")
                entities_failed += 1
        
        # Create relationships in Neo4j
        relationships_created = 0
        relationships_failed = 0
        
        for rel in relationships:
            source_id = entity_map.get(rel.get('source'))
            target_id = entity_map.get(rel.get('target'))
            
            if source_id and target_id:
                try:
                    self._create_relationship(source_id, target_id, rel)
                    relationships_created += 1
                except Exception as e:
                    print(f"Failed to create relationship: {e}")
                    relationships_failed += 1
            else:
                relationships_failed += 1
        
        # Export to SQLite for cross-modal analysis
        if self.crossmodal and entity_map:
            try:
                self.crossmodal.graph_to_table(list(entity_map.values()))
                print("✅ Exported graph metrics to SQLite")
            except Exception as e:
                print(f"Warning: Failed to export to SQLite: {e}")
        
        # Assess persistence uncertainty
        # CRITICAL: Zero uncertainty if everything succeeded (pure storage operation)
        total_items = len(entities) + len(relationships)
        failed_items = entities_failed + relationships_failed
        
        if failed_items == 0:
            # Perfect persistence - no uncertainty
            uncertainty = 0.0
            reasoning = f"All {entities_created} entities and {relationships_created} relationships successfully persisted with perfect fidelity"
        else:
            # Some failures - calculate proportional uncertainty
            uncertainty = failed_items / total_items if total_items > 0 else 1.0
            reasoning = f"Persisted {entities_created}/{len(entities)} entities and {relationships_created}/{len(relationships)} relationships"
            if entities_failed > 0:
                reasoning += f" ({entities_failed} entity failures)"
            if relationships_failed > 0:
                reasoning += f" ({relationships_failed} relationship failures)"
        
        return {
            'success': True,
            'entities_created': entities_created,
            'relationships_created': relationships_created,
            'entities_failed': entities_failed,
            'relationships_failed': relationships_failed,
            'neo4j_ids': entity_map,
            'uncertainty': uncertainty,
            'reasoning': reasoning,
            'construct_mapping': 'knowledge_graph → persisted_graph'
        }
    
    def _create_or_merge_entity(self, entity: Dict) -> str:
        """
        Create or merge entity in Neo4j (FIXES THE BUG!)
        Actually creates Entity nodes, not just Mentions
        """
        query = """
        MERGE (e:VSEntity {canonical_name: $name})
        ON CREATE SET
            e.entity_id = $entity_id,
            e.entity_type = $entity_type,
            e.created_at = datetime()
        SET e += $attributes
        RETURN e.entity_id as entity_id
        """
        
        with self.neo4j.session() as session:
            result = session.run(
                query,
                name=entity.get('name', 'Unknown'),
                entity_id=f"entity_{uuid.uuid4().hex[:12]}",
                entity_type=entity.get('type', 'unknown'),
                attributes=entity.get('attributes', {})
            )
            record = result.single()
            return record['entity_id'] if record else None
    
    def _create_relationship(self, source_id: str, target_id: str, rel: Dict):
        """Create relationship between entities"""
        rel_type = rel.get('type', 'RELATED').upper().replace(' ', '_')
        
        # Use parameterized query with dynamic relationship type
        query = f"""
        MATCH (s:VSEntity {{entity_id: $source_id}})
        MATCH (t:VSEntity {{entity_id: $target_id}})
        CREATE (s)-[r:`{rel_type}`]->(t)
        SET r += $attributes
        SET r.created_at = datetime()
        """
        
        with self.neo4j.session() as session:
            session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                attributes=rel.get('attributes', {})
            )

# Test the persister
if __name__ == "__main__":
    # Setup Neo4j connection
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    
    # Create services
    identity_service = IdentityServiceV3(driver)
    crossmodal_service = CrossModalService(driver, "vertical_slice.db")
    
    # Create persister
    persister = GraphPersister(driver, identity_service, crossmodal_service)
    
    # Test data
    test_kg = {
        'entities': [
            {'id': '1', 'name': 'John Doe', 'type': 'person', 'attributes': {'role': 'CEO'}},
            {'id': '2', 'name': 'TechCorp', 'type': 'organization', 'attributes': {'industry': 'Technology'}}
        ],
        'relationships': [
            {'source': '1', 'target': '2', 'type': 'WORKS_FOR', 'attributes': {'since': '2020'}}
        ]
    }
    
    # Cleanup first
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    
    # Test persistence
    result = persister.process(test_kg)
    print(f"✅ Created {result['entities_created']} entities")
    print(f"✅ Created {result['relationships_created']} relationships")
    print(f"Uncertainty: {result['uncertainty']:.2f}")
    print(f"Reasoning: {result['reasoning']}")
    
    # Cleanup
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    
    driver.close()
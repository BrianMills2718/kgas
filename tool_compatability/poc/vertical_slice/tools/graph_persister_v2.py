#!/usr/bin/env python3
"""Graph persistence with proper document isolation"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.identity_service_v3 import IdentityServiceV3
from services.crossmodal_service import CrossModalService

class GraphPersisterV2:
    """
    Persist knowledge graph with document isolation.
    Each entity and relationship is tagged with document_id and extraction_run_id.
    """
    
    def __init__(self, neo4j_driver, identity_service=None, crossmodal_service=None):
        self.tool_id = "GraphPersisterV2"
        self.neo4j = neo4j_driver
        self.identity = identity_service
        self.crossmodal = crossmodal_service
        # Generate unique extraction run ID for this session
        self.extraction_run_id = f"run_{uuid.uuid4().hex[:12]}"
    
    def process(self, kg_data: Dict, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Persist knowledge graph with document tracking
        
        Args:
            kg_data: Dict with 'entities' and 'relationships' lists
            metadata: Optional dict with 'document_id', 'source_file', etc.
            
        Returns:
            Dict with success status, document_id, and persistence details
        """
        # Extract or generate document_id
        document_id = None
        if metadata:
            document_id = metadata.get('document_id')
            if not document_id and 'source_file' in metadata:
                # Generate from filename
                document_id = Path(metadata['source_file']).stem
        
        if not document_id:
            # Fallback: generate unique ID
            document_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        if not kg_data or 'entities' not in kg_data:
            return {
                'success': False,
                'document_id': document_id,
                'error': 'Invalid knowledge graph data',
                'uncertainty': 1.0,
                'reasoning': 'No entities provided for persistence'
            }
        
        entities = kg_data.get('entities', [])
        relationships = kg_data.get('relationships', [])
        
        # Create entities with document tracking
        entity_map = {}  # Map from names/IDs to Neo4j IDs
        entities_created = 0
        entities_failed = 0
        
        for entity in entities:
            try:
                neo4j_id = self._create_or_merge_entity(entity, document_id)
                if neo4j_id:
                    # Map both ID and name for flexible relationship matching
                    entity_map[entity.get('id', '')] = neo4j_id
                    entity_map[entity.get('name', '').lower()] = neo4j_id
                    entities_created += 1
                else:
                    entities_failed += 1
            except Exception as e:
                print(f"Failed to create entity {entity.get('name')}: {e}")
                entities_failed += 1
        
        # Create relationships with document tracking
        relationships_created = 0
        relationships_failed = 0
        
        for rel in relationships:
            # Try to find source/target by ID or name
            source_key = rel.get('source', '').lower()
            target_key = rel.get('target', '').lower()
            
            source_id = entity_map.get(source_key)
            target_id = entity_map.get(target_key)
            
            if source_id and target_id:
                try:
                    self._create_relationship(source_id, target_id, rel, document_id)
                    relationships_created += 1
                except Exception as e:
                    print(f"Failed to create relationship: {e}")
                    relationships_failed += 1
            else:
                # Debug why relationship failed
                if not source_id:
                    print(f"  Source '{source_key}' not found in entity map")
                if not target_id:
                    print(f"  Target '{target_key}' not found in entity map")
                relationships_failed += 1
        
        # Export to SQLite with document context
        if self.crossmodal and entity_map:
            try:
                # Only export entities from this document
                entity_ids = list(set(entity_map.values()))  # Unique IDs
                self.crossmodal.graph_to_table(entity_ids)
                print(f"✅ Exported {len(entity_ids)} entities to SQLite")
            except Exception as e:
                print(f"Warning: Failed to export to SQLite: {e}")
        
        # Calculate uncertainty
        total_items = len(entities) + len(relationships)
        failed_items = entities_failed + relationships_failed
        
        if failed_items == 0:
            uncertainty = 0.0
            reasoning = f"Perfect persistence: {entities_created} entities, {relationships_created} relationships"
        else:
            uncertainty = failed_items / total_items if total_items > 0 else 1.0
            reasoning = f"Partial persistence: {entities_created}/{len(entities)} entities, "
            reasoning += f"{relationships_created}/{len(relationships)} relationships"
        
        return {
            'success': True,
            'document_id': document_id,
            'extraction_run_id': self.extraction_run_id,
            'entities_created': entities_created,
            'relationships_created': relationships_created,
            'entities_failed': entities_failed,
            'relationships_failed': relationships_failed,
            'uncertainty': uncertainty,
            'reasoning': reasoning,
            'construct_mapping': 'knowledge_graph → persisted_graph'
        }
    
    def _create_or_merge_entity(self, entity: Dict, document_id: str) -> str:
        """Create entity with document tracking"""
        query = """
        MERGE (e:VSEntity {canonical_name: $name, document_id: $document_id})
        ON CREATE SET
            e.entity_id = $entity_id,
            e.entity_type = $entity_type,
            e.extraction_run_id = $extraction_run_id,
            e.created_at = datetime()
        SET e += $attributes
        RETURN e.entity_id as entity_id
        """
        
        with self.neo4j.session() as session:
            result = session.run(
                query,
                name=entity.get('name', 'Unknown'),
                document_id=document_id,
                entity_id=f"entity_{uuid.uuid4().hex[:12]}",
                entity_type=entity.get('type', 'unknown').lower(),  # Normalize type
                extraction_run_id=self.extraction_run_id,
                attributes=entity.get('attributes', {})
            )
            record = result.single()
            return record['entity_id'] if record else None
    
    def _create_relationship(self, source_id: str, target_id: str, rel: Dict, document_id: str):
        """Create relationship with document tracking"""
        rel_type = rel.get('type', 'RELATED').upper().replace(' ', '_')
        
        query = f"""
        MATCH (s:VSEntity {{entity_id: $source_id, document_id: $document_id}})
        MATCH (t:VSEntity {{entity_id: $target_id, document_id: $document_id}})
        CREATE (s)-[r:`{rel_type}`]->(t)
        SET r += $attributes
        SET r.document_id = $document_id
        SET r.extraction_run_id = $extraction_run_id
        SET r.created_at = datetime()
        """
        
        with self.neo4j.session() as session:
            session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                document_id=document_id,
                extraction_run_id=self.extraction_run_id,
                attributes=rel.get('attributes', {})
            )
    
    def get_document_graph(self, document_id: str) -> Dict:
        """Retrieve entities and relationships for a specific document"""
        with self.neo4j.session() as session:
            # Get entities
            entity_query = """
            MATCH (e:VSEntity {document_id: $document_id})
            RETURN e.entity_id as id, e.canonical_name as name, 
                   e.entity_type as type, properties(e) as properties
            """
            entities = session.run(entity_query, document_id=document_id).data()
            
            # Get relationships
            rel_query = """
            MATCH (s:VSEntity {document_id: $document_id})-[r]->(t:VSEntity {document_id: $document_id})
            WHERE r.document_id = $document_id
            RETURN s.canonical_name as source, t.canonical_name as target,
                   type(r) as type, properties(r) as properties
            """
            relationships = session.run(rel_query, document_id=document_id).data()
            
        return {
            'document_id': document_id,
            'entities': entities,
            'relationships': relationships
        }
    
    def cleanup_document(self, document_id: str):
        """Remove all entities and relationships for a document"""
        with self.neo4j.session() as session:
            query = """
            MATCH (e:VSEntity {document_id: $document_id})
            DETACH DELETE e
            """
            session.run(query, document_id=document_id)
            print(f"✅ Cleaned up document {document_id}")


# Test the improved persister
if __name__ == "__main__":
    # Setup Neo4j connection
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    
    # Create persister
    persister = GraphPersisterV2(driver)
    
    # Test data
    test_kg = {
        'entities': [
            {'id': '1', 'name': 'Brian Chhun', 'type': 'PERSON'},
            {'id': '2', 'name': 'University of Melbourne', 'type': 'ORGANIZATION'},
            {'id': '3', 'name': 'KGAS', 'type': 'SYSTEM'}
        ],
        'relationships': [
            {'source': 'Brian Chhun', 'target': 'University of Melbourne', 'type': 'STUDIES_AT'},
            {'source': 'Brian Chhun', 'target': 'KGAS', 'type': 'DEVELOPED'}
        ]
    }
    
    # Test with document metadata
    metadata = {
        'document_id': 'doc_001_test',
        'source_file': 'test_document.txt'
    }
    
    # Persist
    result = persister.process(test_kg, metadata)
    print(f"✅ Document ID: {result['document_id']}")
    print(f"✅ Created {result['entities_created']} entities")
    print(f"✅ Created {result['relationships_created']} relationships")
    
    # Retrieve
    graph = persister.get_document_graph('doc_001_test')
    print(f"\n📊 Retrieved graph for {graph['document_id']}:")
    print(f"  Entities: {len(graph['entities'])}")
    print(f"  Relationships: {len(graph['relationships'])}")
    
    # Cleanup
    persister.cleanup_document('doc_001_test')
    
    driver.close()
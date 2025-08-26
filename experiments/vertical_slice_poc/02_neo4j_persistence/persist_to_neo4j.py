#!/usr/bin/env python3
"""
Experiment 02: Neo4j Persistence
Goal: Write the extracted knowledge graph to Neo4j, creating actual Entity nodes

This fixes the bug where IdentityService only creates Mentions, not Entities.
We're proving we can persist the KG properly before building frameworks.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config

def connect_to_neo4j():
    """
    Connect to Neo4j database.
    Fail fast if connection doesn't work.
    """
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable
    
    try:
        print(f"Connecting to Neo4j at {config.NEO4J_URI}...")
        driver = GraphDatabase.driver(
            config.NEO4J_URI, 
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        # Test connection - fail fast if Neo4j isn't available
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j")
        return driver
        
    except ServiceUnavailable as e:
        print(f"❌ Cannot connect to Neo4j: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker run -d --name neo4j \\")
        print("    -p 7687:7687 -p 7474:7474 \\")
        print("    -e NEO4J_AUTH=neo4j/devpassword \\")
        print("    neo4j:latest")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        sys.exit(1)

def clear_database(driver):
    """
    Clear existing data for clean test.
    Only clears our test data, not everything.
    """
    with driver.session() as session:
        # Clear only entities and relationships we created (marked with source='experiment')
        result = session.run("""
            MATCH (n {source: 'vertical_slice_experiment'})
            DETACH DELETE n
            RETURN count(n) as deleted_count
        """)
        count = result.single()["deleted_count"]
        if count > 0:
            print(f"Cleared {count} existing experimental nodes")

def create_entity(session, entity: Dict[str, Any]) -> str:
    """
    Create or merge an Entity node in Neo4j.
    This FIXES THE BUG - we're creating Entity nodes, not Mentions!
    """
    # Generate Neo4j ID if not provided
    entity_id = entity.get('id', f"entity_{uuid.uuid4().hex[:12]}")
    
    # Build properties - flatten for Neo4j
    properties = entity.get('properties', {})
    properties['source'] = 'vertical_slice_experiment'  # Mark our data
    properties['original_id'] = entity_id  # Keep original ID from extraction
    
    # Create or merge the entity
    query = """
        MERGE (e:Entity {canonical_name: $name})
        ON CREATE SET 
            e.entity_id = $entity_id,
            e.entity_type = $entity_type,
            e.created_at = datetime()
        SET e += $properties
        RETURN e.entity_id as entity_id, 
               e.canonical_name as name,
               'created' as action
    """
    
    result = session.run(
        query,
        name=entity['name'],
        entity_id=f"entity_{uuid.uuid4().hex[:12]}",
        entity_type=entity.get('type', 'unknown'),
        properties=properties
    )
    
    record = result.single()
    if record:
        action = record['action']
        print(f"  {'Created' if action == 'created' else 'Merged'} Entity: {entity['name']} ({entity.get('type')})")
        return record['entity_id']
    
    return None

def create_relationship(session, rel: Dict[str, Any], entity_map: Dict[str, str]):
    """
    Create a relationship between entities in Neo4j.
    """
    source_original = rel.get('source')
    target_original = rel.get('target')
    
    # Map original IDs to Neo4j entity IDs
    source_name = entity_map.get(source_original)
    target_name = entity_map.get(target_original)
    
    if not source_name or not target_name:
        print(f"  ⚠️ Skipping relationship: {source_original} -> {target_original} (entities not found)")
        return False
    
    # Get relationship properties
    properties = rel.get('properties', {})
    properties['source'] = 'vertical_slice_experiment'
    
    # Create the relationship dynamically
    # Note: We can't use parameters for relationship type in Cypher
    rel_type = rel.get('type', 'RELATED_TO').upper().replace(' ', '_')
    
    query = f"""
        MATCH (s:Entity {{canonical_name: $source_name}})
        MATCH (t:Entity {{canonical_name: $target_name}})
        CREATE (s)-[r:{rel_type}]->(t)
        SET r += $properties
        RETURN type(r) as rel_type
    """
    
    try:
        result = session.run(
            query,
            source_name=source_name,
            target_name=target_name,
            properties=properties
        )
        
        record = result.single()
        if record:
            print(f"  Created Relationship: {source_name} --[{rel_type}]--> {target_name}")
            return True
    except Exception as e:
        print(f"  ❌ Failed to create relationship: {e}")
        return False

def persist_knowledge_graph(driver, kg_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist the entire knowledge graph to Neo4j.
    Returns statistics about what was created.
    """
    entities = kg_data.get('entities', [])
    relationships = kg_data.get('relationships', [])
    
    print(f"\nPersisting {len(entities)} entities and {len(relationships)} relationships...")
    
    stats = {
        'entities_processed': len(entities),
        'entities_created': 0,
        'relationships_processed': len(relationships),
        'relationships_created': 0,
        'errors': []
    }
    
    with driver.session() as session:
        # First, create all entities
        print("\n📊 Creating Entities:")
        entity_map = {}  # Map from original IDs to canonical names
        
        for entity in entities:
            try:
                neo4j_id = create_entity(session, entity)
                if neo4j_id:
                    entity_map[entity['id']] = entity['name']
                    stats['entities_created'] += 1
            except Exception as e:
                error_msg = f"Failed to create entity {entity.get('name')}: {e}"
                print(f"  ❌ {error_msg}")
                stats['errors'].append(error_msg)
        
        # Then, create relationships
        print("\n🔗 Creating Relationships:")
        for rel in relationships:
            try:
                if create_relationship(session, rel, entity_map):
                    stats['relationships_created'] += 1
            except Exception as e:
                error_msg = f"Failed to create relationship: {e}"
                print(f"  ❌ {error_msg}")
                stats['errors'].append(error_msg)
    
    return stats

def verify_persistence(driver) -> Dict[str, Any]:
    """
    Query Neo4j to verify what was actually persisted.
    """
    verification = {}
    
    with driver.session() as session:
        # Count entities
        result = session.run("""
            MATCH (e:Entity {source: 'vertical_slice_experiment'})
            RETURN count(e) as entity_count,
                   collect(DISTINCT e.entity_type) as entity_types
        """)
        record = result.single()
        verification['entity_count'] = record['entity_count']
        verification['entity_types'] = record['entity_types']
        
        # Count relationships
        result = session.run("""
            MATCH (s:Entity {source: 'vertical_slice_experiment'})-[r]->(t:Entity {source: 'vertical_slice_experiment'})
            RETURN count(r) as relationship_count,
                   collect(DISTINCT type(r)) as relationship_types
        """)
        record = result.single()
        verification['relationship_count'] = record['relationship_count']
        verification['relationship_types'] = record['relationship_types']
        
        # Get sample entities
        result = session.run("""
            MATCH (e:Entity {source: 'vertical_slice_experiment'})
            RETURN e.canonical_name as name, e.entity_type as type
            LIMIT 5
        """)
        verification['sample_entities'] = [
            {'name': r['name'], 'type': r['type']} 
            for r in result
        ]
        
        # Get sample relationships
        result = session.run("""
            MATCH (s:Entity {source: 'vertical_slice_experiment'})-[r]->(t:Entity {source: 'vertical_slice_experiment'})
            RETURN s.canonical_name as source, 
                   type(r) as rel_type, 
                   t.canonical_name as target
            LIMIT 5
        """)
        verification['sample_relationships'] = [
            f"{r['source']} --[{r['rel_type']}]--> {r['target']}"
            for r in result
        ]
    
    return verification

def analyze_persistence(stats: Dict[str, Any], verification: Dict[str, Any]):
    """
    Analyze and display persistence results.
    """
    print("\n" + "="*60)
    print("PERSISTENCE ANALYSIS")
    print("="*60)
    
    # Persistence statistics
    print("\n📊 Persistence Statistics:")
    print(f"  Entities: {stats['entities_created']}/{stats['entities_processed']} created")
    print(f"  Relationships: {stats['relationships_created']}/{stats['relationships_processed']} created")
    
    if stats['errors']:
        print(f"\n  ⚠️ Errors encountered: {len(stats['errors'])}")
        for error in stats['errors'][:3]:
            print(f"    - {error}")
    
    # Verification results
    print("\n✅ Database Verification:")
    print(f"  Total Entities in Neo4j: {verification['entity_count']}")
    print(f"  Entity Types: {', '.join(verification['entity_types'])}")
    print(f"  Total Relationships: {verification['relationship_count']}")
    print(f"  Relationship Types: {', '.join(verification['relationship_types'])}")
    
    if verification['sample_entities']:
        print("\n  Sample Entities:")
        for entity in verification['sample_entities']:
            print(f"    - {entity['name']} ({entity['type']})")
    
    if verification['sample_relationships']:
        print("\n  Sample Relationships:")
        for rel in verification['sample_relationships']:
            print(f"    - {rel}")
    
    # Success assessment
    print("\n" + "="*60)
    success_rate = (stats['entities_created'] + stats['relationships_created']) / \
                   (stats['entities_processed'] + stats['relationships_processed']) * 100
    
    if success_rate > 80:
        print(f"✅ Persistence SUCCESSFUL ({success_rate:.1f}% success rate)")
        return True
    else:
        print(f"❌ Persistence FAILED ({success_rate:.1f}% success rate)")
        return False

def main():
    """Main experiment function"""
    print("Neo4j Persistence Experiment")
    print("-" * 40)
    
    # Load the extraction result from Experiment 01
    extraction_file = Path(__file__).parent.parent / "01_basic_extraction/outputs/extraction_result.json"
    
    if not extraction_file.exists():
        print(f"❌ Error: Extraction result not found at {extraction_file}")
        print("Run Experiment 01 first: python 01_basic_extraction/extract_kg.py")
        sys.exit(1)
    
    # Load the knowledge graph data
    with open(extraction_file, 'r') as f:
        kg_data = json.load(f)
    
    print(f"Loaded KG with {len(kg_data.get('entities', []))} entities and {len(kg_data.get('relationships', []))} relationships")
    
    # Connect to Neo4j
    driver = connect_to_neo4j()
    
    try:
        # Clear existing experimental data
        clear_database(driver)
        
        # Persist the knowledge graph
        stats = persist_knowledge_graph(driver, kg_data)
        
        # Verify what was persisted
        verification = verify_persistence(driver)
        
        # Analyze results
        success = analyze_persistence(stats, verification)
        
        # Save results
        results = {
            'stats': stats,
            'verification': verification,
            'success': success
        }
        
        output_file = Path(__file__).parent / "persistence_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")
        
        return success
        
    finally:
        driver.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
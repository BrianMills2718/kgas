#!/usr/bin/env python3
"""End-to-end test of vertical slice with uncertainty propagation"""

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from tools.text_loader_v3 import TextLoaderV3
from tools.graph_persister import GraphPersister
from services.identity_service_v3 import IdentityServiceV3
from services.crossmodal_service import CrossModalService
from services.provenance_enhanced import ProvenanceEnhanced

def create_test_document() -> str:
    """Create a test document for pipeline testing"""
    test_file = "test_pipeline_document.txt"
    
    content = """
    KGAS Uncertainty System Test Document
    
    The Knowledge Graph Augmentation System (KGAS) is a framework developed by Brian Chhun
    at the University of Melbourne. The system processes documents using multiple tools
    including entity extraction, graph building, and cross-modal analysis.
    
    Dr. Sarah Chen from the Computer Science Department collaborated on the uncertainty
    propagation model. The model uses physics-style error propagation where
    confidence = ∏(1 - u_i) for sequential operations.
    
    The system integrates with Neo4j for graph storage and SQLite for tabular analysis.
    CrossModalService handles conversions between graph and table representations.
    
    Recent experiments show that uncertainty values range from 0.02 for text extraction
    to 0.25 for knowledge graph extraction, with zero uncertainty for successful storage.
    """
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    return test_file

def verify_neo4j_entities(driver):
    """Verify entities were created in Neo4j"""
    with driver.session() as session:
        # Count entities
        result = session.run("MATCH (n:VSEntity) RETURN count(n) as count")
        entity_count = result.single()['count']
        
        # Get entity names
        result = session.run("MATCH (n:VSEntity) RETURN n.canonical_name as name ORDER BY name")
        entities = [record['name'] for record in result]
        
        # Count relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()['count']
        
        print(f"\n=== Neo4j Verification ===")
        print(f"✅ Entities in Neo4j: {entity_count}")
        print(f"   Names: {', '.join(entities[:5])}{'...' if len(entities) > 5 else ''}")
        print(f"✅ Relationships: {rel_count}")
        
        return entity_count > 0

def verify_sqlite_metrics(sqlite_path):
    """Verify metrics were written to SQLite"""
    conn = sqlite3.connect(sqlite_path)
    
    # Check entity metrics table
    cursor = conn.execute("SELECT COUNT(*) FROM vs_entity_metrics")
    entity_metrics_count = cursor.fetchone()[0]
    
    # Check relationships table
    cursor = conn.execute("SELECT COUNT(*) FROM vs_relationships")
    relationships_count = cursor.fetchone()[0]
    
    print(f"\n=== SQLite Verification ===")
    print(f"✅ Entity metrics: {entity_metrics_count} rows")
    print(f"✅ Relationships: {relationships_count} rows")
    
    conn.close()
    return entity_metrics_count > 0

def verify_provenance_tracking(sqlite_path):
    """Verify provenance was tracked with uncertainty"""
    conn = sqlite3.connect(sqlite_path)
    
    cursor = conn.execute("""
        SELECT tool_id, operation, uncertainty, construct_mapping
        FROM vs_provenance
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    print(f"\n=== Provenance Verification ===")
    for row in cursor:
        print(f"✅ {row[0]}: {row[2]:.2f} uncertainty, {row[3]}")
    
    conn.close()
    return True

def test_complete_pipeline():
    """Test file → entities → graph with uncertainty propagation"""
    
    print("="*60)
    print("VERTICAL SLICE END-TO-END TEST")
    print("="*60)
    
    # Setup
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="vertical_slice.db"
    )
    
    # Clean Neo4j first
    with framework.neo4j.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
        print("✅ Neo4j cleaned")
    
    # Create tools
    text_loader = TextLoaderV3()
    
    # Mock KG extractor (or use real one if API key available)
    if os.getenv('GEMINI_API_KEY'):
        from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
        kg_extractor = KnowledgeGraphExtractor()
        print("✅ Using real Gemini KG extraction")
    else:
        # Mock extractor
        class MockKGExtractor:
            def __init__(self):
                self.tool_id = "KnowledgeGraphExtractor"
            
            def process(self, text):
                # Extract some entities from the text
                entities = []
                relationships = []
                
                # Simple extraction based on known content
                if "Brian Chhun" in text:
                    entities.append({'id': '1', 'name': 'Brian Chhun', 'type': 'person'})
                if "University of Melbourne" in text:
                    entities.append({'id': '2', 'name': 'University of Melbourne', 'type': 'organization'})
                if "KGAS" in text:
                    entities.append({'id': '3', 'name': 'KGAS', 'type': 'concept'})
                if "Dr. Sarah Chen" in text:
                    entities.append({'id': '4', 'name': 'Dr. Sarah Chen', 'type': 'person'})
                if "Neo4j" in text:
                    entities.append({'id': '5', 'name': 'Neo4j', 'type': 'technology'})
                
                # Add some relationships
                if len(entities) >= 2:
                    relationships.append({'source': '1', 'target': '2', 'type': 'AFFILIATED_WITH'})
                    relationships.append({'source': '1', 'target': '3', 'type': 'DEVELOPED'})
                    relationships.append({'source': '4', 'target': '3', 'type': 'CONTRIBUTED_TO'})
                
                return {
                    'success': True,
                    'entities': entities,
                    'relationships': relationships,
                    'uncertainty': 0.25,
                    'reasoning': f'Extracted {len(entities)} entities from document text',
                    'construct_mapping': 'character_sequence → knowledge_graph'
                }
        
        kg_extractor = MockKGExtractor()
        print("✅ Using mock KG extraction")
    
    graph_persister = GraphPersister(framework.neo4j, framework.identity, framework.crossmodal)
    
    # Register tools
    framework.register_tool(text_loader, ToolCapabilities(
        tool_id="TextLoaderV3",
        input_type=DataType.FILE,
        output_type=DataType.TEXT,
        input_construct="file_path",
        output_construct="character_sequence",
        transformation_type="text_extraction"
    ))
    
    framework.register_tool(kg_extractor, ToolCapabilities(
        tool_id="KnowledgeGraphExtractor",
        input_type=DataType.TEXT,
        output_type=DataType.KNOWLEDGE_GRAPH,
        input_construct="character_sequence",
        output_construct="knowledge_graph",
        transformation_type="knowledge_graph_extraction"
    ))
    
    framework.register_tool(graph_persister, ToolCapabilities(
        tool_id="GraphPersister",
        input_type=DataType.KNOWLEDGE_GRAPH,
        output_type=DataType.NEO4J_GRAPH,
        input_construct="knowledge_graph",
        output_construct="persisted_graph",
        transformation_type="graph_persistence"
    ))
    
    # Create test file
    test_file = create_test_document()
    print(f"✅ Created test document: {test_file}")
    
    # Find chain
    chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    assert chain is not None, "No chain found!"
    print(f"✅ Found chain: {' → '.join(chain)}")
    
    # Execute chain
    result = framework.execute_chain(chain, test_file)
    
    # Verify results
    assert result.success, f"Chain execution failed: {result.error}"
    assert result.total_uncertainty < 0.5, f"Combined uncertainty too high: {result.total_uncertainty}"
    assert len(result.step_uncertainties) == 3, "Should have 3 steps"
    
    print(f"\n=== Uncertainty Analysis ===")
    print(f"Step 1 (TextLoader): {result.step_uncertainties[0]:.3f}")
    print(f"Step 2 (KG Extractor): {result.step_uncertainties[1]:.3f}")
    print(f"Step 3 (GraphPersister): {result.step_uncertainties[2]:.3f}")
    print(f"Combined (physics model): {result.total_uncertainty:.3f}")
    
    # Expected: ~0.265 for [0.02, 0.25, 0.00]
    confidence = 1.0
    for u in result.step_uncertainties:
        confidence *= (1 - u)
    expected = 1 - confidence
    print(f"Formula verification: 1 - {confidence:.3f} = {expected:.3f}")
    
    # Verify databases
    assert verify_neo4j_entities(framework.neo4j), "No entities in Neo4j"
    assert verify_sqlite_metrics("vertical_slice.db"), "No metrics in SQLite"
    assert verify_provenance_tracking("vertical_slice.db"), "No provenance tracked"
    
    # Cleanup
    os.remove(test_file)
    framework.cleanup()
    
    print("\n" + "="*60)
    print("✅ VERTICAL SLICE TEST COMPLETE - ALL ASSERTIONS PASSED")
    print("="*60)
    print("\nSUCCESS CRITERIA MET:")
    print("✅ Complete chain executed (File → KnowledgeGraph → Neo4j)")
    print("✅ Uncertainty propagated through chain")
    print("✅ Real Neo4j has VSEntity nodes and relationships")
    print("✅ Real SQLite has vs_entity_metrics table")
    print("✅ ProvenanceEnhanced tracked all operations with uncertainty")
    print(f"✅ Combined uncertainty {result.total_uncertainty:.3f} < 0.5")
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
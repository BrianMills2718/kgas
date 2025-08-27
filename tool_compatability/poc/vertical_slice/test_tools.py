#!/usr/bin/env python3
"""Test all tools with uncertainty"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from neo4j import GraphDatabase
from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
from tools.graph_persister import GraphPersister
from services.identity_service_v3 import IdentityServiceV3
from services.crossmodal_service import CrossModalService
from services.provenance_enhanced import ProvenanceEnhanced

def test_text_loader():
    """Test TextLoaderV3 with different file types"""
    print("\n=== Testing TextLoaderV3 ===")
    
    loader = TextLoaderV3()
    
    # Test with TXT file
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("John Smith is the CEO of TechCorp. TechCorp is based in San Francisco.")
    
    result = loader.process(test_file)
    print(f"✅ Text file: uncertainty={result['uncertainty']:.2f}, reasoning='{result['reasoning']}'")
    
    # Test with MD file
    test_md = "test_document.md"
    with open(test_md, 'w') as f:
        f.write("# Test Document\nThis is markdown content.")
    
    result_md = loader.process(test_md)
    print(f"✅ Markdown file: uncertainty={result_md['uncertainty']:.2f}, reasoning='{result_md['reasoning']}'")
    
    # Cleanup
    os.remove(test_file)
    os.remove(test_md)
    
    return result  # Return for pipeline test

def test_knowledge_graph_extractor(text=None):
    """Test KnowledgeGraphExtractor"""
    print("\n=== Testing KnowledgeGraphExtractor ===")
    
    if not text:
        text = """
        John Smith is the CEO of TechCorp, a technology company based in San Francisco.
        He previously worked at DataSystems where he led the AI team.
        TechCorp recently acquired StartupCo for $10 million.
        """
    
    # If no API key, return simulated result for testing
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Simulating KG extraction (no API key)")
        return {
            'success': True,
            'entities': [
                {'id': '1', 'name': 'John Smith', 'type': 'person', 'attributes': {'role': 'CEO'}},
                {'id': '2', 'name': 'TechCorp', 'type': 'organization', 'attributes': {}},
                {'id': '3', 'name': 'San Francisco', 'type': 'location', 'attributes': {}}
            ],
            'relationships': [
                {'source': '1', 'target': '2', 'type': 'CEO_OF', 'attributes': {}},
                {'source': '2', 'target': '3', 'type': 'LOCATED_IN', 'attributes': {}}
            ],
            'uncertainty': 0.25,
            'reasoning': 'Simulated extraction for testing',
            'construct_mapping': 'character_sequence → knowledge_graph'
        }
    
    extractor = KnowledgeGraphExtractor()
    
    try:
        result = extractor.process(text)
        if result['success']:
            print(f"✅ Extracted {len(result['entities'])} entities, {len(result['relationships'])} relationships")
            print(f"   Uncertainty: {result['uncertainty']:.2f}")
            print(f"   Reasoning: {result['reasoning']}")
            return result
        else:
            print(f"❌ Extraction failed: {result.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_graph_persister(kg_data=None):
    """Test GraphPersister"""
    print("\n=== Testing GraphPersister ===")
    
    # Setup
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    identity_service = IdentityServiceV3(driver)
    crossmodal_service = CrossModalService(driver, "vertical_slice.db")
    persister = GraphPersister(driver, identity_service, crossmodal_service)
    
    # Use provided data or create test data
    if not kg_data:
        kg_data = {
            'entities': [
                {'id': '1', 'name': 'Test Person', 'type': 'person'},
                {'id': '2', 'name': 'Test Company', 'type': 'organization'}
            ],
            'relationships': [
                {'source': '1', 'target': '2', 'type': 'WORKS_AT'}
            ]
        }
    
    # Clean Neo4j first
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    
    # Test persistence
    result = persister.process(kg_data)
    print(f"✅ Created {result['entities_created']} entities, {result['relationships_created']} relationships")
    print(f"   Uncertainty: {result['uncertainty']:.2f}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Verify in Neo4j
    with driver.session() as session:
        count_result = session.run("MATCH (n:VSEntity) RETURN count(n) as count")
        node_count = count_result.single()['count']
        print(f"✅ Verified {node_count} nodes in Neo4j")
    
    driver.close()
    return result

def test_end_to_end_pipeline():
    """Test complete pipeline with uncertainty propagation"""
    print("\n=== Testing End-to-End Pipeline ===")
    
    # Track uncertainties
    uncertainties = []
    
    # Step 1: Load text
    print("\nStep 1: TextLoader")
    loader_result = test_text_loader()
    if loader_result['success']:
        uncertainties.append(loader_result['uncertainty'])
        text = loader_result['text']
    else:
        print("❌ Pipeline failed at text loading")
        return
    
    # Step 2: Extract knowledge graph
    print("\nStep 2: KnowledgeGraphExtractor")
    kg_result = test_knowledge_graph_extractor(text)
    if kg_result and kg_result['success']:
        uncertainties.append(kg_result['uncertainty'])
    else:
        print("❌ Pipeline failed at KG extraction")
        return
    
    # Step 3: Persist to Neo4j
    print("\nStep 3: GraphPersister")
    persist_result = test_graph_persister(kg_result)
    if persist_result['success']:
        uncertainties.append(persist_result['uncertainty'])
    else:
        print("❌ Pipeline failed at persistence")
        return
    
    # Calculate combined uncertainty (physics model)
    confidence = 1.0
    for u in uncertainties:
        confidence *= (1 - u)
    total_uncertainty = 1 - confidence
    
    print("\n=== Pipeline Complete ===")
    print(f"Step uncertainties: {[f'{u:.2f}' for u in uncertainties]}")
    print(f"Combined uncertainty: {total_uncertainty:.3f}")
    print(f"Formula: 1 - ∏(1 - uᵢ) = 1 - {confidence:.3f} = {total_uncertainty:.3f}")
    
    # Track in provenance
    provenance = ProvenanceEnhanced("vertical_slice.db")
    op_id = provenance.track_operation(
        tool_id="Pipeline",
        operation="complete_extraction",
        inputs={"file": "test_document.txt"},
        outputs={
            "entities": persist_result['entities_created'],
            "relationships": persist_result['relationships_created']
        },
        uncertainty=total_uncertainty,
        reasoning=f"Complete pipeline with {len(uncertainties)} steps",
        construct_mapping="file → persisted_graph"
    )
    print(f"✅ Tracked in provenance: {op_id}")
    
    # Cleanup Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    with driver.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
    driver.close()

if __name__ == "__main__":
    # Check for Gemini API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not set, using simulated KG extraction")
        
    # Run individual tool tests
    test_text_loader()
    test_knowledge_graph_extractor()
    test_graph_persister()
    
    # Run end-to-end pipeline test
    print("\n" + "="*50)
    test_end_to_end_pipeline()
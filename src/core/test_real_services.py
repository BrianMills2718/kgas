#!/usr/bin/env python3
"""
Test with REAL services - NO MOCKS
This is critical for thesis evidence
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import hashlib

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tool_compatability" / "poc"))

# Import data schemas
from data_types import DataSchema

# Load environment
load_dotenv(project_root / '.env')

def test_real_gemini_api():
    """Test EntityExtractor with actual Gemini API"""
    print("\n" + "="*60)
    print("TEST: Real Gemini API Entity Extraction")
    print("="*60)
    
    # Import real tool
    from tool_compatability.poc.tools.entity_extractor import EntityExtractor
    from src.core.composition_service import CompositionService
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    # Create service and register real tool
    service = CompositionService()
    extractor = EntityExtractor()
    service.register_any_tool(extractor)
    
    # Test text with known entities
    test_text = """
    Apple CEO Tim Cook announced new AI features at WWDC 2024.
    Google's Sundar Pichai responded with Gemini updates.
    Microsoft CEO Satya Nadella discussed Copilot integration.
    """
    
    # Create proper TextData format
    text_data = DataSchema.TextData(
        content=test_text,
        char_count=len(test_text),
        checksum=hashlib.md5(test_text.encode()).hexdigest()
    )
    
    # Process through real API
    start = time.time()
    result = extractor.process(text_data)
    duration = time.time() - start
    
    if not result.success:
        print(f"❌ Extraction failed: {result.error}")
        return False
    
    # Verify entities found
    # result.data is EntitiesData object
    if hasattr(result.data, 'entities'):
        entities = result.data.entities
        print(f"\n📊 Results:")
        print(f"  - API call duration: {duration:.2f}s")
        print(f"  - Entities found: {len(entities)}")
        
        # Show some entities
        print(f"\n  Extracted entities:")
        for entity in entities[:5]:
            print(f"    - {entity.text} ({entity.type}) confidence: {entity.confidence:.2f}")
    else:
        print(f"❌ Unexpected result format: {type(result.data)}")
        return False
    
    return len(entities) > 0

def test_real_neo4j():
    """Test GraphBuilder with actual Neo4j"""
    print("\n" + "="*60)
    print("TEST: Real Neo4j Graph Building")
    print("="*60)
    
    from tool_compatability.poc.tools.graph_builder import GraphBuilder
    from neo4j import GraphDatabase
    
    # Test Neo4j connection
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        driver.verify_connectivity()
        print("✅ Neo4j connected")
        
        # Clear old test entities to avoid conflicts
        with driver.session() as session:
            session.run("MATCH (n:Entity) WHERE n.id IN ['entity_1', 'entity_2', 'entity_3'] DELETE n")
            print("  Cleared old test entities")
            
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("  Try: docker run -d -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/devpassword neo4j")
        return False
    
    # Create test entities with required 'id' field
    test_entities = [
        DataSchema.Entity(
            id="entity_1",
            text="Apple", 
            type="ORGANIZATION", 
            confidence=0.95,
            context="Test entity"
        ),
        DataSchema.Entity(
            id="entity_2",
            text="Tim Cook", 
            type="PERSON", 
            confidence=0.90,
            context="Test entity"
        ),
        DataSchema.Entity(
            id="entity_3",
            text="Microsoft", 
            type="ORGANIZATION", 
            confidence=0.93,
            context="Test entity"
        ),
    ]
    
    # Create proper EntitiesData format with all required fields
    import hashlib
    from datetime import datetime
    
    source_text = "Test data for Neo4j"
    entities_data = DataSchema.EntitiesData(
        entities=test_entities,
        source_text=source_text,
        extraction_method="manual",
        source_checksum=hashlib.md5(source_text.encode()).hexdigest(),
        extraction_model="test_model",
        extraction_timestamp=datetime.now().isoformat()
    )
    
    # Build graph
    builder = GraphBuilder()
    result = builder.process(entities_data)
    
    if not result.success:
        print(f"❌ Graph building failed: {result.error}")
        return False
    
    # Verify nodes in Neo4j
    with driver.session() as session:
        count_result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = count_result.single()["count"]
    
    driver.close()
    
    print(f"\n📊 Results:")
    print(f"  - Nodes in database: {node_count}")
    print(f"  - Graph result: {result.data}")
    
    return node_count > 0

def test_real_pipeline():
    """Test complete pipeline with real services"""
    print("\n" + "="*60)
    print("TEST: Real End-to-End Pipeline")
    print("="*60)
    
    from src.core.composition_service import CompositionService
    from tool_compatability.poc.tools.text_loader import TextLoader
    from tool_compatability.poc.tools.entity_extractor import EntityExtractor
    from tool_compatability.poc.tools.graph_builder import GraphBuilder
    from data_types import DataType
    
    # Create test file
    test_file = Path("test_data/real_test.txt")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("""
    In 2024, major tech companies are investing heavily in AI.
    Apple's Tim Cook unveiled Apple Intelligence at WWDC.
    Google CEO Sundar Pichai announced Gemini 2.0.
    Microsoft's Satya Nadella integrated AI into Office 365.
    """)
    
    # Setup composition service
    service = CompositionService()
    
    # Register REAL tools
    service.register_any_tool(TextLoader())
    service.register_any_tool(EntityExtractor())
    service.register_any_tool(GraphBuilder())
    
    # Find chain
    chains = service.find_chains(DataType.FILE, DataType.GRAPH)
    if not chains:
        print("❌ No chains found")
        return False
    
    chain = chains[0]
    print(f"  Chain: {' → '.join(chain)}")
    
    # Create proper FileData format
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=test_file.stat().st_size,
        mime_type="text/plain"
    )
    
    # Execute with timing
    start = time.time()
    result = service.execute_chain(chain, file_data)
    duration = time.time() - start
    
    if not result.success:
        print(f"❌ Pipeline failed: {result.error}")
        return False
    
    print(f"\n📊 Pipeline Metrics:")
    print(f"  - Total duration: {duration:.2f}s")
    print(f"  - Final uncertainty: {result.uncertainty:.3f}")
    print(f"  - Reasoning: {result.reasoning}")
    
    # Check for thesis evidence
    metrics = service.get_metrics()
    print(f"\n📈 Thesis Evidence:")
    print(f"  - Tools adapted: {metrics['tools_adapted']}")
    print(f"  - Chains discovered: {metrics['chains_discovered']}")
    print(f"  - Execution times: {metrics['execution_time']}")
    
    return True

def main():
    """Run all real service tests"""
    print("="*60)
    print("REAL SERVICE INTEGRATION TESTS")
    print("NO MOCKS - ACTUAL APIS")
    print("="*60)
    
    tests = [
        ("Gemini API", test_real_gemini_api),
        ("Neo4j Database", test_real_neo4j),
        ("Full Pipeline", test_real_pipeline),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("REAL SERVICE TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All real service tests passed!")
        print("THESIS EVIDENCE: System works with actual services")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Cannot claim real-world viability without these passing")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
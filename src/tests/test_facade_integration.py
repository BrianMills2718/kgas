"""
Integration tests for the unified facade
"""

import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Set environment variables
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'devpassword'

import pytest
from src.facade.unified_kgas_facade import UnifiedKGASFacade

def test_full_pipeline():
    """Test complete pipeline: Text → Entities → Graph → PageRank → Query"""
    
    print("\n" + "="*60)
    print("KGAS UNIFIED FACADE - INTEGRATION TEST")
    print("="*60)
    
    # Initialize facade
    print("\n📦 Initializing unified facade...")
    facade = UnifiedKGASFacade()
    print("✅ Facade initialized")
    
    # Test text
    text = """
    Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino, California.
    Microsoft Corporation, led by CEO Satya Nadella, is based in Redmond, Washington.
    """
    
    print("\n📄 Test document:")
    print(text[:100] + "...")
    
    # Process document
    print("\n🔄 Processing document through full pipeline...")
    result = facade.process_document(text)
    
    # Verify entities created
    assert result["success"] == True, f"Pipeline failed: {result.get('error')}"
    assert len(result["entities"]) > 0, "No entities created"
    assert len(result["edges"]) > 0, "No edges created"
    assert len(result["pagerank"]) > 0, "No PageRank scores calculated"
    
    print(f"\n✅ Pipeline test passed!")
    print(f"  📊 Entities: {len(result['entities'])}")
    print(f"  🔗 Edges: {len(result['edges'])}")
    print(f"  📈 PageRank scores: {len(result['pagerank'])}")
    
    # Show sample entities
    if result['entities']:
        print("\n  Sample entities:")
        for entity in result['entities'][:3]:
            print(f"    - {entity.get('canonical_name', 'N/A')} ({entity.get('entity_type', 'N/A')})")
    
    # Test query
    print("\n❓ Testing query: 'Who leads Apple?'")
    answers = facade.query("Who leads Apple?")
    assert len(answers) > 0, "No query answers returned"
    
    print(f"  💡 Query answers: {len(answers)}")
    if answers:
        print("  Sample answer:")
        print(f"    {answers[0].get('answer', 'N/A')}")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED - KGAS PIPELINE WORKING!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_full_pipeline()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
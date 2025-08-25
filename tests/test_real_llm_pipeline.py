#!/usr/bin/env python3
"""Test KGAS Pipeline with REAL LLM and fictional data"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

from src.pipeline.kgas_pipeline import KGASPipeline

def test_nexora_pipeline():
    """Full pipeline test with fictional Nexora Technologies document"""
    
    print("=" * 60)
    print("KGAS PIPELINE TEST WITH REAL LLM")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = KGASPipeline()
    
    # Load fictional document
    with open("test_data/nexora_technologies.txt", "r") as f:
        document = f.read()
    
    print(f"\n1. Document loaded: {len(document)} characters")
    print(f"   First 100 chars: {document[:100]}...")
    
    # Process document through pipeline
    print("\n2. Processing document through pipeline...")
    results = pipeline.process_document(document)
    
    # Validate LLM extraction
    print("\n3. Validating LLM extraction...")
    entities = results["llm_extraction"]["entities"]
    relationships = results["llm_extraction"]["relationships"]
    
    print(f"   Entities found: {len(entities)}")
    print(f"   Relationships found: {len(relationships)}")
    
    # Check for expected fictional entities
    entity_names = [e["name"] for e in entities]
    expected_entities = ["Nexora Technologies", "Zara Klingston", "Velmont City"]
    
    for expected in expected_entities:
        found = any(expected in name for name in entity_names)
        print(f"   ✓ Found '{expected}': {found}")
        assert found, f"Missing expected entity: {expected}"
    
    # Test queries
    print("\n4. Testing queries...")
    queries = [
        "Who leads Nexora Technologies?",
        "Where is Nexora Technologies headquartered?",
    ]
    
    query_results = []
    for query in queries:
        print(f"\n   Query: {query}")
        answer = pipeline.query(query)
        query_results.append(answer)
        
        if answer["answers"]:
            for ans in answer["answers"]:
                print(f"   Answer: {ans['answer']}")
        else:
            print("   No answer found")
    
    # Validate specific answers
    print("\n5. Validating answers...")
    
    # Query 1: Who leads Nexora?
    q1_answer = query_results[0]
    assert q1_answer["answers"], "No answer for leadership query"
    assert "Zara Klingston" in q1_answer["answers"][0]["answer"], \
        f"Wrong leader: {q1_answer['answers'][0]['answer']}"
    print("   ✓ Correctly identified Zara Klingston as leader")
    
    # Query 2: Where is Nexora headquartered?
    q2_answer = query_results[1]
    assert q2_answer["answers"], "No answer for location query"
    assert "Velmont City" in q2_answer["answers"][0]["answer"], \
        f"Wrong location: {q2_answer['answers'][0]['answer']}"
    print("   ✓ Correctly identified Velmont City as headquarters")
    
    # Generate evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "nexora_pipeline_e2e",
        "status": "success",
        "llm_model": results["llm_extraction"]["model"],
        "document_length": len(document),
        "entities_extracted": len(entities),
        "relationships_extracted": len(relationships),
        "entities_stored": results["pipeline_stages"][1]["entities_stored"],
        "relationships_stored": results["pipeline_stages"][2]["relationships_stored"],
        "sample_entities": entity_names[:10],
        "queries_tested": len(queries),
        "queries_answered": sum(1 for q in query_results if q["answers"]),
        "validation": {
            "found_nexora": "Nexora Technologies" in entity_names,
            "found_zara": "Zara Klingston" in entity_names,
            "correct_leader": "Zara Klingston" in str(query_results[0]),
            "correct_location": "Velmont City" in str(query_results[1])
        }
    }
    
    # Save evidence
    os.makedirs("evidence", exist_ok=True)
    with open("evidence/pipeline_end_to_end.json", "w") as f:
        json.dump(evidence, f, indent=2)
    
    # Save raw LLM response
    with open("evidence/llm_extraction_nexora.json", "w") as f:
        json.dump(results["llm_extraction"], f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE TEST SUCCESSFUL")
    print("Evidence saved to:")
    print("  - evidence/pipeline_end_to_end.json")
    print("  - evidence/llm_extraction_nexora.json")
    print("=" * 60)
    
    # Cleanup
    pipeline.cleanup()
    
    return True

if __name__ == "__main__":
    success = test_nexora_pipeline()
    exit(0 if success else 1)
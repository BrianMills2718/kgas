#!/usr/bin/env python3
"""
Test consistency of knowledge graph extraction across multiple runs.
This helps us understand LLM variability and reliability.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the extraction function
from extract_kg import extract_knowledge_graph_gemini, extract_knowledge_graph_openai, analyze_extraction
import config

def run_multiple_extractions(text: str, num_runs: int = 3) -> List[Dict[str, Any]]:
    """Run extraction multiple times to test consistency"""
    results = []
    
    for i in range(num_runs):
        print(f"\nRun {i+1}/{num_runs}...")
        
        if config.LLM_PROVIDER in ["gemini", "google"]:
            kg_data = extract_knowledge_graph_gemini(text)
        elif config.LLM_PROVIDER == "openai":
            kg_data = extract_knowledge_graph_openai(text)
        else:
            print(f"Unsupported provider: {config.LLM_PROVIDER}")
            return results
        
        results.append(kg_data)
        
        # Brief pause to avoid rate limiting
        if i < num_runs - 1:
            time.sleep(2)
    
    return results

def analyze_consistency(results: List[Dict[str, Any]]):
    """Analyze consistency across multiple extraction runs"""
    print("\n" + "="*60)
    print("CONSISTENCY ANALYSIS")
    print("="*60)
    
    if not results:
        print("No results to analyze")
        return
    
    # Entity consistency
    print("\n📊 Entity Extraction Consistency:")
    entity_sets = []
    for i, result in enumerate(results):
        entities = result.get("entities", [])
        entity_names = {e.get("name", "").lower() for e in entities}
        entity_sets.append(entity_names)
        print(f"  Run {i+1}: {len(entities)} entities")
    
    # Find common entities
    if entity_sets:
        common_entities = set.intersection(*entity_sets)
        all_entities = set.union(*entity_sets)
        print(f"\n  Common entities across all runs: {len(common_entities)}")
        print(f"  Total unique entities found: {len(all_entities)}")
        if len(all_entities) > 0:
            consistency_rate = len(common_entities) / len(all_entities) * 100
            print(f"  Consistency rate: {consistency_rate:.1f}%")
        
        # Show common entities
        if common_entities:
            print("\n  Entities found in all runs:")
            for entity in sorted(list(common_entities)[:5]):
                print(f"    - {entity}")
    
    # Relationship consistency
    print("\n🔗 Relationship Extraction Consistency:")
    rel_sets = []
    for i, result in enumerate(results):
        relationships = result.get("relationships", [])
        # Create a normalized representation of relationships
        rel_tuples = {
            (r.get("source", "").lower(), 
             r.get("type", "").upper(), 
             r.get("target", "").lower())
            for r in relationships
        }
        rel_sets.append(rel_tuples)
        print(f"  Run {i+1}: {len(relationships)} relationships")
    
    # Find common relationships
    if rel_sets:
        common_rels = set.intersection(*rel_sets)
        all_rels = set.union(*rel_sets)
        print(f"\n  Common relationships across all runs: {len(common_rels)}")
        print(f"  Total unique relationships found: {len(all_rels)}")
        if len(all_rels) > 0:
            consistency_rate = len(common_rels) / len(all_rels) * 100
            print(f"  Consistency rate: {consistency_rate:.1f}%")
    
    # Uncertainty consistency
    print("\n🎯 Uncertainty Assessment Consistency:")
    uncertainties = []
    for i, result in enumerate(results):
        uncertainty = result.get("uncertainty")
        if uncertainty is not None:
            uncertainties.append(uncertainty)
            print(f"  Run {i+1}: {uncertainty:.2f}")
            reasoning = result.get("reasoning", "No reasoning")
            print(f"    Reasoning: {reasoning[:100]}...")
    
    if uncertainties:
        avg_uncertainty = sum(uncertainties) / len(uncertainties)
        min_uncertainty = min(uncertainties)
        max_uncertainty = max(uncertainties)
        range_uncertainty = max_uncertainty - min_uncertainty
        
        print(f"\n  Average uncertainty: {avg_uncertainty:.3f}")
        print(f"  Range: {min_uncertainty:.3f} - {max_uncertainty:.3f} (δ={range_uncertainty:.3f})")
        
        if range_uncertainty < 0.1:
            print("  ✅ Uncertainty assessments are consistent")
        elif range_uncertainty < 0.2:
            print("  ⚠️ Moderate variation in uncertainty assessments")
        else:
            print("  ❌ High variation in uncertainty assessments")
    
    print("\n" + "="*60)

def main():
    """Main consistency test"""
    print("Knowledge Graph Extraction Consistency Test")
    print(f"Provider: {config.LLM_PROVIDER} / {config.LLM_MODEL}")
    print("-" * 40)
    
    # Read test document
    test_file = Path(__file__).parent / "test_document.txt"
    if not test_file.exists():
        print(f"Error: Test document not found at {test_file}")
        return False
    
    with open(test_file, 'r') as f:
        text = f.read()
    
    print(f"Document length: {len(text)} characters")
    
    # Run multiple extractions
    num_runs = 3
    print(f"\nRunning {num_runs} extraction attempts...")
    results = run_multiple_extractions(text, num_runs)
    
    # Save all results
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    for i, result in enumerate(results):
        output_file = output_dir / f"consistency_run_{i+1}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    # Analyze consistency
    analyze_consistency(results)
    
    # Overall assessment
    print("\n" + "="*60)
    print("OVERALL ASSESSMENT")
    print("="*60)
    
    all_succeeded = all(
        r.get("entities") and r.get("uncertainty") is not None 
        for r in results
    )
    
    if all_succeeded:
        print("✅ All extraction runs succeeded")
        
        # Check if we got reasonable consistency
        if results:
            entity_counts = [len(r.get("entities", [])) for r in results]
            if max(entity_counts) - min(entity_counts) <= 3:
                print("✅ Entity counts are consistent")
            else:
                print("⚠️ Entity counts vary significantly")
        
        return True
    else:
        print("❌ Some extraction runs failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
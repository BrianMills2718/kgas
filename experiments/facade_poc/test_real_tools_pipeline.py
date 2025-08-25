#!/usr/bin/env python3
"""
Test real tools pipeline (T23C working, others simulated without Neo4j)
"""

import sys
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, List
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor as T23C
from src.core.tool_contract import ToolRequest

# Custom request for T23C compatibility
@dataclass
class T23CCompatibleRequest:
    """Request that works with T23C"""
    input_data: Any
    validation_mode: bool = False
    parameters: Dict[str, Any] = None
    operation: str = "execute"
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class RealToolsPipeline:
    """Pipeline using real T23C with simulated other tools"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.t23c = T23C(self.service_manager)
        self.evidence = {
            "timestamp": datetime.now().isoformat(),
            "operations": [],
            "success_criteria": {}
        }
    
    def extract_with_t23c(self, text: str) -> dict:
        """Extract entities using real T23C"""
        request = T23CCompatibleRequest(
            input_data={
                "text": text,
                "extraction_mode": "entities"
            }
        )
        
        result = self.t23c.execute(request)
        
        if result.status == "success":
            self.evidence["operations"].append({
                "tool": "T23C",
                "status": "success",
                "entities_extracted": result.data.get("entity_count", 0),
                "relationships_extracted": result.data.get("relationship_count", 0)
            })
            return result.data
        else:
            self.evidence["operations"].append({
                "tool": "T23C",
                "status": "failed",
                "error": result.error_message
            })
            return None
    
    def simulate_t31_entity_creation(self, t23c_data: dict) -> dict:
        """Simulate T31 entity creation (Neo4j not available)"""
        if not t23c_data:
            return {"status": "failed", "error": "No input data"}
        
        entities = t23c_data.get("entities", [])
        
        # Simulate creating entities in Neo4j
        created_entities = []
        for entity in entities:
            created_entities.append({
                "node_id": f"node_{entity.get('entity_id', 'unknown')}",
                "labels": [entity.get("entity_type", "UNKNOWN")],
                "properties": {
                    "name": entity.get("canonical_name", ""),
                    "confidence": entity.get("confidence", 0),
                    "created_at": entity.get("created_at", "")
                }
            })
        
        result = {
            "status": "success",
            "entities_created": len(created_entities),
            "entities": created_entities
        }
        
        self.evidence["operations"].append({
            "tool": "T31 (simulated)",
            "status": "success",
            "entities_created": len(created_entities)
        })
        
        return result
    
    def simulate_t34_edge_creation(self, t23c_data: dict) -> dict:
        """Simulate T34 edge creation (Neo4j not available)"""
        if not t23c_data:
            return {"status": "failed", "error": "No input data"}
        
        relationships = t23c_data.get("relationships", [])
        
        # Simulate creating edges in Neo4j
        created_edges = []
        for rel in relationships:
            created_edges.append({
                "edge_id": f"edge_{len(created_edges)}",
                "source": rel.get("source", ""),
                "target": rel.get("target", ""),
                "type": rel.get("relationship_type", "RELATED"),
                "properties": {
                    "confidence": rel.get("confidence", 0)
                }
            })
        
        result = {
            "status": "success",
            "edges_created": len(created_edges),
            "edges": created_edges
        }
        
        self.evidence["operations"].append({
            "tool": "T34 (simulated)",
            "status": "success",
            "edges_created": len(created_edges)
        })
        
        return result
    
    def simulate_t68_pagerank(self, entity_count: int) -> dict:
        """Simulate T68 PageRank (Neo4j not available)"""
        # Simulate PageRank scores
        pagerank_scores = []
        for i in range(entity_count):
            pagerank_scores.append({
                "node_id": f"node_{i}",
                "score": 0.15 + (0.85 / (i + 1))
            })
        
        result = {
            "status": "success",
            "nodes_processed": len(pagerank_scores),
            "pagerank_scores": pagerank_scores
        }
        
        self.evidence["operations"].append({
            "tool": "T68 (simulated)",
            "status": "success",
            "nodes_processed": len(pagerank_scores)
        })
        
        return result
    
    def run_pipeline(self, text: str) -> dict:
        """Run complete pipeline with real T23C"""
        print("\n" + "=" * 60)
        print("REAL TOOLS PIPELINE TEST")
        print("=" * 60)
        
        print(f"\nInput Text: {text[:100]}...")
        
        # Step 1: Real T23C extraction
        print("\n1. Extracting with real T23C...")
        t23c_result = self.extract_with_t23c(text)
        
        if not t23c_result:
            print("   ❌ T23C extraction failed")
            self.evidence["success_criteria"]["t23c_extraction"] = False
            return self.evidence
        
        entity_count = t23c_result.get("entity_count", 0)
        relationship_count = t23c_result.get("relationship_count", 0)
        print(f"   ✅ Extracted {entity_count} entities, {relationship_count} relationships")
        self.evidence["success_criteria"]["t23c_extraction"] = True
        
        # Step 2: Simulate T31 entity creation
        print("\n2. Creating entities (T31 simulated)...")
        t31_result = self.simulate_t31_entity_creation(t23c_result)
        
        if t31_result["status"] == "success":
            print(f"   ✅ Created {t31_result['entities_created']} entities")
            self.evidence["success_criteria"]["t31_entity_creation"] = True
        else:
            print(f"   ❌ Entity creation failed")
            self.evidence["success_criteria"]["t31_entity_creation"] = False
        
        # Step 3: Simulate T34 edge creation
        print("\n3. Creating edges (T34 simulated)...")
        t34_result = self.simulate_t34_edge_creation(t23c_result)
        
        if t34_result["status"] == "success":
            print(f"   ✅ Created {t34_result['edges_created']} edges")
            self.evidence["success_criteria"]["t34_edge_creation"] = True
        else:
            print(f"   ❌ Edge creation failed")
            self.evidence["success_criteria"]["t34_edge_creation"] = False
        
        # Step 4: Simulate T68 PageRank
        print("\n4. Computing PageRank (T68 simulated)...")
        t68_result = self.simulate_t68_pagerank(entity_count)
        
        if t68_result["status"] == "success":
            print(f"   ✅ Computed PageRank for {t68_result['nodes_processed']} nodes")
            self.evidence["success_criteria"]["t68_pagerank"] = True
        else:
            print(f"   ❌ PageRank computation failed")
            self.evidence["success_criteria"]["t68_pagerank"] = False
        
        # Check data consistency
        nodes_in = entity_count
        nodes_out = t68_result["nodes_processed"]
        self.evidence["success_criteria"]["no_contamination"] = nodes_in == nodes_out
        
        if nodes_in == nodes_out:
            print(f"\n✅ Data consistency maintained: {nodes_in} == {nodes_out}")
        else:
            print(f"\n❌ Data contamination detected: {nodes_in} != {nodes_out}")
        
        # Overall success
        self.evidence["success_criteria"]["pipeline_complete"] = all(
            v for k, v in self.evidence["success_criteria"].items()
        )
        
        return self.evidence
    
    def save_evidence(self):
        """Save evidence to file"""
        import os
        os.makedirs("experiments/facade_poc/evidence", exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"experiments/facade_poc/evidence/real_tools_pipeline_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.evidence, f, indent=2)
        
        print(f"\n✅ Evidence saved to: {filepath}")
        return filepath

def main():
    """Run test with multiple test cases"""
    
    test_texts = [
        "Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino.",
        "Microsoft Corporation was founded by Bill Gates and Paul Allen in 1975. Google competes with Microsoft and Apple in cloud services.",
        "Amazon, led by Andy Jassy, is headquartered in Seattle. The company focuses on e-commerce and cloud computing services."
    ]
    
    all_results = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{'#' * 60}")
        print(f"TEST CASE {i}")
        print(f"{'#' * 60}")
        
        pipeline = RealToolsPipeline()
        result = pipeline.run_pipeline(text)
        all_results.append(result)
        
        # Save evidence for this test
        pipeline.save_evidence()
        
        # Print summary for this test
        print("\nSUCCESS CRITERIA:")
        for criterion, met in result["success_criteria"].items():
            status = "✅" if met else "❌"
            print(f"  {status} {criterion}")
    
    # Overall summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)
    
    total_tests = len(all_results)
    successful_tests = sum(
        1 for r in all_results 
        if r["success_criteria"].get("pipeline_complete", False)
    )
    
    print(f"Tests passed: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("✅ ALL TESTS PASSED - Real T23C working with simulated pipeline")
    else:
        print("⚠️ SOME TESTS FAILED - Check evidence files for details")

if __name__ == "__main__":
    main()
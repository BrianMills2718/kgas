#!/usr/bin/env python3
"""
Measure actual precision of relationship discovery
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.cross_document_linker import CrossDocumentLinker
from typing import List, Dict, Any, Set, Tuple


def create_test_documents_with_ground_truth():
    """Create test documents with known relationships"""
    documents = [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing in 2023. Her work at Stanford University focuses on treating genetic diseases using precision medicine approaches.",
            "metadata": {"authors": ["Dr. Sarah Chen"], "date": "2023-03-15"}
        },
        {
            "path": "doc2.txt", 
            "content": "The CRISPR-Cas9 system has revolutionized biotechnology since Jennifer Doudna's pioneering work led to breakthrough discoveries. Recent advances by researchers like Sarah Chen have shown promising results in clinical trials.",
            "metadata": {"authors": ["Dr. Michael Rodriguez"], "date": "2023-05-20"}
        },
        {
            "path": "doc3.txt",
            "content": "Stanford University's genetics program has been at the forefront of precision medicine. Dr. Chen's recent publication demonstrates the potential of gene therapy for hereditary conditions.",
            "metadata": {"authors": ["Prof. Lisa Wang"], "date": "2023-07-10"}
        },
        {
            "path": "doc4.txt",
            "content": "Jennifer Doudna received the Nobel Prize for CRISPR development. Her collaboration with Emmanuelle Charpentier laid the foundation for modern gene editing technologies.",
            "metadata": {"authors": ["Science Writer"], "date": "2023-08-15"}
        }
    ]
    
    # Ground truth relationships (simplified - not exhaustive)
    ground_truth_relationships = [
        # Causal relationships
        ("Sarah Chen", "research", "causal"),  # Sarah Chen published research
        ("Jennifer Doudna", "breakthrough discoveries", "causal"),  # Doudna's work led to discoveries
        ("Jennifer Doudna", "CRISPR development", "causal"),  # Doudna developed CRISPR
        
        # Temporal relationships  
        ("research", "2023", "temporal"),  # Research in 2023
        ("Nobel Prize", "CRISPR development", "temporal"),  # Prize after development
        
        # Associative relationships
        ("Sarah Chen", "Stanford University", "associative"),  # Chen at Stanford
        ("Jennifer Doudna", "Emmanuelle Charpentier", "associative"),  # Collaboration
        ("CRISPR", "gene editing", "associative"),  # CRISPR is gene editing
        
        # Hierarchical relationships
        ("Stanford University", "genetics program", "hierarchical"),  # University has program
        ("gene therapy", "precision medicine", "hierarchical"),  # Gene therapy is part of precision medicine
    ]
    
    return documents, ground_truth_relationships


def normalize_entity(entity: str) -> str:
    """Normalize entity names for comparison"""
    # Simple normalization - lowercase and remove extra spaces
    normalized = entity.lower().strip()
    # Remove common prefixes
    for prefix in ["dr.", "prof.", "professor"]:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    return normalized


def evaluate_discovered_relationships(discovered_rels, ground_truth):
    """Calculate precision and recall for discovered relationships"""
    
    # Normalize and create sets for comparison
    discovered_set = set()
    for rel_type, rel_list in discovered_rels.items():
        if hasattr(rel_list, '__iter__'):
            for rel in rel_list:
                if hasattr(rel, 'source_entity') and hasattr(rel, 'target_entity'):
                    source = normalize_entity(str(rel.source_entity))
                    target = normalize_entity(str(rel.target_entity))
                    rel_type_str = getattr(rel, 'relationship_type', rel_type)
                    discovered_set.add((source, target, rel_type_str))
    
    # Normalize ground truth
    ground_truth_set = set()
    for source, target, rel_type in ground_truth:
        ground_truth_set.add((normalize_entity(source), normalize_entity(target), rel_type))
    
    # Find matches (we'll be lenient and count partial matches)
    true_positives = 0
    partial_matches = []
    
    for disc_rel in discovered_set:
        disc_source, disc_target, disc_type = disc_rel
        
        # Check for exact match
        if disc_rel in ground_truth_set:
            true_positives += 1
        else:
            # Check for partial matches (same entities, maybe different type)
            for gt_source, gt_target, gt_type in ground_truth_set:
                if (disc_source in gt_source or gt_source in disc_source) and \
                   (disc_target in gt_target or gt_target in disc_target):
                    partial_matches.append((disc_rel, (gt_source, gt_target, gt_type)))
                    true_positives += 0.5  # Give half credit for partial matches
                    break
    
    false_positives = len(discovered_set) - true_positives
    false_negatives = len(ground_truth_set) - true_positives
    
    precision = true_positives / len(discovered_set) if discovered_set else 0
    recall = true_positives / len(ground_truth_set) if ground_truth_set else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_discovered": len(discovered_set),
        "total_ground_truth": len(ground_truth_set),
        "discovered_relationships": discovered_set,
        "partial_matches": partial_matches
    }


async def measure_relationship_discovery_precision():
    """Measure actual precision of relationship discovery"""
    
    # Get test data with ground truth
    documents, ground_truth = create_test_documents_with_ground_truth()
    
    # Run relationship discovery
    linker = CrossDocumentLinker()
    all_relationships = await linker.discover_all_relationships(documents)
    
    # Extract discovered relationships into a unified format
    discovered = {"all": []}
    
    # Causal relationships
    if "causal_relationships" in all_relationships:
        for rel in all_relationships["causal_relationships"].causal_relationships:
            discovered["all"].append(rel)
    
    # Hierarchical relationships from concept hierarchy
    if "concept_hierarchy" in all_relationships:
        for rel in all_relationships["concept_hierarchy"].concept_relationships:
            discovered["all"].append(rel)
    
    # Get cached relationships
    for entity, rels in linker.relationship_cache.items():
        for rel in rels:
            if isinstance(rel, dict):
                # Convert dict to object-like structure
                class RelObj:
                    def __init__(self, d):
                        self.source_entity = d.get('source_entity', '')
                        self.target_entity = d.get('target_entity', '')
                        self.relationship_type = d.get('relationship_type', '')
                discovered["all"].append(RelObj(rel))
            else:
                discovered["all"].append(rel)
    
    # Calculate metrics
    metrics = evaluate_discovered_relationships(discovered, ground_truth)
    
    print("=" * 60)
    print("RELATIONSHIP DISCOVERY PRECISION MEASUREMENT")
    print("=" * 60)
    
    print(f"\nDataset:")
    print(f"  Documents: {len(documents)}")
    print(f"  Ground truth relationships: {len(ground_truth)}")
    
    print(f"\nDiscovered Relationships by Type:")
    for key in ["causal_relationships", "temporal_relationships", "influence_network", "concept_hierarchy"]:
        if key in all_relationships:
            result = all_relationships[key]
            if hasattr(result, '__dict__'):
                attrs = vars(result)
                for attr_name, attr_value in attrs.items():
                    if isinstance(attr_value, list):
                        print(f"  {key}.{attr_name}: {len(attr_value)} items")
    
    print(f"\nAccuracy Metrics:")
    print(f"  Precision: {metrics['precision']:.2%} (correct relationships / all discovered)")
    print(f"  Recall: {metrics['recall']:.2%} (correct relationships / all ground truth)")
    print(f"  F1 Score: {metrics['f1_score']:.2%}")
    
    print(f"\nDetailed Counts:")
    print(f"  Total discovered: {metrics['total_discovered']}")
    print(f"  Total ground truth: {metrics['total_ground_truth']}")
    print(f"  True Positives: {metrics['true_positives']}")
    print(f"  False Positives: {metrics['false_positives']:.1f}")
    print(f"  False Negatives: {metrics['false_negatives']:.1f}")
    
    # Show example discovered relationships
    print(f"\nExample Discovered Relationships:")
    for i, rel in enumerate(list(metrics['discovered_relationships'])[:10]):
        source, target, rel_type = rel
        print(f"  {i+1}. {source} -> {target} ({rel_type})")
    
    print(f"\n{'='*60}")
    print(f"OVERALL PRECISION: {metrics['precision']:.1%}")
    print(f"{'='*60}")
    
    return metrics


if __name__ == "__main__":
    metrics = asyncio.run(measure_relationship_discovery_precision())
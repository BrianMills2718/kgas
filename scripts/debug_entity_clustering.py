#!/usr/bin/env python3
"""
Debug entity clustering to understand why SpaCy resolver is creating too many clusters
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver_spacy import SpacyEntityResolver
from scripts.measure_entity_accuracy import create_test_documents_with_ground_truth


async def debug_clustering():
    """Debug the clustering algorithm"""
    
    # Get test data
    documents, ground_truth = create_test_documents_with_ground_truth()
    
    print("=" * 70)
    print("DEBUGGING ENTITY CLUSTERING")
    print("=" * 70)
    
    # Create SpaCy resolver
    spacy_resolver = SpacyEntityResolver()
    
    # Extract entity references from all documents
    print("\n1. EXTRACTING ENTITIES FROM DOCUMENTS:")
    print("-" * 40)
    all_entity_refs = []
    for doc in documents:
        entity_refs = await spacy_resolver._extract_entity_references_spacy(doc)
        print(f"\nDocument: {doc['path']}")
        for ref in entity_refs:
            print(f"  - {ref.entity_name} ({ref.entity_type}) - confidence: {ref.confidence_score:.3f}")
            all_entity_refs.append(ref)
    
    print(f"\nTotal entity references extracted: {len(all_entity_refs)}")
    
    # Debug clustering process
    print("\n2. CLUSTERING ENTITIES:")
    print("-" * 40)
    
    # Group by type first
    from collections import defaultdict
    entities_by_type = defaultdict(list)
    for ref in all_entity_refs:
        entities_by_type[ref.entity_type].append(ref)
    
    print(f"Entity types found: {list(entities_by_type.keys())}")
    for entity_type, refs in entities_by_type.items():
        print(f"  {entity_type}: {len(refs)} references")
    
    # Focus on PERSON entities (most problematic)
    person_refs = entities_by_type.get("PERSON", [])
    print(f"\n3. ANALYZING PERSON ENTITY CLUSTERING ({len(person_refs)} references):")
    print("-" * 40)
    
    # Show unique names
    unique_names = set(ref.entity_name for ref in person_refs)
    print(f"Unique person names: {unique_names}")
    
    # Test similarity calculations
    print("\n4. TESTING SIMILARITY CALCULATIONS:")
    print("-" * 40)
    
    test_pairs = [
        ("Sarah Chen", "Chen"),
        ("Sarah Chen", "Dr. Sarah Chen"),
        ("Sarah Chen", "James Chen"),
        ("Jennifer Doudna", "Jennifer Doudna's"),
        ("Chen", "Chen"),
    ]
    
    # Create dummy refs for testing
    for name1, name2 in test_pairs:
        ref1 = next((r for r in person_refs if r.entity_name == name1), None)
        ref2 = next((r for r in person_refs if r.entity_name == name2), None)
        
        if ref1 and ref2:
            similarity = spacy_resolver._calculate_entity_similarity_smart(ref1, ref2)
            print(f"'{name1}' vs '{name2}': similarity = {similarity:.3f} (threshold = {spacy_resolver.similarity_threshold})")
    
    # Now do actual clustering
    print("\n5. ACTUAL CLUSTERING RESULTS:")
    print("-" * 40)
    clusters = spacy_resolver._cluster_entities_smart(all_entity_refs)
    
    print(f"Total clusters created: {len(clusters)}")
    
    # Show cluster details
    for i, cluster in enumerate(clusters[:10]):  # Show first 10 clusters
        members = [ref.entity_name for ref in cluster.entity_references]
        print(f"\nCluster {i+1}: {cluster.canonical_name} ({cluster.entity_type})")
        print(f"  Members: {members}")
        print(f"  Confidence: {cluster.cluster_confidence:.3f}")
    
    # Analyze problematic clusters
    print("\n6. CLUSTER ANALYSIS:")
    print("-" * 40)
    
    # Find Sarah Chen clusters
    sarah_clusters = [c for c in clusters if "Sarah" in c.canonical_name or "Chen" in c.canonical_name]
    print(f"Clusters related to Sarah Chen: {len(sarah_clusters)}")
    for cluster in sarah_clusters:
        members = [ref.entity_name for ref in cluster.entity_references]
        print(f"  - {cluster.canonical_name}: {members}")
    
    # Find singleton clusters (only one member)
    singleton_clusters = [c for c in clusters if len(c.entity_references) == 1]
    print(f"\nSingleton clusters (only 1 member): {len(singleton_clusters)}/{len(clusters)}")
    
    # Ground truth comparison
    print("\n7. GROUND TRUTH COMPARISON:")
    print("-" * 40)
    print(f"Expected clusters: {len(ground_truth)}")
    print("Expected entities:")
    for entity_id, mentions in ground_truth.items():
        print(f"  - {entity_id}: {mentions}")
    
    print("\n" + "=" * 70)
    print("DEBUGGING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(debug_clustering())
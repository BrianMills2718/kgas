#!/usr/bin/env python3
"""
Debug entity resolution to understand why accuracy is low
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver import EntityResolver

async def debug_entity_resolution():
    """Debug entity resolution step by step"""
    
    # Simple test case with known expected links
    test_doc = {
        "path": "test.txt",
        "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing in 2023. Her work at Stanford University focuses on treating genetic diseases.",
        "metadata": {"authors": ["Dr. Sarah Chen"]}
    }
    
    resolver = EntityResolver()
    
    # Extract entity references from single document
    entity_refs = resolver._extract_entity_references(test_doc)
    
    print("=" * 60)
    print("EXTRACTED ENTITY REFERENCES:")
    print("=" * 60)
    
    for i, ref in enumerate(entity_refs):
        print(f"\n{i+1}. Entity: '{ref.entity_name}'")
        print(f"   Type: {ref.entity_type}")
        print(f"   Context: ...{ref.mention_context[:50]}...")
        print(f"   Confidence: {ref.confidence_score:.2f}")
        print(f"   Position: {ref.position_in_doc}")
        print(f"   Aliases: {ref.aliases}")
    
    # Check if we found "Her" as a pronoun reference
    pronoun_found = any("Her" in str(ref.aliases) for ref in entity_refs)
    print(f"\n'Her' pronoun detected: {pronoun_found}")
    
    # Now test clustering
    print("\n" + "=" * 60)
    print("TESTING ENTITY CLUSTERING:")
    print("=" * 60)
    
    clusters = resolver._cluster_entities(entity_refs)
    
    for i, cluster in enumerate(clusters):
        print(f"\nCluster {i+1}: {cluster.canonical_name}")
        print(f"  Type: {cluster.entity_type}")
        print(f"  Confidence: {cluster.cluster_confidence:.3f}")
        print(f"  Members ({len(cluster.entity_references)}):")
        for ref in cluster.entity_references:
            print(f"    - {ref.entity_name} (pos: {ref.position_in_doc})")
    
    # Test with multiple documents
    print("\n" + "=" * 60)
    print("TESTING CROSS-DOCUMENT RESOLUTION:")
    print("=" * 60)
    
    test_docs = [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR. Her work is influential.",
            "metadata": {"authors": ["Dr. Sarah Chen"]}
        },
        {
            "path": "doc2.txt",
            "content": "Sarah Chen has shown promising results. Dr. Chen's recent publication demonstrates potential.",
            "metadata": {"authors": ["Dr. Michael Rodriguez"]}
        }
    ]
    
    result = await resolver.resolve_entity_coreferences(test_docs)
    
    # Find Sarah Chen cluster
    sarah_cluster = None
    for cluster in result.entity_clusters:
        names = [ref.entity_name for ref in cluster.entity_references]
        if any("Sarah" in name for name in names):
            sarah_cluster = cluster
            break
    
    if sarah_cluster:
        print(f"\nSarah Chen cluster found!")
        print(f"  Canonical name: {sarah_cluster.canonical_name}")
        print(f"  Members: {len(sarah_cluster.entity_references)}")
        for ref in sarah_cluster.entity_references:
            print(f"    - '{ref.entity_name}' from {ref.document_path}")
    else:
        print("\nNo Sarah Chen cluster found!")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_entity_resolution())
#!/usr/bin/env python3
"""Debug the disambiguation test"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver import EntityResolver


async def debug_disambiguation():
    """Debug why James Chen isn't being identified"""
    
    # Create test documents
    ambiguous_docs = [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing. Chen's work focuses on genetic diseases.",
            "metadata": {}
        },
        {
            "path": "doc2.txt", 
            "content": "Dr. James Chen from Harvard Medical School published a study on cancer immunotherapy. This Dr. Chen is different from Sarah Chen at Stanford.",
            "metadata": {}
        },
        {
            "path": "doc3.txt",
            "content": "The Chen lab at Stanford continues to advance gene editing techniques.",
            "metadata": {}
        }
    ]
    
    entity_resolver = EntityResolver()
    result = await entity_resolver.disambiguate_entities(ambiguous_docs)
    
    print("=" * 70)
    print("DISAMBIGUATION DEBUG")
    print("=" * 70)
    
    print(f"\nTotal disambiguated entities: {len(result.disambiguated_entities)}")
    
    # Find Chen clusters
    chen_clusters = [cluster for cluster in result.disambiguated_entities
                    if any("chen" in ref.entity_name.lower() for ref in cluster.entity_references)]
    
    print(f"\nChen clusters found: {len(chen_clusters)}")
    
    for i, cluster in enumerate(chen_clusters):
        print(f"\n--- Chen Cluster {i+1} ---")
        print(f"Canonical name: {cluster.canonical_name}")
        print(f"Type: {cluster.entity_type}")
        print(f"Confidence: {cluster.cluster_confidence:.3f}")
        print(f"Disambiguation confidence: {cluster.disambiguation_confidence:.3f}")
        
        print("Entity references:")
        for ref in cluster.entity_references:
            print(f"  - {ref.entity_name} (doc: {ref.document_path})")
            print(f"    Context: {ref.mention_context[:100]}...")
        
        # Check for research areas
        contexts = [ref.mention_context.lower() for ref in cluster.entity_references]
        combined_context = " ".join(contexts)
        
        print("Research area detection:")
        if "crispr" in combined_context or "gene editing" in combined_context:
            print("  ✓ CRISPR/Gene editing research")
        if "cancer" in combined_context or "immunotherapy" in combined_context:
            print("  ✓ Cancer/Immunotherapy research")
        
        # Show disambiguation features if available
        if hasattr(cluster, 'disambiguation_features'):
            print(f"Disambiguation features: {cluster.disambiguation_features}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    sarah_chen_cluster = None
    james_chen_cluster = None
    
    for cluster in chen_clusters:
        contexts = [ref.mention_context.lower() for ref in cluster.entity_references]
        if any("crispr" in context or "gene editing" in context for context in contexts):
            sarah_chen_cluster = cluster
            print("✓ Found Sarah Chen cluster (CRISPR researcher)")
        elif any("cancer" in context or "immunotherapy" in context for context in contexts):
            james_chen_cluster = cluster
            print("✓ Found James Chen cluster (cancer researcher)")
    
    if sarah_chen_cluster is None:
        print("✗ Sarah Chen cluster NOT found")
    if james_chen_cluster is None:
        print("✗ James Chen cluster NOT found")
        
        # Debug why James Chen wasn't found
        print("\nDebugging James Chen extraction:")
        doc2_content = ambiguous_docs[1]["content"]
        print(f"Doc2 content: {doc2_content}")
        
        # Check if James Chen is extracted at all
        all_entities = []
        for cluster in result.disambiguated_entities:
            for ref in cluster.entity_references:
                all_entities.append(f"{ref.entity_name} ({ref.document_path})")
        
        print(f"\nAll extracted entities: {all_entities}")
        
        james_entities = [e for e in all_entities if "james" in e.lower()]
        print(f"James entities found: {james_entities}")


if __name__ == "__main__":
    asyncio.run(debug_disambiguation())
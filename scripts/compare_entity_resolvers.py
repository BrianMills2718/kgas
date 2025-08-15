#!/usr/bin/env python3
"""
Compare regex-based entity resolver with SpaCy-based entity resolver
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver import EntityResolver as RegexResolver
from src.relationships.entity_resolver_spacy import SpacyEntityResolver
from scripts.measure_entity_accuracy import create_test_documents_with_ground_truth, calculate_accuracy_metrics


async def compare_resolvers():
    """Compare performance of regex vs SpaCy entity resolvers"""
    
    # Get test data
    documents, ground_truth = create_test_documents_with_ground_truth()
    
    print("=" * 70)
    print("ENTITY RESOLVER COMPARISON: Regex vs SpaCy")
    print("=" * 70)
    
    # Test regex-based resolver
    print("\n1. REGEX-BASED ENTITY RESOLVER:")
    print("-" * 40)
    regex_resolver = RegexResolver()
    regex_result = await regex_resolver.resolve_entity_coreferences(documents)
    regex_metrics = calculate_accuracy_metrics(regex_result.entity_clusters, ground_truth)
    
    print(f"   Entity clusters found: {len(regex_result.entity_clusters)}")
    print(f"   Precision: {regex_metrics['precision']:.2%}")
    print(f"   Recall: {regex_metrics['recall']:.2%}")
    print(f"   F1 Score: {regex_metrics['f1_score']:.2%}")
    
    # Test SpaCy-based resolver
    print("\n2. SPACY-BASED ENTITY RESOLVER:")
    print("-" * 40)
    spacy_resolver = SpacyEntityResolver()
    spacy_result = await spacy_resolver.resolve_entity_coreferences(documents)
    spacy_metrics = calculate_accuracy_metrics(spacy_result.entity_clusters, ground_truth)
    
    print(f"   Entity clusters found: {len(spacy_result.entity_clusters)}")
    print(f"   Precision: {spacy_metrics['precision']:.2%}")
    print(f"   Recall: {spacy_metrics['recall']:.2%}")
    print(f"   F1 Score: {spacy_metrics['f1_score']:.2%}")
    
    # Calculate improvement
    print("\n3. IMPROVEMENT METRICS:")
    print("-" * 40)
    f1_improvement = (spacy_metrics['f1_score'] - regex_metrics['f1_score']) / regex_metrics['f1_score'] * 100
    precision_improvement = (spacy_metrics['precision'] - regex_metrics['precision']) / max(regex_metrics['precision'], 0.01) * 100
    recall_improvement = (spacy_metrics['recall'] - regex_metrics['recall']) / max(regex_metrics['recall'], 0.01) * 100
    
    print(f"   F1 Score Improvement: {f1_improvement:+.1f}%")
    print(f"   Precision Improvement: {precision_improvement:+.1f}%")
    print(f"   Recall Improvement: {recall_improvement:+.1f}%")
    
    # Show example clusters from SpaCy
    print("\n4. EXAMPLE SPACY CLUSTERS:")
    print("-" * 40)
    for i, cluster in enumerate(spacy_result.entity_clusters[:5]):
        entities = [f"{ref.entity_name} ({ref.entity_type})" for ref in cluster.entity_references]
        print(f"   Cluster {i+1}: {cluster.canonical_name}")
        print(f"      Type: {cluster.entity_type}")
        print(f"      Members: {', '.join(entities[:3])}")
        print(f"      Confidence: {cluster.cluster_confidence:.3f}")
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("-" * 40)
    
    if spacy_metrics['f1_score'] > regex_metrics['f1_score']:
        print(f"✅ SpaCy resolver is {f1_improvement:.1f}% better than regex resolver!")
    else:
        print(f"❌ SpaCy resolver needs more tuning (currently {f1_improvement:.1f}% worse)")
    
    print(f"\nTarget: >60% F1 Score")
    print(f"Current Best: {max(regex_metrics['f1_score'], spacy_metrics['f1_score']):.1%}")
    print(f"Gap to Target: {60 - max(regex_metrics['f1_score'], spacy_metrics['f1_score']) * 100:.1f} percentage points")
    
    print("=" * 70)
    
    return spacy_metrics, regex_metrics


if __name__ == "__main__":
    spacy_metrics, regex_metrics = asyncio.run(compare_resolvers())
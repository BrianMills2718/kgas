#!/usr/bin/env python3
"""
Measure actual accuracy of entity coreference resolution
"""

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver import EntityResolver
from typing import List, Dict, Any, Set, Tuple


def create_test_documents_with_ground_truth():
    """Create test documents with known entity coreferences"""
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
            "content": "Professor Jennifer Doudna at UC Berkeley won the Nobel Prize. Doudna's collaboration with Emmanuelle Charpentier was groundbreaking.",
            "metadata": {"authors": ["Science Writer"], "date": "2023-08-15"}
        },
        {
            "path": "doc5.txt",
            "content": "Dr. James Chen from Harvard Medical School published a study on cancer immunotherapy. This Dr. Chen is different from Sarah Chen at Stanford.",
            "metadata": {"authors": ["Medical Journal"], "date": "2023-09-01"}
        }
    ]
    
    # Ground truth: which entities should be linked together
    ground_truth = {
        "sarah_chen": {
            ("doc1.txt", "Dr. Sarah Chen"),
            ("doc1.txt", "Her"),  # Pronoun reference
            ("doc2.txt", "Sarah Chen"),
            ("doc3.txt", "Dr. Chen"),  # Assuming context makes it clear this is Sarah
        },
        "jennifer_doudna": {
            ("doc2.txt", "Jennifer Doudna"),
            ("doc4.txt", "Professor Jennifer Doudna"),
            ("doc4.txt", "Doudna"),
        },
        "stanford": {
            ("doc1.txt", "Stanford University"),
            ("doc3.txt", "Stanford University"),
        },
        "crispr": {
            ("doc1.txt", "CRISPR"),
            ("doc2.txt", "CRISPR-Cas9"),
        },
        "james_chen": {
            ("doc5.txt", "Dr. James Chen"),
            ("doc5.txt", "This Dr. Chen"),
        },
        "emmanuelle_charpentier": {
            ("doc4.txt", "Emmanuelle Charpentier"),
        }
    }
    
    return documents, ground_truth


def calculate_accuracy_metrics(predicted_clusters, ground_truth):
    """Calculate precision, recall, and F1 score"""
    
    # Convert predicted clusters to pairs of entities that are linked
    predicted_pairs = set()
    for cluster in predicted_clusters:
        entities = [(ref.document_path, ref.entity_name) for ref in cluster.entity_references]
        # Create all pairs within cluster
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                predicted_pairs.add(frozenset([entities[i], entities[j]]))
    
    # Convert ground truth to pairs
    true_pairs = set()
    for entity_group in ground_truth.values():
        entities = list(entity_group)
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                true_pairs.add(frozenset([entities[i], entities[j]]))
    
    # Calculate metrics
    true_positives = len(predicted_pairs & true_pairs)
    false_positives = len(predicted_pairs - true_pairs)
    false_negatives = len(true_pairs - predicted_pairs)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_predicted_pairs": len(predicted_pairs),
        "total_true_pairs": len(true_pairs)
    }


async def measure_entity_resolution_accuracy():
    """Measure actual accuracy of entity coreference resolution"""
    
    # Get test data with ground truth
    documents, ground_truth = create_test_documents_with_ground_truth()
    
    # Run entity resolution
    resolver = EntityResolver()
    result = await resolver.resolve_entity_coreferences(documents)
    
    # Calculate accuracy
    metrics = calculate_accuracy_metrics(result.entity_clusters, ground_truth)
    
    print("=" * 60)
    print("ENTITY COREFERENCE RESOLUTION ACCURACY MEASUREMENT")
    print("=" * 60)
    
    print(f"\nDataset:")
    print(f"  Documents: {len(documents)}")
    print(f"  Ground truth entity groups: {len(ground_truth)}")
    print(f"  Total ground truth pairs: {metrics['total_true_pairs']}")
    
    print(f"\nPrediction Results:")
    print(f"  Entity clusters found: {len(result.entity_clusters)}")
    print(f"  Total predicted pairs: {metrics['total_predicted_pairs']}")
    
    print(f"\nAccuracy Metrics:")
    print(f"  Precision: {metrics['precision']:.2%} (correct links / all predicted links)")
    print(f"  Recall: {metrics['recall']:.2%} (correct links / all true links)")
    print(f"  F1 Score: {metrics['f1_score']:.2%} (harmonic mean)")
    
    print(f"\nDetailed Counts:")
    print(f"  True Positives: {metrics['true_positives']} (correctly linked pairs)")
    print(f"  False Positives: {metrics['false_positives']} (incorrectly linked pairs)")
    print(f"  False Negatives: {metrics['false_negatives']} (missed links)")
    
    # Show example clusters for debugging
    print(f"\nExample Clusters Found:")
    for i, cluster in enumerate(result.entity_clusters[:5]):
        entities = [f"{ref.entity_name} ({ref.document_path})" for ref in cluster.entity_references]
        print(f"  Cluster {i+1} (confidence {cluster.cluster_confidence:.3f}): {entities}")
    
    # Overall accuracy (for the claim)
    overall_accuracy = metrics['f1_score']
    print(f"\n{'='*60}")
    print(f"OVERALL ACCURACY (F1 Score): {overall_accuracy:.1%}")
    print(f"{'='*60}")
    
    return metrics


if __name__ == "__main__":
    metrics = asyncio.run(measure_entity_resolution_accuracy())
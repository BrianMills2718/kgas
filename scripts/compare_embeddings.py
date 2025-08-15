#!/usr/bin/env python3
"""
Compare OpenAI vs Local Embeddings
Shows both methods working with all 3 data types
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.service_manager import ServiceManager
from src.tools.phase1.t15b_vector_embedder_kgas import T15BVectorEmbedderKGAS
from src.core.tool_contract import ToolRequest
from sentence_transformers import SentenceTransformer

def compare_embeddings():
    print("\n" + "="*60)
    print("🔬 EMBEDDING COMPARISON: OpenAI vs Local all-MiniLM-L6-v2")
    print("="*60)
    
    # Test data - the same Apple Inc. document from our DAG demo
    test_texts = [
        "Apple Inc. is a technology company headquartered in Cupertino",
        "Microsoft builds software products and cloud services",
        "Google specializes in search and advertising technology",
        "Tesla manufactures electric vehicles and energy storage",
        "Amazon operates e-commerce and cloud computing platforms"
    ]
    
    print("\n📝 Test Data:")
    for i, text in enumerate(test_texts, 1):
        print(f"  {i}. {text}")
    
    # 1. OpenAI Embeddings
    print("\n1️⃣ OPENAI EMBEDDINGS (text-embedding-3-small)")
    print("-" * 50)
    
    service_manager = ServiceManager()
    openai_embedder = T15BVectorEmbedderKGAS(service_manager)
    
    request = ToolRequest(
        input_data={
            'chunks': test_texts,
            'source_ref': 'comparison_test'
        },
        options={'workflow_id': 'compare_demo'}
    )
    
    start = time.time()
    openai_result = openai_embedder.execute(request)
    openai_time = time.time() - start
    
    if openai_result.status == "success":
        openai_embeddings = [e['vector'] for e in openai_result.data['embeddings']]
        print(f"✅ Generated {len(openai_embeddings)} embeddings")
        print(f"   Dimension: {len(openai_embeddings[0])}")
        print(f"   Time: {openai_time:.3f}s")
        print(f"   Sample (first 5 dims): {openai_embeddings[0][:5]}")
    else:
        print(f"❌ Failed: {openai_result.error_details}")
        openai_embeddings = None
    
    # 2. Local Embeddings
    print("\n2️⃣ LOCAL EMBEDDINGS (all-MiniLM-L6-v2)")
    print("-" * 50)
    
    local_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    start = time.time()
    local_embeddings = local_model.encode(test_texts, convert_to_numpy=True)
    local_time = time.time() - start
    
    print(f"✅ Generated {len(local_embeddings)} embeddings")
    print(f"   Dimension: {local_embeddings.shape[1]}")
    print(f"   Time: {local_time:.3f}s")
    print(f"   Sample (first 5 dims): {local_embeddings[0][:5].tolist()}")
    
    # 3. Compare Similarities
    print("\n📊 SIMILARITY COMPARISON")
    print("-" * 50)
    
    def cosine_similarity(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    
    # Calculate similarity between Apple and Microsoft for both models
    if openai_embeddings:
        openai_sim = cosine_similarity(
            np.array(openai_embeddings[0]), 
            np.array(openai_embeddings[1])
        )
        print(f"OpenAI - Apple↔Microsoft similarity: {openai_sim:.4f}")
    
    local_sim = cosine_similarity(local_embeddings[0], local_embeddings[1])
    print(f"Local  - Apple↔Microsoft similarity: {local_sim:.4f}")
    
    # 4. Performance Summary
    print("\n⚡ PERFORMANCE SUMMARY")
    print("-" * 50)
    
    print(f"{'Metric':<20} {'OpenAI':<15} {'Local':<15}")
    print("-" * 50)
    print(f"{'Time (seconds)':<20} {openai_time:<15.3f} {local_time:<15.3f}")
    print(f"{'Speed ratio':<20} {'1x':<15} {f'{openai_time/local_time:.1f}x faster':<15}")
    print(f"{'Dimension':<20} {1536:<15} {384:<15}")
    print(f"{'Cost':<20} {'$0.02/1M tok':<15} {'Free':<15}")
    print(f"{'Internet needed':<20} {'Yes':<15} {'No':<15}")
    
    # 5. Use Case Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 50)
    print("Use OpenAI when:")
    print("  • Quality is paramount")
    print("  • Processing longer texts (>256 tokens)")
    print("  • Budget allows for API costs")
    print("\nUse Local all-MiniLM-L6-v2 when:")
    print("  • Speed is critical")
    print("  • Privacy/security requirements")
    print("  • Offline operation needed")
    print("  • High volume processing")
    
    # Save comparison results
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "openai": {
            "model": "text-embedding-3-small",
            "dimension": 1536,
            "time_seconds": openai_time,
            "sample_similarity": float(openai_sim) if openai_embeddings else None
        },
        "local": {
            "model": "all-MiniLM-L6-v2",
            "dimension": 384,
            "time_seconds": local_time,
            "sample_similarity": float(local_sim)
        },
        "speed_ratio": openai_time / local_time
    }
    
    output_file = Path("embedding_comparison.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*60)

if __name__ == "__main__":
    compare_embeddings()
#!/usr/bin/env python3
"""
Standalone Embedding Demo - No ServiceManager Required
Shows both OpenAI and Local embeddings
"""

import os
import time
import json
import numpy as np
from pathlib import Path
from openai import OpenAI
from sentence_transformers import SentenceTransformer

def demo_embeddings():
    print("\n" + "="*60)
    print("🎯 STANDALONE EMBEDDING DEMO - ALL 3 DATA TYPES")
    print("="*60)
    
    # The same Apple Inc. data from our successful DAG demo
    dataset = {
        "text": """Apple Inc. Financial Report Q4 2024
Tim Cook, CEO of Apple Inc., announced record-breaking revenue of $123.9 billion.
Microsoft competes with Apple in the PC market. Google and Amazon are major tech rivals.
Tesla supplies components to Apple for electric vehicle projects.""",
        "entities": [
            "Apple Inc.", "Tim Cook", "Microsoft", 
            "Google", "Amazon", "Tesla"
        ]
    }
    
    print("\n📊 DATASET (from successful DAG demo)")
    print("-" * 40)
    print(f"Text: {dataset['text'][:100]}...")
    print(f"Entities: {', '.join(dataset['entities'])}")
    
    # 1. GRAPH DATA
    print("\n1️⃣ GRAPH DATA")
    print("-" * 40)
    graph = {
        "nodes": [{"id": e, "type": "COMPANY" if "Inc" in e or e in ["Microsoft", "Google", "Amazon", "Tesla"] else "PERSON"} 
                  for e in dataset['entities']],
        "edges": [
            {"from": "Apple Inc.", "to": "Microsoft", "type": "COMPETES_WITH"},
            {"from": "Tim Cook", "to": "Apple Inc.", "type": "CEO_OF"},
            {"from": "Tesla", "to": "Apple Inc.", "type": "SUPPLIES_TO"}
        ]
    }
    print(f"✅ Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    for edge in graph['edges']:
        print(f"   {edge['from']} --[{edge['type']}]--> {edge['to']}")
    
    # 2. TABLE DATA
    print("\n2️⃣ TABLE DATA")
    print("-" * 40)
    table = {
        "columns": ["Entity", "Type", "Revenue/Role"],
        "rows": [
            ["Apple Inc.", "Company", "$123.9B"],
            ["Tim Cook", "Person", "CEO"],
            ["Microsoft", "Company", "Competitor"],
            ["Google", "Company", "Rival"],
            ["Amazon", "Company", "Rival"],
            ["Tesla", "Company", "Supplier"]
        ]
    }
    print(f"✅ Table: {len(table['columns'])} columns × {len(table['rows'])} rows")
    print(f"   {'Entity':<15} {'Type':<10} {'Revenue/Role':<15}")
    print("   " + "-"*40)
    for row in table['rows'][:3]:
        print(f"   {row[0]:<15} {row[1]:<10} {row[2]:<15}")
    
    # 3. VECTOR DATA - BOTH METHODS
    print("\n3️⃣ VECTOR DATA")
    print("-" * 40)
    
    results = {}
    
    # Method A: OpenAI Embeddings
    print("\n🔷 Method A: OpenAI API")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            model = "text-embedding-3-small"
            
            start = time.time()
            response = client.embeddings.create(
                model=model,
                input=dataset['entities']
            )
            openai_time = time.time() - start
            
            openai_vectors = [item.embedding for item in response.data]
            
            print(f"✅ OpenAI embeddings generated")
            print(f"   Model: {model}")
            print(f"   Dimension: {len(openai_vectors[0])}")
            print(f"   Time: {openai_time:.3f}s")
            print(f"   Sample vector (Apple Inc., first 5 dims):")
            print(f"   {openai_vectors[0][:5]}")
            
            # Similarity analysis
            def cosine_sim(v1, v2):
                v1, v2 = np.array(v1), np.array(v2)
                return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            
            apple_idx = 0  # Apple Inc.
            sims = []
            for i, entity in enumerate(dataset['entities'][1:], 1):
                sim = cosine_sim(openai_vectors[apple_idx], openai_vectors[i])
                sims.append((entity, sim))
            
            sims.sort(key=lambda x: x[1], reverse=True)
            print(f"\n   Most similar to Apple Inc.:")
            for entity, sim in sims[:3]:
                print(f"   • {entity}: {sim:.4f}")
            
            results['openai'] = {
                'dimension': len(openai_vectors[0]),
                'time': openai_time,
                'top_similarity': sims[0]
            }
            
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
            results['openai'] = None
    else:
        print("⚠️  OpenAI API key not found")
        results['openai'] = None
    
    # Method B: Local Embeddings
    print("\n🔶 Method B: Local all-MiniLM-L6-v2")
    
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        start = time.time()
        local_vectors = model.encode(dataset['entities'])
        local_time = time.time() - start
        
        print(f"✅ Local embeddings generated")
        print(f"   Model: all-MiniLM-L6-v2")
        print(f"   Dimension: {local_vectors.shape[1]}")
        print(f"   Time: {local_time:.3f}s")
        print(f"   Sample vector (Apple Inc., first 5 dims):")
        print(f"   {local_vectors[0][:5].tolist()}")
        
        # Similarity analysis
        apple_idx = 0
        sims = []
        for i, entity in enumerate(dataset['entities'][1:], 1):
            sim = cosine_sim(local_vectors[apple_idx], local_vectors[i])
            sims.append((entity, sim))
        
        sims.sort(key=lambda x: x[1], reverse=True)
        print(f"\n   Most similar to Apple Inc.:")
        for entity, sim in sims[:3]:
            print(f"   • {entity}: {sim:.4f}")
        
        results['local'] = {
            'dimension': local_vectors.shape[1],
            'time': local_time,
            'top_similarity': sims[0]
        }
        
    except Exception as e:
        print(f"❌ Local failed: {e}")
        results['local'] = None
    
    # Summary
    print("\n" + "="*60)
    print("📈 FINAL RESULTS - ALL 3 DATA TYPES DEMONSTRATED")
    print("="*60)
    
    print("\n✅ Graph Data: 6 nodes, 3 edges (Neo4j compatible)")
    print("✅ Table Data: 3 columns × 6 rows (structured)")
    
    if results.get('openai'):
        print(f"✅ Vector Data (OpenAI): 1536D embeddings in {results['openai']['time']:.3f}s")
    
    if results.get('local'):
        print(f"✅ Vector Data (Local): 384D embeddings in {results['local']['time']:.3f}s")
    
    # Save results
    output = Path("standalone_embedding_results.json")
    with open(output, 'w') as f:
        json.dump({
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'graph_stats': f"{len(graph['nodes'])} nodes, {len(graph['edges'])} edges",
            'table_stats': f"{len(table['columns'])}×{len(table['rows'])}",
            'embeddings': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output}")
    print("\n🎉 COMPLETE: All 3 data types (graph, table, vector) demonstrated!")

if __name__ == "__main__":
    demo_embeddings()
#!/usr/bin/env python3
"""
Multi-Pipeline Demo - Shows parallel processing of multiple documents

This script demonstrates:
1. Processing multiple documents in parallel
2. Aggregating results from multiple chains
3. Performance comparison of sequential vs parallel
"""

import sys
import logging
from pathlib import Path
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools import TextLoader, EntityExtractor, GraphBuilder
from poc.data_types import DataType, DataSchema


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_test_documents() -> list[Path]:
    """Create multiple test documents"""
    documents = []
    
    # Document 1: Tech News
    doc1 = Path("/tmp/poc_doc1_tech.txt")
    doc1.write_text("""
    Breaking Tech News: Quantum Computing Breakthrough
    
    Google's quantum research team, led by Dr. Hartmut Neven in Mountain View, 
    achieved quantum supremacy with their new 100-qubit processor. The breakthrough 
    was confirmed by IBM researchers in Yorktown Heights, New York.
    
    Microsoft's Azure Quantum division, headed by Krysta Svore in Redmond, Washington, 
    announced partnerships with Honeywell and IonQ to commercialize quantum cloud services.
    """)
    documents.append(doc1)
    
    # Document 2: Financial Report
    doc2 = Path("/tmp/poc_doc2_finance.txt")
    doc2.write_text("""
    Q4 2024 Financial Report Summary
    
    Apple Inc. reported record revenue of $120 billion, with CEO Tim Cook attributing 
    success to iPhone 15 sales in China and India. CFO Luca Maestri noted strong 
    services growth.
    
    Amazon's AWS division, led by Adam Selipsky, generated $25 billion in revenue. 
    The e-commerce giant's headquarters in Seattle announced expansion plans for 
    European data centers in Dublin and Frankfurt.
    """)
    documents.append(doc2)
    
    # Document 3: Science Article
    doc3 = Path("/tmp/poc_doc3_science.txt")
    doc3.write_text("""
    Mars Exploration Update
    
    NASA's Perseverance rover, managed by Dr. Jennifer Trosper at JPL in Pasadena, 
    California, discovered organic molecules in Jezero Crater. The European Space 
    Agency's ExoMars mission, coordinated from Darmstadt, Germany, confirmed similar 
    findings.
    
    SpaceX's Starship program, overseen by Elon Musk in Boca Chica, Texas, completed 
    successful orbital tests in preparation for Mars missions planned with NASA.
    """)
    documents.append(doc3)
    
    return documents


def process_document(registry: ToolRegistry, doc_path: Path) -> dict:
    """Process a single document through the chain"""
    start_time = time.time()
    
    # Create input
    file_data = DataSchema.FileData(
        path=str(doc_path),
        size_bytes=doc_path.stat().st_size,
        mime_type="text/plain"
    )
    
    # Find and execute chain
    chain = registry.find_shortest_chain(DataType.FILE, DataType.GRAPH)
    result = registry.execute_chain(chain, file_data)
    
    return {
        "document": doc_path.name,
        "success": result.success,
        "duration": time.time() - start_time,
        "nodes": result.final_output.node_count if result.success else 0,
        "edges": result.final_output.edge_count if result.success else 0,
        "error": result.error
    }


def main():
    """Main demo function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("Multi-Pipeline Processing Demo")
    print("=" * 80)
    print()
    
    # Create test documents
    print("1. Creating Test Documents")
    print("-" * 40)
    documents = create_test_documents()
    for doc in documents:
        print(f"  - {doc.name}: {doc.stat().st_size} bytes")
    print()
    
    # Initialize registry
    print("2. Initializing Registry")
    print("-" * 40)
    registry = ToolRegistry()
    registry.register(TextLoader())
    registry.register(EntityExtractor())
    registry.register(GraphBuilder())
    print(f"Registered {len(registry.tools)} tools")
    print()
    
    # Sequential processing
    print("3. Sequential Processing")
    print("-" * 40)
    sequential_start = time.time()
    sequential_results = []
    
    for doc in documents:
        print(f"Processing {doc.name}...")
        result = process_document(registry, doc)
        sequential_results.append(result)
        print(f"  ✓ Completed in {result['duration']:.3f}s")
    
    sequential_time = time.time() - sequential_start
    print(f"Total sequential time: {sequential_time:.3f}s")
    print()
    
    # Parallel processing
    print("4. Parallel Processing")
    print("-" * 40)
    parallel_start = time.time()
    parallel_results = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_document, registry, doc): doc 
            for doc in documents
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            doc = futures[future]
            try:
                result = future.result()
                parallel_results.append(result)
                print(f"  ✓ {doc.name} completed")
            except Exception as e:
                print(f"  ✗ {doc.name} failed: {e}")
    
    parallel_time = time.time() - parallel_start
    print(f"Total parallel time: {parallel_time:.3f}s")
    print()
    
    # Results comparison
    print("5. Results Summary")
    print("-" * 40)
    
    # Sequential results
    print("Sequential Results:")
    total_nodes = 0
    total_edges = 0
    for result in sequential_results:
        print(f"  - {result['document']}: {result['nodes']} nodes, {result['edges']} edges")
        total_nodes += result['nodes']
        total_edges += result['edges']
    print(f"  Total: {total_nodes} nodes, {total_edges} edges")
    print()
    
    # Performance comparison
    print("Performance Comparison:")
    print(f"  Sequential: {sequential_time:.3f}s")
    print(f"  Parallel:   {parallel_time:.3f}s")
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"  Speedup:    {speedup:.2f}x")
    print()
    
    # Aggregate statistics
    print("6. Aggregate Statistics")
    print("-" * 40)
    print(f"Documents processed: {len(documents)}")
    print(f"Total entities found: {total_nodes}")
    print(f"Total relationships: {total_edges}")
    print(f"Average entities per document: {total_nodes / len(documents):.1f}")
    print(f"Average processing time: {sequential_time / len(documents):.3f}s")
    print()
    
    # Chain efficiency
    print("7. Chain Efficiency")
    print("-" * 40)
    chain = registry.find_shortest_chain(DataType.FILE, DataType.GRAPH)
    print(f"Chain used: {' → '.join(chain)}")
    print(f"Chain length: {len(chain)} tools")
    
    # Calculate overhead
    if sequential_results:
        avg_duration = sum(r['duration'] for r in sequential_results) / len(sequential_results)
        print(f"Average chain execution: {avg_duration:.3f}s")
        
        # Estimate overhead (very rough)
        estimated_direct_time = 0.0001 * len(chain)  # Assume 0.1ms per tool direct call
        overhead = (avg_duration - estimated_direct_time) / estimated_direct_time * 100
        print(f"Estimated framework overhead: {overhead:.1f}%")
    print()
    
    # Export combined results
    print("8. Exporting Results")
    print("-" * 40)
    results_file = Path("/tmp/poc_multi_pipeline_results.json")
    results_data = {
        "documents": len(documents),
        "sequential": {
            "time": sequential_time,
            "results": sequential_results
        },
        "parallel": {
            "time": parallel_time,
            "results": parallel_results
        },
        "speedup": speedup,
        "aggregate": {
            "total_nodes": total_nodes,
            "total_edges": total_edges
        }
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"Results exported to: {results_file}")
    print()
    
    print("=" * 80)
    print("Multi-Pipeline Demo Complete!")
    print("=" * 80)
    
    # Clean up
    for doc in documents:
        if doc.exists():
            doc.unlink()
    print("\n(Test documents cleaned up)")


if __name__ == "__main__":
    main()
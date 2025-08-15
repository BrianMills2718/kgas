#!/usr/bin/env python3
"""
Test to measure ACTUAL sequential vs parallel execution times for multi-document processing.
This will provide real evidence of speedup, not estimates.
"""

import asyncio
import time
from pathlib import Path
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.orchestration.real_dag_orchestrator import RealDAGOrchestrator
from src.core.service_manager import get_service_manager
from test_multi_document_dag import create_test_documents, build_multi_document_dag


async def measure_sequential_execution(documents):
    """Execute DAG nodes sequentially and measure time"""
    print("\n" + "="*60)
    print("📊 SEQUENTIAL EXECUTION TEST")
    print("="*60)
    
    service_manager = get_service_manager()
    orchestrator = RealDAGOrchestrator(service_manager)
    
    # Add Phase C tools
    from src.tools.phase_c.temporal_tool import TemporalTool
    from src.tools.phase_c.clustering_tool import ClusteringTool
    from src.tools.phase_c.cross_modal_tool import CrossModalTool
    from src.tools.phase_c.collaborative_tool import CollaborativeTool
    
    orchestrator.tools['TEMPORAL'] = TemporalTool(service_manager)
    orchestrator.tools['CLUSTERING'] = ClusteringTool(service_manager)
    orchestrator.tools['CROSS_MODAL'] = CrossModalTool(service_manager)
    orchestrator.tools['COLLABORATIVE'] = CollaborativeTool(service_manager)
    
    # Build DAG
    build_multi_document_dag(orchestrator, documents)
    
    # Force sequential execution by modifying the orchestrator
    original_execute = orchestrator.execute_dag
    
    async def sequential_execute(input_data):
        """Execute all nodes sequentially"""
        orchestrator.validate_dag()
        completed = set()
        results = {}
        
        while len(completed) < len(orchestrator.nodes):
            ready = orchestrator.get_ready_nodes(completed)
            
            if not ready:
                pending = [n for n in orchestrator.nodes if n not in completed]
                raise RuntimeError(f"Deadlock detected. Pending nodes: {pending}")
            
            # Execute ready nodes ONE AT A TIME (sequential)
            for node_id in ready:
                print(f"  Sequential execution: {node_id}")
                # Pass the right data for each node
                node = orchestrator.nodes[node_id]
                node_specific_data = input_data.copy()
                
                # For document loaders, add the document path
                if 'load_doc' in node_id:
                    doc_index = int(node_id.replace('load_doc', ''))
                    if doc_index < len(documents):
                        node_specific_data['document'] = str(documents[doc_index])
                        node.parameters = {'document': str(documents[doc_index])}
                
                result = await orchestrator.execute_node(node_id, node_specific_data)
                results[node_id] = result
                completed.add(node_id)
        
        return results
    
    # Execute sequentially
    start_time = time.time()
    
    input_data = {
        "workflow_id": "sequential_test",
        "documents": [str(d) for d in documents]
    }
    
    results = await sequential_execute(input_data)
    
    sequential_time = time.time() - start_time
    
    print(f"\n✅ Sequential Execution Complete")
    print(f"  Total nodes: {len(orchestrator.nodes)}")
    print(f"  Execution time: {sequential_time:.3f}s")
    
    return sequential_time, len(orchestrator.nodes)


async def measure_parallel_execution(documents):
    """Execute DAG with parallel execution and measure time"""
    print("\n" + "="*60)
    print("🚀 PARALLEL EXECUTION TEST")
    print("="*60)
    
    service_manager = get_service_manager()
    orchestrator = RealDAGOrchestrator(service_manager)
    
    # Add Phase C tools
    from src.tools.phase_c.temporal_tool import TemporalTool
    from src.tools.phase_c.clustering_tool import ClusteringTool
    from src.tools.phase_c.cross_modal_tool import CrossModalTool
    from src.tools.phase_c.collaborative_tool import CollaborativeTool
    
    orchestrator.tools['TEMPORAL'] = TemporalTool(service_manager)
    orchestrator.tools['CLUSTERING'] = ClusteringTool(service_manager)
    orchestrator.tools['CROSS_MODAL'] = CrossModalTool(service_manager)
    orchestrator.tools['COLLABORATIVE'] = CollaborativeTool(service_manager)
    
    # Build DAG
    build_multi_document_dag(orchestrator, documents)
    
    # Execute with parallel support (default)
    start_time = time.time()
    
    input_data = {
        "workflow_id": "parallel_test",
        "documents": [str(d) for d in documents]
    }
    
    results = await orchestrator.execute_dag(input_data)
    
    parallel_time = time.time() - start_time
    
    print(f"\n✅ Parallel Execution Complete")
    print(f"  Total nodes: {len(orchestrator.nodes)}")
    print(f"  Execution time: {parallel_time:.3f}s")
    
    return parallel_time, len(orchestrator.nodes)


async def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🔬 MEASURING ACTUAL SEQUENTIAL VS PARALLEL EXECUTION TIMES")
    print("="*80)
    
    # Create test documents
    print("\n📄 Creating Test Documents...")
    documents = create_test_documents(3)
    
    try:
        # Measure sequential execution
        seq_time, num_nodes = await measure_sequential_execution(documents)
        
        # Measure parallel execution
        par_time, _ = await measure_parallel_execution(documents)
        
        # Calculate actual speedup
        actual_speedup = seq_time / par_time if par_time > 0 else 0
        
        print("\n" + "="*80)
        print("📈 PERFORMANCE COMPARISON - ACTUAL MEASUREMENTS")
        print("="*80)
        
        print(f"\n🔧 Sequential Execution:")
        print(f"   Time: {seq_time:.3f}s")
        print(f"   Nodes: {num_nodes}")
        print(f"   Avg per node: {seq_time/num_nodes:.3f}s")
        
        print(f"\n🚀 Parallel Execution:")
        print(f"   Time: {par_time:.3f}s")
        print(f"   Nodes: {num_nodes}")
        print(f"   Avg per node: {par_time/num_nodes:.3f}s")
        
        print(f"\n✨ Actual Speedup:")
        print(f"   Speedup: {actual_speedup:.2f}x")
        print(f"   Time saved: {seq_time - par_time:.3f}s")
        print(f"   Efficiency: {(1 - par_time/seq_time)*100:.1f}%")
        
        # Create evidence file
        evidence = f"""# Evidence: Actual Sequential vs Parallel Execution Measurements

## Date: {datetime.now().isoformat()}

## Test Configuration
- Documents: {len(documents)}
- DAG Nodes: {num_nodes}
- Test Type: Real execution with timing

## Measured Results

### Sequential Execution
- **Total Time**: {seq_time:.3f}s
- **Average per Node**: {seq_time/num_nodes:.3f}s

### Parallel Execution  
- **Total Time**: {par_time:.3f}s
- **Average per Node**: {par_time/num_nodes:.3f}s

### Performance Metrics
- **Actual Speedup**: {actual_speedup:.2f}x
- **Time Saved**: {seq_time - par_time:.3f}s
- **Efficiency Gain**: {(1 - par_time/seq_time)*100:.1f}%

## Validation
These are ACTUAL measured times, not estimates. Both executions processed the same documents through the same DAG structure.

## Conclusion
{"✅ SPEEDUP CONFIRMED" if actual_speedup > 1.5 else "⚠️ LIMITED SPEEDUP"}: Measured speedup of {actual_speedup:.2f}x
"""
        
        with open("Evidence_Actual_Speedup_Measurement.md", "w") as f:
            f.write(evidence)
        
        print(f"\n📄 Evidence file created: Evidence_Actual_Speedup_Measurement.md")
        
        return actual_speedup
        
    finally:
        # Cleanup
        for doc in documents:
            if doc.exists():
                doc.unlink()


if __name__ == "__main__":
    speedup = asyncio.run(main())
    print(f"\n{'✅' if speedup > 1.5 else '⚠️'} Final Result: {speedup:.2f}x speedup")